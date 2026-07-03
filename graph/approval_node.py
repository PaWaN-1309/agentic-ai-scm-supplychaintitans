from datetime import datetime
from typing import Any, Optional
from langgraph.types import interrupt, Command
from langgraph.errors import GraphInterrupt
from graph.state import SCMState


def log_event(message: str) -> None:
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(f"[{timestamp}] {message}")


def _format_reason(state: SCMState) -> str:
    total_cost = state.get("po_total_cost", 0.0) or 0.0
    quantity = state.get("po_quantity", 0) or 0
    if total_cost > 10000.0:
        return f"Purchase order total cost (${total_cost:,.2f}) exceeds high-value threshold."
    if quantity > 500:
        return f"Order quantity ({quantity}) exceeds standard inventory replenishment limits."
    return "Standard manual review threshold for procurement operations."


def _display_approval_request(state: SCMState, reason: str) -> None:
    po_number = state.get("po_number", "N/A")
    sku = state.get("sku", "N/A")
    supplier = state.get("supplier_name", "N/A")
    quantity = state.get("po_quantity", 0)
    price = state.get("supplier_price", 0.0)
    total_cost = state.get("po_total_cost", 0.0)
    warehouse = state.get("warehouse", "N/A")
    delivery_time = state.get("delivery_time", "N/A")

    print("\n" + "=" * 60)
    print("                 SCM HUMAN APPROVAL REQUIRED")
    print("=" * 60)
    print(f"PO Number           : {po_number}")
    print(f"SKU                 : {sku}")
    print(f"Supplier            : {supplier}")
    print(f"Quantity            : {quantity}")
    print(f"Unit Price          : ${price:,.2f}")
    print(f"Total Cost          : ${total_cost:,.2f}")
    print(f"Warehouse           : {warehouse}")
    print(f"Delivery Time       : {delivery_time}")
    print(f"Reason for Approval : {reason}")
    print("=" * 60 + "\n")


def approval_node(state: SCMState) -> Command | SCMState:
    try:
        if not state.get("approval_required", False):
            return state

        reason = _format_reason(state)
        _display_approval_request(state, reason)

        payload = {
            "po_number": state.get("po_number"),
            "sku": state.get("sku"),
            "supplier": state.get("supplier_name"),
            "quantity": state.get("po_quantity"),
            "unit_price": state.get("supplier_price"),
            "total_cost": state.get("po_total_cost"),
            "warehouse": state.get("warehouse"),
            "delivery_time": state.get("delivery_time"),
            "reason_for_approval": reason
        }

        log_event("Approval Requested")
        
        response = interrupt(payload)
        
        log_event("Workflow Resumed")

        if "execution_history" not in state or state["execution_history"] is None:
            state["execution_history"] = []

        if not response:
            raise ValueError("Empty or missing approval response payload.")

        if not isinstance(response, dict):
            raise TypeError("Approval response must be a structured dictionary.")

        action = response.get("action")
        if not action:
            raise ValueError("Response payload is missing the 'action' field.")

        action_upper = str(action).upper()

        if action_upper == "APPROVED":
            state["approval_status"] = "APPROVED"
            state["workflow_status"] = "Approved"
            state["execution_history"].append("Approval Node: Approved")
            log_event("Approval Approved")

        elif action_upper == "REJECTED":
            state["approval_status"] = "REJECTED"
            state["workflow_status"] = "Rejected"
            state["final_response"] = "Purchase Order Rejected by Human."
            state["execution_history"].append("Approval Node: Rejected")
            log_event("Approval Rejected")

        elif action_upper == "EDITED":
            data = response.get("data") or response.get("edited_data") or response
            
            raw_quantity = data.get("quantity") or data.get("po_quantity")
            raw_supplier = data.get("supplier") or data.get("supplier_name")
            raw_price = data.get("price") or data.get("supplier_price")
            raw_delivery_time = data.get("delivery_time")

            if raw_quantity is not None:
                state["po_quantity"] = int(raw_quantity)
            if raw_supplier is not None:
                state["supplier_name"] = str(raw_supplier)
            if raw_price is not None:
                state["supplier_price"] = float(raw_price)
            if raw_delivery_time is not None:
                state["delivery_time"] = str(raw_delivery_time)

            if raw_quantity is not None or raw_price is not None:
                qty = state.get("po_quantity", 0) or 0
                price = state.get("supplier_price", 0.0) or 0.0
                state["po_total_cost"] = float(qty * price)

            state["approval_status"] = "EDITED"
            state["workflow_status"] = "Edited and Approved"
            state["execution_history"].append(
                f"Approval Node: Edited (New Qty: {state.get('po_quantity')}, "
                f"Supplier: {state.get('supplier_name')}, Price: {state.get('supplier_price')}, "
                f"Delivery: {state.get('delivery_time')})"
            )
            log_event("Approval Edited")

        else:
            raise ValueError(f"Unexpected action value: {action}")

        return Command(update=state)

    except GraphInterrupt:
        raise
    except Exception as e:
        error_msg = f"Unexpected error during human approval handling: {str(e)}"
        log_event(error_msg)
        state["error"] = error_msg
        state["workflow_status"] = "Error"
        if "execution_history" not in state or state["execution_history"] is None:
            state["execution_history"] = []
        state["execution_history"].append(f"Approval Node Error: {error_msg}")
        return Command(update=state)
