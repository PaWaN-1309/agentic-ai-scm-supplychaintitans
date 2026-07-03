import os
from pathlib import Path

from crewai import LLM  # type: ignore
from dotenv import load_dotenv  # type: ignore

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def _azure_configured() -> bool:
    required = (
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_KEY",
    )
    return all(os.getenv(key) for key in required)


LLM_READY = _azure_configured()
llm = None

if LLM_READY:
    try:
        llm = LLM(
            model=f"azure/{os.getenv('AZURE_OPENAI_DEPLOYMENT')}",
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            temperature=0.3
        )
    except Exception:
        llm = None
        LLM_READY = False

COMPANY_NAME = "SCM by Supply Chain Titans"
LOW_STOCK_THRESHOLD = 20
PURCHASE_APPROVAL_LIMIT = 500000
