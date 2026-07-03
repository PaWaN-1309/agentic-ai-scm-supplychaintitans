from typing import Type

import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Load sales history once
sales_df = pd.read_csv("data/sales_history.csv")
products_df = pd.read_csv("data/products.csv")


class ForecastToolInput(BaseModel):
    sku: str = Field(..., description="SKU to forecast demand for")


class ForecastTool(BaseTool):
    name: str = "forecast_tool"
    description: str = "Forecast demand for a SKU or product name using average historical sales."
    args_schema: Type[BaseModel] = ForecastToolInput

    def _run(self, sku: str):
        """
        Forecast demand for a SKU or product name using average historical sales.

        Input:
            SKU or product name (e.g., ELC-1001 or Wireless Earbuds Pro)

        Returns:
            Expected Demand
            Demand Level (High/Medium/Low)
        """

        query = sku.lower().strip()

        matched_products = products_df[
            (products_df["sku"].str.lower() == query) |
            (products_df["product_name"].str.lower() == query)
        ]

        if matched_products.empty:
            return {
                "message": f"No product found for '{sku}'."
            }

        resolved_sku = matched_products.iloc[0]["sku"]

        sku_sales = sales_df[
            sales_df["sku"].str.lower() == resolved_sku.lower()
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
            "SKU": resolved_sku.upper(),
            "Expected Demand": expected_demand,
            "Demand Level": demand_level
        }


forecast_tool = ForecastTool()