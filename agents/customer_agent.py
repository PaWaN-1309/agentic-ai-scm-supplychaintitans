from crewai import Agent  # type: ignore
from config.config import llm
from tools.notify_tool import send_system_notification

def get_customer_agent() -> Agent:
    return Agent(
        role="Customer Comms Communicator",
        goal="Draft clear, empathetic, and professional order-status updates and delay notifications for HexaShop customers.",
        backstory="You are the voice of customer care at HexaShop. You proactively eliminate uncertainty by broadcasting transactional statuses.",
        tools=[send_system_notification],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )