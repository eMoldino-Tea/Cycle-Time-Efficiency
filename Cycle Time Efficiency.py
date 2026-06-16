import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Cycle Time Efficiency",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ==========================================
# 2. ENTERPRISE DARK MODE CSS
# ==========================================
st.markdown("""
<style>
/* Base Dark Theme Overrides */
.stApp {
    background-color: #0f1117;
    color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Hide Streamlit Defaults Safely */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background-color: transparent !important;}

.block-container {padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1600px;}

/* Title Header */
.dash-header {
    font-size: 1.85rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1.5rem;
    letter-spacing: 0.5px;
}

/* Dashboard Card HTML Styles */
.dash-card {
    background-color: #1a1d26;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #2d3748;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.dash-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
    border-color: #4a5568;
}

/* Streamlit Native Container Overrides */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #1a1d26 !important;
    border-radius: 12px !important;
    padding: 20px 24px !important;
    border: 1px solid #2d3748 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1) !important;
    margin-bottom: 24px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2) !important;
    border-color: #4a5568 !important;
}

/* KPI Card Typography */
.kpi-title-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.kpi-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #cbd5e1;
    letter-spacing: 0.3px;
}

/* Metric Rows */
.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-size: 1.05rem;
}
.metric-row:last-child {
    margin-bottom: 0;
}
.metric-label {
    color: #94a3b8;
    font-weight: 500;
}
.metric-value {
    font-weight: 700;
    text-align: right;
}

/* Color Tokens */
.text-green { color: #5cb85c !important; }
.text-yellow { color: #eab308 !important; }
.text-red { color: #d9534f !important; }
.text-neutral { color: #f8fafc !important; }

/* Panel Specific Styles */
.panel-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 24px;
    letter-spacing: 0.3px;
}
.col-header {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.3px;
    padding-bottom: 8px;
    margin-bottom: 16px;
    border-bottom: 1px solid #334155;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #ffffff;
    margin-top: 1rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #2d3748;
}

/* Tab Overrides */
[data-testid="stTabs"] button {
    font-size: 1.1rem;
    font-weight: 600;
}

/* Ensure buttons align perfectly regardless of text wrap */
[data-testid="stButton"] button {
    min-height: 3.5rem;
}

/* Print formatting: Hide sidebar and specific UI elements during PDF export */
@media print {
    [data-testid="stSidebar"], header, footer, button, .stToolbar {
        display: none !important;
    }
    .stApp, section.main, .main {
        background-color: transparent !important;
        overflow: visible !important;
        height: auto !important;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        overflow: visible !important;
    }
    /* Force all tabs to display in print */
    [data-baseweb="tab-panel"], div[role="tabpanel"] {
        display: block !important;
        visibility: visible !important;
        position: static !important;
        height: auto !important;
        overflow: visible !important;
        opacity: 1 !important;
    }
    /* Hide tab buttons */
    [data-baseweb="tab-list"], div[role="tablist"] {
        display: none !important;
    }
    /* Prevent squishing and cutting across page breaks */
    .element-container, .stVerticalBlock, .dash-card, [data-testid="stVerticalBlockBorderWrapper"], div.stPlotlyChart, div[data-testid="stDataFrame"] {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    /* Force tables to expand to full height for printing */
    div[data-testid="stDataFrame"] > div, div[data-testid="stDataFrame"] iframe {
        max-height: none !important;
        height: auto !important;
        overflow: visible !important;
    }
    h1, h2, h3, .panel-title, .section-title, .dash-header {
        page-break-after: avoid !important;
        break-after: avoid !important;
    }
    @page {
        size: landscape;
        margin: 15mm;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. MATHEMATICALLY STRICT DATA LOADING
# ==========================================
@st.cache_data
def load_base_data():
    np.random.seed(42)
    
    T_GAIN_HRS = 15.2 
    T_LOSS_HRS = 3.0833333333333335 
    T_GAIN_SHOTS = 12553725
    T_LOSS_SHOTS = 5342431
    T_FIN_GAIN = 1688
    T_FIN_LOSS = 1712
    
    T_USED_FAST_MINS = 7337 
    T_USED_SLOW_MINS = 1457 
    
    N_FAST = 300
    N_SLOW = 150
    N_WITHIN = 600
    
    suppliers_f = np.tile(['Foxconn', 'Jabil', 'Flex'], 100)
    tooling_f = np.repeat(['Injection Molding', 'High Pressure Die Casting', 'Progressive Stamping'], 100)
    np.random.shuffle(tooling_f)
    products_f = np.tile(['Product X248', 'Product X277', 'Product X418'], 100)
    np.random.shuffle(products_f)
    parts_f = np.tile(['Part-001', 'Part-002', 'Part-003'], 100)
    np.random.shuffle(parts_f)
    
    suppliers_s = np.tile(['Sanmina', 'Pegatron', 'Celestica'], 50)
    tooling_s = np.repeat(['Thermoforming', 'Blow Molding', 'Vacuum Forming'], 50)
    np.random.shuffle(tooling_s)
    products_s = np.tile(['Product X620D', 'Product V15', 'Product V12'], 50)
    np.random.shuffle(products_s)
    parts_s = np.tile(['Part-004', 'Part-005', 'Part-006'], 50)
    np.random.shuffle(parts_s)
    
    b_sup_f = {'Foxconn': 1.6, 'Jabil': 0.9, 'Flex': 0.5}
    b_tool_f = {'Injection Molding': 1.4, 'High Pressure Die Casting': 1.0, 'Progressive Stamping': 0.6}
    b_prod_f = {'Product X248': 1.25, 'Product X277': 1.05, 'Product X418': 0.7}
    w_gain_f = np.array([b_sup_f[s] * b_tool_f[t] * b_prod_f[p] for s, t, p in zip(suppliers_f, tooling_f, products_f)])
    w_gain_f /= w_gain_f.sum() 
    w_used_f = np.random.uniform(0.9, 1.1, N_FAST)
    w_used_f /= w_used_f.sum() 
    
    b_sup_s = {'Sanmina': 1.6, 'Pegatron': 0.9, 'Celestica': 0.5}
    b_tool_s = {'Thermoforming': 1.4, 'Blow Molding': 1.0, 'Vacuum Forming': 0.6}
    b_prod_s = {'Product X620D': 1.25, 'Product V15': 1.05, 'Product V12': 0.7}
    w_loss_s = np.array([b_sup_s[s] * b_tool_s[t] * b_prod_s[p] for s, t, p in zip(suppliers_s, tooling_s, products_s)])
    w_loss_s /= w_loss_s.sum() 
    w_used_s = np.random.uniform(0.9, 1.1, N_SLOW)
    w_used_s /= w_used_s.sum() 

    parts_w = np.random.choice([f"Part-{i:03d}" for i in range(7, 25)], N_WITHIN)

    def exact_distribute(target_int, weights):
        floored = np.floor(weights * target_int).astype(int)
        remainder = int(target_int - floored.sum())
        if remainder > 0:
            fractions = (weights * target_int) - floored
            indices = np.argsort(fractions)[::-1]
            for i in range(remainder):
                floored[indices[i]] += 1
        return floored

    gain_mins = exact_distribute(912, w_gain_f) 
    used_mins_f = exact_distribute(T_USED_FAST_MINS, w_used_f) 
    df_fast = pd.DataFrame({
        'Tolerance_Status': ['Fast'] * N_FAST,
        'Gain_Hours': gain_mins / 60.0,
        'Loss_Hours': 0.0,
        'Shots_Gained': exact_distribute(T_GAIN_SHOTS, w_gain_f),
        'Shots_Lost': 0.0,
        'Used_Hours': used_mins_f / 60.0,
        'Base_Fin_Gain': exact_distribute(T_FIN_GAIN, w_gain_f).astype(float),
        'Base_Fin_Loss': 0.0,
        'Supplier': suppliers_f,
        'Tooling Type': tooling_f,
        'Product': products_f,
        'Part': parts_f
    })
    df_fast['Expected_Hours'] = df_fast['Used_Hours'] + df_fast['Gain_Hours']

    loss_mins = exact_distribute(185, w_loss_s) 
    used_mins_s = exact_distribute(T_USED_SLOW_MINS, w_used_s)
    df_slow = pd.DataFrame({
        'Tolerance_Status': ['Slow'] * N_SLOW,
        'Gain_Hours': 0.0,
        'Loss_Hours': loss_mins / 60.0,
        'Shots_Gained': 0.0,
        'Shots_Lost': exact_distribute(T_LOSS_SHOTS, w_loss_s),
        'Used_Hours': used_mins_s / 60.0,
        'Base_Fin_Gain': 0.0,
        'Base_Fin_Loss': exact_distribute(T_FIN_LOSS, w_loss_s).astype(float),
        'Supplier': suppliers_s,
        'Tooling Type': tooling_s,
        'Product': products_s,
        'Part': parts_s
    })
    df_slow['Expected_Hours'] = df_slow['Used_Hours'] - df_slow['Loss_Hours']
    
    df_within = pd.DataFrame({
        'Tolerance_Status': ['Within'] * N_WITHIN,
        'Gain_Hours': 0.0,
        'Loss_Hours': 0.0,
        'Shots_Gained': 0.0,
        'Shots_Lost': 0.0,
        'Expected_Hours': np.random.uniform(5.0, 20.0, N_WITHIN),
        'Base_Fin_Gain': 0.0,
        'Base_Fin_Loss': 0.0,
        'Supplier': np.random.choice(['Supplier Alpha', 'Neutral Corp'], N_WITHIN),
        'Tooling Type': np.random.choice(['Compression Molding', 'Rubber Molding', 'Silicone Molding'], N_WITHIN),
        'Product': np.random.choice(['Product Y99', 'Product Z11'], N_WITHIN),
        'Part': parts_w
    })
    df_within['Used_Hours'] = df_within['Expected_Hours']
    
    data = pd.concat([df_fast, df_slow, df_within], ignore_index=True)
    
    data['Total_Shots'] = data['Shots_Gained'] + data['Shots_Lost']
    data.loc[data['Tolerance_Status'] == 'Within', 'Total_Shots'] = np.random.randint(5000, 50000, N_WITHIN)
    data['ACT'] = (data['Expected_Hours'] * 3600) / data['Total_Shots']
    data['Actual_CT'] = (data['Used_Hours'] * 3600) / data['Total_Shots']
    data['Efficiency_%'] = np.where(data['Used_Hours'] > 0, (data['Expected_Hours'] / data['Used_Hours']) * 100, 0)
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=89)
    date_offsets = np.random.randint(0, 90, len(data))
    data['Date'] = [start_date + timedelta(days=int(x)) for x in date_offsets]
    
    data['OEM Business Division'] = np.random.choice(['NA Auto', 'EU Consumer', 'APAC Enterprise', 'LATAM Industrial'], len(data))
    data['Toolmaker'] = np.random.choice(['TM-A', 'TM-B', 'TM-C', 'TM-D'], len(data))
    data['Plant'] = np.random.choice(['Plant 1 (MX)', 'Plant 2 (DE)', 'Plant 3 (CN)', 'Plant 4 (VN)'], len(data))
    
    part_names_pool = [
        'Unused', 'Housing Top', 'Housing Bottom', 'Display Lens', 'Battery Bracket',
        'Main Chassis', 'Camera Frame', 'Speaker Grill', 'Mic Mesh', 'Antenna Band',
        'Haptic Motor', 'USB Port', 'Power Key', 'Volume Key', 'SIM Slot',
        'Bezel', 'Rear Glass', 'Cooling Pad', 'EMI Shield', 'Biometric Scanner',
        'IR Sensor', 'Flash Module', 'Charging Coil', 'NFC Tag', 'Vapor Chamber'
    ]
    data['Part Name'] = data['Part'].apply(lambda x: part_names_pool[int(x.split('-')[1])])
    data['Tooling'] = [f"TL-{np.random.randint(1, 40):03d}" for _ in range(len(data))]
    
    return data

df = load_base_data()

# ==========================================
# 4. SIDEBAR FILTERS & FINANCIALS
# ==========================================
st.sidebar.markdown("### Time Range Filter")
time_range = st.sidebar.radio("Select Time Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"], index=2)

min_date = df['Date'].min()
max_date = df['Date'].max()

if time_range == "Last 7 Days":
    start_date = max_date - timedelta(days=7)
    end_date = max_date
elif time_range == "Last 30 Days":
    start_date = max_date - timedelta(days=30)
    end_date = max_date
elif time_range == "Last 90 Days":
    start_date = min_date - timedelta(days=1) 
    end_date = max_date + timedelta(days=1)
else:
    c1, c2 = st.sidebar.columns(2)
    with c1:
        start_date_input = st.date_input("Start Date", min_date.date(), max_value=max_date.date())
    with c2:
        end_date_input = st.date_input("End Date", max_date.date(), max_value=max_date.date())
    start_date = pd.to_datetime(start_date_input)
    end_date = pd.to_datetime(end_date_input) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### Financial Parameters")
labor_rate = st.sidebar.number_input("Labor Rate ($/hour)", min_value=0.0, value=40.0, step=1.0)
machine_rate = st.sidebar.number_input("Machine Rate ($/hour)", min_value=0.0, value=180.0, step=1.0)
combined_rate = labor_rate + machine_rate

rate_scalar = combined_rate / 220.0
filtered_df['Active_Rate'] = combined_rate
filtered_df['Financial_Gain'] = filtered_df['Base_Fin_Gain'] * rate_scalar
filtered_df['Financial_Loss'] = filtered_df['Base_Fin_Loss'] * rate_scalar

st.sidebar.markdown("---")
st.sidebar.markdown("### Master Filter")
selected_oem = st.sidebar.multiselect("OEM Business Division", options=filtered_df['OEM Business Division'].unique())
filtered_df = filtered_df[filtered_df['OEM Business Division'].isin(selected_oem)] if selected_oem else filtered_df

selected_supplier = st.sidebar.multiselect("Supplier", options=filtered_df['Supplier'].unique())
filtered_df = filtered_df[filtered_df['Supplier'].isin(selected_supplier)] if selected_supplier else filtered_df

selected_toolmaker = st.sidebar.multiselect("Toolmaker", options=filtered_df['Toolmaker'].unique())
filtered_df = filtered_df[filtered_df['Toolmaker'].isin(selected_toolmaker)] if selected_toolmaker else filtered_df

selected_plant = st.sidebar.multiselect("Plant", options=filtered_df['Plant'].unique())
filtered_df = filtered_df[filtered_df['Plant'].isin(selected_plant)] if selected_plant else filtered_df

selected_tooling_type = st.sidebar.multiselect("Tooling Type", options=filtered_df['Tooling Type'].unique())
filtered_df = filtered_df[filtered_df['Tooling Type'].isin(selected_tooling_type)] if selected_tooling_type else filtered_df

selected_product = st.sidebar.multiselect("Product", options=filtered_df['Product'].unique())
filtered_df = filtered_df[filtered_df['Product'].isin(selected_product)] if selected_product else filtered_df

selected_part = st.sidebar.multiselect("Part", options=filtered_df['Part'].unique())
filtered_df = filtered_df[filtered_df['Part'].isin(selected_part)] if selected_part else filtered_df

selected_tooling = st.sidebar.multiselect("Tooling", options=filtered_df['Tooling'].unique())
filtered_df = filtered_df[filtered_df['Tooling'].isin(selected_tooling)] if selected_tooling else filtered_df

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


# ==========================================
# 5. GLOBAL CALCULATIONS & HELPERS
# ==========================================
gained_hrs = filtered_df['Gain_Hours'].sum()
lost_hrs = filtered_df['Loss_Hours'].sum()
gained_shots = filtered_df['Shots_Gained'].sum()
lost_shots = filtered_df['Shots_Lost'].sum()
gained_fin = filtered_df['Financial_Gain'].sum()
lost_fin = filtered_df['Financial_Loss'].sum()

net_hrs = gained_hrs - lost_hrs
net_shots = gained_shots - lost_shots
net_fin = gained_fin - lost_fin

def calc_weighted_eff(df_subset):
    used = df_subset['Used_Hours'].sum()
    expected = df_subset['Expected_Hours'].sum()
    if used == 0: return np.nan
    return (expected / used) * 100

eff_fast = calc_weighted_eff(filtered_df[filtered_df['Tolerance_Status'] == 'Fast'])
eff_slow = calc_weighted_eff(filtered_df[filtered_df['Tolerance_Status'] == 'Slow'])
eff_within = calc_weighted_eff(filtered_df[filtered_df['Tolerance_Status'] == 'Within'])

def format_hm(hours_float):
    if pd.isna(hours_float) or hours_float == 0: return "0H 0M"
    sign = "-" if hours_float < 0 else ""
    h_float = abs(hours_float)
    total_mins = int(round(h_float * 60))
    h = total_mins // 60
    m = total_mins % 60
    return f"{sign}{h}H {m}M"

disp_gained_hrs = format_hm(gained_hrs)
disp_lost_hrs = format_hm(lost_hrs)
disp_net_hrs = format_hm(net_hrs)

disp_gained_shots = f"{int(round(gained_shots)):,}"
disp_lost_shots = f"{int(round(lost_shots)):,}"
disp_net_shots = f"{int(round(net_shots)):,}"

disp_gained_fin = f"${gained_fin:,.0f}"
disp_lost_fin = f"-${abs(lost_fin):,.0f}"

disp_eff_fast = f"+{eff_fast:.2f}%" if pd.notna(eff_fast) else "N/A"
disp_eff_slow = f"-{abs(100 - eff_slow):.2f}%" if pd.notna(eff_slow) else "N/A" 

def build_html(*lines):
    return "".join(line.strip() for line in lines)

def export_pdf_ui():
    components.html(
        """
        <div style="text-align: right; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <button onclick="window.parent.print()" style="background-color: #1e293b; color: #f8fafc; border: 1px solid #475569; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600;">
                Export to PDF
            </button>
        </div>
        """,
        height=50
    )

def compute_comprehensive_row(name, group, group_col):
    tot_shots = group['Total_Shots'].sum()