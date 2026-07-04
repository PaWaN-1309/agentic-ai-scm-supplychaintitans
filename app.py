import sys
from config.config import LLM_READY, PURCHASE_APPROVAL_LIMIT
from graph.workflow import build_scm_graph

def run_use_case_1_demo(graph):
    print("\n==================================================")
    print("RUNNING USE CASE 1: Single-Agent Inventory Q&A")
    print("==================================================")
    
    # Configuration thread required for LangGraph memory tracking
    config = {"configurable": {"thread_id": "uc1_test_thread"}}
    
    # Input dictionary matching our SCMState schema
    initial_input = {
        "sku": "",
        "warehouse": "",
        "current_question": "Can you check the database and tell me the on_hand stock and reorder point for SKU: 1001?",
        "single_agent_response": "",
        "low_stock_items": [],
        "draft_po": None,
        "po_approved": None,
        "action_taken": "",
        "logs": []
    }
    
    print(f"User Question: {initial_input['current_question']}\nThinking...")
    
    # Execute the graph
    final_state = graph.invoke(initial_input, config)
    
    print("\n--- Agent Response ---")
    print(final_state.get("single_agent_response"))
    print("==================================================\n")


def run_use_case_2_demo(graph):
    print("==================================================")
    print("RUNNING USE CASE 2: Multi-Agent Replenishment Loop")
    print("==================================================")
    
    # Use a separate unique thread for the automated replenishment flow
    config = {"configurable": {"thread_id": "uc2_replenish_thread"}}
    
    # Target an item that is currently under its reorder threshold (e.g., ELC-1001)
    initial_input = {
        "sku": "ELC-1001",
        "warehouse": "North DC",
        "current_question": "",  # Empty question signals the multi-agent automation path
        "single_agent_response": "",
        "low_stock_items": [],
        "draft_po": None,
        "po_approved": None,
        "action_taken": "",
        "logs": []
    }
    
    print(f"Starting automatic stock analysis for SKU: {initial_input['sku']} at {initial_input['warehouse']}...")
    
    # Step 1: Run the graph until it hits the registered human interrupt breakpoint
    for event in graph.stream(initial_input, config, stream_mode="values"):
        current_po = event.get("draft_po")
        if current_po:
            print(f"\n[CrewAI Agent Alert] Draft Purchase Order Generated:")
            print(f" - SKU: {current_po.get('sku')}")
            print(f" - Quantity: {current_po.get('qty')}")
            print(f" - Supplier ID: {current_po.get('supplier')}")
            print(f" - Total Value: ${current_po.get('total_cost')}")
    
    # Step 2: Read the runtime state to confirm the graph is currently paused
    graph_state = graph.get_state(config)
    
    if graph_state.next:
        print(f"\n[LangGraph Human Gate] Execution paused before node: '{graph_state.next[0]}'")
        print(f"Approval Limit Threshold Configuration: ${PURCHASE_APPROVAL_LIMIT}")
        
        # Simulate human operator choice directly via terminal input
        user_choice = input("\nDo you approve placing this Purchase Order? (Y/N): ").strip().upper()
        is_approved = True if user_choice == 'Y' else False
        
        # Step 3: Write the human operator decision back into the checkpoint state
        print("\nUpdating state with decision and resuming graph execution...")
        graph.update_state(config, {"po_approved": is_approved}, as_node="human_approval_node")
        
        # Step 4: Resume execution by passing None as the input along with the same config thread
        for event in graph.stream(None, config, stream_mode="values"):
            if event.get("action_taken"):
                print("\n--- Final Workflow Outcome ---")
                print(event.get("action_taken"))
    else:
        print("\nWorkflow finished immediately without needing an approval gate check.")
    
    print("==================================================")


if __name__ == "__main__":
    print("Initializing HexaShop SCM Agentic System...")
    
    if not LLM_READY:
        print("\n[CRITICAL ERROR] Azure OpenAI credentials are missing or incorrect in your .env file.")
        print("Please check your deployment name, endpoint, and security keys.")
        sys.exit(1)
        
    # Build and compile our state machine graph with memory checkpointers
    scm_graph = build_scm_graph()
    
    # Execute Use Case 1 Demo
    run_use_case_1_demo(scm_graph)
    
    # Execute Use Case 2 Demo
    run_use_case_2_demo(scm_graph)