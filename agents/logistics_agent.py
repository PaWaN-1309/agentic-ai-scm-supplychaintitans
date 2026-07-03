from crewai import Agent # type: ignore
from config.config import llm
from tools.shipping_tool import shipping_tool

logistics_agent = Agent(
    name="LogisticsAgent",
    role="Logistics Coordinator",
    goal="""
        Plan shipment schedules and recommend the best logistics
        options for product delivery.
    """,
    backstory="""
        You coordinate warehouse dispatch, transportation,
        and delivery schedules to ensure timely product movement.
    """,
    tools=[shipping_tool],
    llm=llm,
    verbose=True
)
