from typing import Type

import pandas as pd # type: ignore
from crewai.tools import BaseTool # type: ignore
from pydantic import BaseModel, Field # type: ignore

# Load CSVs once
inventory_df = pd.read_csv("data/inventory.csv")
products_df = pd.read_csv("data/products.csv")

class InventoryToolInput(BaseModel):
    search: str = Field(..., description="SKU, product name, or low stock query")


class InventoryTool(BaseTool):
    name: str = "inventory_tool"
    description: str = (
        "Search inventory by SKU, Product Name, or return all products below reorder level."
    )
    args_schema: Type[BaseModel] = InventoryToolInput

    def _run(self, search: str):
        """
        Search inventory by SKU, Product Name,
        or return all products below reorder level.
        """

        search = search.lower().strip()

        merged_df = inventory_df.merge(
            products_df[["sku", "product_name"]],
            on="sku",
            how="left"
        )

        def _build_row_output(row):
            return {
                "SKU": row["sku"],
                "Product": row["product_name"] if pd.notna(row["product_name"]) else row["sku"],
                "Current Stock": int(row["on_hand"]),
                "Reorder Level": int(row["reorder_point"]),
                "Warehouse": row["warehouse"]
            }

        # Case 1: Show all low-stock products
        if search in ["below reorder level", "low stock", "reorder"]:

            low_stock = inventory_df[
                inventory_df["on_hand"] < inventory_df["reorder_point"]
            ]

            low_stock = low_stock.merge(
                products_df[["sku", "product_name"]],
                on="sku",
                how="left"
            )

            if low_stock.empty:
                return {"message": "No products are below reorder level."}

            results = []

            for _, row in low_stock.iterrows():
                results.append(_build_row_output(row))

            return results

        # Case 2: Search by SKU or Product Name
        result = merged_df[
            (merged_df["sku"].str.lower() == search) |
            (merged_df["product_name"].fillna("").str.lower() == search)
        ]

        if result.empty:
            return {"message": f"No inventory found for '{search}'."}

        row = result.iloc[0]

        return _build_row_output(row)


inventory_tool = InventoryTool()