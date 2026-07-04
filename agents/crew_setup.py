from crewai import Crew, Process, Task  # type: ignore
from prompts.procurement_prompt import PROCUREMENT_TASK_TEMPLATE

# Import factory functions
from agents.inventory_agent import get_inventory_agent
from agents.forecast_agent import get_forecast_agent
from agents.procurement_agent import get_procurement_agent
from agents.logistics_agent import get_logistics_agent
from agents.customer_agent import get_customer_agent

def create_scm_crew(target_sku: str) -> Crew:
    """Creates and assembles the specialized supply chain crew context."""
    
    # Instantiate agents
    inventory_agent = get_inventory_agent()
    forecast_agent = get_forecast_agent()
    procurement_agent = get_procurement_agent()
    logistics_agent = get_logistics_agent()
    customer_agent = get_customer_agent()
    
    # 1. Define Forecasting Task
    forecast_task = Task(
        description=f"Analyze transaction demand history parameters and identify potential replenishment shortages for SKU: {target_sku}.",
        expected_output="A structured assessment highlighting average run rate and near-term deficit counts.",
        agent=forecast_agent
    )
    
    # 2. Define Procurement / Supplier Task
    procurement_task = Task(
        description=PROCUREMENT_TASK_TEMPLATE.format(items=target_sku, suppliers="supplier catalog listings"),
        expected_output="Raw JSON object containing: sku, qty, supplier, unit_cost, total_cost, lead_time_days.",
        agent=procurement_agent
    )
    
    # 3. Define Logistics Routing Task
    logistics_task = Task(
        description=f"Review available transit matrices to recommend the optimal freight provider for SKU: {target_sku}.",
        expected_output="A prioritized summary of carrier choices, costs, and arrival time estimates.",
        agent=logistics_agent
    )
    
    # Assemble Crew sequentially for clean processing flow
    return Crew(
        agents=[inventory_agent, forecast_agent, procurement_agent, logistics_agent, customer_agent],
        tasks=[forecast_task, procurement_task, logistics_task],
        process=Process.sequential,
        verbose=True
    )