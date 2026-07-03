from crewai import Crew, Process # type: ignore

from agents.inventory_agent import inventory_agent
from agents.forecast_agent import forecast_agent
from agents.procurement_agent import procurement_agent
from agents.logistics_agent import logistics_agent
from agents.customer_agent import customer_agent

from agents.tasks import (
    inventory_task,
    forecast_task,
    procurement_task,
    logistics_task,
    customer_task
)

supply_chain_crew = Crew(
    agents=[
        inventory_agent,
        forecast_agent,
        procurement_agent,
        logistics_agent,
        customer_agent
    ],

    tasks=[
        inventory_task,
        forecast_task,
        procurement_task,
        logistics_task,
        customer_task
    ],

    process=Process.sequential,

    verbose=True
)


if __name__ == "__main__":

    result = supply_chain_crew.kickoff()

    print("\n")
    print("=" * 70)
    print("SUPPLY CHAIN REPORT")
    print("=" * 70)

    print(result)