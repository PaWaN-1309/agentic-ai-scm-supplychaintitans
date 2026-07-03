from typing import Type

import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

customers_df = pd.read_csv("data/customers.csv")


class NotifyToolInput(BaseModel):
    customer_id: str = Field(..., description="Customer identifier")
    message: str = Field(..., description="Notification message to send")
    channel: str = Field("email", description="Notification channel")


class NotifyTool(BaseTool):
    name: str = "notify_tool"
    description: str = "Sends a mock notification to a customer."
    args_schema: Type[BaseModel] = NotifyToolInput

    def _run(self, customer_id: str, message: str, channel: str = "email"):
        """
        Sends a mock notification to a customer.
        """

        customer = customers_df[
            customers_df["customer_id"] == customer_id
        ]

        if customer.empty:
            return {
                "status": "failed",
                "message": f"Customer '{customer_id}' not found."
            }

        customer = customer.iloc[0]

        if channel.lower() == "email" or "phone" not in customer.index:
            contact = customer["email"]
        else:
            contact = customer["phone"]

        print(f"{channel.upper()} sent to {contact}: {message}")

        return {
            "status": "sent",
            "channel": channel,
            "customer_id": customer_id,
            "contact": contact,
            "message": message
        }


notify_tool = NotifyTool()