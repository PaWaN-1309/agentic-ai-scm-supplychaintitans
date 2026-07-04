from crewai import Agent  # type: ignore
from config.config import llm
from tools.shipping_tool import get_shipping_options

def get_logistics_agent() -> Agent:
    return Agent(
        role="Logistics & Routing Optimizer",
        goal="Compare available carriers on transit costs and ETAs to produce an optimized fulfilment plan for pending orders.",
        backstory="You are an expert distribution planner at HexaShop. You minimize shipping spend and optimize routes across every coverage region.",
        tools=[get_shipping_options],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )