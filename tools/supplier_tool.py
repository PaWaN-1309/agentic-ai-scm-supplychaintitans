from typing import Type

import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Load CSVs once
catalog_df = pd.read_csv("data/supplier_catalog.csv")
supplier_df = pd.read_csv("data/suppliers.csv")
products_df = pd.read_csv("data/products.csv")


class SupplierToolInput(BaseModel):
    sku: str = Field(..., description="SKU to look up the best supplier for")


class SupplierTool(BaseTool):
    name: str = "supplier_tool"
    description: str = "Returns the best supplier details for a given SKU or product name."
    args_schema: Type[BaseModel] = SupplierToolInput

    def _run(self, sku: str):
        """
        Returns the best supplier details for a given SKU or product name.

        Input:
            SKU or product name (e.g., ELC-1001 or Wireless Earbuds Pro)

        Returns:
            Supplier Name
            Delivery Time
            Supplier Rating
            Price
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

        # Find suppliers for the resolved SKU
        catalog = catalog_df[
            catalog_df["sku"].str.lower() == resolved_sku.lower()
        ]

        if catalog.empty:
            return {
                "message": f"No supplier found for '{sku}'."
            }

        # Choose the cheapest supplier
        best = catalog.sort_values("unit_cost").iloc[0]

        supplier = supplier_df[
            supplier_df["supplier_id"] == best["supplier_id"]
        ].iloc[0]

        return {
            "SKU": best["sku"],
            "Supplier Name": supplier["supplier_name"],
            "Price": float(best["unit_cost"]),
            "Delivery Time": int(best["lead_time_days"]),
            "Supplier Rating": round(float(supplier["reliability_score"]) * 5, 2),
            "Available Quantity": int(best["available_qty"])
        }


supplier_tool = SupplierTool()