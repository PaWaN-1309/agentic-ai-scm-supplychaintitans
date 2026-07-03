from crewai import Agent # type: ignore
from config.config import llm

procurement_agent = Agent(
    name="ProcurementAgent",
    role="Procurement Specialist",
    goal="""
        Recommend suppliers and generate purchase recommendations
        whenever inventory replenishment is required.
    """,
    backstory="""
        You specialize in supplier selection, procurement planning,
        and purchase order recommendations while considering
        supplier reliability and cost.
    """,
    tools=[],
    llm=llm,
    verbose=True
)

