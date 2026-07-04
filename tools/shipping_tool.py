import pandas as pd  # type: ignore
from crewai.tools import tool  # type: ignore
from config.config import CARRIERS_CSV

@tool("Get Shipping Carrier Rates and ETAs")
def get_shipping_options(region: str = "") -> str:
    """
    Queries active carrier configurations to isolate available transit methods.
    If a region parameter is specified, filters options strictly matching their coverage profiles.
    """
    try:
        df = pd.read_csv(CARRIERS_CSV)
        if region and region.strip():
            region_upper = region.strip().upper()
            matched = df[df['regions_covered'].str.upper().str.contains(region_upper, na=False)]
            if matched.empty:
                return f"No active carrier found explicitly covering '{region}'. Alternative system fallbacks:\n{df.to_string(index=False)}"
            return matched.to_string(index=False)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error gathering freight metrics: {str(e)}"