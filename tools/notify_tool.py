import pandas as pd
from langchain_core.tools import tool

customers_df = pd.read_csv("data/customers.csv")


@tool
def notify_tool(customer_id: str, message: str, channel: str = "email"):
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

    if channel.lower() == "email":
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