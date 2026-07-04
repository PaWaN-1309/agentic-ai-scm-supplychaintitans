import pandas as pd  # type: ignore
from crewai.tools import tool  # type: ignore
from config.config import SALES_HISTORY_CSV

@tool("Calculate SKU Demand Forecast")
def forecast_sku_demand(sku: str, days_to_forecast: int = 7) -> str:
    """
    Processes historical transactions inside sales_history.csv to build a rolling run-rate sales trend.
    Outputs the expected future unit demand over the requested window.
    """
    try:
        df = pd.read_csv(SALES_HISTORY_CSV)
        sku_upper = sku.strip().upper()
        sku_sales = df[df['sku'].str.upper() == sku_upper]
        
        if sku_sales.empty:
            fallback = 5 * days_to_forecast
            return f"No sales history discovered for SKU {sku_upper}. Using fallback demand: {fallback} units."
        
        avg_daily = sku_sales['units_sold'].mean()
        predicted = round(avg_daily * days_to_forecast)
        return f"SKU {sku_upper} historical average: {avg_daily:.2f} units/day. Forecasted total demand for next {days_to_forecast} days: {predicted} units."
    except Exception as e:
        return f"Error calculating demand projection: {str(e)}"