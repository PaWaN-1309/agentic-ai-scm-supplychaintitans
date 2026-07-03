from crewai import Agent # type: ignore
from config.config import llm
from tools.forecast_tool import forecast_tool

forecast_agent = Agent(
    name="ForecastAgent",
    role="Demand Forecast Specialist",
    goal="Analyze historical sales data and predict future product demand.",
    backstory="""
        You are a demand forecasting expert who studies sales trends,
        seasonal patterns, and customer demand to help maintain
        optimal inventory levels.
    """,
    tools=[forecast_tool],
    llm=llm,
    verbose=True
)
