import pandas as pd  # type: ignore
from crewai.tools import tool  # type: ignore
from config.config import INVENTORY_CSV

@tool("Query Inventory Database")
def query_inventory_db(sku: str = "") -> str:
    """
    Queries the central inventory database. 
    If a specific SKU is provided, it returns all warehouse stock metrics for that item.
    If sku is empty, it outputs the complete stock table.
    """
    try:
        df = pd.read_csv(INVENTORY_CSV)
        if sku and sku.strip():
            sku_clean = sku.strip().upper()
            result = df[df['sku'].str.upper() == sku_clean]

            if result.empty:
                result = df[df['sku'].str.upper().str.contains(sku_clean, na=False)]
                
            if result.empty:
                return f"SKU '{sku}' was not found in active inventory inventory records."
            return result.to_string(index=False)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error executing inventory query: {str(e)}"

@tool("Update Inventory Stock Level")
def update_inventory_stock(sku: str, warehouse: str, quantity_change: int) -> str:
    """
    Modifies the 'on_hand' stock balance for an item inside a specific warehouse location.
    Pass negative values when an order is packed, or positive values when a replenishment restock is delivered.
    """
    try:
        df = pd.read_csv(INVENTORY_CSV)
        sku_upper = sku.strip().upper()
        wh_upper = warehouse.strip().upper()
        
        mask = (df['sku'].str.upper() == sku_upper) & (df['warehouse'].str.upper() == wh_upper)
        if not mask.any():
            return f"Error: SKU '{sku}' inside location '{warehouse}' does not exist."
        
        idx = df[mask].index[0]
        df.at[idx, 'on_hand'] = int(df.at[idx, 'on_hand']) + quantity_change
        df.to_csv(INVENTORY_CSV, index=False)
        return f"Updated {sku_upper} at {wh_upper}. New balance: {df.at[idx, 'on_hand']} units."
    except Exception as e:
        return f"Error modifying inventory data record: {str(e)}"