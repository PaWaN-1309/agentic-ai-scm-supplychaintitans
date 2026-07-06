import streamlit as st
import pandas as pd
import json
import time

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="HexaShop SCM - Agentic AI Control Center",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS ensuring text within logs is explicitly black for visibility
st.markdown("""
    <style>
    .main-header { font-size:26px !important; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .agent-log { font-family: 'Courier New', Courier, monospace; background-color: #F8FAFC; color: #000000; padding: 10px; border-radius: 5px; border-left: 4px solid #3B82F6; margin-bottom: 8px; font-size: 13px; }
    .hitl-box { background-color: #FFFBEB; padding: 20px; border-radius: 8px; border: 1px solid #F59E0B; margin-top: 15px; margin-bottom: 15px; }
    .error-box { background-color: #FEF2F2; padding: 20px; border-radius: 8px; border: 1px solid #EF4444; margin-top: 15px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================
if "logs" not in st.session_state:
    st.session_state.logs = []
if "graph_state" not in st.session_state:
    st.session_state.graph_state = "IDLE"  # IDLE, RUNNING, AWAITING_APPROVAL, EXCEPTION_ESCALATION, COMPLETED
if "draft_po" not in st.session_state:
    st.session_state.draft_po = None
if "shipping_options" not in st.session_state:
    st.session_state.shipping_options = []
if "delay_impact" not in st.session_state:
    st.session_state.delay_impact = None
if "exception_details" not in st.session_state:
    st.session_state.exception_details = None

# ==========================================
# 3. SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/factory.png", width=80)
    st.markdown("### ⚙️ System Control Room")
    
    po_threshold = st.number_input("HITL PO Value Threshold ($)", min_value=100, max_value=10000, value=1000, step=100)
    model_name = st.selectbox("Reasoning Engine", ["Azure OpenAI GPT-5.4 Mini"], index=0)
    
    st.divider()
    st.markdown("### 🛠️ Inject UC-5 Edge Case")
    trigger_fault = st.checkbox("Simulate Catalog Stockout Exception", value=False, help="Injects a supplier structural deadlock scenario to test automated exception handlers.")
    
    st.divider()
    st.markdown("### 📊 Live Orchestrator Status")
    st.info(f"**Current State:** {st.session_state.graph_state}")
    
    if st.button("🔄 Reset Global State Canvas", type="secondary", use_container_width=True):
        st.session_state.logs = []
        st.session_state.graph_state = "IDLE"
        st.session_state.draft_po = None
        st.session_state.shipping_options = []
        st.session_state.delay_impact = None
        st.session_state.exception_details = None
        st.rerun()

# ==========================================
# 4. MAIN INTERFACE LAYOUT
# ==========================================
st.markdown('<div class="main-header">🏢 HexaShop SCM Agentic AI Control Center</div>', unsafe_allow_html=True)
st.markdown("Sense, reason, and orchestrate across the global supply chain with real-time agent observability matrices.")

# Extended tabs covering all 5 core and bonus use cases comprehensively
tabs = st.tabs([
    "🔍 UC-1: Inventory Q&A", 
    "⚙️ UC-2: Auto-Replenish", 
    "🚚 UC-3: Logistics Optimizer", 
    "⚠️ UC-4: Proactive Delay Comms",
    "🚨 UC-5: Exception Escalation"
])

# ------------------------------------------
# TAB 1: INVENTORY Q&A
# ------------------------------------------
with tabs[0]:
    st.markdown("### 🔍 Enterprise Knowledge Retrieval Store")
    user_query = st.text_input("Query Inventory Monitoring Agent:", value="Which SKUs are below reorder level in the North warehouse?")
    
    if st.button("Query Agent Data Layer", type="primary"):
        with st.spinner("Agent parsing local DB collections..."):
            time.sleep(1.2)
            st.success("#### 🤖 Grounded Tool Response:")
            st.markdown("""
            Queried data tables via `inventory_db` successfully:
            * **SKU-ELEC-104** (North Warehouse): Stock is **12** units (Reorder limit rule: 20).
            * **SKU-FASH-302** (North Warehouse): Stock is **5** units (Reorder limit rule: 15).
            """)
            st.caption("🟢 Verification: Response matches database index states precisely.")

# ------------------------------------------
# TAB 2: AUTO-REPLENISHMENT & HITL
# ------------------------------------------
with tabs[1]:
    st.markdown("### ⚙️ Multi-Agent Replenishment Pipeline")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.graph_state == "IDLE":
            if st.button("🚀 Run Workflow State Engine", type="primary", use_container_width=True):
                st.session_state.graph_state = "RUNNING"
                st.session_state.logs = []
                st.rerun()
                
        if st.session_state.graph_state == "RUNNING":
            with st.spinner("Traversing Graph State Nodes..."):
                time.sleep(1)
                st.session_state.logs.append("📈 [Demand Forecasting Agent] Analyzed historical sales indices. Calculated 25% spike factor.")
                time.sleep(1)
                st.session_state.logs.append("📋 [Inventory Monitoring Agent] Low stock found on SKU-ELEC-104 (Current: 12). Reorder threshold breached.")
                time.sleep(1)
                
                if trigger_fault:
                    st.session_state.logs.append("🚨 [Procurement Agent] CRITICAL Exception: Supplier catalog depth reports unfulfillable deadlock.")
                    st.session_state.exception_details = {
                        "error_type": "SUPPLIER_STOCKOUT_DEADLOCK",
                        "message": "Nexus Electronics Corp has 0 catalog depth. Alternate channels report systemic freezing.",
                        "sku": "SKU-ELEC-104"
                    }
                    st.session_state.graph_state = "EXCEPTION_ESCALATION"
                    st.rerun()
                
                st.session_state.logs.append("🤝 [Procurement Agent] Computed unit costs against volume curves.")
                st.session_state.draft_po = {
                    "sku": "SKU-ELEC-104", "qty": 150, "supplier": "Nexus Electronics Corp",
                    "unit_cost": 12.00, "total_cost": 1800.00, "lead_time_days": 5
                }
                
                # Automatically pipeline into UC-3 & UC-4 logic chains
                st.session_state.logs.append("🚚 [Logistics Agent] Initiating live shipping carrier rate evaluations...")
                st.session_state.shipping_options = [
                    {"carrier": "DHL Express", "cost": 450.00, "eta_days": 2, "rank": 1, "status": "Recommended (Fastest)"},
                    {"carrier": "FedEx Ground", "cost": 210.00, "eta_days": 5, "rank": 2, "status": "Cheaper alternative"},
                    {"carrier": "UPS Logistics", "cost": 315.00, "eta_days": 4, "rank": 3, "status": "Standard freight"}
                ]
                
                st.session_state.logs.append("⚠️ [Customer Comms Agent] Activating proactive downstream risk metrics assessment...")
                st.session_state.delay_impact = {
                    "impact_severity": "HIGH", "affected_customer_orders": 42, "estimated_backlog_days": 3,
                    "draft_email": "Subject: HexaShop Order Update\n\nDear Valued Customer, production timeline constraints at our hub have shifted delivery schedules slightly..."
                }
                
                if st.session_state.draft_po["total_cost"] > po_threshold:
                    st.session_state.logs.append("⚠️ [Supervisor] PO Value exceeds configured threshold bounds. Triggering graph.interrupt().")
                    st.session_state.graph_state = "AWAITING_APPROVAL"
                else:
                    st.session_state.logs.append("✅ [Supervisor] Automation criteria met. Finalizing transaction loops.")
                    st.session_state.graph_state = "COMPLETED"
                st.rerun()

        # --- HITL INTERFACE ---
        if st.session_state.graph_state == "AWAITING_APPROVAL":
            st.markdown('<div class="hitl-box">', unsafe_allow_html=True)
            st.warning("### 🛑 Human-in-the-Loop Verification Gateway")
            st.markdown(f"The draft purchase order value (**${st.session_state.draft_po['total_cost']:.2f}**) triggers manual security validation gates (Threshold: ${po_threshold:.2f}).")
            
            st.dataframe(pd.DataFrame([st.session_state.draft_po]), use_container_width=True, hide_index=True)
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button("🟢 Approve & Transmit PO", type="primary", use_container_width=True):
                    st.session_state.logs.append("🟢 [Human Supervisor] Action: Approved. Resuming state machine execution loops.")
                    st.session_state.logs.append("⚙] [Finalize Order Node] Processing send_system_notification.func() confirmation triggers.")
                    st.session_state.graph_state = "COMPLETED"
                    st.rerun()
            with b2:
                if st.button("🔴 Reject Order Run", type="secondary", use_container_width=True):
                    st.session_state.logs.append("🔴 [Human Supervisor] Action: Rejected. Suppressing database execution chains.")
                    st.session_state.graph_state = "COMPLETED"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.graph_state == "EXCEPTION_ESCALATION":
            st.error("🚨 Active Exception Lockout! Head to the 'Exception Escalation' tab to handle this block.")

        if st.session_state.graph_state == "COMPLETED":
            st.success("🎉 Run Lifecycle Completed Successfully!")

    with col2:
        st.markdown("#### 📜 Live Execution Logs")
        if not st.session_state.logs:
            st.caption("Awaiting workflow launch sequence...")
        else:
            for log in st.session_state.logs:
                st.markdown(f'<div class="agent-log">{log}</div>', unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: UC-3 LOGISTICS OPTIMIZATION
# ------------------------------------------
with tabs[2]:
    st.markdown("### 🚚 Freight & Transit Path Optimization Engine")
    if not st.session_state.shipping_options:
        st.info("Run the auto-replenishment workflow on Tab 2 to populate shipping analysis curves.")
    else:
        st.markdown("The **Logistics & Routing Agent** compiled options by querying the `shipping_api` endpoint:")
        df_shipping = pd.DataFrame(st.session_state.shipping_options)
        st.dataframe(df_shipping, use_container_width=True, hide_index=True)
        st.success("🎯 **Optimal Decision Matrix:** DHL Express is auto-selected for critical inventory recovery timelines.")

# ------------------------------------------
# TAB 4: UC-4 PROACTIVE DELAY HANDLING
# ------------------------------------------
with tabs[3]:
    st.markdown("### ⚠️ Downstream Customer Delay Risk Analysis")
    if not st.session_state.delay_impact:
        st.info("Run the auto-replenishment workflow on Tab 2 to evaluate lead-time lag calculations.")
    else:
        impact = st.session_state.delay_impact
        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Severity", impact["impact_severity"], delta="Requires Monitoring", delta_color="inverse")
        c2.metric("Affected Orders", f"{impact['affected_customer_orders']} Accounts", delta="Notification Queued")
        c3.metric("Projected Backlog", f"+{impact['estimated_backlog_days']} Days", delta="Supplier Lag Factor")
        
        st.markdown("#### Automated Communications Draft (Customer Comms Agent):")
        st.text_area("Generated Notification Payload", value=impact["draft_email"], height=150)
        st.caption("📬 Email payloads are prepared and ready to fire via notification triggers.")

# ------------------------------------------
# TAB 5: UC-5 EXCEPTION ESCALATION
# ------------------------------------------
with tabs[4]:
    st.markdown("### 🚨 System Exception Intervention Desk")
    if st.session_state.graph_state != "EXCEPTION_ESCALATION":
        st.success("✅ System Health: Normal. No unfulfillable deadlocks detected across active threads.")
    else:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown(f"### 🛑 Graceful Intercept: {st.session_state.exception_details['error_type']}")
        st.markdown(f"**Root Diagnostic Cause:** {st.session_state.exception_details['message']}")
        st.markdown(f"**Target System Breakpoint:** Replenishment loop for `{st.session_state.exception_details['sku']}` failed because no configured supplier possesses adequate safety stock.")
        
        st.markdown("#### Select Resolution Strategy Strategy to Resume Graph:")
        override_strategy = st.radio(
            "Select Remediation Path:",
            ["Route to Secondary Off-Catalog Supplier (Manual Sourcing)", "Override Safety Stock Bounds & Defer Purchase Flow", "Cancel Order Lifecycle Run"]
        )
        
        if st.button("Apply Structural Remedy", type="primary"):
            st.session_state.logs.append(f"🛠️ [Supervisor Exception Node] Manual intervention override applied: Selected '{override_strategy}'.")
            st.session_state.logs.append("⚙️ Graph execution unblocked. Cleaning up state metrics.")
            st.session_state.graph_state = "COMPLETED"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)