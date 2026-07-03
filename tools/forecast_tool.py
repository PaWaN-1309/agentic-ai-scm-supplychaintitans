import pandas as pd
from langchain_core.tools import tool

# Load sales history once
sales_df = pd.read_csv("data/sales_history.csv")


@tool
def forecast_tool(sku: str):
    """
    Forecast demand for a SKU using average historical sales.

    Input:
        SKU (e.g., ELC-1001)

    Returns:
        Expected Demand
        Demand Level (High/Medium/Low)
    """

    sku_sales = sales_df[
        sales_df["sku"].str.lower() == sku.lower()
    ]

    if sku_sales.empty:
        return {
            "message": f"No sales data found for '{sku}'."
        }

    expected_demand = round(sku_sales["units_sold"].mean())

    if expected_demand >= 50:
        demand_level = "High"
    elif expected_demand >= 20:
        demand_level = "Medium"
    else:
        demand_level = "Low"

    return {
        "SKU": sku.upper(),
        "Expected Demand": expected_demand,
        "Demand Level": demand_level
    }