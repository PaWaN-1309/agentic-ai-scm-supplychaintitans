import pandas as pd  # type: ignore
from crewai.tools import tool  # type: ignore
from config.config import CUSTOMERS_CSV

@tool("Send Multi-Channel System Notification")
def send_system_notification(recipient_id: str, channel: str, message: str) -> str:
    """
    Dispatches alerts or status updates over a requested medium (Email, Slack, SMS).
    If recipient_id is a customer_id, matches and extracts contact emails automatically.
    """
    try:
        df = pd.read_csv(CUSTOMERS_CSV)
        match = df[df['customer_id'].astype(str).str.upper() == recipient_id.strip().upper()]
        
        target_name = recipient_id
        if not match.empty:
            target_name = f"{match.iloc[0]['customer_name']} ({match.iloc[0]['email']})"
            
        banner = f"--- [MOCK NOTIFICATION VIA {channel.upper()}] ---"
        print(f"\n{banner}\nTo: {target_name}\nContent: {message}\n--------------------------------------\n")
        return f"Notification cleanly simulated and sent to {target_name}."
    except Exception:
        # Fallback if parsing fails or record doesn't exist
        print(f"\n--- [MOCK NOTIFICATION VIA {channel.upper()}] ---\nTo: {recipient_id}\nContent: {message}\n")
        return f"Notification cleanly simulated and sent to {recipient_id}."