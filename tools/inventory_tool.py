import pandas as pd
from langchain_core.tools import tool

# Load CSV once
inventory_df = pd.read_csv("data/inventory.csv")


@tool
def inventory_tool(search: str):
    """
    Search inventory by SKU, Product Name,
    or return all products below reorder level.
    """

    search = search.lower().strip()

    # Case 1: Show all low-stock products
    if search in ["below reorder level", "low stock", "reorder"]:

        low_stock = inventory_df[
            inventory_df["Current_Stock"] < inventory_df["Reorder_Level"]
        ]

        if low_stock.empty:
            return {"message": "No products are below reorder level."}

        results = []

        for _, row in low_stock.iterrows():
            results.append({
                "SKU": row["SKU"],
                "Product": row["Product"],
                "Current Stock": int(row["Current_Stock"]),
                "Reorder Level": int(row["Reorder_Level"]),
                "Warehouse": row["Warehouse"]
            })

        return results

    # Case 2: Search by SKU or Product Name
    result = inventory_df[
        (inventory_df["SKU"].str.lower() == search) |
        (inventory_df["Product"].str.lower() == search)
    ]

    if result.empty:
        return {"message": f"No inventory found for '{search}'."}

    row = result.iloc[0]

    return {
        "SKU": row["SKU"],
        "Product": row["Product"],
        "Current Stock": int(row["Current_Stock"]),
        "Reorder Level": int(row["Reorder_Level"]),
        "Warehouse": row["Warehouse"]
    }