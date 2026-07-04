from crewai import Agent  # type: ignore
from config.config import llm
from tools.inventory_tool import query_inventory_db, update_inventory_stock

def get_inventory_agent() -> Agent:
    return Agent(
        role="Inventory Monitoring Watcher",
        goal="Compare active stock counts vs reorder thresholds and emit a prioritized list of items needing replenishment.",
        backstory="You are the hyper-vigilant warehouse tracking system for HexaShop. You scan on-hand quantities across all regions to prevent severe supply deficits.",
        tools=[query_inventory_db, update_inventory_stock],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )