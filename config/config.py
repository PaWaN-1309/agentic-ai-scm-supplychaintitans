import os
from pathlib import Path
from dotenv import load_dotenv  # type: ignore
from crewai import LLM  # type: ignore
from langchain_openai import AzureChatOpenAI  # type: ignore

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
print(f"Loading environment variables from: {env_path}")

def _azure_configured() -> bool:
    required = (
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_KEY",
    )
    # for key in required:
    #     print(f"{key} =", repr(os.getenv(key)))
    return all(os.getenv(key) for key in required)

LLM_READY = _azure_configured()
llm = None           # Used directly by CrewAI Agents
langchain_llm = None # Used directly by LangGraph & Core Chains

if LLM_READY:
    try:
        # CrewAI native LLM instance
        llm = LLM(
            model=f"azure/{os.getenv('AZURE_OPENAI_DEPLOYMENT')}",
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            temperature=0.3
        )
        
        # LangChain ChatOpenAI instance for LangGraph routing orchestration
        langchain_llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            temperature=0.3
        )
    except Exception as e:
        print(f"Error occurred while initializing LLMs: {e}")
        llm = None
        langchain_llm = None
        LLM_READY = False

# HexaShop Case Company & Project Constants
COMPANY_NAME = "HexaShop E-Commerce Pvt. Ltd." # [cite: 4]
PURCHASE_APPROVAL_LIMIT = 5000.0  # Configurable threshold for human approval [cite: 32]

# Explicit, Clean File Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CARRIERS_CSV = DATA_DIR / "carriers.csv"
CUSTOMERS_CSV = DATA_DIR / "customers.csv"
INVENTORY_CSV = DATA_DIR / "inventory.csv"
ORDERS_CSV = DATA_DIR / "orders.csv"
PRODUCTS_CSV = DATA_DIR / "products.csv"
SALES_HISTORY_CSV = DATA_DIR / "sales_history.csv"
SUPPLIER_CATALOG_CSV = DATA_DIR / "supplier_catalog.csv"
SUPPLIERS_CSV = DATA_DIR / "suppliers.csv"