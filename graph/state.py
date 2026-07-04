from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict  # type: ignore

class SCMState(TypedDict):
    """
    Shared orchestration state representing the data context 
    passed between nodes in the supply chain workflow.
    """
    sku: str                             # Target SKU being evaluated
    warehouse: str                       # Targeted warehouse location
    current_question: str                # User prompt text (For UC-1 Q&A Routing)
    single_agent_response: str           # Stores direct answers from UC-1 agent
    low_stock_items: List[Dict[str, Any]]# Identified replenishment items
    draft_po: Optional[Dict[str, Any]]   # Structured PO object from Procurement Specialist
    po_approved: Optional[bool]          # Human Reviewer Checkpoint status: True/False/None
    action_taken: str                    # Audit text logging completion actions
    logs: List[str]                      # Observability text trace list