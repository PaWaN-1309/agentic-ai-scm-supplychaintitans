from crewai import Agent # type: ignore
from config.config import llm

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
    tools=[],
    llm=llm,
    verbose=True
)
