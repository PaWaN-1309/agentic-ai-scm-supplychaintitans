from crewai import Task # type: ignore

from agents.inventory_agent import inventory_agent
from agents.forecast_agent import forecast_agent
from agents.procurement_agent import procurement_agent
from agents.logistics_agent import logistics_agent
from agents.customer_agent import customer_agent

inventory_task = Task(

    description="""
        Analyze the current inventory data.

        Identify:
        - Products below reorder level
        - Current stock quantity
        - Products that require replenishment

        Prepare a short inventory report.
    """,

    expected_output="""
        Inventory Report containing:
        - Product Name
        - Current Stock
        - Reorder Status
    """,

    agent=inventory_agent
)

forecast_task = Task(

    description="""
        Analyze historical sales data.

        Predict future demand for each product.

        Identify high-demand and low-demand products.
    """,

    expected_output="""
        Demand Forecast Report containing:
        - Product Name
        - Predicted Demand
        - Demand Trend
    """,

    agent=forecast_agent
)

procurement_task = Task(

    description="""
        Review inventory and demand forecast.

        Recommend suppliers and prepare purchase
        recommendations for products requiring replenishment.
    """,

    expected_output="""
        Procurement Report containing:
        - Supplier Name
        - Product
        - Recommended Quantity
        - Estimated Cost
    """,

    agent=procurement_agent
)

logistics_task = Task(

    description="""
        Plan shipment for the approved purchase orders.

        Select suitable shipping method and estimate
        delivery timeline.
    """,

    expected_output="""
        Logistics Plan containing:
        - Shipping Method
        - Estimated Delivery
        - Warehouse Destination
    """,

    agent=logistics_agent
)

customer_task = Task(

    description="""
        Prepare customer notifications regarding
        shipment status, delays, or order confirmation.
    """,

    expected_output="""
        Customer Notification Message
    """,

    agent=customer_agent
)