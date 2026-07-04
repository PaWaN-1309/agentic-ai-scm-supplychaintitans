import pandas as pd  # type: ignore
from crewai.tools import tool  # type: ignore
from config.config import SUPPLIERS_CSV, SUPPLIER_CATALOG_CSV

@tool("Fetch Supplier Quotes and Details")
def get_supplier_quotes(sku: str) -> str:
    """
    Retrieves full procurement quotation metrics (unit_cost, moq, lead_time_days) matched against 
    vendor operational stats (reliability_score, on_time_rate) for any given SKU.
    """
    try:
        catalog = pd.read_csv(SUPPLIER_CATALOG_CSV)
        vendors = pd.read_csv(SUPPLIERS_CSV)
        
        sku_upper = sku.strip().upper()
        catalog_matches = catalog[catalog['sku'].str.upper() == sku_upper]
        
        if catalog_matches.empty:
            return f"No certified vendors found in supplier catalog for SKU {sku_upper}."
        
        # Merge catalog listings with core supplier scores automatically
        merged = pd.merge(catalog_matches, vendors, on="supplier_id", how="left")
        
        target_view = [
            'supplier_id', 'supplier_name', 'unit_cost', 'moq', 
            'lead_time_days', 'reliability_score', 'on_time_rate'
        ]
        existing_view = [c for c in target_view if c in merged.columns]
        return merged[existing_view].to_string(index=False)
    except Exception as e:
        return f"Error loading procurement listings: {str(e)}"