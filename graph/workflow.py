from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import SCMState
from graph.approval_node import approval_node

from config.config import LLM_READY

from tools.forecast_tool import forecast_tool
from tools.supplier_tool import supplier_tool
from tools.shipping_tool import shipping_tool
from tools.notify_tool import notify_tool

try:
    from agents.forecast_agent import forecast_agent
    from agents.procurement_agent import procurement_agent
    from agents.logistics_agent import logistics_agent
    from agents.customer_agent import customer_agent
except Exception:
    forecast_agent = procurement_agent = logistics_agent = customer_agent = None

# Highest possible PO with the sample data is ~$1,559, so the threshold
# must sit below that for the human-approval path to be reachable.
APPROVAL_THRESHOLD = 1000

NOTIFY_CUSTOMER_ID = "CUS-5000"


def _agent_result(agent):
    """Run a CrewAI agent and return its dict output, or None when the
    LLM is not configured or the agent fails."""
    if not LLM_READY or agent is None:
        return None
    try:
        result = agent.kickoff()
        return result if isinstance(result, dict) else None
    except Exception:
        return None


def forecast_node(state: SCMState):
    result = _agent_result(forecast_agent)
    if result is None:
        tool_out = forecast_tool.run(sku=state["sku"])
        result = {
            "predicted_demand": int(tool_out.get("Expected Demand", 0)),
            "demand_level": tool_out.get("Demand Level", "Low"),
        } if isinstance(tool_out, dict) else {}
    return {
        "predicted_demand": result.get("predicted_demand", 0),
        "demand_level": result.get("demand_level", "Low"),
        "current_node": "forecast",
        "next_node": "inventory",
        "execution_history": state.get("execution_history", [])
        + ["Forecast Completed"]
    }


def inventory_node(state: SCMState):
    current_stock = state["current_stock"]
    reorder_level = state["reorder_level"]
    inventory_status = (
        "LOW_STOCK"
        if current_stock < reorder_level
        else "SUFFICIENT"
    )
    return {
        "inventory_status": inventory_status,
        "current_node": "inventory",
        "next_node": "supplier",
        "execution_history": state["execution_history"]
        + ["Inventory Checked"]
    }


def supplier_node(state: SCMState):
    result = _agent_result(procurement_agent)
    if result is None:
        tool_out = supplier_tool.run(sku=state["sku"])
        result = {
            "supplier_name": tool_out.get("Supplier Name"),
            "supplier_rating": tool_out.get("Supplier Rating"),
            "supplier_price": tool_out.get("Price"),
            "delivery_time": f"{tool_out.get('Delivery Time')} days",
        } if isinstance(tool_out, dict) and "Supplier Name" in tool_out else {}
    return {
        "supplier_name": result.get("supplier_name"),
        "supplier_rating": result.get("supplier_rating"),
        "supplier_price": result.get("supplier_price"),
        "delivery_time": result.get("delivery_time"),
        "current_node": "supplier",
        "next_node": "purchase_order",
        "execution_history": state["execution_history"]
        + ["Supplier Selected"]
    }


def po_node(state: SCMState):
    quantity = max(
        state["predicted_demand"] - state["current_stock"],
        0
    )
    unit_price = state.get("supplier_price") or 0.0
    total_cost = quantity * unit_price
    return {
        "po_number": f"PO-{state['sku']}",
        "po_quantity": quantity,
        "po_total_cost": total_cost,
        "approval_required": total_cost > APPROVAL_THRESHOLD,
        "current_node": "purchase_order",
        "execution_history": state["execution_history"]
        + ["PO Created"]
    }


def approval_router(state: SCMState):
    if state["approval_required"]:
        return "approval"
    return "shipping"


def shipping_node(state: SCMState):
    result = _agent_result(logistics_agent)
    if result is None:
        tool_out = shipping_tool.run(region="North")
        result = {
            "courier": tool_out.get("Courier"),
            "eta": tool_out.get("ETA"),
            "tracking_id": tool_out.get("Tracking ID"),
        } if isinstance(tool_out, dict) and "Courier" in tool_out else {}
    return {
        "courier": result.get("courier"),
        "eta": result.get("eta"),
        "tracking_id": result.get("tracking_id"),
        "current_node": "shipping",
        "next_node": "notification",
        "execution_history": state["execution_history"]
        + ["Shipping Planned"]
    }


def notification_node(state: SCMState):
    message = (
        f"Purchase order {state.get('po_number')} for "
        f"{state.get('po_quantity')} units of {state.get('sku')} has been "
        f"placed with {state.get('supplier_name')}. Shipment is planned via "
        f"{state.get('courier')} (ETA {state.get('eta')}, tracking "
        f"{state.get('tracking_id')})."
    )
    result = _agent_result(customer_agent)
    if result is None:
        try:
            notify_tool.run(
                customer_id=NOTIFY_CUSTOMER_ID,
                message=message,
                channel="email"
            )
        except Exception:
            pass
        notification_message = message
    else:
        notification_message = str(result)
    return {
        "notification_sent": True,
        "notification_message": notification_message,
        "workflow_status": "COMPLETED",
        "current_node": "notification",
        "final_response":
            f"PO {state['po_number']} approved and shipment created.",
        "execution_history": state["execution_history"]
        + ["Notification Sent"]
    }


def rejected_node(state: SCMState):
    return {
        "workflow_status": "REJECTED",
        "final_response":
            f"PO {state['po_number']} was rejected.",
        "execution_history": state["execution_history"]
        + ["PO Rejected"]
    }


def approval_result_router(state: SCMState):
    if state["approval_status"].lower() in ["approved", "edited"]:
        return "shipping"
    return "rejected"


workflow = StateGraph(SCMState)

workflow.add_node("forecast", forecast_node)
workflow.add_node("inventory", inventory_node)
workflow.add_node("supplier", supplier_node)
workflow.add_node("purchase_order", po_node)
workflow.add_node("approval", approval_node)
workflow.add_node("shipping", shipping_node)
workflow.add_node("notification", notification_node)
workflow.add_node("rejected", rejected_node)

workflow.set_entry_point("forecast")

workflow.add_edge("forecast", "inventory")
workflow.add_edge("inventory", "supplier")
workflow.add_edge("supplier", "purchase_order")

workflow.add_conditional_edges(
    "purchase_order",
    approval_router,
    {
        "approval": "approval",
        "shipping": "shipping"
    }
)

workflow.add_conditional_edges(
    "approval",
    approval_result_router,
    {
        "shipping": "shipping",
        "rejected": "rejected"
    }
)

workflow.add_edge("shipping", "notification")
workflow.add_edge("notification", END)
workflow.add_edge("rejected", END)

memory = MemorySaver()

graph = workflow.compile(
    checkpointer=memory
)
