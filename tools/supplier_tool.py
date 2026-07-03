import pandas as pd
from langchain_core.tools import tool

# Load CSVs once
catalog_df = pd.read_csv("data/supplier_catalog.csv")
supplier_df = pd.read_csv("data/suppliers.csv")


@tool
def supplier_tool(sku: str):
    """
    Returns the best supplier details for a given SKU.

    Input:
        SKU (e.g., ELC-1001)

    Returns:
        Supplier Name
        Delivery Time
        Supplier Rating
        Price
    """

    # Find suppliers for the SKU
    catalog = catalog_df[
        catalog_df["sku"].str.lower() == sku.lower()
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