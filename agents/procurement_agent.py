from crewai import Agent # type: ignore
from config.config import llm
from tools.supplier_tool import supplier_tool

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
    tools=[supplier_tool],
    llm=llm,
    verbose=True
)

