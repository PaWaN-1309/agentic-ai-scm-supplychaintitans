from crewai import Agent # type: ignore
from config.config import llm

customer_agent = Agent(
    name="CustomerAgent",
    role="Customer Communication Specialist",
    goal="""
        Prepare customer-friendly notifications regarding
        order status, shipment updates, and supply delays.
    """,
    backstory="""
        You are responsible for maintaining customer satisfaction
        by communicating accurate and timely updates about
        order processing and deliveries.
    """,
    tools=[],
    llm=llm,
    verbose=True
)