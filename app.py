import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import datetime
import contextlib  # <-- ADD THIS
import re
from fdd_core import RealWorldForensicEnvironment
import database as db

# ==========================================
# 1. APP CONFIGURATION & MULTI-TENANCY
# ==========================================
st.set_page_config(page_title="FDD Data Engine", layout="wide", initial_sidebar_state="expanded")

if 'env' not in st.session_state:
    st.session_state.env = RealWorldForensicEnvironment(standard='IND_AS')
    
    # --- HOTFIX: Inject missing schemas into the backend registry ---
    # This prevents the ValueError when committing Tab 4 Operational Registers
    missing_schemas = {
        "PAYROLL_REGISTER": ['TXN_ID', 'DATE', 'AMOUNT', 'EMPLOYEE_ID'],
        "HRMS_MASTER": ['EMPLOYEE_ID', 'JOINING_DATE', 'EXIT_DATE', 'STATUS'],
        "INVENTORY_AGING": ['ITEM_CODE', 'VALUE', 'DAYS_STAGNANT'],
        "IT_PROJECT_TRACKER": ['PROJECT_ID', 'STATUS', 'CAPITALIZED_AMOUNT'],
        "BANK_RECONCILIATION_STATEMENT": ['DATE', 'PARTICULARS', 'UNRECONCILED_AMOUNT'],
        "RELATED_PARTY_DIRECTORY": ['NAME', 'RELATIONSHIP_TYPE'],
        "LEASE_REGISTER": ['LEASE_ID', 'END_DATE', 'MONTHLY_RENT', 'SPECIFIC_IBR']
    }
    for schema, targets in missing_schemas.items():
        if schema not in st.session_state.env.OPERATIONAL_SCHEMA_REGISTRY:
            st.session_state.env.OPERATIONAL_SCHEMA_REGISTRY[schema] = {'mandatory': targets}

# --- DEAL WORKSPACE CONTROLS ---
st.sidebar.header("🏢 Deal Workspace")

# 1. Start completely blank.
deal_name = st.sidebar.text_input(
    "Active Project Name", 
    value="", 
    placeholder="e.g. Project_Apollo",
    help="Type a deal name to instantly isolate or switch SQL databases."
)

# 2. Add the Password Gate
deal_password = st.sidebar.text_input(
    "Workspace Password",
    value="",
    type="password",
    placeholder="Enter password",
    help="Required to unlock the deal environment."
)

st.sidebar.markdown("### ⚙️ Deal Parameters")
selected_cutoff = st.sidebar.date_input(
    "Fiscal Cut-Off Date", 
    value=datetime.date(2025, 3, 31),
    help="Dynamic time horizon. The engine uses this anchor to detect pre-dated revenues, post-dated expenses, and calculate exact IFRS 16 lease end dates."
)

# 3. The Security Gate & Clean Landing Page
MASTER_PASSWORD = "admin" 

if not deal_name or deal_password != MASTER_PASSWORD:
    st.title("🔎 Financial Due Diligence (FDD) Engine")
    
    # --- TOP-PINNED CALL-TO-ACTION BANNER ---
    if not deal_name:
        st.warning("👈 **Action Required:** Please type an Active Project Name in the sidebar to initialize your workspace.")
    elif deal_password != MASTER_PASSWORD:
        st.error("👈 **Access Denied:** Incorrect Workspace Password.")

    st.markdown("""
    Welcome to the FDD Engine. A high-performance, full-population algorithmic workspace engineered to eliminate manual sampling, sanitize messy ERP data, and generate partner-ready Quality of Earnings (QoE) bridges.
    """)
    
    st.divider()
    st.markdown("### 🚀 Platform Capabilities")
    
    # --- 2x2 CARD GRID LAYOUT ---
    col_grid1, col_grid2 = st.columns(2)
    
    with col_grid1:
        st.markdown("#### 📂 Phase 1: Data Sanitization")
        st.markdown("Standardize messy ERP extractions, fix broken accounting formats, normalize text strings, and export a clean 'Normalized Databook' (.csv) for modeling.")
        
        st.markdown("#### 🔬 Phase 3: Forensic Sweep")
        st.markdown("Dynamically shift between Ind AS, US GAAP, and IFRS to execute 25 automated testing protocols, flagging cut-offs, shadow debt, and ECL shortfalls.")
        
    with col_grid2:
        st.markdown("#### 🔀 Phase 2: Triangulation & AI")
        st.markdown("Cross-reference GL transactions against subledgers (Warehouse, Bank) and deploy the AI Fallback Prompt to structure legacy account names.")
        
        st.markdown("#### 🧑‍💼 Phase 4: Workbench & Output")
        st.markdown("Review definitive and pending risk flags, commit pro-forma overrides with mandatory evidence (.pdf/.xlsx), and download multi-sheet QoE reports.")
        
    st.stop()

# 4. If credentials pass, create the SQL prefix and proceed to render the app
st.session_state.deal_prefix = "".join([c for c in deal_name if c.isalnum() or c == '_']).upper()

def save_deal_data(table_name, df):
    """Saves data isolated to the active deal workspace"""
    db.save_to_vault(f"{st.session_state.deal_prefix}_{table_name}", df)

@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith(('.xls', '.xlsx')):
        return pd.read_excel(file)
    return None

def render_mapping_ui(df, book_type, target_columns):
    with st.expander(f"👁️ View {book_type} Raw Data Preview"):
        st.dataframe(df.head(5), use_container_width=True)

    mapping_dictionary = {}
    uploaded_columns = ['--- Not Present ---'] + list(df.columns)

    # --- UPGRADE: Clean Grid Layout (4 per row) ---
    chunk_size = 4
    for i in range(0, len(target_columns), chunk_size):
        chunk = target_columns[i:i+chunk_size]
        cols = st.columns(len(chunk))
        for idx, target in enumerate(chunk):
            with cols[idx]:
                default_idx = uploaded_columns.index(target) if target in uploaded_columns else 0
                
                selected_col = st.selectbox(
                    f"Map to: {target}", 
                    options=uploaded_columns, 
                    index=default_idx,
                    key=f"{book_type}_{target}"
                )
                if selected_col != '--- Not Present ---':
                    mapping_dictionary[selected_col] = target
    return mapping_dictionary

def render_waterfall_chart(results_dict):
    """Generates an M&A Standard EBITDA Bridge Waterfall Chart"""
    math = results_dict['Valuation_Math']
    
    fig = go.Figure(go.Waterfall(
        name="20", orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Reported EBITDA", "Verified Adjustments (Red)", "Pending Exposure (Amber)", "Adjusted EBITDA"],
        textposition="outside",
        text=[
            f"₹{math['Reported_EBITDA']/100000:,.1f}L", 
            f"₹{math['Total_Verified_Adjustments']/100000:,.1f}L", 
            f"₹{-math['Total_Pending_Exposure']/100000:,.1f}L", 
            f"₹{(math['Current_Adjusted_EBITDA'] - math['Total_Pending_Exposure'])/100000:,.1f}L"
        ],
        y=[
            math['Reported_EBITDA'], 
            math['Total_Verified_Adjustments'], 
            -math['Total_Pending_Exposure'], 
            0
        ],
        connector={"line":{"color":"rgb(63, 63, 63)"}},
        decreasing={"marker":{"color":"#ff4b4b"}},
        increasing={"marker":{"color":"#00cc96"}},
        totals={"marker":{"color":"#1f77b4"}}
    ))
    
    fig.update_layout(title="Quality of Earnings (QoE) Bridge", showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
    return fig

def generate_excel_report(results, deal, analyst_ledger_df=None):
    """Generates a multi-sheet, partner-ready Excel file in memory"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Summary Math
        math_df = pd.DataFrame([results['Valuation_Math']])
        math_df.to_excel(writer, sheet_name="QoE Summary", index=False)
        
        # Sheet 2: Red Flags
        if not results['Definitive_Bridge'].empty:
            results['Definitive_Bridge'].to_excel(writer, sheet_name="Red Flags (Definitive)", index=False)
            
        # Sheet 3: Amber Flags
        if not results['Suspense_Bucket'].empty:
            results['Suspense_Bucket'].to_excel(writer, sheet_name="Amber Flags (Suspense)", index=False)
            
        # Sheet 4: Green Flags
        if 'Green_Bucket' in results and not results['Green_Bucket'].empty:
            results['Green_Bucket'].to_excel(writer, sheet_name="Green Flags (Waived)", index=False)
            
        # Sheet 5: Vault B (The Audit Trail)
        if analyst_ledger_df is not None and not analyst_ledger_df.empty:
            analyst_ledger_df.to_excel(writer, sheet_name="Analyst Ledger", index=False)
            
    return output.getvalue()

# ==========================================
# 2. SIMPLIFIED HEADER
# ==========================================
st.title("🔎 Financial Due Diligence (FDD) Engine")
st.markdown(f"**Active Workspace:** `{deal_name}`")
st.markdown("""
**How to use this workspace:**
1. **Core Books:** Upload the raw General Ledger and Trial Balance here.
2. **Account Mapping:** Tell the Engine how to read the client's custom account names.
3. **Financials & Aging:** Upload reported P&L/Balance Sheets and AP/AR aging reports.
4. **Operational Registers:** Upload non-financial logs (like Bank Statements or Disclosures) for deep cross-referencing.
""")
st.divider()

# ==========================================
# 3. PHASE 1: THE FIVE DOORS (INGESTION & WIKI)
# ==========================================
tab1, tab2, tab3, tab4, tab_wiki = st.tabs([
    "📂 1. Core Books", 
    "🔀 2. Account Mapping", 
    "⏳ 3. Financials & Aging", 
    "📚 4. Operational Registers",
    "📖 5. Methodology Wiki"
])


# ------------------------------------------
# DOOR 1: CORE BOOKS (GL & TB)
# ------------------------------------------
with tab1:
    col_tb, col_gl = st.columns(2)
    
    with col_tb:
        st.subheader("⚖️ Trial Balance")
        tb_file = st.file_uploader(
            "Upload Trial Balance", 
            type=['csv', 'xlsx'], 
            key="tb_up",
            help="Ensures the target's ledgers fundamentally balance to zero before forensic bridging begins."
        )
        if tb_file:
            tb_df = load_data(tb_file)
            
            if tb_df is not None:
                tb_mapping = render_mapping_ui(tb_df, "TRIAL_BALANCE", ['ACCOUNT_NAME', 'DEBIT', 'CREDIT'])
                if st.button("Commit TB to Vault", type="primary", key="btn_tb"):
                    mapped_tb = tb_df.rename(columns=tb_mapping)
                    st.session_state.env.ingest_subledger_or_aging('TRIAL_BALANCE', mapped_tb)
                    save_deal_data('TRIAL_BALANCE', mapped_tb)
                    st.success("Trial Balance locked in SQL Vault!")

    with col_gl:
        st.subheader("📓 General Ledger")
        gl_file = st.file_uploader(
            "Upload General Ledger", 
            type=['csv', 'xlsx'], 
            key="gl_up",
            help="The primary transaction data lake. Required to execute 90% of the Quality of Earnings adjustments."
        )
        
        if gl_file:
            st.markdown("##### ⚙️ Engine Tuning for General Ledger")
            
            # --- Lever 1: Materiality ---
            c_mat, c_mat_auto = st.columns([3, 1])
            auto_mat = c_mat_auto.checkbox("🤖 Auto (0.5% Rev)", value=True, help="Applies the standard M&A rule of thumb: 0.5% of trailing revenue.")
            custom_mat = c_mat.number_input(
                "Materiality Limit (₹)", 
                value=500000, 
                step=50000, 
                disabled=auto_mat, 
                help="Filters out immaterial noise. Sets the minimum currency value required to flag an entry as a definitive QoE adjustment."
            )
            st.session_state.env.user_materiality_value = None if auto_mat else custom_mat
            st.session_state.env.runtime_thresholds['materiality_limit_in_currency'] = custom_mat

            # --- Lever 2: Cut-Off Buffer ---
            c_cut, c_cut_auto = st.columns([3, 1])
            auto_cut = c_cut_auto.checkbox("🤖 Auto (15 Days)", value=True, help="Applies the Big 4 standard 15-day pre/post fiscal year-end buffer.")
            custom_cut = c_cut.number_input(
                "Cut-Off Testing Buffer (Days)", 
                value=15, 
                step=5, 
                disabled=auto_cut, 
                help="Defines the days before and after the fiscal year-end to scan for prematurely recognized revenue or deferred expenses."
            )
            st.session_state.env.runtime_thresholds['cutoff_window_days'] = 15 if auto_cut else custom_cut

            # --- Lever 3: Outlier Sensitivity ---
            c_sens, c_sens_auto = st.columns([3, 1])
            auto_sens = c_sens_auto.checkbox("🤖 Auto (Normal)", value=True, help="Applies standard Z-score limits for run-rate volatility.")
            custom_sens = c_sens.selectbox(
                "Outlier Sensitivity", 
                options=["STRICT", "NORMAL", "LOOSE"], 
                index=1, 
                disabled=auto_sens, 
                help="Controls statistical strictness. 'STRICT' isolates extreme fraud spikes, while 'LOOSE' flags minor operational deviations."
            )
            st.session_state.env.runtime_thresholds['outlier_sensitivity'] = "NORMAL" if auto_sens else custom_sens

            # --- Lever 4: De Minimis CapEx ---
            c_cap, c_cap_auto = st.columns([3, 1])
            auto_cap = c_cap_auto.checkbox("🤖 Auto (₹50k)", value=True, help="Applies a standard ₹50,000 corporate policy limit.")
            custom_cap = c_cap.number_input(
                "De Minimis CapEx Floor (₹)", 
                value=50000, 
                step=10000, 
                disabled=auto_cap, 
                help="The company's capitalization threshold. Purchases below this amount are reclassified from Fixed Assets to OPEX, reducing Adjusted EBITDA."
            )
            st.session_state.env.runtime_thresholds['capex_floor'] = 50000 if auto_cap else custom_cap

            gl_df = load_data(gl_file)
            if gl_df is not None:
                gl_mapping = render_mapping_ui(gl_df, "GENERAL_LEDGER", ['TXN_ID', 'DATE', 'ACCOUNT_NAME', 'PARTY_NAME', 'DEBIT', 'CREDIT', 'AMOUNT', 'NARRATION'])
                if st.button("Commit GL to Vault", type="primary", key="btn_gl"):
                    mapped_gl = gl_df.rename(columns=gl_mapping)
                    st.session_state.env.ingest_general_ledger(mapped_gl)
                    save_deal_data('GENERAL_LEDGER', mapped_gl)
                    st.success("General Ledger locked in SQL Vault!")

# ------------------------------------------
# DOOR 2: ACCOUNT MAPPING & DATABOOK
# ------------------------------------------
with tab2:
    col_map1, col_map2 = st.columns([2, 1])
    
    with col_map1:
        st.subheader("🔀 Account Mapping Guide")
        st.markdown("""
        Every company names their accounts differently. The Engine needs a simple two-column file to translate the client's names into our standard FDD buckets. 
        **Do not map individual vendors.** Map the ledger account names.
        
        | Client's Raw Account Name | 🎯 Maps To FDD Bucket |
        | :--- | :--- |
        | Software Subscriptions | `OPEX` |
        | Scrap Sales | `OTHER_INCOME` |
        | HDFC Current A/C | `BANK` |
        """)
        
        map_file = st.file_uploader(
            "Upload Mapping Matrix", 
            type=['csv', 'xlsx'], 
            key="map_up",
            help="Translates the target company's custom chart of accounts into standardized FDD categories (e.g., OPEX, REVENUE, COGS)."
        )
        
        if map_file:
            map_df = load_data(map_file)
            if map_df is not None:
                map_dict = render_mapping_ui(map_df, "MAPPING_SCHEDULE", ['RAW_ACCOUNT_NAME', 'FDD_REPORT_LINE'])
                if st.button("Apply Mapping to Vault", type="primary"):
                    mapped_schedule = map_df.rename(columns=map_dict)
                    st.session_state.env.ingest_mapping_schedule(mapped_schedule)
                    save_deal_data('MAPPING_SCHEDULE', mapped_schedule)
                    
                    if 'GENERAL_LEDGER' in st.session_state.env._ledgers_reconciliations:
                        st.session_state.env.apply_mapping_to_gl()
                        st.success("Mapping applied to General Ledger and locked in SQL Vault!")
                    else:
                        st.warning("Mapping schedule saved to Vault. Upload the General Ledger in Tab 1 to apply it.")
                        
    # --- INDEPENDENT FEATURE: NORMALIZED DATABOOK ---
    with col_map2:
        st.subheader("📥 Data Export")
        st.info("The Normalized Databook is the fully cleaned, standardized, and tagged transaction ledger. Used by the buyer's IT and FP&A teams for ERP migration and internal modeling.")
        
        all_tables_db = db.check_vault_contents()
        deal_tabs_db = [t.replace(f"{st.session_state.deal_prefix}_", "") for t in all_tables_db if t.startswith(st.session_state.deal_prefix)]
        
        if 'GENERAL_LEDGER' in deal_tabs_db and 'MAPPING_SCHEDULE' in deal_tabs_db:
            if st.button("Prepare Normalized Databook (.csv)", use_container_width=True):
                with st.spinner("Standardizing strings, numbers, and applying mapping tags..."):
                    raw_gl = db.get_from_vault(f"{st.session_state.deal_prefix}_GENERAL_LEDGER")
                    raw_map = db.get_from_vault(f"{st.session_state.deal_prefix}_MAPPING_SCHEDULE")
                    
                    temp_env = RealWorldForensicEnvironment(standard='IND_AS')
                    temp_env.ingest_general_ledger(raw_gl)
                    temp_env.ingest_mapping_schedule(raw_map)
                    temp_env.apply_mapping_to_gl()
                    
                    csv_data = temp_env._ledgers_reconciliations['GENERAL_LEDGER'].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Databook CSV", 
                        data=csv_data, 
                        file_name=f"{deal_name}_Normalized_Databook.csv", 
                        mime="text/csv",
                        type="primary",
                        use_container_width=True
                    )
        else:
            st.warning("Upload a General Ledger and Mapping Schedule to unlock the Databook export.")

        st.markdown("---")
        with st.expander("💡 Architecture Note: Enterprise AI Mapping & The Cost Center Reality"):
            st.info(
            "**The Institutional Hybrid Ingestion Strategy:**\n\n"
            "In a live SAP/Oracle transaction environment, mapping purely by text strings fails due to dimensional context "
            "(e.g., 'Contract Labor' is COGS in an assembly cost center, but OPEX in an administrative cost center). "
            "Enterprise deal teams first map the rigid numerical GL Codes and Cost Center hierarchies. "
            "This AI agent is deployed as a highly efficient fallback engine to categorize the unstructured spillover "
            "(messy subledgers, legacy ERP dumps, or vague narrations) that rigid rules miss, entirely bypassing memory bottlenecks."
            )
        
            st.markdown("**Production AI Fallback Prompt:**")
            st.code('''You are an elite financial data engineer. Your task is to map a provided list of messy, raw General Ledger account names into a strict Quality of Earnings (QoE) schema. 

            CONTEXT: 
            The target company operates in the following industry/business model: [INSERT BUSINESS TYPE/INDUSTRY HERE]

            You must map each account to EXACTLY ONE of the following approved categories: 
            ["REVENUE", "COGS", "OPEX", "OTHER_INCOME", "ASSET", "LIABILITY", "BANK", "UNCLASSIFIED"]

            STRICT RULES:
            1. COGS: Strictly for direct materials, factory labor, manufacturing overhead, and inbound freight. Adjust classification logic strictly based on the specific business model provided above.
            2. OPEX: For SG&A, admin, outbound logistics, professional fees, and general payroll.
            3. OTHER_INCOME: For non-operating items (scrap sales, interest, forex gains).
            4. UNCLASSIFIED (The Failsafe): If an account name is highly ambiguous (e.g., "Suspense", "Misc"), or you lack the Cost Center dimensions required to make a 95% confident decision, you MUST classify it as "UNCLASSIFIED" to force manual deal team review.
            5. Output format: Return strictly as a valid JSON dictionary where keys are the exact raw account names and values are the mapped categories. No markdown, no conversational text. 

            INPUT DATA (Unique Account Strings):
            [INSERT LIST OF UNIQUE ACCOUNT NAMES HERE]''', language='text')
            
# ------------------------------------------
# DOOR 3: FINANCIALS & AGING
# ------------------------------------------
with tab3:
    col_fin, col_aging = st.columns(2)
    
    with col_fin:
        st.subheader("📈 Historical Financials")
        st.markdown("Upload Management's reported P&L and Balance Sheet statements aligned to your fiscal cutoff timeline.")
        
        reported_ebitda_input = st.number_input(
            "Reported EBITDA (₹)", 
            value=5000000.0, 
            step=500000.0, 
            help="The management-adjusted EBITDA baseline. Our forensic engine adjustments will bridge directly off this anchor."
        )
        st.session_state.temp_ebitda = reported_ebitda_input
        
        # Dynamically align the 3 historical years ending in the cut-off year
        cutoff_year = selected_cutoff.year
        aligned_years = [f"FY{str(y)[-2:]}" for y in range(cutoff_year - 2, cutoff_year + 1)]
        
        st.markdown(f"**Aligned Historical Period:** `{'`, `'.join(aligned_years)}` (derived from cutoff year {cutoff_year})")
        
        fin_type = st.selectbox("Statement Type", ["Profit & Loss", "Balance Sheet"], key="fin_statement_type")
        
        # Create persistent, individual uploaders for each aligned financial year
        cols_fin = st.columns(len(aligned_years))
        for idx, yr in enumerate(aligned_years):
            with cols_fin[idx]:
                st.markdown(f"##### {yr}")
                fin_file = st.file_uploader(
                    f"Upload {yr} {fin_type}", 
                    type=['csv', 'xlsx'], 
                    key=f"fin_up_{yr}_{fin_type}",
                    help=f"Upload the reported {fin_type} for {yr}."
                )
                if fin_file:
                    fin_df = load_data(fin_file)
                    if fin_df is not None:
                        with st.expander(f"👁️ View {yr} {fin_type} Preview"):
                            st.dataframe(fin_df.head(3), use_container_width=True)
                        
                        fin_mapping = render_mapping_ui(fin_df, f"{yr}_{fin_type.upper().replace(' ', '_')}", ['ACCOUNT_NAME', 'AMOUNT'] if 'AMOUNT' in fin_df.columns else list(fin_df.columns))
                        
                        mapped_fin = fin_df.rename(columns=fin_mapping)
                        st.session_state.env.ingest_financial_statement(f"{yr}_{fin_type.upper().replace(' ', '_')}", mapped_fin)
                        save_deal_data(f"{yr}_{fin_type.upper().replace(' ', '_')}", mapped_fin)
                        st.success(f"{yr} {fin_type} locked in SQL Vault!")

    with col_aging:
        st.subheader("⏳ Aging Reports")
        sub_type = st.selectbox("Select Ledger", ['AR_AGING', 'AP_AGING'], key="aging_select_ledger")
        
        std_sub_file = st.file_uploader(
            f"Upload {sub_type}", 
            type=['csv', 'xlsx'], 
            key=f"std_sub_up_{sub_type}", 
            help="Evaluates working capital lockups, supplier concentration risk, and calculates expected credit loss."
        )
        
        # --- Lever 5: IFRS 9 ECL Matrix ---[cite: 2]
        if std_sub_file and sub_type == 'AR_AGING':
            st.markdown("##### ⚙️ IFRS 9 Expected Credit Loss (ECL) Matrix")
            st.info("Define the baseline default probabilities for each aging bucket to calculate the required AR provision.")
            
            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            ecl_30 = c_m1.number_input("0-30 Days (%)", value=1.0, step=0.5, key="ecl_30_in") / 100.0
            ecl_60 = c_m2.number_input("31-60 Days (%)", value=5.0, step=1.0, key="ecl_60_in") / 100.0
            ecl_90 = c_m3.number_input("61-90 Days (%)", value=15.0, step=2.0, key="ecl_90_in") / 100.0
            ecl_180 = c_m4.number_input(">90 Days (%)", value=50.0, step=5.0, key="ecl_180_in") / 100.0
            
            # Store the matrix in the environment state
            st.session_state.env.runtime_thresholds['ecl_matrix'] = {
                '0-30': ecl_30,
                '31-60': ecl_60,
                '61-90': ecl_90,
                '91-9999': ecl_180
            }
                    
        if std_sub_file:
            std_sub_df = load_data(std_sub_file)
            if std_sub_df is not None:
                aging_targets = ['PARTY_NAME', 'VALUE', 'DAYS_OVERDUE']
                std_sub_map = render_mapping_ui(std_sub_df, sub_type, aging_targets)
                
                if st.button(f"Commit {sub_type} to Vault", type="primary", key="commit_aging_btn"):
                    mapped_std_sub = std_sub_df.rename(columns=std_sub_map)
                    st.session_state.env.ingest_subledger_or_aging(sub_type, mapped_std_sub)
                    save_deal_data(sub_type, mapped_std_sub)
                    st.success(f"{sub_type} locked in SQL Vault!")
                    
# ------------------------------------------
# DOOR 4: OPERATIONAL REGISTERS
# ------------------------------------------
with tab4:
    st.subheader("📚 Specialized Operational Logs & Disclosures")
    st.info(
        "📋 **Data Room Upload Requirements (Cut-Off Testing):**\n"
        "To accurately execute Ind AS 115 and cash window-dressing tests, your uploaded "
        "Bank Statements, Warehouse Dispatch Logs, and Purchase Registers **must include at least 15 to 30 days of data AFTER the fiscal cut-off date.**"
    )
    
    REGISTER_DESCRIPTIONS = {
        "BANK_STATEMENT": "Cross-references physical cash movements against reported revenue to flag fake billing.",
        "DISPATCH_REGISTER": "Verifies that recorded product sales actually physically left the warehouse.",
        "FIXED_ASSET_REGISTER": "Tracks asset utilization rates to hunt for ghost machinery and dead capital.",
        "HRMS_MASTER": "The master HR roster used to cross-reference against payroll to flag terminated employees still receiving pay.",
        "PAYROLL_REGISTER": "Analyzes salary disbursements to find ghost employees and unauthorized executive payouts.",
        "INVENTORY_AGING": "Evaluates the age of stock to force write-offs for dead or obsolete inventory.",
        "NOTES_TO_ACCOUNTS": "Scans qualitative text for hidden lawsuits, guarantees, or off-balance sheet risks.",
        "IT_PROJECT_TRACKER": "Evaluates internal software development logs to verify if capitalized IT costs are genuine or hidden OPEX.",
        "BANK_RECONCILIATION_STATEMENT": "Identifies stale cheques, unrecorded debits, and timing differences masking cash shortfalls.",
        "LEASE_REGISTER": "Calculates true IFRS 16 / Ind AS 116 shadow debt by executing an NPV calculation across active lease schedules.",
        "RELATED_PARTY_DIRECTORY": "Master watchlist of all related entities, founders, and directors. Used by Tests 12, 16, and 21 to flag unauthorized cash leakage or sweetheart deals.",
        "VENDOR_MASTER_FILE": "Master list of approved suppliers. Used to cross-reference against Employee and Related Party data to flag conflict of interest or ghost vendors.",
    }
    
    available_subledgers = list(st.session_state.env.OPERATIONAL_SCHEMA_REGISTRY.keys())
    forced_books = ["NOTES_TO_ACCOUNTS", "PAYROLL_REGISTER", "INVENTORY_AGING", "HRMS_MASTER", "IT_PROJECT_TRACKER", "BANK_RECONCILIATION_STATEMENT", "RELATED_PARTY_DIRECTORY", "LEASE_REGISTER"]
    for book in forced_books:
        if book not in available_subledgers:
            available_subledgers.append(book)
    
    selected_register = st.selectbox("Select Register Type", available_subledgers)
    
    dynamic_help_text = REGISTER_DESCRIPTIONS.get(
        selected_register, 
        "Used for specialized forensic cross-referencing against the General Ledger."
    )
    
    # --- UPGRADE: Dynamic Uploader Key prevents Ghost Uploads in Tab 4 ---
    reg_file = st.file_uploader(
        f"Upload {selected_register}", 
        type=['csv', 'xlsx'], 
        key=f"reg_up_{selected_register}", 
        help=dynamic_help_text
    )

    # --- Contextual Local Levers based on selection ---
    if reg_file and selected_register in ['PAYROLL_REGISTER', 'HRMS_MASTER']:
        st.markdown(f"##### ⚙️ Engine Tuning for {selected_register}")
        c_pay, c_pay_auto = st.columns([3, 1])
        auto_pay = c_pay_auto.checkbox("🤖 Auto (30 Days)", value=True, help="Applies standard 30-day Full & Final (F&F) settlement grace period.")
        custom_pay = c_pay.number_input(
            "Zombie Pay Grace Period (Days)", 
            value=30, 
            step=15, 
            disabled=auto_pay, 
            help="Accounts for the company's legitimate F&F settlement delays, preventing false 'Ghost Employee' flags for recent departures."
        )
        st.session_state.env.runtime_thresholds['zombie_pay_grace_days'] = 30 if auto_pay else custom_pay

    if reg_file and selected_register == 'INVENTORY_AGING':
        st.markdown(f"##### ⚙️ Engine Tuning for {selected_register}")
        c_inv, c_inv_auto = st.columns([3, 1])
        auto_inv = c_inv_auto.checkbox("🤖 Auto (365 Days)", value=True, help="Flags stock older than 365 days and assumes a 50% QoE write-off.")
        custom_inv = c_inv.number_input(
            "Dead Stock Cliff (Days)", 
            value=365, 
            step=90, 
            disabled=auto_inv, 
            help="The age at which stagnant inventory is considered obsolete. Required to calculate write-downs that negatively impact EBITDA."
        )
        st.session_state.env.runtime_thresholds['dead_stock_cliff_days'] = 365 if auto_inv else custom_inv

        c_prov, c_prov_auto = st.columns([3, 1])
        auto_prov = c_prov_auto.checkbox("🤖 Auto (50% Loss)", value=True, help="Standard salvage assumption for obsolete stock.")
        custom_prov = c_prov.slider(
            "Provision Coverage Ratio (%)", 
            min_value=10, 
            max_value=100, 
            value=50, 
            step=10, 
            disabled=auto_prov, 
            help="The percentage of dead stock value to write off. Aggressive buyers assume a 100% loss; standard salvage value assumes 50%."
        )
        st.session_state.env.runtime_thresholds['inventory_provision_ratio'] = 0.50 if auto_prov else (custom_prov/100)
    
    if reg_file:
        reg_df = load_data(reg_file)
        if reg_df is not None:
            # --- SANITIZED DIRECTORY & REGISTER MAPPING ---
            if selected_register == "NOTES_TO_ACCOUNTS":
                reg_targets = ['DISCLOSURE_CATEGORY', 'NARRATIVE']
            elif selected_register == "HRMS_MASTER":
                reg_targets = ['EMPLOYEE_ID', 'JOINING_DATE', 'EXIT_DATE', 'STATUS']
            elif selected_register == "RELATED_PARTY_DIRECTORY":
                reg_targets = ['NAME', 'RELATIONSHIP_TYPE']
            elif selected_register == "VENDOR_MASTER_FILE":
                reg_targets = ['PARTY_NAME', 'ADDRESS', 'TAX_ID']
            elif selected_register == "IT_PROJECT_TRACKER":
                reg_targets = ['PROJECT_ID', 'STATUS', 'CAPITALIZED_AMOUNT']
            elif selected_register == "BANK_RECONCILIATION_STATEMENT":
                reg_targets = ['DATE', 'PARTICULARS', 'UNRECONCILED_AMOUNT']
            else:
                reg_targets = st.session_state.env.OPERATIONAL_SCHEMA_REGISTRY.get(selected_register, {}).get('mandatory', ['ID', 'DATE', 'VALUE'])
                
            reg_mapping = render_mapping_ui(reg_df, selected_register, reg_targets)
            
            if st.button(f"Commit {selected_register} to Vault", type="primary"):
                mapped_reg = reg_df.rename(columns=reg_mapping)
                mapped_reg.columns = [str(c).strip().upper() for c in mapped_reg.columns]
                
                # --- PROPER VAULT ROUTING ---
                if selected_register in ["HRMS_MASTER", "RELATED_PARTY_DIRECTORY"]:
                    st.session_state.env.ingest_directory(selected_register, mapped_reg)
                elif selected_register != "NOTES_TO_ACCOUNTS":
                    dummy_map = {c: c for c in mapped_reg.columns}
                    st.session_state.env.ingest_operational_register(selected_register, mapped_reg, dummy_map)
                
                save_deal_data(selected_register, mapped_reg)
                st.success(f"{selected_register} locked in SQL Vault!")

# ------------------------------------------
# DOOR 5: THE METHODOLOGY WIKI
# ------------------------------------------
with tab_wiki:
    st.markdown("""
## 🧠 FDD Engine: Analytical Test Directory

This methodology wiki explains the logic behind the engine’s automated forensic tests. Each protocol is designed to evaluate a specific accounting risk using the books, subledgers, schedules, directories, and disclosures already loaded into the workspace.

The objective is not simply to produce flags. The objective is to explain what the engine is checking, why the issue matters in due diligence, what data the test depends on, how the trigger works, and what an analyst should request next when the evidence path is not obvious.

---

## 📌 Index of Tests

1. [**Test_01** — Revenue Integrity Screen](#test_01)  
2. [**Test_03** — Bill-and-Hold Verification](#test_03)  
3. [**Test_04** — Run-Rate Smoothing](#test_04)  
4. [**Test_04_Gap** — Execution Gap Screen](#test_04_gap)  
5. [**Test_05_Phantom** — Phantom Vendor Screen](#test_05_phantom)  
6. [**Test_05_Cutoff** — Cut-Off Squeeze Screen](#test_05_cutoff)  
7. [**Test_06** — Round-Tripping Volume](#test_06)  
8. [**Test_08** — Overhead Absorption](#test_08)  
9. [**Test_09** — Inventory Obsolescence](#test_09)  
10. [**Test_10** — Expense Cut-Off Deferral](#test_10)  
11. [**Test_11** — Extraordinary Expenses](#test_11)  
12. [**Test_12** — Comprehensive RPT Sweep](#test_12)  
13. [**Test_13** — Contingent Liabilities](#test_13)  
14. [**Test_14** — Bad Debt Provisioning](#test_14)  
15. [**Test_15** — Lease Capitalization](#test_15)  
16. [**Test_16** — Payroll Integrity](#test_16)  
17. [**Test_17** — Advance Revenue Classification](#test_17)  
18. [**Test_18** — Asset Impairment & Obsolescence](#test_18)  
19. [**Test_19** — Intangible Assets Multi-Book](#test_19)  
20. [**Test_20** — Cash Window Dressing](#test_20)  
21. [**Test_21** — Management Fees & ESOPs](#test_21)  
22. [**Test_22** — Foreign Exchange Isolation](#test_22)  
23. [**Test_23** — Behavioral Subledger Evasion](#test_23)  
24. [**Test_24** — Tax & Statutory Integrity](#test_24)  
25. [**Test_25** — Net Debt & Working Capital](#test_25)  

---

<a id="test_01"></a>
## **Test_01** — Revenue Integrity Screen

| Field | Detail |
|---|---|
| Primary Risk | Year-end top-line inflation |
| Books Required | General Ledger; optional bank-clearing support |
| Output Type | Amber |
| Typical Follow-Up | Invoices, dispatch proof, credit notes, customer confirmation, receipts trail |

**What this test checks**  
This test looks for unusually large year-end revenue spikes that do not resemble the company’s normal transaction pattern.

**Why it matters**  
A closing-week revenue surge can indicate channel stuffing, unsupported cut-off recognition, temporary billing, or artificial acceleration of sales into the diligence period.

**Detection logic**  
The engine isolates revenue-coded ledger entries, calculates a normal transaction baseline outside the final week, and identifies closing-period revenue entries whose absolute value is more than five times the normal median. It then performs a cash-realization cross-check using available bank-clearing style support for the same window.

**Trigger condition**  
A flag is raised when the final-week revenue spike is materially abnormal and cash realization does not support the billing pattern.

---

<a id="test_03"></a>
## **Test_03** — Bill-and-Hold Verification

| Field | Detail |
|---|---|
| Primary Risk | Revenue recorded without transfer of control |
| Books Required | General Ledger, Warehouse Dispatch / Gate Pass Register |
| Output Type | Amber |
| Typical Follow-Up | Dispatch logs, LR copies, custody letters, customer hold instructions |

**What this test checks**  
This test checks whether high-value year-end revenue has evidence of physical dispatch or transfer before cut-off.

**Why it matters**  
An invoice alone does not prove revenue was earned. For physical goods, the key diligence issue is whether control actually transferred before the reporting date.

**Detection logic**  
The engine isolates revenue booked in the final 14 days of the period, applies the materiality threshold, and cross-references those sales against dispatch records dated on or before cut-off. If no warehouse register is provided, the engine treats all material closing-period revenue as unsupported for this procedure.

**Trigger condition**  
A flag is raised when a material closing-period invoice has no corresponding dispatch footprint before the cut-off date.

**Analyst Ask**  
Request dispatch support, customer hold correspondence, and any signed bill-and-hold custody documentation for the flagged sale.

---

<a id="test_04"></a>
## **Test_04** — Run-Rate Smoothing

| Field | Detail |
|---|---|
| Primary Risk | Non-recurring or non-operating revenue inside EBITDA |
| Books Required | General Ledger; mapping improves quality |
| Output Type | Red and Amber |
| Typical Follow-Up | Contracts, customer revenue bridge, recurrence proof, management explanation |

**What this test checks**  
This test evaluates whether reported revenue includes one-off items or abnormal counterparty concentration that should not be treated as recurring run-rate earnings.

**Why it matters**  
QoE analysis is not only about whether revenue is booked, but whether it is operating, recurring, and representative of future earnings.

**Detection logic**  
The engine runs two filters. First, it uses a lexical net for non-operating terms such as interest, dividend, sale of assets, rent, or forex gains. Second, it runs a behavioral concentration test that identifies parties with very few transactions but unusually high median order values versus the broader ledger pattern. Sensitivity changes based on the runtime control selected by the user.

**Trigger condition**  
- Lexical trigger: explicit non-operating income language appears in revenue lines  
- Behavioral trigger: a party has low transaction count but unusually high concentration and average ticket size

---

<a id="test_04_gap"></a>
## **Test_04_Gap** — Execution Gap Screen

| Field | Detail |
|---|---|
| Primary Risk | Billing ahead of physical execution |
| Books Required | General Ledger, Warehouse / Dispatch Register |
| Output Type | Amber |
| Typical Follow-Up | Deferred revenue schedules, milestone terms, dispatch support |

**What this test checks**  
This test checks whether billed revenue for physical products materially exceeds the value of goods actually dispatched.

**Why it matters**  
A billing-versus-dispatch mismatch may indicate early billing, incomplete performance, bundled obligations, or aggressive revenue pull-forward.

**Detection logic**  
The engine excludes obvious service-style categories where mapping is available, aggregates billed value by party, aggregates dispatch value by party, and compares the two. It allows a 20 percent tolerance to absorb freight, taxes, and minor structural differences.

**Trigger condition**  
A flag is raised when billed physical-product revenue exceeds dispatch value by more than 20 percent and the gap is above materiality.

---

<a id="test_05_phantom"></a>
## **Test_05_Phantom** — Phantom Vendor Screen

| Field | Detail |
|---|---|
| Primary Risk | Fictitious or off-book procurement |
| Books Required | General Ledger, AP Aging |
| Output Type | Amber |
| Typical Follow-Up | Vendor master, invoice support, tax IDs, payment proof |

**What this test checks**  
This test checks whether material cost vendors in the ledger have any legitimate footprint in the AP population.

**Why it matters**  
A vendor generating significant cost but absent from recognized payables may indicate phantom suppliers, cash siphoning, or margin suppression.

**Detection logic**  
The engine isolates COGS-type ledger entries, aggregates spend by party, filters for material vendors, and cross-references those names against the official AP aging population.

**Trigger condition**  
A flag is raised when a material vendor appears in GL cost flows but not at all in AP aging.

---

<a id="test_05_cutoff"></a>
## **Test_05_Cutoff** — Cut-Off Squeeze Screen

| Field | Detail |
|---|---|
| Primary Risk | Pre-year-end billing backed by post-year-end dispatch |
| Books Required | General Ledger, Warehouse / Dispatch Register |
| Output Type | Amber |
| Typical Follow-Up | INCOTERMS, customer mails, delivery terms, dispatch timestamps |

**What this test checks**  
This test checks whether sales booked just before cut-off were actually dispatched only after year-end.

**Why it matters**  
Even where a transaction is ultimately valid, the accounting period can still be wrong.

**Detection logic**  
The engine isolates material revenue entries in the final days before cut-off and then checks whether dispatch for the same party appears only after the year-end date.

**Trigger condition**  
A flag is raised when material closing-period revenue is followed by post-cut-off dispatch evidence.

**Analyst Ask**  
Request delivery terms, customer instructions, and proof of when control contractually transferred.

---

<a id="test_06"></a>
## **Test_06** — Round-Tripping Volume

| Field | Detail |
|---|---|
| Primary Risk | Circular trading / artificial gross volume |
| Books Required | General Ledger; mapping strongly recommended |
| Output Type | Amber |
| Typical Follow-Up | Counterparty ledgers, bank proof, contracts, margin rationale |

**What this test checks**  
This test checks whether the same party appears as both customer and vendor and whether the activity is being settled mainly through non-cash loops.

**Why it matters**  
Circular trading can inflate revenue and procurement volume without corresponding economic substance.

**Detection logic**  
The engine separates revenue, cost, and bank-type activity, identifies overlapping counterparties, computes total trading volume with those parties, and compares that volume against actual bank-settled cash movement.

**Trigger condition**  
A flag is raised when overlap volume is material and cash settlement is disproportionately low relative to total trade volume.

**Analyst Ask**  
Request bank-settlement proof and the commercial rationale for two-way trading with the same counterparty.

---

<a id="test_08"></a>
## **Test_08** — Overhead Absorption

| Field | Detail |
|---|---|
| Primary Risk | Improper capitalization / hidden OPEX |
| Books Required | General Ledger |
| Output Type | Red and Amber |
| Typical Follow-Up | Capex policy, FAR additions, internal JV backup, approvals |

**What this test checks**  
This test checks whether operating expenses are being inappropriately capitalized or whether asset lines are being used to suppress period costs.

**Why it matters**  
Improper capitalization can inflate EBITDA by moving real operating expense into the balance sheet.

**Detection logic**  
The engine runs a dual-trap model. One trap searches for abnormal spikes in vague OPEX heads such as repairs, admin, consulting, legal, or maintenance. The second trap scans for month-end internal journal behavior that routes cost into asset-style accounts using capitalization logic.

**Trigger condition**  
A flag is raised when the amount, timing, or journal behavior is inconsistent with ordinary expense recognition.

---

<a id="test_09"></a>
## **Test_09** — Inventory Obsolescence

| Field | Detail |
|---|---|
| Primary Risk | Under-provisioned stale or obsolete stock |
| Books Required | Trial Balance, Inventory Aging |
| Output Type | Amber |
| Typical Follow-Up | SKU aging, sales movement, scrap history, provision policy |

**What this test checks**  
This test checks whether the inventory provision recorded in the books is adequate relative to the physical aging profile of stock.

**Why it matters**  
Inventory is often carried above realizable value when slow-moving or dead stock is not adequately reserved.

**Detection logic**  
The engine identifies inventory-obsolescence style provisions in the trial balance using provision-related keywords. It then groups stock by category, applies category-specific or default aging limits, measures stale inventory value, and calculates the required provision based on the configured coverage ratio.

**Trigger condition**  
A flag is raised when the required provision exceeds the recorded provision by more than materiality.

---

<a id="test_10"></a>
## **Test_10** — Expense Cut-Off Deferral

| Field | Detail |
|---|---|
| Primary Risk | Delayed booking of pre-cut-off expense |
| Books Required | Purchase Register with booking date and invoice date |
| Output Type | Red |
| Typical Follow-Up | Invoice copies, GRN, posting logs, approval trail |

**What this test checks**  
This test checks whether expenses relating to the diligence period were recorded only after year-end.

**Why it matters**  
Delayed expense recognition can overstate current-period EBITDA.

**Detection logic**  
The engine reviews purchase-book entries recorded after cut-off and isolates those where the actual vendor invoice date falls on or before the reporting date. It then applies materiality and treats the delayed booking as a prior-period cost.

**Trigger condition**  
A flag is raised when a material expense is posted after cut-off even though the vendor invoice date proves it belongs to the earlier period.

**Analyst Ask**  
Request the original vendor invoice and the internal posting trail showing why the booking was delayed.

---

<a id="test_11"></a>
## **Test_11** — Extraordinary Expenses

| Field | Detail |
|---|---|
| Primary Risk | One-time cost buried in operating expenses |
| Books Required | General Ledger |
| Output Type | Amber |
| Typical Follow-Up | Contracts, legal papers, approval notes, recurrence history |

**What this test checks**  
This test checks whether unusual expense items may qualify as non-recurring QoE adjustments.

**Why it matters**  
Not every large expense is an add-back, but restructuring, settlement, penalty, and other exceptional items often require normalization review.

**Detection logic**  
The engine combines structural rarity analysis with text-based keyword screening and cadence filtering. It looks for infrequent vendors, unusual ticket sizes, and keyword-matched items that do not recur like normal operating expense.

**Trigger condition**  
A flag is raised when a material OPEX item is either structurally rare or textually extraordinary and does not recur on a normal cadence.

---

<a id="test_12"></a>
## **Test_12** — Comprehensive RPT Sweep

| Field | Detail |
|---|---|
| Primary Risk | Declared or undeclared related-party leakage |
| Books Required | General Ledger, Related Party Directory, Vendor Master, HRMS / people directories |
| Output Type | Amber |
| Typical Follow-Up | RPT register, tax IDs, board approvals, KYC, statutory extracts |

**What this test checks**  
This test checks for both declared and undeclared related-party exposures.

**Why it matters**  
Related-party leakage can distort pricing, margin quality, procurement economics, and the standalone earnings profile of the target.

**Detection logic**  
The engine runs three gates: direct directory matching, concentration sweeps on unknown parties, and identity-collision checks using address and tax-style identifiers across vendors, employees, and insiders.

**Trigger condition**  
A flag is raised when a party is declared, unusually concentrated, or structurally collides with insider identity data.

**Analyst Ask**  
Request vendor KYC, tax identifiers, and any board or statutory disclosures supporting the relationship status.

---

<a id="test_13"></a>
## **Test_13** — Contingent Liabilities

| Field | Detail |
|---|---|
| Primary Risk | Off-balance-sheet obligations and commitments |
| Books Required | Litigation / guarantee / commitment registers, or Notes to Accounts |
| Output Type | Amber |
| Typical Follow-Up | Legal tracker, BG copies, LC register, management rep memo |

**What this test checks**  
This test checks whether contingent liabilities, guarantees, or commitments are underdisclosed or economically ignored.

**Why it matters**  
Some of the most material deal issues do not sit in the ordinary ledger and only appear in schedules or narrative disclosures.

**Detection logic**  
The engine follows a dual-tier model. It first uses structured litigation, guarantee, and commitment books where available. If those books are absent, it falls back to disclosure parsing in the Notes to Accounts.

**Trigger condition**  
A flag is raised when structured registers or disclosure language indicate obligations that are not clearly reflected in the financial picture.

---

<a id="test_14"></a>
## **Test_14** — Bad Debt Provisioning

| Field | Detail |
|---|---|
| Primary Risk | Under-provisioned receivables |
| Books Required | Trial Balance, AR Aging |
| Output Type | Amber |
| Typical Follow-Up | Post-period receipts, dispute tracker, credit notes, provisioning memo |

**What this test checks**  
This test evaluates whether trade receivables are overstated because expected credit loss provisioning is too low.

**Why it matters**  
Weak provisioning can overstate both earnings quality and net working capital.

**Detection logic**  
The engine normalizes column casing, derives overdue days if needed, applies either the configured ECL matrix or default aging logic, and compares the required allowance against the provision visible in the books.

**Trigger condition**  
A flag is raised when the required receivables allowance exceeds the booked provision beyond the materiality threshold.

**Analyst Ask**  
Request post-period collection evidence and management’s basis for the current provisioning matrix.

---

<a id="test_15"></a>
## **Test_15** — Lease Capitalization

| Field | Detail |
|---|---|
| Primary Risk | Unrecorded or understated lease liability |
| Books Required | Lease Register |
| Output Type | Debt-like / quantified adjustment |
| Typical Follow-Up | Lease contracts, escalation clauses, renewal assumptions, liability reconciliation |

**What this test checks**  
This test checks whether lease commitments create unrecorded or understated debt-like obligations.

**Why it matters**  
Operating-style rent can hide financing obligations that matter directly for enterprise value and net debt.

**Detection logic**  
The engine uses structured lease fields such as lease ID, end date, monthly rent, and specific discount rate to calculate the present value of remaining lease commitments.

**Trigger condition**  
A flag is raised when the NPV of active lease commitments reveals material obligations not properly reflected in the books or deal analysis.

---

<a id="test_16"></a>
## **Test_16** — Payroll Integrity

| Field | Detail |
|---|---|
| Primary Risk | Ghost employees, zombie pay, statutory leakage |
| Books Required | Payroll Register, HRMS Master; optional challans and bank support |
| Output Type | Amber or quantified |
| Typical Follow-Up | Employee master, exit file, bank mapping, PF/ESI backup |

**What this test checks**  
This test checks for ghost employees, post-exit salary payments, and payroll or statutory leakage.

**Why it matters**  
Payroll fraud distorts margin quality and can reveal broad control weakness.

**Detection logic**  
The engine uses a dual-plan model. One plan compares payroll flows against HRMS records to detect ghost or zombie pay. The fallback plan uses statutory challans and support logs to detect headcount inconsistencies or bypass behavior.

**Trigger condition**  
A flag is raised when salary is paid after exit, identity logic is suspicious, or statutory evidence suggests incomplete payroll recognition.

---

<a id="test_17"></a>
## **Test_17** — Advance Revenue Classification

| Field | Detail |
|---|---|
| Primary Risk | Advance receipts recognized as earned revenue |
| Books Required | General Ledger, Dispatch Register |
| Output Type | Amber |
| Typical Follow-Up | Contracts, milestone terms, dispatch proof, liability movement |

**What this test checks**  
This test checks whether deposits, mobilization receipts, or advance collections have been recognized as revenue before performance actually occurred.

**Why it matters**  
Advance cash receipt is not the same as earned revenue. If performance is incomplete, the amount may belong in contract liabilities instead.

**Detection logic**  
The engine scans for advance-style revenue language and cross-references those entries against dispatch evidence. It looks for complete absence of dispatch support and dispatch occurring only after the evaluation date.

**Trigger condition**  
A flag is raised when ledger revenue exists without timely operational execution support.

---

<a id="test_18"></a>
## **Test_18** — Asset Impairment & Obsolescence

| Field | Detail |
|---|---|
| Primary Risk | Overstated carrying value of long-lived assets |
| Books Required | FAR; optional NRV / fair value and utilization support |
| Output Type | Amber |
| Typical Follow-Up | NBV schedule, impairment memo, production logs, resale estimates |

**What this test checks**  
This test checks whether long-lived assets are carried above recoverable value or above their real economic usefulness.

**Why it matters**  
Idle, loss-making, or obsolete assets can overstate book value and misrepresent capital intensity.

**Detection logic**  
The engine applies a layered review including context recovery for imperfect asset data, bleeding-CGU logic, NRV-versus-NBV comparisons, and utilization-drop screening.

**Trigger condition**  
A flag is raised when carrying value appears unsupported by economics, fair value, or actual use.

---

<a id="test_19"></a>
## **Test_19** — Intangible Assets Multi-Book

| Field | Detail |
|---|---|
| Primary Risk | Unsupported capitalization of development or software cost |
| Books Required | General Ledger, IT Project Tracker, Vendor Master, Timesheets |
| Output Type | Amber |
| Typical Follow-Up | Project charters, go-live proof, vendor invoices, timesheets, capitalization memo |

**What this test checks**  
This test checks whether capitalized intangible assets are supported by real project activity and valid capitalization criteria.

**Why it matters**  
Development capitalization is a common route for shifting operating cost into the balance sheet.

**Detection logic**  
The engine cross-references GL capitalization behavior against project status, external vendor support, and internal labor evidence to distinguish genuine development effort from unsupported capitalization.

**Trigger condition**  
A flag is raised when capitalized intangible value does not align with project execution evidence.

---

<a id="test_20"></a>
## **Test_20** — Cash Window Dressing

| Field | Detail |
|---|---|
| Primary Risk | Temporary inflation of year-end cash |
| Books Required | General Ledger, Bank Statement, optional BRS |
| Output Type | Amber |
| Typical Follow-Up | Post-cut-off bank statements, treasury support, financing explanation |

**What this test checks**  
This test checks whether year-end cash balances were temporarily inflated by short-lived inflows that reversed soon after cut-off.

**Why it matters**  
Window-dressed cash overstates liquidity and can distort the true net debt position.

**Detection logic**  
The engine validates the post-cut-off review horizon, scans for high-value closing-period inflows, and searches subsequent bank activity for matching reversals using tokenized narration overlap and normalized references.

**Trigger condition**  
A flag is raised when a significant closing inflow is followed by a closely matching reversal suggesting a temporary financing loop.

**Analyst Ask**  
Request 15 to 30 days of post-cut-off bank statements and the treasury explanation for the inflow source.

---

<a id="test_21"></a>
## **Test_21** — Management Fees & ESOPs

| Field | Detail |
|---|---|
| Primary Risk | Value leakage through fees, royalty, or omitted share-based cost |
| Books Required | GL, MSA, IP License Agreements, ESOP Register |
| Output Type | Amber or quantified |
| Typical Follow-Up | Agreements, board approvals, valuation workings, KMP compensation files |

**What this test checks**  
This test checks for excessive management charges, royalty-style tolls, IP-linked leakage, and omitted or accelerated share-based payment expense.

**Why it matters**  
These are common value-extraction mechanisms in promoter-led or related-party-heavy structures.

**Detection logic**  
The engine normalizes fee terms to a comparable period basis, compares those caps against ledger charges, scans IP-linked flows independently of declared RPT lists, maps key employee identities carefully, and checks ESOP fair-value timing inside the audit window.

**Trigger condition**  
A flag is raised when charges exceed contractual logic, royalty economics appear aggressive, or ESOP accounting appears incomplete or accelerated.

**Analyst Ask**  
Request the governing agreements, board approvals, and the valuation support behind any ESOP or royalty charge.

---

<a id="test_22"></a>
## **Test_22** — Foreign Exchange Isolation

| Field | Detail |
|---|---|
| Primary Risk | Non-cash FX noise distorting earnings |
| Books Required | General Ledger |
| Output Type | Typically quantified normalization |
| Typical Follow-Up | Journal drilldown, treasury policy, realized vs unrealized split |

**What this test checks**  
This test checks whether foreign-exchange gains or losses are merely paper remeasurement entries rather than realized cash economics.

**Why it matters**  
QoE normalization often requires separating non-cash FX noise from operating performance.

**Detection logic**  
The engine isolates FX-looking transactions using text and date logic, then performs an alibi check at the journal level. If no cash or bank leg exists in the same transaction, the entry is treated as a non-cash paper adjustment.

**Trigger condition**  
A flag is raised when a material FX line appears to be unrealized and non-cash.

---

<a id="test_23"></a>
## **Test_23** — Behavioral Subledger Evasion

| Field | Detail |
|---|---|
| Primary Risk | Pattern-based expense manipulation hidden in ordinary-looking activity |
| Books Required | General Ledger; supporting subledger detail where available |
| Output Type | Amber |
| Typical Follow-Up | Monthly spend bridge, invoices, payment trail, JV support |

**What this test checks**  
This test checks whether expense manipulation is being hidden through unusual cadence, smoothing behavior, or non-cash settlement patterns.

**Why it matters**  
Some manipulation is behavioral, not theatrical. It is designed to survive basic sampling.

**Detection logic**  
The engine combines dual-horizon variance logic, vendor cadence analysis, and non-cash clearing review to identify synthetic billing behavior and subledger evasion.

**Trigger condition**  
A flag is raised when spend behavior is statistically odd, billing cadence looks manufactured, or settlement patterns suggest ledger engineering.

---

<a id="test_24"></a>
## **Test_24** — Tax & Statutory Integrity

| Field | Detail |
|---|---|
| Primary Risk | Unpaid statutory dues, withholding gaps, tax-evasion patterns |
| Books Required | Statutory Challan Register, GL, tax support |
| Output Type | Amber or quantified obligation |
| Typical Follow-Up | Challans, return filings, GST recon, TDS working papers, notices |

**What this test checks**  
This test checks for unpaid tax obligations, statutory timing failures, ITC reversal risk, TDS gaps, and threshold-smurfing behavior.

**Why it matters**  
Statutory leakages create direct debt-like exposures and often signal weak control discipline.

**Detection logic**  
The engine runs multiple prongs, including challan-gap analysis, timing and penalty review, 180-day ITC reversal logic, TDS non-deduction tests, and aggregate threshold checks to identify fragmented transactions designed to avoid compliance triggers.

**Trigger condition**  
A flag is raised when statutory liabilities appear unpaid, credits appear impaired, withholding is missing, or transaction fragmentation suggests deliberate avoidance.

**Analyst Ask**  
Request challans, return filings, and the section-wise tax working supporting the company’s compliance position.

---

<a id="test_25"></a>
## **Test_25** — Net Debt & Working Capital

| Field | Detail |
|---|---|
| Primary Risk | Hidden debt-like items and engineered peg behavior |
| Books Required | General Ledger; optional lease and treasury support |
| Output Type | Amber and debt-like analysis |
| Typical Follow-Up | AP payment runs, customer discount approvals, weekly receivable movement |

**What this test checks**  
This test checks for hidden debt-like obligations and engineered working-capital behavior near closing.

**Why it matters**  
Net debt and NWC peg distortion can change deal value directly, even if EBITDA itself appears stable.

**Detection logic**  
The engine runs a multi-prong framework that incorporates lease-style debt detection, shadow-debt logic via payment-velocity collapse, and working-capital engineering screens such as receivables acceleration through discounting or aggressive collection behavior.

**Trigger condition**  
A flag is raised when payment behavior, rent economics, or receivables acceleration patterns imply off-balance-sheet financing or artificial period-end support.

**Analyst Ask**  
Request AP payment runs, customer discount approvals, and weekly receivables movement around the cut-off window.
    """, unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR VAULT MANAGER (PURGE UTILITY)
# ==========================================
all_tables_in_db = db.check_vault_contents()
# Filter tables to only show those belonging to the Active Deal Workspace
deal_tables = [t.replace(f"{st.session_state.deal_prefix}_", "") for t in all_tables_in_db if t.startswith(st.session_state.deal_prefix)]

st.sidebar.divider()
with st.sidebar.expander("🗄️ Vault Manager (Data Purge)", expanded=True):
    if deal_tables:
        st.success(f"Deal Active: {len(deal_tables)} files")
        
        # CHANGED: Swapped 'selectbox' for 'radio' to prevent screen clipping 
        # and trigger a natural sidebar scrollbar.
        table_to_drop = st.radio(
            "Select table to remove:", 
            options=deal_tables, 
            key="vault_purge_select"
        )
        
    if st.button("🗑️ Drop Selected Table", type="secondary", use_container_width=True):
        db.drop_from_vault(f"{st.session_state.deal_prefix}_{table_to_drop}")
        
        # --- SAFE RESET FOR VAULT A ---
        # If base data is deleted, we must wipe the results and force a new sweep
        if 'results' in st.session_state:
            del st.session_state['results']
            
        st.rerun()

    else:
        st.warning("Workspace is empty.")

# ==========================================
# 4. PHASE 2: THE EXECUTION DECK
# ==========================================
st.divider()
st.markdown("### ⚙️ Phase 2: The Execution Deck")

if 'GENERAL_LEDGER' in deal_tables:
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🟢 General Ledger detected for {deal_name}.")
    with col2:
        st.info(f"📊 Additional Books Detected: {len(deal_tables) - 1}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 EXECUTE FORENSIC SWEEP", type="primary", use_container_width=True):
        with st.spinner(f"Executing Vectorized Forensic Analytics Suite for {deal_name}..."):
            from fdd_core import ForensicAnalyticsSuite
            
            # Load Deal-Specific Mapping
            if 'MAPPING_SCHEDULE' in deal_tables:
                map_df = db.get_from_vault(f"{st.session_state.deal_prefix}_MAPPING_SCHEDULE")
                st.session_state.env.ingest_mapping_schedule(map_df)
            else:
                st.session_state.env.grouping_map = {}
            
            # Ingest all Deal-Specific Books during execution
            for table in deal_tables:
                if table == 'MAPPING_SCHEDULE':
                    continue 
                
                df = db.get_from_vault(f"{st.session_state.deal_prefix}_{table}")
                if table == 'GENERAL_LEDGER':
                    st.session_state.env.ingest_general_ledger(df)
                    st.session_state.env.apply_mapping_to_gl()
                elif table == 'TRIAL_BALANCE':
                    st.session_state.env.ingest_subledger_or_aging(table, df)
                elif table in ['AR_AGING', 'AP_AGING']:
                    st.session_state.env.ingest_subledger_or_aging(table, df)
                elif table in ["HRMS_MASTER", "RELATED_PARTY_DIRECTORY"]:
                    st.session_state.env.ingest_directory(table, df)
                elif table in st.session_state.env.OPERATIONAL_SCHEMA_REGISTRY:
                    dummy_map = {col: col for col in df.columns}
                    st.session_state.env.ingest_operational_register(table, df, dummy_map)
                    
            suite = ForensicAnalyticsSuite(st.session_state.env)
            
            # Use dynamic EBITDA input from Tab 3
            ebitda_anchor = st.session_state.get('temp_ebitda', 5000000.0)
            st.session_state.env.initialize_qoe_bridge(reported_ebitda=ebitda_anchor)
            
            # --- SILENT STATE INJECTION ---
            st.session_state.env.runtime_thresholds['ap_itc_cliff_days'] = 180
            st.session_state.env.runtime_thresholds['rpt_concentration_limit'] = 0.05
            st.session_state.env.runtime_thresholds['round_tripping_window_days'] = 30
            st.session_state.env.runtime_thresholds['overhead_absorption_variance'] = 0.05
            st.session_state.env.runtime_thresholds['fx_variance_tolerance'] = 0.03
            st.session_state.env.runtime_thresholds['shadow_debt_z_score'] = -2.0
            
            cutoff_str = str(selected_cutoff)
            ecl_matrix = st.session_state.env.runtime_thresholds.get('ecl_matrix', None)
            test_coverage_log = []

            def safe_run(test_id, test_name, func):
                try:
                    func()
                except Exception as ex:
                    # Only catch actual fatal Python crashes, not scope limitations
                    st.sidebar.error(f"Fatal Engine Error [{test_id}]: {str(ex)}")


            # Execute All 25 Protocols
            safe_run("Test_01", "Revenue Integrity Screen", lambda: suite.execute_test_01_revenue_integrity_screen())
            safe_run("Test_03", "Bill-and-Hold Verification", lambda: suite.execute_test_03_bill_and_hold_verification())
            safe_run("Test_04", "Run-Rate Smoothing", lambda: suite.execute_test_04_run_rate_smoothing())
            safe_run("Test_04_Gap", "Execution Gap Screen", lambda: suite.execute_test_04_execution_gap())
            safe_run("Test_05_Phantom", "Phantom Vendor Screen", lambda: suite.execute_test_05_phantom_vendor_screen())
            safe_run("Test_05_Cutoff", "Cut-Off Squeeze Screen", lambda: suite.execute_test_05_cutoff_squeeze(fiscal_cutoff_date=cutoff_str))
            safe_run("Test_06", "Round-Tripping Volume", lambda: suite.execute_test_06_round_tripping())
            safe_run("Test_08", "Overhead Absorption", lambda: suite.execute_test_08_overhead_absorption())
            safe_run("Test_09", "Inventory Obsolescence v2", lambda: suite.execute_test_09_inventory_obsolescence_v2())
            safe_run("Test_10", "Expense Cutoff Deferral", lambda: suite.execute_test_10_expense_cutoff_deferral(fiscal_cutoff_date=cutoff_str))
            safe_run("Test_11", "Extraordinary Expenses", lambda: suite.execute_test_11_extraordinary_expenses())
            safe_run("Test_12", "Comprehensive RPT Sweep", lambda: suite.execute_test_12_comprehensive_rpt_sweep())
            safe_run("Test_13", "Contingent Liabilities", lambda: suite.execute_test_13_contingent_liabilities())
            safe_run("Test_14", "Bad Debt Provisioning v2", lambda: suite.execute_test_14_bad_debt_provisioning_v2(aging_loss_matrix=ecl_matrix, evaluation_date=cutoff_str))
            safe_run("Test_15", "Lease Capitalization", lambda: suite.execute_test_15_lease_capitalization(fiscal_cutoff_date=cutoff_str))
            safe_run("Test_16", "Payroll Integrity", lambda: suite.execute_test_16_payroll_integrity())
            safe_run("Test_17", "Advance Revenue Classification", lambda: suite.execute_test_17_advance_revenue_misclassification(evaluation_date=cutoff_str))
            safe_run("Test_18", "Asset Impairment & Obsolescence", lambda: suite.execute_test_18_asset_impairment_and_obsolescence(evaluation_date=cutoff_str))
            safe_run("Test_19", "Intangible Assets Multi-Book", lambda: suite.execute_test_19_intangible_assets_multi_book())
            safe_run("Test_20", "Cash Window Dressing", lambda: suite.execute_test_20_cash_window_dressing(fiscal_cutoff_date=cutoff_str))
            safe_run("Test_21", "Management Fees & ESOPs", lambda: suite.execute_test_21_management_fees_and_share_based_payments(fiscal_cutoff_date=cutoff_str))
            safe_run("Test_22", "Foreign Exchange Isolation", lambda: suite.execute_test_22_foreign_exchange_isolation(fiscal_cutoff_date=cutoff_str))
            safe_run("Test_23", "Behavioral Subledger Evasion", lambda: suite.execute_test_23_behavioral_subledger_evasion(fiscal_cutoff_date=cutoff_str))
            safe_run("Test_24", "Tax & Statutory Integrity", lambda: suite.execute_test_24_tax_and_statutory_integrity(fiscal_cutoff_date=cutoff_str))
            safe_run("Test_25", "Net Debt & Working Capital", lambda: suite.execute_test_25_net_debt_and_working_capital(fiscal_cutoff_date=cutoff_str, dpo_z_score_threshold=-2.0))

            # --- DEEP TRACE WIPEOUT COMPLETE. NEW PIPELINE INJECTED. ---
            # Retrieve Analyst Ledger from Vault B before final math execution
            st.session_state.active_analyst_ledger = db.get_analyst_ledger(st.session_state.deal_prefix)
            
            # Pass Vault B data directly into the math engine
            st.session_state.results = st.session_state.env.get_qoe_summary(analyst_ledger_df=st.session_state.active_analyst_ledger)
            st.session_state.test_coverage_log = pd.DataFrame(test_coverage_log)
            
            st.success("✅ Complete 25-Protocol Forensic Sweep & Pro-Forma Overrides Executed!")

# ==========================================
# RESULTS RENDERING & ANALYST WORKBENCH
# ==========================================
if 'results' in st.session_state:
    st.divider()
    math = st.session_state.results['Valuation_Math']
        
    st.markdown(f"## 📊 {deal_name} - Quality of Earnings (QoE) Summary")
        
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Reported EBITDA", f"₹{math['Reported_EBITDA']:,.0f}")
    m2.metric("Verified Adjustments (Red/Green)", f"₹{math['Total_Verified_Adjustments']:,.0f}")
    m3.metric("Pending Risk (Amber)", f"₹{math['Total_Pending_Exposure']:,.0f}")
        
    adjusted = math['Current_Adjusted_EBITDA'] - math['Total_Pending_Exposure']
    m4.metric("Risk-Adjusted EBITDA", f"₹{adjusted:,.0f}", delta=f"₹{adjusted - math['Reported_EBITDA']:,.0f}")
        
    st.plotly_chart(render_waterfall_chart(st.session_state.results), use_container_width=True)

    # Partner-Ready Export
    excel_file = generate_excel_report(
        st.session_state.results, 
        deal_name, 
        st.session_state.get('active_analyst_ledger')
    )
    
    st.download_button(
        label="📥 Download Partner-Ready QoE Report (.xlsx)",
        data=excel_file,
        file_name=f"{st.session_state.deal_prefix}_QoE_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

    st.markdown("### 🗂️ FDD Engine Discoveries")
    
    # --- THE 3-TAB INTERFACE ---
    tab_red, tab_amber, tab_green = st.tabs([
        "🔴 Red Flags (Definitive)", 
        "⚠️ Amber Flags (Pending)", 
        "🟢 Green Flags (Waived/Positive)"
    ])
    
    with tab_red:
        if not st.session_state.results['Definitive_Bridge'].empty:
            st.dataframe(st.session_state.results['Definitive_Bridge'], use_container_width=True)
        else:
            st.success("✅ No definitive red flags detected.")
            
    with tab_amber:
        if not st.session_state.results['Suspense_Bucket'].empty:
            st.dataframe(st.session_state.results['Suspense_Bucket'], use_container_width=True)
        else:
            st.success("✅ No pending amber risks detected.")
            
    with tab_green:
        st.info("💡 **Note for Analysts:** The Green Tab is exclusively for Human Intervention. It only populates when a deal team member explicitly waives an automated risk or manually logs a positive EBITDA add-back via the Analyst Workbench below.")
        
        green_df = st.session_state.results.get('Green_Bucket', pd.DataFrame())
        if not green_df.empty:
            # Force copy and type alignment to prevent Streamlit silent rendering crashes
            display_green = green_df.copy().astype(str)
            st.dataframe(display_green, use_container_width=True)
        else:
            st.success("✅ No waived or positive adjustments logged.")

    # ==========================================
    # PHASE 3: THE ANALYST WORKBENCH
    # ==========================================
    st.markdown("### 🧑‍💼 Analyst Workbench & Deal Room Pro-Formas")
    st.info("Execute manual overrides or log new discoveries. All entries strictly require justification and evidentiary proof.")
    
    # Fetch active IDs for the dropdown
    available_refs = []
    if not st.session_state.results['Definitive_Bridge'].empty:
        available_refs += st.session_state.results['Definitive_Bridge']['Test_Ref'].tolist()
    if not st.session_state.results['Suspense_Bucket'].empty:
        available_refs += st.session_state.results['Suspense_Bucket']['Test_Ref'].tolist()
    available_refs = list(set(available_refs))

    # Command Center Forms
    col_mod, col_new = st.columns(2)
    
    with col_mod:
        st.markdown("#### 🔧 Modify Engine Flag")
        mod_ref = st.selectbox("Select Target Flag", options=["-- Select --"] + available_refs)
        mod_status = st.selectbox("Override Polarity", ["Waive Risk (Green)", "Definitive (Red)", "Pending/Unquantified (Amber)"], key='mod_pol')
        mod_amt = st.number_input("Revised Impact (₹) [Use negatives for deductions]", step=50000.0, key='mod_amt')
        mod_just = st.text_input("Partner Rationale (Mandatory)", key='mod_just')
        
        # --- ENFORCED FILE TYPE RESTRICTIONS ---
        mod_file = st.file_uploader(
            "Upload Evidence (Mandatory)", 
            type=['pdf', 'xlsx'], 
            help="The system strictly accepts .pdf and .xlsx files for evidentiary support.", 
            key='mod_file'
        )
        
        if st.button("Commit Modification", type="primary", use_container_width=True):
            if mod_ref == "-- Select --":
                st.error("Select a target flag.")
            elif not mod_just.strip():
                st.error("Compliance Block: Rationale is mandatory.")
            elif not mod_file:
                st.error("Compliance Block: Evidence upload is mandatory.")
            else:
                saved_file = db.save_evidence_file(st.session_state.deal_prefix, mod_file)
                adj_dict = {
                    'REF_ID': mod_ref,
                    'STATUS': mod_status,
                    'ANALYST_AMOUNT': mod_amt,
                    'RATIONALE': mod_just,
                    'EVIDENCE_FILE': saved_file,
                    'CATEGORY': "Analyst Modification",
                    'PARTY_NAME': "Adjusted Profile"
                }
                db.save_analyst_adjustment(st.session_state.deal_prefix, adj_dict)
                
                st.session_state.active_analyst_ledger = db.get_analyst_ledger(st.session_state.deal_prefix)
                st.session_state.results = st.session_state.env.get_qoe_summary(analyst_ledger_df=st.session_state.active_analyst_ledger)
                
                st.success("Modification committed and math updated instantly!")
                st.rerun()

    with col_new:
        st.markdown("#### ➕ Manual Discovery")
        new_name = st.text_input("Discovery Title / Risk Name", key='new_name')
        new_status = st.selectbox("Risk Polarity", ["Definitive (Red)", "Pending/Unquantified (Amber)"], key='new_pol')
        new_amt = st.number_input("Financial Impact (₹) [Use negatives for deductions]", step=50000.0, key='new_amt')
        new_just = st.text_input("Partner Rationale (Mandatory)", key='new_just')
        
        # --- ENFORCED FILE TYPE RESTRICTIONS ---
        new_file = st.file_uploader(
            "Upload Evidence (Mandatory)", 
            type=['pdf', 'xlsx'], 
            help="The system strictly accepts .pdf and .xlsx files for evidentiary support.", 
            key='new_file'
        )
        
        if st.button("Commit Discovery", type="primary", use_container_width=True):
            if not new_name.strip():
                st.error("Provide a discovery title.")
            elif not new_just.strip():
                st.error("Compliance Block: Rationale is mandatory.")
            elif not new_file:
                st.error("Compliance Block: Evidence upload is mandatory.")
            else:
                saved_file = db.save_evidence_file(st.session_state.deal_prefix, new_file)
                adj_dict = {
                    'REF_ID': f"MANUAL_{new_name.replace(' ', '_').upper()}",
                    'STATUS': new_status,
                    'ANALYST_AMOUNT': new_amt,
                    'RATIONALE': new_just,
                    'EVIDENCE_FILE': saved_file,
                    'CATEGORY': "Net-New Manual Discovery",
                    'PARTY_NAME': "Analyst Identified"
                }
                db.save_analyst_adjustment(st.session_state.deal_prefix, adj_dict)
                
                st.session_state.active_analyst_ledger = db.get_analyst_ledger(st.session_state.deal_prefix)
                st.session_state.results = st.session_state.env.get_qoe_summary(analyst_ledger_df=st.session_state.active_analyst_ledger)
                
                st.success("Discovery committed and math updated instantly!")
                st.rerun()
                
    # ==========================================
    # VAULT B: DUAL-LEDGER & REVERT UTILITY
    # ==========================================
    st.markdown("#### 🗄️ Vault B: Analyst Ledger (Immutable Audit Trail)")
    analyst_ledger = st.session_state.get('active_analyst_ledger', pd.DataFrame())
    
    if not analyst_ledger.empty:
        st.dataframe(analyst_ledger, use_container_width=True)
        
        st.markdown("##### 🛠️ Ledger Utilities & Evidence Review")
        rev_col1, rev_col2 = st.columns(2)
        
        with rev_col1:
            target_revert = st.radio("Select entry to Manage:", options=analyst_ledger['REF_ID'].tolist(), key='revert_radio')
            
            if st.button("🗑️ Revert to Baseline (Delete Entry)", type="secondary"):
                db.remove_analyst_adjustment(st.session_state.deal_prefix, target_revert)
                
                # --- INSTANT SYNC FIX ---
                st.session_state.active_analyst_ledger = db.get_analyst_ledger(st.session_state.deal_prefix)
                st.session_state.results = st.session_state.env.get_qoe_summary(analyst_ledger_df=st.session_state.active_analyst_ledger)
                
                st.success(f"Removed {target_revert}. Math snapped back to baseline.")
                st.rerun()
                
        with rev_col2:
            import os
            target_file = analyst_ledger[analyst_ledger['REF_ID'] == target_revert]['EVIDENCE_FILE'].iloc[0]
            
            if target_file and target_file != "No File Attached":
                # FIX: database.py saves files with the deal_prefix appended to the front. We must reconstruct that physical filename.
                actual_filename = f"{st.session_state.deal_prefix}_{target_file}"
                file_path = os.path.join(db.EVIDENCE_DIR, actual_filename)
                
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"📥 Download Attached Evidence",
                            data=f,
                            file_name=target_file, # Let the user download it without the internal prefix
                            mime="application/octet-stream",
                            type="primary"
                        )
                    st.caption(f"Filename: `{target_file}`")
                else:
                    st.warning("⚠️ Evidence file could not be located on the local disk.")
            else:
                st.info("No physical evidence file is attached to this entry.")