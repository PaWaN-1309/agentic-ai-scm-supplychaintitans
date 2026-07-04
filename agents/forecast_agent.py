from crewai import Agent  # type: ignore
from config.config import llm
from tools.forecast_tool import forecast_sku_demand
from tools.inventory_tool import query_inventory_db

def get_forecast_agent() -> Agent:
    return Agent(
        role="Demand Forecasting Analyst",
        goal="Predict near-term unit demand per SKU from sales history and flag upcoming risk of stock-outs or overstock conditions.",
        backstory="You are a meticulous statistics researcher at HexaShop. You translate customer order intervals into highly accurate future demand projections.",
        tools=[forecast_sku_demand, query_inventory_db],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )