from crewai import Agent # type: ignore
from config.config import llm
from tools.inventory_tool import inventory_tool # type: ignore

inventory_agent = Agent(
    name="InventoryAgent",
    role="Inventory Monitoring Specialist",
    goal="Monitor inventory levels, identify low-stock products, \
            and provide accurate inventory status to the supply chain manager.",
    backstory="You are an experienced inventory analyst responsible for monitoring \
        warehouse stock levels. You help identify products that require \
        replenishment before stock shortages occur.",
    tools=[inventory_tool],
    llm=llm,
    verbose=True
)