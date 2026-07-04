from crewai import Agent  # type: ignore
from config.config import llm
from tools.supplier_tool import get_supplier_quotes
from prompts.procurement_prompt import PROCUREMENT_ROLE, PROCUREMENT_GOAL, PROCUREMENT_BACKSTORY

def get_procurement_agent() -> Agent:
    return Agent(
        role=PROCUREMENT_ROLE,
        goal=PROCUREMENT_GOAL,
        backstory=PROCUREMENT_BACKSTORY,
        tools=[get_supplier_quotes],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )