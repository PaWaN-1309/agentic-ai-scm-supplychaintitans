from langgraph.graph import StateGraph, END  # type: ignore
from langgraph.checkpoint.memory import MemorySaver  # type: ignore
from config.config import PURCHASE_APPROVAL_LIMIT
from graph.state import SCMState
from graph.nodes import (
    inventory_qa_node,
    monitor_and_forecast_node,
    procurement_draft_node,
    human_approval_node,
    finalize_order_node
)

def route_initial_intent(state: SCMState) -> str:
    """Evaluates whether incoming trigger is a single-agent question or automated replenishment cycle."""
    if state.get("current_question", "").strip():
        return "single_agent_branch"
    return "multi_agent_replenishment_branch"

def route_approval_limit(state: SCMState) -> str:
    """Conditional Edge: Inspects PO limit to determine if high-stakes approval gate is triggered."""
    po = state.get("draft_po")
    if not po:
        return "skip_to_end"
        
    total_cost = po.get("total_cost", 0.0)
    # Check if PO value exceeds configurable human approval threshold limits
    if total_cost > PURCHASE_APPROVAL_LIMIT:
        return "trigger_human_interrupt"
    return "bypass_straight_to_finalize"

def build_scm_graph():
    """Initializes and builds the stateful supply chain graph architecture."""
    workflow = StateGraph(SCMState)
    
    # 1. Register operational node blocks
    workflow.add_node("inventory_qa_node", inventory_qa_node)
    workflow.add_node("monitor_and_forecast_node", monitor_and_forecast_node)
    workflow.add_node("procurement_draft_node", procurement_draft_node)
    workflow.add_node("human_approval_node", human_approval_node)
    workflow.add_node("finalize_order_node", finalize_order_node)
    
    # 2. Add Conditional Core Routing Entrances
    workflow.set_conditional_entry_point(
        route_initial_intent,
        {
            "single_agent_branch": "inventory_qa_node",
            "multi_agent_replenishment_branch": "monitor_and_forecast_node"
        }
    )
    
    # Simple straight-line path mappings for UC-1
    workflow.add_edge("inventory_qa_node", END)
    
    # Sequential structural execution flow links for UC-2
    workflow.add_edge("monitor_and_forecast_node", "procurement_draft_node")
    
    # 3. Insert Configurable Value Guardrail Conditional Routing
    workflow.add_conditional_edges(
        "procurement_draft_node",
        route_approval_limit,
        {
            "trigger_human_interrupt": "human_approval_node",
            "bypass_straight_to_finalize": "finalize_order_node",
            "skip_to_end": END
        }
    )
    
    workflow.add_edge("human_approval_node", "finalize_order_node")
    workflow.add_edge("finalize_order_node", END)
    
    # 4. Compile with built-in memory checkpoint and explicit human gate pauses
    memory = MemorySaver()
    compiled_graph = workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_approval_node"]  # Safe structural pause before high-stakes execution
    )
    return compiled_graph