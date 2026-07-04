import json
import pandas as pd  # type: ignore
from typing import Dict, Any
from crewai import Task # type: ignore
from config.config import PURCHASE_APPROVAL_LIMIT, INVENTORY_CSV
from agents.crew_setup import create_scm_crew
from agents.inventory_agent import get_inventory_agent
from tools.inventory_tool import query_inventory_db
from tools.notify_tool import send_system_notification
from graph.state import SCMState

def inventory_qa_node(state: SCMState) -> Dict[str, Any]:
    """UC-1 Single-Agent Workflow: Uses the Inventory Watcher to safely resolve user text queries."""
    question = state.get("current_question", "")
    logs = state.get("logs", [])
    logs.append("Executing Node: inventory_qa_node")
    
    # Ground the agent strictly by triggering its tool directly
    agent = get_inventory_agent()
    
    # Wrap the string query inside a formal CrewAI Task object instance
    qa_task = Task(
        description=f"Analyze the following data table request and provide a clear, accurate response: {question}. Use the tool provided.",
        expected_output="The exact stock level (on_hand) and reorder point metrics directly from the data logs for the requested SKU.",
        agent=agent
    )
    
    # Execute passing the newly instantiated Task object wrapper
    response = agent.execute_task(task=qa_task)
    
    return {
        "single_agent_response": str(response),
        "logs": logs
    }

def monitor_and_forecast_node(state: SCMState) -> Dict[str, Any]:
    """UC-2 Step 1: Evaluates current inventory and forecasts demand run rates."""
    sku = state.get("sku", "").strip().upper()
    wh = state.get("warehouse", "").strip().upper()
    logs = state.get("logs", [])
    logs.append(f"Executing Node: monitor_and_forecast_node for SKU {sku}")
    
    low_stock_list = []
    try:
        df = pd.read_csv(INVENTORY_CSV)
        
        # Robust filtering logic supporting partial SKUs
        mask = df['sku'].str.upper() == sku
        if wh:
            mask = mask & (df['warehouse'].str.upper() == wh)
            
        target_rows = df[mask]
        
        # Substring fallback matching block
        if target_rows.empty:
            mask = df['sku'].str.upper().str.contains(sku, na=False)
            if wh:
                mask = mask & (df['warehouse'].str.upper() == wh)
            target_rows = df[mask]
        
        for _, row in target_rows.iterrows():
            if int(row['on_hand']) <= int(row['reorder_point']):
                low_stock_list.append({
                    "sku": row['sku'],
                    "warehouse": row['warehouse'],
                    "on_hand": int(row['on_hand']),
                    "reorder_qty": int(row['reorder_qty'])
                })
    except Exception as e:
        logs.append(f"Error checking inventory limits: {str(e)}")
        
    return {
        "low_stock_items": low_stock_list,
        "logs": logs
    }

def procurement_draft_node(state: SCMState) -> Dict[str, Any]:
    """UC-2 Step 2: Utilizes CrewAI sequential processing to pick a supplier and draft a PO."""
    items = state.get("low_stock_items", [])
    logs = state.get("logs", [])
    logs.append("Executing Node: procurement_draft_node")
    
    if not items:
        logs.append("No low stock items detected. Skipping PO compilation.")
        return {"draft_po": None, "logs": logs}
    
    target_sku = items[0]["sku"]
    # Instantiates CrewAI structure to run sub-tasks
    crew = create_scm_crew(target_sku=target_sku)
    crew_output = crew.kickoff()
    
    # Clean extract pattern to extract raw JSON configuration blocks safely
    raw_str = str(crew_output).strip()
    if "```json" in raw_str:
        raw_str = raw_str.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_str:
        raw_str = raw_str.split("```")[1].split("```")[0].strip()
        
    try:
        po_dict = json.loads(raw_str)
    except Exception:
        # Secure fallback parsing method to keep system completely crash-resilient
        po_dict = {
            "sku": target_sku,
            "qty": items[0]["reorder_qty"],
            "supplier": "SUPPLIER_01",
            "unit_cost": 25.0,
            "total_cost": float(items[0]["reorder_qty"] * 25.0),
            "lead_time_days": 5
        }
        logs.append("Failed JSON parse; generated graceful fallback PO dict record.")
        
    return {
        "draft_po": po_dict,
        "logs": logs
    }

def human_approval_node(state: SCMState) -> Dict[str, Any]:
    """
    UC-2 Step 3 (HITL Breakpoint Node): 
    This is an explicit placeholder node. Graph compilation will automatically interrupt BEFORE this 
    node executes, allowing an external actor to approve, reject, or edit state parameters.
    """
    logs = state.get("logs", [])
    logs.append("Executing Node: human_approval_node (Resuming after Human Gate Checkpoint)")
    return {"logs": logs}

def finalize_order_node(state: SCMState) -> Dict[str, Any]:
    """UC-2 Step 4: Finalizes orders by committing inventory levels or broadcasting tracking updates."""
    po = state.get("draft_po")
    approved = state.get("po_approved", False)
    logs = state.get("logs", [])
    logs.append("Executing Node: finalize_order_node")
    
    if not po:
        return {"action_taken": "No active PO was drafted for fulfillment.", "logs": logs}
        
    if approved:
        action = f"Successfully placed purchase order for {po['qty']} units of SKU {po['sku']} with Supplier {po['supplier']}."
        # Dispatch external communication logs via simulated tool alerts
        send_system_notification.func(
            recipient_id="SCM_Manager", 
            channel="Email", 
            message=action
        )
    else:
        action = f"Purchase Order for SKU {po['sku']} was explicitly REJECTED/CANCELLED by human reviewer."
        
    return {
        "action_taken": action,
        "logs": logs
    }