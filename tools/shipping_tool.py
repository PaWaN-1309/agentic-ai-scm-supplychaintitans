from typing import Type

import pandas as pd
import random
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Load carrier data once
carrier_df = pd.read_csv("data/carriers.csv")


class ShippingToolInput(BaseModel):
    region: str = Field("North", description="Region to find a shipping option for")


class ShippingTool(BaseTool):
    name: str = "shipping_tool"
    description: str = "Returns the best shipping option for a region."
    args_schema: Type[BaseModel] = ShippingToolInput

    def _run(self, region: str = "North"):
        """
        Returns the best shipping option for a region.

        Input:
            Region (optional)

        Returns:
            Courier
            ETA
            Tracking ID
        """

        # Find carriers serving the region
        available = carrier_df[
            carrier_df["regions_covered"].str.contains(region, case=False)
        ]

        if available.empty:
            return {
                "message": f"No carrier available for '{region}'."
            }

        # Choose fastest carrier
        best = available.sort_values("eta_days").iloc[0]

        tracking_id = f"TRK{random.randint(100000,999999)}"

        return {
            "Courier": best["carrier_name"],
            "Service": best["service_level"],
            "ETA": f"{best['eta_days']} Days",
            "Tracking ID": tracking_id
        }


shipping_tool = ShippingTool()