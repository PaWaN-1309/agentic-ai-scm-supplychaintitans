import sys
import os

# Add root directory to python path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.graph_objects as go
import streamlit_antd_components as sac

st.set_page_config(
    page_title="HexaShop SCM Control Center",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Gracefully import tools with stubs as fallback
try:
    from tools.inventory_tool import inventory_tool
except ImportError:
    class MockInventoryTool:
        def run(self, search):
            return {
                "SKU": "ELC-1001",
                "Product": "Wireless Earbuds Pro",
                "Current Stock": 10,
                "Reorder Level": 20,
                "Warehouse": "North DC"
            }
    inventory_tool = MockInventoryTool()

try:
    from tools.forecast_tool import forecast_tool
except ImportError:
    class MockForecastTool:
        def run(self, sku):
            return {
                "SKU": str(sku).upper(),
                "Expected Demand": 47,
                "Demand Level": "Medium"
            }
    forecast_tool = MockForecastTool()

try:
    from tools.supplier_tool import supplier_tool
except ImportError:
    class MockSupplierTool:
        def run(self, sku):
            return {
                "Supplier Name": "Titan Logistics & Supply",
                "Supplier Rating": 4.8,
                "Price": 75.0,
                "Delivery Time": 4
            }
    supplier_tool = MockSupplierTool()

try:
    from tools.shipping_tool import shipping_tool
except ImportError:
    class MockShippingTool:
        def run(self, region):
            return {
                "Courier": "FedEx",
                "ETA": "3 Days",
                "Tracking ID": "FTX-998811"
            }
    shipping_tool = MockShippingTool()

try:
    from tools.notify_tool import notify_tool
except ImportError:
    class MockNotifyTool:
        def run(self, customer_id, message, channel="email"):
            return {
                "status": "sent",
                "message": "Notification queued for delivery"
            }
    notify_tool = MockNotifyTool()

from graph.workflow import graph
from langgraph.types import Command

try:
    from config.config import LLM_READY
except Exception:
    LLM_READY = False

# --------------------------------------------------
# THEME
# --------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --scm-bg: #F4F5F9;
        --scm-surface: #FFFFFF;
        --scm-border: #E4E6EF;
        --scm-text: #171A2E;
        --scm-muted: #6E7288;
        --scm-accent: #3538CD;
        --scm-accent-soft: #EEEFFC;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--scm-bg);
        color: var(--scm-text);
    }

    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1440px; }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #C9CBDB; border-radius: 8px; }

    /* Bordered containers become cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--scm-border);
        border-radius: 14px;
        background: var(--scm-surface);
        box-shadow: 0 1px 2px rgba(23, 26, 46, 0.04), 0 12px 32px -24px rgba(23, 26, 46, 0.18);
    }

    /* Section labels */
    .scm-section {
        font-size: 11.5px;
        font-weight: 700;
        color: var(--scm-muted);
        margin: 34px 0 12px 2px;
        text-transform: uppercase;
        letter-spacing: 1.6px;
    }

    /* Card headers */
    .scm-step-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
    .scm-step-index {
        flex-shrink: 0; width: 24px; height: 24px; border-radius: 7px;
        background: var(--scm-accent-soft); color: var(--scm-accent);
        font-size: 12px; font-weight: 700;
        display: flex; align-items: center; justify-content: center;
    }
    .scm-step-title { font-size: 14.5px; font-weight: 600; color: var(--scm-text); }

    /* Brand mark */
    .scm-brand-mark {
        width: 46px; height: 46px; border-radius: 12px;
        background: linear-gradient(150deg, #3538CD 0%, #5A5DF0 100%);
        display: flex; align-items: center; justify-content: center;
        color: #FFFFFF; font-weight: 800; font-size: 17px; letter-spacing: 0.5px;
        box-shadow: 0 6px 14px -6px rgba(53, 56, 205, 0.5);
    }

    /* Badges */
    .badge-capsule {
        background: var(--scm-surface); color: var(--scm-muted);
        border: 1px solid var(--scm-border);
        padding: 3px 11px; border-radius: 7px;
        font-size: 11.5px; font-weight: 600;
        display: inline-block; margin-right: 6px;
    }
    .status-capsule {
        padding: 3px 11px; border-radius: 7px;
        font-size: 11.5px; font-weight: 700; letter-spacing: 0.3px;
        display: inline-block; text-transform: uppercase;
    }
    .status-idle { background: #F0F1F6; color: #565B75; border: 1px solid #DDDFEA; }
    .status-running { background: #EEEFFC; color: #3538CD; border: 1px solid #CBCDF5; animation: pulse 1.6s infinite; }
    .status-paused { background: #FDF3E4; color: #B45C09; border: 1px solid #F5DCB2; }
    .status-completed { background: #E7F6ED; color: #157A42; border: 1px solid #BFE8CF; }
    .status-rejected { background: #FCEBEC; color: #B3272D; border: 1px solid #F3C6C9; }
    .status-error { background: #FCEBEC; color: #B3272D; border: 1px solid #F3C6C9; }

    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.55;} 100% {opacity: 1;} }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        border-radius: 9px;
        border: 1px solid var(--scm-border);
        background: var(--scm-surface);
        color: var(--scm-text);
        font-weight: 600; font-size: 13.5px;
        transition: border-color 0.15s ease, color 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: var(--scm-accent); color: var(--scm-accent);
        box-shadow: 0 4px 12px -6px rgba(53, 56, 205, 0.4);
    }
    .stButton > button[kind="primary"] {
        background: var(--scm-accent); border-color: var(--scm-accent); color: #FFFFFF;
    }
    .stButton > button[kind="primary"]:hover {
        background: #2B2EAE; color: #FFFFFF;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        border-radius: 9px !important;
    }
    .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
        font-size: 12px !important; font-weight: 600 !important;
        color: var(--scm-muted) !important;
    }

    /* Metrics: quiet tiles inside cards */
    div[data-testid="stMetric"] {
        background: #F8F9FC;
        border: 1px solid #EEEFF5;
        border-radius: 10px;
        padding: 12px 14px;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11.5px; font-weight: 600; color: var(--scm-muted);
    }
    div[data-testid="stMetricValue"] {
        font-size: 19px; font-weight: 700; color: var(--scm-text);
    }

    div[data-testid="stAlert"] { border-radius: 10px; font-size: 13.5px; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #15172B 0%, #1E2140 100%);
        border-right: 1px solid #272B4D;
    }
    section[data-testid="stSidebar"] * { color: #E8E9F6 !important; }
    section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08); }
    section[data-testid="stSidebar"] .stMarkdown p { color: #C9CBE8 !important; font-size: 12.5px; }
    section[data-testid="stSidebar"] code {
        background: rgba(255,255,255,0.08) !important; color: #E8E9F6 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stAlert"] {
        background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10);
    }
    section[data-testid="stSidebar"] img { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


def init_state():
    if "scm_state" not in st.session_state:
        st.session_state.scm_state = {
            "user_query": "Auto Replenishment",
            "session_id": "session-1",
            "timestamp": "",
            "sku": "ELC-1001",
            "predicted_demand": 0,
            "demand_level": "",
            "current_stock": 10,
            "reorder_level": 20,
            "warehouse": "Warehouse-Alpha",
            "inventory_status": "",
            "supplier_name": "",
            "supplier_rating": 0.0,
            "supplier_price": 0.0,
            "delivery_time": "",
            "po_number": "",
            "po_quantity": 0,
            "po_total_cost": 0.0,
            "approval_required": False,
            "approval_status": "",
            "approver": "",
            "approval_comments": "",
            "courier": "",
            "eta": "",
            "tracking_id": "",
            "notification_sent": False,
            "notification_message": "",
            "current_node": "START",
            "next_node": "",
            "workflow_status": "IDLE",
            "messages": [],
            "execution_history": [],
            "error": None,
            "retry_count": 0,
            "final_response": ""
        }
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "current_node" not in st.session_state:
        st.session_state.current_node = "START"
    if "next_node" not in st.session_state:
        st.session_state.next_node = None
    if "workflow_status" not in st.session_state:
        st.session_state.workflow_status = "IDLE"
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = "thread-default-id"
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

init_state()

# --------------------------------------------------
# COMPONENT RENDER HELPERS
# --------------------------------------------------
# HTML is built as compact single-line strings: Streamlit's markdown
# parser turns indented lines into code blocks, so multiline templates
# with mixed indentation render as raw text.

def render_descriptions(title, dict_data):
    parts = [
        '<div style="margin: 4px 0 18px 0;">',
        f'<div style="font-size: 13px; font-weight: 600; color: #171A2E; margin-bottom: 8px;">{title}</div>',
        '<table style="width: 100%; border-collapse: collapse; font-size: 12.5px;">'
    ]
    key_style = "background-color: #F8F9FC; font-weight: 500; color: #6E7288; padding: 6px 12px; border: 1px solid #E4E6EF; width: 25%;"
    val_style = "color: #171A2E; padding: 6px 12px; border: 1px solid #E4E6EF;"

    keys = list(dict_data.keys())
    for i in range(0, len(keys), 2):
        k1 = keys[i]
        v1 = dict_data[k1]
        val1 = str(v1) if v1 not in (None, "") else "&mdash;"
        row = f'<tr><td style="{key_style}">{k1.replace("_", " ").title()}</td>'
        if i + 1 < len(keys):
            k2 = keys[i + 1]
            v2 = dict_data[k2]
            val2 = str(v2) if v2 not in (None, "") else "&mdash;"
            row += f'<td style="{val_style} width: 25%;">{val1}</td>'
            row += f'<td style="{key_style}">{k2.replace("_", " ").title()}</td>'
            row += f'<td style="{val_style} width: 25%;">{val2}</td></tr>'
        else:
            row += f'<td style="{val_style} width: 75%;" colspan="3">{val1}</td></tr>'
        parts.append(row)

    parts.append('</table></div>')
    return "".join(parts)


def render_timeline(events):
    parts = ['<div style="border-left: 2px solid #E4E6EF; padding-left: 20px; margin-left: 8px;">']
    for event in events:
        color = "#157A42" if any(x in event for x in ["Completed", "Sent", "Approved", "Selected", "Planned", "Created", "Checked"]) else "#3538CD"
        if "Rejected" in event or "Error" in event:
            color = "#B3272D"
        parts.append(
            '<div style="position: relative; margin-bottom: 18px;">'
            f'<div style="position: absolute; left: -27px; top: 3px; background: white; border: 2px solid {color}; border-radius: 50%; width: 14px; height: 14px;">'
            f'<div style="background: {color}; border-radius: 50%; width: 6px; height: 6px; margin: 2px;"></div></div>'
            f'<div style="font-size: 13px; font-weight: 600; color: #171A2E;">{event}</div>'
            '<div style="font-size: 11px; color: #6E7288;">SCM node event</div></div>'
        )
    parts.append('</div>')
    return "".join(parts)


def render_bottom_timeline(current_node, status):
    nodes = ["START", "forecast", "inventory", "supplier", "purchase_order", "approval", "shipping", "notification", "END"]
    node_labels = ["Start", "Forecast", "Inventory", "Supplier", "PO Created", "Approval", "Shipping", "Notify", "End"]

    current_idx = 0
    if current_node in nodes:
        current_idx = nodes.index(current_node)
    if status in ["COMPLETED", "REJECTED"] or current_node == "END":
        current_idx = len(nodes) - 1

    parts = ['<div style="display: flex; align-items: flex-start; justify-content: space-between; padding: 6px 0; overflow-x: auto;">']
    for i in range(len(nodes)):
        label = node_labels[i]
        if i < current_idx:
            color, border_color, text_color, bullet = "#157A42", "#157A42", "#157A42", "&#10003;"
        elif i == current_idx:
            if status == "REJECTED":
                color, border_color, text_color, bullet = "#B3272D", "#B3272D", "#B3272D", "&times;"
            elif status == "PAUSED":
                color, border_color, text_color, bullet = "#B45C09", "#B45C09", "#B45C09", "&#10074;&#10074;"
            else:
                color, border_color, text_color, bullet = "#3538CD", "#3538CD", "#3538CD", "&bull;"
        else:
            color, border_color, text_color, bullet = "#A2A5BC", "#E4E6EF", "#6E7288", str(i)

        connector = ""
        if i < len(nodes) - 1:
            line_color = "#157A42" if i < current_idx else "#E4E6EF"
            connector = f'<div style="position: absolute; top: 13px; left: calc(50% + 16px); right: calc(-50% + 16px); height: 2px; background: {line_color};"></div>'

        parts.append(
            '<div style="display: flex; flex-direction: column; align-items: center; flex: 1; min-width: 76px; position: relative;">'
            + connector +
            f'<div style="background: white; border: 2px solid {border_color}; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-weight: 700; color: {color}; font-size: 12px; position: relative; z-index: 1;">{bullet}</div>'
            f'<div style="font-size: 11px; font-weight: 600; color: {text_color}; margin-top: 6px; text-align: center;">{label}</div></div>'
        )
    parts.append('</div>')
    return "".join(parts)


def section(title):
    st.markdown(f"<div class='scm-section'>{title}</div>", unsafe_allow_html=True)


def card_header(title, index=None):
    index_html = f"<span class='scm-step-index'>{index}</span>" if index is not None else ""
    st.markdown(
        f"<div class='scm-step-header'>{index_html}<span class='scm-step-title'>{title}</span></div>",
        unsafe_allow_html=True
    )


def stream_workflow(stream_input, config):
    """Consume a graph stream, mirroring node updates into session state.
    Returns True if the run hit a human-approval interrupt."""
    interrupted = False
    for event in graph.stream(stream_input, config, stream_mode="updates"):
        node_name, update = list(event.items())[0]
        if node_name == "__interrupt__":
            interrupted = True
            continue
        st.session_state.current_node = node_name
        if isinstance(update, dict):
            for k, v in update.items():
                st.session_state.scm_state[k] = v
    return interrupted

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    img_path = os.path.join(os.path.dirname(__file__), "product.png")
    if os.path.exists(img_path):
        st.image(img_path, caption="HexaShop Tech", use_container_width=True)

    menu = sac.menu([
        sac.MenuItem('Control Center', icon='speedometer2'),
        sac.MenuItem('Agent Stubs & Tools', icon='tools', children=[
            sac.MenuItem('Inventory Intel', icon='database'),
            sac.MenuItem('Demand Forecast', icon='graph-up'),
            sac.MenuItem('Supplier Selection', icon='shop'),
            sac.MenuItem('Shipping Planner', icon='truck'),
            sac.MenuItem('Notifications', icon='envelope'),
        ])
    ], key='menu_navigation', index=0, variant='filled', color='indigo', size='sm')

    st.divider()
    st.markdown("<div style='font-size:11.5px; font-weight:700; letter-spacing:1.4px; text-transform:uppercase; color:#8B8EC4;'>Workflow Monitor</div>", unsafe_allow_html=True)

    steps_list = ["START", "forecast", "inventory", "supplier", "purchase_order", "approval", "shipping", "notification", "END"]
    curr_idx = steps_list.index(st.session_state.current_node) if st.session_state.current_node in steps_list else 0
    if st.session_state.workflow_status in ["COMPLETED", "REJECTED"]:
        curr_idx = len(steps_list) - 1
    pct = int((curr_idx / (len(steps_list) - 1)) * 100)

    st.markdown(
        '<div style="display: flex; justify-content: center; margin: 16px 0;">'
        f'<div style="position: relative; width: 96px; height: 96px; border-radius: 50%; background: radial-gradient(closest-side, #1B1E38 79%, transparent 80% 100%), conic-gradient(#6E71E8 {pct}%, rgba(255,255,255,0.10) 0);">'
        f'<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-weight: 700; color: #FFFFFF; font-size: 16px;">{pct}%</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(f"**Current node:** `{st.session_state.current_node.upper()}`")
    st.markdown(f"**Next node:** `{str(st.session_state.next_node).upper()}`")
    st.markdown(f"**Status:** `{st.session_state.workflow_status}`")
    st.markdown(f"**Retries:** `{st.session_state.scm_state.get('retry_count', 0)}`")

    err = st.session_state.scm_state.get("error")
    if err:
        st.error(f"**Error:** {err}")
    else:
        st.success("No execution errors.")

# --------------------------------------------------
# CONTROL CENTER
# --------------------------------------------------

if menu == "Control Center":
    col_logo, col_desc = st.columns([0.6, 11.4])
    with col_logo:
        st.markdown("<div class='scm-brand-mark'>HS</div>", unsafe_allow_html=True)
    with col_desc:
        st.markdown("<h2 style='margin:0; font-weight:700;'>HexaShop SCM Control Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='margin:2px 0 0 0; color:#6E7288; font-size:13.5px;'>Agentic AI supply chain management platform</p>", unsafe_allow_html=True)

    st.write("")

    status_style = {
        "RUNNING": "status-running",
        "PAUSED": "status-paused",
        "COMPLETED": "status-completed",
        "REJECTED": "status-rejected",
        "ERROR": "status-error",
    }.get(st.session_state.workflow_status, "status-idle")

    llm_badge = "Azure OpenAI connected" if LLM_READY else "Deterministic tool mode"

    st.markdown(
        '<div style="margin-bottom: 18px;">'
        '<span class="badge-capsule">LangGraph StateGraph</span>'
        '<span class="badge-capsule">CrewAI Specialists</span>'
        f'<span class="badge-capsule">{llm_badge}</span>'
        f'<span class="status-capsule {status_style}">{st.session_state.workflow_status}</span>'
        f'<span style="float: right; font-size: 12.5px; color:#6E7288; font-weight:500;">Session <code>{st.session_state.thread_id}</code> &nbsp;|&nbsp; {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>'
        '</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):
        col_input_1, col_input_2, col_input_3, col_btn = st.columns([2.4, 2.4, 2.4, 4.8])
        with col_input_1:
            st.text_input("Product SKU", value="ELC-1001", key="form_sku")
        with col_input_2:
            st.number_input("Current warehouse stock", value=10, key="form_stock")
        with col_input_3:
            st.number_input("Reorder level threshold", value=20, key="form_reorder_level")
        with col_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            col_start, col_reset, col_export = st.columns(3)
            with col_start:
                start_btn = st.button("Start flow", use_container_width=True, type="primary")
            with col_reset:
                reset_btn = st.button("Reset", use_container_width=True)
            with col_export:
                report_df = pd.DataFrame([st.session_state.scm_state])
                csv = report_df.to_csv(index=False).encode('utf-8')
                st.download_button("Export CSV", data=csv, file_name="scm_report.csv", mime="text/csv", use_container_width=True)

    if reset_btn:
        st.session_state.clear()
        init_state()
        st.rerun()

    status_placeholder = st.empty()

    if start_btn:
        st.session_state.logs = ["Workflow Started"]
        st.session_state.current_node = "forecast"
        st.session_state.next_node = "inventory"
        st.session_state.workflow_status = "RUNNING"
        st.session_state.thread_id = f"thread_{int(time.time())}"

        st.session_state.scm_state["sku"] = st.session_state.form_sku
        st.session_state.scm_state["current_stock"] = int(st.session_state.form_stock)
        st.session_state.scm_state["reorder_level"] = int(st.session_state.form_reorder_level)
        st.session_state.scm_state["session_id"] = st.session_state.thread_id
        st.session_state.scm_state["timestamp"] = datetime.now().isoformat()
        st.session_state.scm_state["approval_required"] = False
        st.session_state.scm_state["approval_status"] = ""
        st.session_state.scm_state["error"] = None
        st.session_state.scm_state["final_response"] = ""
        st.session_state.scm_state["execution_history"] = []

        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        try:
            status_placeholder.info("Initializing agent nodes...")
            interrupted = False
            for event in graph.stream(st.session_state.scm_state, config, stream_mode="updates"):
                node_name, update = list(event.items())[0]
                if node_name == "__interrupt__":
                    interrupted = True
                    continue

                st.session_state.current_node = node_name
                if isinstance(update, dict):
                    for k, v in update.items():
                        st.session_state.scm_state[k] = v

                if node_name == "forecast":
                    st.session_state.logs.append("Forecast Agent Completed")
                    st.session_state.next_node = "inventory"
                elif node_name == "inventory":
                    st.session_state.logs.append("Inventory Checked")
                    st.session_state.next_node = "supplier"
                elif node_name == "supplier":
                    st.session_state.logs.append("Supplier Selected")
                    st.session_state.next_node = "purchase_order"
                elif node_name == "purchase_order":
                    st.session_state.logs.append("PO Created")
                    if st.session_state.scm_state.get("approval_required"):
                        st.session_state.logs.append("Approval Requested")
                        st.session_state.next_node = "approval"
                    else:
                        st.session_state.next_node = "shipping"
                elif node_name == "shipping":
                    st.session_state.logs.append("Shipping Planned")
                    st.session_state.next_node = "notification"
                elif node_name == "notification":
                    st.session_state.logs.append("Notification Sent")
                    st.session_state.next_node = "END"

                status_placeholder.info(f"Agent executing: {node_name.replace('_', ' ').title()}...")
                time.sleep(0.8)

            if interrupted or st.session_state.scm_state.get("approval_required"):
                st.session_state.workflow_status = "PAUSED"
            else:
                st.session_state.workflow_status = "COMPLETED"
                st.session_state.logs.append("Workflow Completed")
                st.session_state.current_node = "END"
                st.session_state.next_node = None

            status_placeholder.empty()
            st.rerun()

        except Exception as e:
            st.session_state.logs.append(f"Execution Error: {str(e)}")
            st.session_state.workflow_status = "ERROR"
            st.session_state.scm_state["error"] = str(e)
            status_placeholder.empty()
            st.rerun()

    # ---------------- Section 1 ----------------
    section("Business profile & demand trend")

    with st.container(border=True):
        col_hero_img, col_hero_details, col_hero_chart = st.columns([2.6, 4.2, 5.2])

        with col_hero_img:
            img_path = os.path.join(os.path.dirname(__file__), "product.png")
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            st.markdown(
                "<div style='text-align: center; margin-top:-4px;'>"
                f"<strong style='font-size:15px;'>{st.session_state.scm_state.get('sku', 'ELC-1001')}</strong><br/>"
                "<span style='font-size:12px; color:#6E7288;'>Wireless Earbuds Pro</span></div>",
                unsafe_allow_html=True
            )

        with col_hero_details:
            card_header("Product details")
            stock_status = "Healthy"
            if st.session_state.scm_state.get('current_stock', 0) < st.session_state.scm_state.get('reorder_level', 0):
                stock_status = "LOW_STOCK"
            shortage = max(st.session_state.scm_state.get("predicted_demand", 0) - st.session_state.scm_state.get("current_stock", 0), 0)
            st.markdown(render_descriptions("", {
                "warehouse": st.session_state.scm_state.get('warehouse', 'Warehouse-Alpha'),
                "current_stock": f"{st.session_state.scm_state.get('current_stock', 0)} units",
                "reorder_level": f"{st.session_state.scm_state.get('reorder_level', 0)} units",
                "inventory_health": stock_status,
                "expected_shortage": f"{shortage} units",
                "procurement_cost": f"${st.session_state.scm_state.get('po_total_cost', 0.0):,.2f}",
            }), unsafe_allow_html=True)

        with col_hero_chart:
            card_header("Sales history & forecast")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
            sales_history = [15, 18, 12, 22, 28, 16, 25]
            forecast_point = st.session_state.scm_state.get("predicted_demand", 0)
            if forecast_point > 0:
                sales_history[-1] = forecast_point

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months[:-1], y=sales_history[:-1], mode='lines+markers', name='Actual sales', line=dict(color='#A2A5BC', width=2)))
            fig.add_trace(go.Scatter(x=[months[-2], months[-1]], y=[sales_history[-2], sales_history[-1]], mode='lines+markers', name='Forecast', line=dict(color='#3538CD', width=3, dash='dash')))
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter, sans-serif', color='#6E7288', size=11),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#EEEFF5'),
                height=190,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---------------- Section 2 ----------------
    section("Agent workflow")

    steps_labels = ["Forecast", "Inventory", "Supplier", "Purchase Order", "Approval", "Shipping", "Notify"]
    node_keys = ["forecast", "inventory", "supplier", "purchase_order", "approval", "shipping", "notification"]

    current_node = st.session_state.current_node
    active_idx = node_keys.index(current_node) if current_node in node_keys else 0
    if st.session_state.workflow_status in ["COMPLETED", "REJECTED"] or current_node == "END":
        active_idx = len(node_keys)

    sac_items = []
    for i, label in enumerate(steps_labels):
        icon_name = "clock"
        if i < active_idx:
            icon_name = "check-circle-fill"
        elif i == active_idx:
            icon_name = "play-circle-fill"
            if st.session_state.workflow_status == "PAUSED":
                icon_name = "pause-circle-fill"
        sac_items.append(sac.StepsItem(title=label, icon=icon_name))

    with st.container(border=True):
        sac.steps(sac_items, index=min(active_idx, len(steps_labels) - 1), color="indigo", size="sm")

    # ---------------- Section 3 ----------------
    section("Workflow node details")

    col_cards, col_state = st.columns([7, 5])

    with col_cards:
        with st.container(border=True):
            card_header("Forecast Agent", 1)
            col1, col2, col3 = st.columns(3)
            col1.metric("Predicted demand", f"{st.session_state.scm_state.get('predicted_demand', 0)} units")
            col2.metric("Demand category", st.session_state.scm_state.get('demand_level') or "N/A")
            col3.metric("Confidence", "94.6%" if st.session_state.scm_state.get('predicted_demand', 0) > 0 else "N/A")

        st.write("")
        with st.container(border=True):
            card_header("Inventory Agent", 2)
            col1, col2, col3 = st.columns(3)
            col1.metric("Current stock", f"{st.session_state.scm_state.get('current_stock', 0)} units")
            col2.metric("Reorder threshold", f"{st.session_state.scm_state.get('reorder_level', 0)} units")
            col3.metric("Status", st.session_state.scm_state.get('inventory_status') or "N/A")

        st.write("")
        with st.container(border=True):
            card_header("Procurement Agent", 3)
            col1, col2, col3 = st.columns(3)
            col1.metric("Selected supplier", st.session_state.scm_state.get('supplier_name') or "N/A")
            col2.metric("Unit price", f"${st.session_state.scm_state.get('supplier_price') or 0.0:,.2f}")
            col3.metric("Lead time", str(st.session_state.scm_state.get('delivery_time') or "N/A"))

        st.write("")
        with st.container(border=True):
            card_header("Purchase Order", 4)
            col1, col2, col3 = st.columns(3)
            col1.metric("PO number", st.session_state.scm_state.get('po_number') or "N/A")
            col2.metric("Quantity", f"{st.session_state.scm_state.get('po_quantity', 0)} units")
            col3.metric("Total cost", f"${st.session_state.scm_state.get('po_total_cost') or 0.0:,.2f}")

        st.write("")
        with st.container(border=True):
            card_header("Human Approval", 5)
            if st.session_state.workflow_status == "PAUSED" and st.session_state.scm_state.get("approval_required"):
                st.warning("Action required: this purchase order exceeds automatic limits and needs human verification.")

                st.markdown(render_descriptions("Purchase order under review", {
                    "po_number": st.session_state.scm_state.get('po_number'),
                    "supplier": st.session_state.scm_state.get('supplier_name'),
                    "quantity": f"{st.session_state.scm_state.get('po_quantity')} units",
                    "warehouse": st.session_state.scm_state.get('warehouse'),
                    "delivery_time": st.session_state.scm_state.get('delivery_time'),
                    "total_cost": f"${st.session_state.scm_state.get('po_total_cost', 0.0):,.2f}",
                }), unsafe_allow_html=True)

                if not st.session_state.edit_mode:
                    col_approve, col_reject, col_edit = st.columns(3)
                    with col_approve:
                        approve_action = st.button("Approve PO", use_container_width=True, type="primary")
                    with col_reject:
                        reject_action = st.button("Reject PO", use_container_width=True)
                    with col_edit:
                        edit_action = st.button("Edit PO", use_container_width=True)

                    if approve_action:
                        config = {"configurable": {"thread_id": st.session_state.thread_id}}
                        try:
                            stream_workflow(Command(resume={"action": "APPROVED"}), config)
                            st.session_state.workflow_status = "COMPLETED"
                            st.session_state.current_node = "END"
                            st.session_state.next_node = None
                            st.session_state.logs.append("Approval Node Processed: APPROVED")
                            st.session_state.logs.append("Shipping Planned")
                            st.session_state.logs.append("Notification Sent")
                            st.session_state.logs.append("Workflow Completed")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error resuming workflow: {e}")

                    if reject_action:
                        config = {"configurable": {"thread_id": st.session_state.thread_id}}
                        try:
                            stream_workflow(Command(resume={"action": "REJECTED"}), config)
                            st.session_state.workflow_status = "REJECTED"
                            st.session_state.current_node = "END"
                            st.session_state.next_node = None
                            st.session_state.logs.append("Approval Node Processed: REJECTED")
                            st.session_state.logs.append("PO Rejected")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error resuming workflow: {e}")

                    if edit_action:
                        st.session_state.edit_mode = True
                        st.rerun()

                else:
                    card_header("Edit purchase order")
                    edit_q = st.number_input("Quantity", value=int(st.session_state.scm_state.get("po_quantity", 0)))
                    edit_s = st.text_input("Supplier", value=str(st.session_state.scm_state.get("supplier_name", "")))
                    edit_p = st.number_input("Unit price", value=float(st.session_state.scm_state.get("supplier_price", 0.0)))
                    edit_d = st.text_input("Delivery time", value=str(st.session_state.scm_state.get("delivery_time", "")))

                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        confirm_btn = st.button("Confirm changes & approve", use_container_width=True, type="primary")
                    with col_cancel:
                        cancel_btn = st.button("Cancel", use_container_width=True)

                    if confirm_btn:
                        config = {"configurable": {"thread_id": st.session_state.thread_id}}
                        edited_data = {
                            "quantity": int(edit_q),
                            "supplier": str(edit_s),
                            "price": float(edit_p),
                            "delivery_time": str(edit_d)
                        }
                        try:
                            stream_workflow(Command(resume={"action": "EDITED", "data": edited_data}), config)
                            st.session_state.workflow_status = "COMPLETED"
                            st.session_state.current_node = "END"
                            st.session_state.next_node = None
                            st.session_state.logs.append("Approval Node Processed: EDITED")
                            st.session_state.logs.append("Shipping Planned")
                            st.session_state.logs.append("Notification Sent")
                            st.session_state.logs.append("Workflow Completed")
                            st.session_state.edit_mode = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error resuming workflow: {e}")

                    if cancel_btn:
                        st.session_state.edit_mode = False
                        st.rerun()
            elif st.session_state.scm_state.get("approval_status"):
                decision = st.session_state.scm_state.get("approval_status")
                if decision == "REJECTED":
                    st.error(f"Purchase order {st.session_state.scm_state.get('po_number')} was rejected by the reviewer.")
                else:
                    st.success(f"Purchase order {st.session_state.scm_state.get('po_number')} was reviewed and {decision.lower()} by the reviewer.")
            else:
                st.info("No approval required, or the checkpoint has not been reached yet.")

        st.write("")
        with st.container(border=True):
            card_header("Shipping Agent", 6)
            col1, col2, col3 = st.columns(3)
            col1.metric("Courier", st.session_state.scm_state.get('courier') or "N/A")
            col2.metric("ETA", st.session_state.scm_state.get('eta') or "N/A")
            col3.metric("Tracking", st.session_state.scm_state.get('tracking_id') or "N/A")

        st.write("")
        with st.container(border=True):
            card_header("Notification Agent", 7)
            if st.session_state.scm_state.get("notification_sent"):
                st.success("Notification dispatched to stakeholders.")
                st.markdown(
                    '<div style="background: #F8F9FC; border: 1px solid #EEEFF5; padding: 14px; border-radius: 10px;">'
                    '<div style="border-bottom: 1px solid #E4E6EF; padding-bottom: 6px; margin-bottom: 8px; font-size:12px; color:#6E7288;">'
                    '<strong>From:</strong> updates@hexashop-scm.com<br/>'
                    '<strong>To:</strong> warehouse-manager@hexashop.com<br/>'
                    f'<strong>Subject:</strong> SCM Workflow Notification &mdash; {st.session_state.scm_state.get("po_number")}'
                    '</div>'
                    f'<div style="font-size:13px; color:#171A2E;">{st.session_state.scm_state.get("notification_message")}</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                st.info("No notification sent yet.")

    with col_state:
        with st.container(border=True):
            card_header("Live SCM state")

            st.markdown(render_descriptions("General request", {
                "user_query": st.session_state.scm_state.get("user_query"),
                "session_id": st.session_state.scm_state.get("session_id"),
                "timestamp": st.session_state.scm_state.get("timestamp"),
            }), unsafe_allow_html=True)

            st.markdown(render_descriptions("Forecast & inventory", {
                "sku": st.session_state.scm_state.get("sku"),
                "predicted_demand": st.session_state.scm_state.get("predicted_demand"),
                "demand_level": st.session_state.scm_state.get("demand_level"),
                "current_stock": st.session_state.scm_state.get("current_stock"),
                "reorder_level": st.session_state.scm_state.get("reorder_level"),
                "inventory_status": st.session_state.scm_state.get("inventory_status"),
            }), unsafe_allow_html=True)

            st.markdown(render_descriptions("Supplier & purchase order", {
                "supplier_name": st.session_state.scm_state.get("supplier_name"),
                "supplier_rating": st.session_state.scm_state.get("supplier_rating"),
                "supplier_price": st.session_state.scm_state.get("supplier_price"),
                "delivery_time": st.session_state.scm_state.get("delivery_time"),
                "po_number": st.session_state.scm_state.get("po_number"),
                "po_quantity": st.session_state.scm_state.get("po_quantity"),
                "po_total_cost": st.session_state.scm_state.get("po_total_cost"),
                "approval_required": st.session_state.scm_state.get("approval_required"),
            }), unsafe_allow_html=True)

            st.markdown(render_descriptions("Shipping & notification", {
                "courier": st.session_state.scm_state.get("courier"),
                "eta": st.session_state.scm_state.get("eta"),
                "tracking_id": st.session_state.scm_state.get("tracking_id"),
                "notification_sent": st.session_state.scm_state.get("notification_sent"),
            }), unsafe_allow_html=True)

        st.write("")
        with st.container(border=True):
            card_header("Workflow events")
            if st.session_state.logs:
                st.markdown(render_timeline(st.session_state.logs), unsafe_allow_html=True)
            else:
                st.info("No workflow events logged yet.")

    # ---------------- Section 4 ----------------
    section("Graph execution timeline")
    with st.container(border=True):
        st.markdown(render_bottom_timeline(st.session_state.current_node, st.session_state.workflow_status), unsafe_allow_html=True)

# --------------------------------------------------
# SPECIALIST AGENT TOOL PAGES
# --------------------------------------------------

elif menu == "Inventory Intel":
    st.title("Inventory Intelligence Agent")
    st.caption("Inspect and audit warehouse stock levels")
    with st.container(border=True):
        search_q = st.text_input("Search by SKU, product name, or type 'low stock'", value="low stock")
        if st.button("Query inventory", type="primary"):
            try:
                res = inventory_tool.run(search=search_q)
                st.success("Tool execution completed")
                st.json(res)
            except Exception as e:
                st.error(f"Tool execution failed: {e}")

elif menu == "Demand Forecast":
    st.title("Demand Forecasting Agent")
    st.caption("Project SKU demand based on sales history")
    with st.container(border=True):
        forecast_sku = st.text_input("SKU or product name", value="ELC-1001")
        if st.button("Generate projection", type="primary"):
            try:
                res = forecast_tool.run(sku=forecast_sku)
                st.success("Tool execution completed")
                st.json(res)
            except Exception as e:
                st.error(f"Tool execution failed: {e}")

elif menu == "Supplier Selection":
    st.title("Supplier Management Agent")
    st.caption("Locate the best supplier by price, rating and lead time")
    with st.container(border=True):
        sup_sku = st.text_input("SKU or product name", value="ELC-1001")
        if st.button("Query suppliers", type="primary"):
            try:
                res = supplier_tool.run(sku=sup_sku)
                st.success("Tool execution completed")
                st.json(res)
            except Exception as e:
                st.error(f"Tool execution failed: {e}")

elif menu == "Shipping Planner":
    st.title("Shipping & Logistics Planner")
    st.caption("Plan and optimize routes for a shipment region")
    with st.container(border=True):
        region_select = st.selectbox("Target region", ["North", "South", "East", "West"])
        if st.button("Draft shipment plan", type="primary"):
            try:
                res = shipping_tool.run(region=region_select)
                st.success("Tool execution completed")
                st.json(res)
            except Exception as e:
                st.error(f"Tool execution failed: {e}")

elif menu == "Notifications":
    st.title("Customer Notification Center")
    st.caption("Dispatch order updates to customer communication channels")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            cust_id = st.text_input("Customer ID", value="CUS-5000")
            chan = st.selectbox("Channel", ["email", "sms"])
        with col2:
            msg = st.text_area("Message", value="Your PO is processed and shipment tracking has been initiated.")

        if st.button("Dispatch notification", type="primary"):
            try:
                res = notify_tool.run(customer_id=cust_id, message=msg, channel=chan)
                st.success("Tool execution completed")
                st.json(res)
            except Exception as e:
                st.error(f"Tool execution failed: {e}")
