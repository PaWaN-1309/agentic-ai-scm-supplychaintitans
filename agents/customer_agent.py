from crewai import Agent # type: ignore
from config.config import llm
from tools.notify_tool import notify_tool # type: ignore

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
    tools=[notify_tool],
    llm=llm,
    verbose=True
)