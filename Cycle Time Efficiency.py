import streamlit as st
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

/* Hide Streamlit Defaults */
header {visibility: hidden;}
.css-18ni7ap {visibility: hidden;}
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

/* Streamlit Native Container Overrides (for Plotly panels) */
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

/* Section Title For Drill-down */
.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #ffffff;
    margin-top: 3rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #2d3748;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. MATHEMATICALLY STRICT DATA LOADING
# ==========================================
@st.cache_data
def load_base_data():
    np.random.seed(42)
    
    # 1. HARDCODED TARGETS FROM SPEC/SCREENSHOT
    T_GAIN_HRS = 15.2
    T_LOSS_HRS = 3.0833333333333335
    T_GAIN_SHOTS = 12553725
    T_LOSS_SHOTS = 5342431
    T_FIN_GAIN = 1688
    T_FIN_LOSS = 1712
    
    # 2. DERIVE REQUIRED BASE HOURS TO HIT EXACT EFFICIENCY %
    T_USED_FAST = T_GAIN_HRS / 0.1243
    T_EXP_FAST = T_USED_FAST + T_GAIN_HRS
    
    T_USED_SLOW = T_LOSS_HRS / 0.1270
    T_EXP_SLOW = T_USED_SLOW - T_LOSS_HRS
    
    # 3. ROW DISTRIBUTION
    N_FAST = 800
    N_SLOW = 400
    N_WITHIN = 1300
    
    w_f = np.random.uniform(0.5, 1.5, N_FAST)
    w_f /= w_f.sum()
    
    w_s = np.random.uniform(0.5, 1.5, N_SLOW)
    w_s /= w_s.sum()
    
    # Generate perfectly distributed sub-dataframes
    df_fast = pd.DataFrame({
        'Tolerance_Status': ['Fast'] * N_FAST,
        'Gain_Hours': w_f * T_GAIN_HRS,
        'Loss_Hours': 0.0,
        'Shots_Gained': w_f * T_GAIN_SHOTS,
        'Shots_Lost': 0.0,
        'Expected_Hours': w_f * T_EXP_FAST,
        'Used_Hours': w_f * T_USED_FAST,
        'Base_Fin_Gain': w_f * T_FIN_GAIN,
        'Base_Fin_Loss': 0.0,
        'Supplier': np.random.choice(['Foxconn', 'Jabil', 'Flex'], N_FAST),
        'Tooling Type': np.random.choice(['Injection Molding', 'High Pressure Die Casting', 'Progressive Stamping'], N_FAST),
        'Product': np.random.choice(['Product X248', 'Product X277', 'Product X418'], N_FAST)
    })
    
    df_slow = pd.DataFrame({
        'Tolerance_Status': ['Slow'] * N_SLOW,
        'Gain_Hours': 0.0,
        'Loss_Hours': w_s * T_LOSS_HRS,
        'Shots_Gained': 0.0,
        'Shots_Lost': w_s * T_LOSS_SHOTS,
        'Expected_Hours': w_s * T_EXP_SLOW,
        'Used_Hours': w_s * T_USED_SLOW,
        'Base_Fin_Gain': 0.0,
        'Base_Fin_Loss': w_s * T_FIN_LOSS,
        'Supplier': np.random.choice(['Sanmina', 'Pegatron', 'Celestica'], N_SLOW),
        'Tooling Type': np.random.choice(['Thermoforming', 'Blow Molding', 'Vacuum Forming'], N_SLOW),
        'Product': np.random.choice(['Product X620D', 'Product V15', 'Product V12'], N_SLOW)
    })
    
    df_within = pd.DataFrame({
        'Tolerance_Status': ['Neutral'] * N_WITHIN,
        'Gain_Hours': 0.0,
        'Loss_Hours': 0.0,
        'Shots_Gained': 0.0,
        'Shots_Lost': 0.0,
        'Expected_Hours': np.random.uniform(5.0, 20.0, N_WITHIN),
        'Base_Fin_Gain': 0.0,
        'Base_Fin_Loss': 0.0,
        'Supplier': np.random.choice(['Supplier Alpha', 'Neutral Corp'], N_WITHIN),
        'Tooling Type': np.random.choice(['Compression Molding', 'Rubber Molding', 'Silicone Molding'], N_WITHIN),
        'Product': np.random.choice(['Product Y99', 'Product Z11'], N_WITHIN)
    })
    df_within['Used_Hours'] = df_within['Expected_Hours']
    
    data = pd.concat([df_fast, df_slow, df_within], ignore_index=True)
    
    # Finalize derived metrics
    data['Total_Shots'] = data['Shots_Gained'] + data['Shots_Lost']
    data.loc[data['Tolerance_Status'] == 'Neutral', 'Total_Shots'] = np.random.randint(5000, 50000, N_WITHIN)
    
    data['ACT'] = (data['Expected_Hours'] * 3600) / data['Total_Shots']
    data['Actual_CT'] = (data['Used_Hours'] * 3600) / data['Total_Shots']
    data['Efficiency_%'] = np.where(data['Used_Hours'] > 0, (data['Expected_Hours'] / data['Used_Hours']) * 100, 0)
    
    # Uniformly distribute dates to ensure default "Last 90 Days" filter captures 100% of data
    end_date = datetime.today()
    start_date = end_date - timedelta(days=89)
    date_offsets = np.random.randint(0, 90, len(data))
    data['Date'] = [start_date + timedelta(days=int(x)) for x in date_offsets]
    
    # Generic metadata
    data['OEM Business Division'] = np.random.choice(['NA Auto', 'EU Consumer', 'APAC Enterprise', 'LATAM Industrial'], len(data))
    data['Toolmaker'] = np.random.choice(['TM-A', 'TM-B', 'TM-C', 'TM-D'], len(data))
    data['Plant'] = np.random.choice(['Plant 1 (MX)', 'Plant 2 (DE)', 'Plant 3 (CN)', 'Plant 4 (VN)'], len(data))
    data['Part'] = [f"Part-{np.random.randint(100, 999)}" for _ in range(len(data))]
    data['Tooling'] = [f"TL-{np.random.randint(1000, 9999)}" for _ in range(len(data))]
    
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
    start_date = min_date - timedelta(days=1) # Bounds widened strictly to capture 100% of baseline rows
    end_date = max_date + timedelta(days=1)
else:
    c1, c2 = st.sidebar.columns(2)
    with c1:
        start_date_input = st.date_input("Start Date", min_date.date(), max_value=max_date.date())
    with c2:
        end_date_input = st.date_input("End Date", max_date.date(), max_value=max_date.date())
    start_date = pd.to_datetime(start_date_input)
    end_date = pd.to_datetime(end_date_input) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

# Apply global time filter
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### Financial Parameters")
labor_rate = st.sidebar.number_input("Labor Rate ($/hour)", min_value=0.0, value=40.0, step=1.0)
machine_rate = st.sidebar.number_input("Machine Rate ($/hour)", min_value=0.0, value=180.0, step=1.0)
combined_rate = labor_rate + machine_rate

# Financial elasticity: Default $220/hr equates perfectly to the requested $1688 and $1712 targets.
rate_scalar = combined_rate / 220.0
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
# 5. DASHBOARD HEADER & CALCULATIONS
# ==========================================
st.markdown('<div class="dash-header">Cycle Time Efficiency</div>', unsafe_allow_html=True)

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
eff_within = calc_weighted_eff(filtered_df[filtered_df['Tolerance_Status'] == 'Neutral'])

def format_hm(hours_float):
    if pd.isna(hours_float) or hours_float == 0: return "0H 0M"
    sign = "-" if hours_float < 0 else ""
    h_float = abs(hours_float)
    h = int(h_float)
    m = int(round((h_float - h) * 60))
    if m == 60:
        h += 1
        m = 0
    return f"{sign}{h}H {m}M"

disp_gained_hrs = format_hm(gained_hrs)
disp_lost_hrs = format_hm(lost_hrs)
disp_net_hrs = format_hm(net_hrs)

disp_gained_shots = f"{int(gained_shots):,}"
disp_lost_shots = f"{int(lost_shots):,}"
disp_net_shots = f"{int(net_shots):,}"

disp_gained_fin = f"${gained_fin:,.0f}"
disp_lost_fin = f"-${abs(lost_fin):,.0f}"
fin_sign = "-$" if net_fin < 0 else "$"
disp_net_fin = f"{fin_sign}{abs(net_fin):,.0f}"

disp_eff_fast = f"+{eff_fast:.2f}%" if pd.notna(eff_fast) else "N/A"
disp_eff_slow = f"-{eff_slow:.2f}%" if pd.notna(eff_slow) else "N/A" 
disp_eff_within = f"{eff_within:.0f}%" if pd.notna(eff_within) else "N/A"

def build_html(*lines):
    return "".join(line.strip() for line in lines)

# ==========================================
# 6. SECTION 1: KPI SUMMARY CARDS
# ==========================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

html_kpi1 = build_html(
    '<div class="dash-card">',
    f'<div class="kpi-title-container"><span class="kpi-title">Net Hours: {disp_net_hrs}</span></div>',
    f'<div class="metric-row"><span class="metric-label">Gained</span><span class="metric-value text-green">{disp_gained_hrs}</span></div>',
    f'<div class="metric-row"><span class="metric-label">Lost</span><span class="metric-value text-red">{disp_lost_hrs}</span></div>',
    '</div>'
)
kpi1.markdown(html_kpi1, unsafe_allow_html=True)

html_kpi2 = build_html(
    '<div class="dash-card">',
    f'<div class="kpi-title-container"><span class="kpi-title">Net Shots: {disp_net_shots}</span></div>',
    f'<div class="metric-row"><span class="metric-label">Gained</span><span class="metric-value text-green">{disp_gained_shots}</span></div>',
    f'<div class="metric-row"><span class="metric-label">Lost</span><span class="metric-value text-red">{disp_lost_shots}</span></div>',
    '</div>'
)
kpi2.markdown(html_kpi2, unsafe_allow_html=True)

html_kpi3 = build_html(
    '<div class="dash-card">',
    f'<div class="kpi-title-container"><span class="kpi-title">Net Financial: {disp_net_fin}</span></div>',
    f'<div class="metric-row"><span class="metric-label">Gain</span><span class="metric-value text-green">{disp_gained_fin}</span></div>',
    f'<div class="metric-row"><span class="metric-label">Lost</span><span class="metric-value text-red">{disp_lost_fin}</span></div>',
    '</div>'
)
kpi3.markdown(html_kpi3, unsafe_allow_html=True)

html_kpi4 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container"><span class="kpi-title">Efficiency</span></div>',
    f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Fast</span><span class="metric-value text-green">{disp_eff_fast}</span></div>',
    f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Slow</span><span class="metric-value text-red">{disp_eff_slow}</span></div>',
    f'<div class="metric-row"><span class="metric-label">Within</span><span class="metric-value text-neutral">{disp_eff_within}</span></div>',
    '</div>'
)
kpi4.markdown(html_kpi4, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)


# ==========================================
# 7. PERFORMANCE ANALYTICS CHARTS
# ==========================================
def get_aggregated_stats(df, category):
    grouped = df.groupby(category)[['Expected_Hours', 'Used_Hours']].sum().reset_index()
    grouped['Efficiency_%'] = np.where(grouped['Used_Hours'] > 0, (grouped['Expected_Hours'] / grouped['Used_Hours']) * 100, 0)
    fast_df = grouped[grouped['Efficiency_%'] > 105].sort_values('Efficiency_%', ascending=False).head(3)
    slow_df = grouped[grouped['Efficiency_%'] < 95].sort_values('Efficiency_%', ascending=True).head(3)
    return fast_df, slow_df

# --- ROW 1: SUPPLIER PERFORMANCE ---
def build_plotly_vbar(df, x_col, y_col, color, is_fast=True):
    if df.empty: return None
    df_sorted = df.sort_values(y_col, ascending=False if is_fast else True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted[x_col], y=df_sorted[y_col] - 100, base=100, marker_color=color,
        text=df_sorted[y_col], texttemplate='%{text:.1f}%', textposition='outside',
        hovertemplate="<b>%{x}</b><br>Cycle Time Efficiency %: %{text:.1f}%<extra></extra>"
    ))

    if is_fast:
        max_val = df[y_col].max()
        y_range = [100, max(106, max_val * 1.05)]
    else:
        min_val = df[y_col].min()
        y_range = [min(94, min_val * 0.95), 100]

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Cycle Time Efficiency %",
        yaxis=dict(showgrid=True, gridcolor='#334155', range=y_range, title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8')),
        xaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)),
        margin=dict(l=55, r=10, t=20, b=30), height=240
    )
    return fig

with st.container(border=True):
    st.markdown('<div class="panel-title">Supplier Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    supp_fast, supp_slow = get_aggregated_stats(filtered_df, 'Supplier')
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Suppliers</div>', unsafe_allow_html=True)
        fig_sfast = build_plotly_vbar(supp_fast, 'Supplier', 'Efficiency_%', '#5cb85c', is_fast=True)
        if fig_sfast: st.plotly_chart(fig_sfast, use_container_width=True, key="supp_fast")
        else: st.markdown("<span style='color: #64748b;'>No suppliers >105% Efficiency.</span>", unsafe_allow_html=True)
        
    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Suppliers</div>', unsafe_allow_html=True)
        fig_sslow = build_plotly_vbar(supp_slow, 'Supplier', 'Efficiency_%', '#d9534f', is_fast=False)
        if fig_sslow: st.plotly_chart(fig_sslow, use_container_width=True, key="supp_slow")
        else: st.markdown("<span style='color: #64748b;'>No suppliers <95% Efficiency.</span>", unsafe_allow_html=True)


# --- ROW 2: TOOLING TYPE PERFORMANCE ---
def build_plotly_hbar(df, x_col, y_col, color, is_fast=True):
    if df.empty: return None
    df_sorted = df.sort_values(x_col, ascending=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted[y_col], x=df_sorted[x_col] - 100, base=100, orientation='h', marker_color=color,
        text=df_sorted[x_col], texttemplate='%{text:.1f}%', textposition='outside',
        hovertemplate="<b>%{y}</b><br>Cycle Time Efficiency %: %{text:.1f}%<extra></extra>"
    ))

    if is_fast:
        max_val = df[x_col].max()
        x_range = [100, max(106, max_val * 1.05)]
    else:
        min_val = df[x_col].min()
        x_range = [min(94, min_val * 0.95), 100]

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Cycle Time Efficiency %",
        xaxis=dict(showgrid=False, visible=True, range=x_range, title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8')),
        yaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)),
        margin=dict(l=0, r=40, t=10, b=30), height=220
    )
    return fig

with st.container(border=True):
    st.markdown('<div class="panel-title">Tooling Type Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    tool_fast, tool_slow = get_aggregated_stats(filtered_df, 'Tooling Type')
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Tooling Types</div>', unsafe_allow_html=True)
        fig_tfast = build_plotly_hbar(tool_fast, 'Efficiency_%', 'Tooling Type', '#5cb85c', is_fast=True)
        if fig_tfast: st.plotly_chart(fig_tfast, use_container_width=True, key="bar_fast")
        else: st.markdown("<span style='color: #64748b;'>No tooling types >105% Efficiency.</span>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Tooling Types</div>', unsafe_allow_html=True)
        fig_tslow = build_plotly_hbar(tool_slow, 'Efficiency_%', 'Tooling Type', '#d9534f', is_fast=False)
        if fig_tslow: st.plotly_chart(fig_tslow, use_container_width=True, key="bar_slow")
        else: st.markdown("<span style='color: #64748b;'>No tooling types <95% Efficiency.</span>", unsafe_allow_html=True)


# --- ROW 3: PRODUCT PERFORMANCE ---
def build_plotly_bubble(df, x_col, y_col, color, is_fast=True):
    if df.empty: return None
    if is_fast:
        df['Bubble_Size'] = df[x_col] - 100
        max_val = df[x_col].max()
        x_range = [100, max(106, max_val * 1.03)]
    else:
        df['Bubble_Size'] = 100 - df[x_col]
        min_val = df[x_col].min()
        x_range = [min(94, min_val * 0.97), 100]

    df['Bubble_Size'] = df['Bubble_Size'].clip(lower=0.5)

    fig = px.scatter(df, x=x_col, y=y_col, size='Bubble_Size', text=x_col, size_max=25)
    fig.update_traces(
        marker_color=color, texttemplate='%{text:.1f}%', textposition='middle right', 
        marker=dict(line=dict(width=1.5, color='#ffffff')),
        hovertemplate="<b>%{y}</b><br>Cycle Time Efficiency %: %{x:.1f}%<extra></extra>"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Cycle Time Efficiency %",
        xaxis=dict(showgrid=True, gridcolor='#334155', title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8'), range=x_range),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='', tickfont=dict(color='#e2e8f0', size=13)),
        margin=dict(l=0, r=40, t=10, b=40), height=240, showlegend=False
    )
    return fig

with st.container(border=True):
    st.markdown('<div class="panel-title">Product Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    prod_fast, prod_slow = get_aggregated_stats(filtered_df, 'Product')
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Products</div>', unsafe_allow_html=True)
        fig_pfast = build_plotly_bubble(prod_fast, 'Efficiency_%', 'Product', '#5cb85c', is_fast=True)
        if fig_pfast: st.plotly_chart(fig_pfast, use_container_width=True, key="bubble_fast")
        else: st.markdown("<span style='color: #64748b;'>No products >105% Efficiency.</span>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Products</div>', unsafe_allow_html=True)
        fig_pslow = build_plotly_bubble(prod_slow, 'Efficiency_%', 'Product', '#d9534f', is_fast=False)
        if fig_pslow: st.plotly_chart(fig_pslow, use_container_width=True, key="bubble_slow")
        else: st.markdown("<span style='color: #64748b;'>No products <95% Efficiency.</span>", unsafe_allow_html=True)


# ==========================================
# 8. INTERACTIVE DRILL-DOWN ANALYSIS
# ==========================================
st.markdown('<div class="section-title">Interactive Drill-Down Analysis</div>', unsafe_allow_html=True)

# Helper function to generate standardized drill-down tables mapping strictly to selected widgets
def get_widget_drilldown_table(df, group_col, widget_type):
    if df.empty: return pd.DataFrame()
    
    count_col = 'Product' if group_col in ['Supplier', 'Tooling Type'] else 'Supplier'
    count_label = 'Number of Products' if group_col in ['Supplier', 'Tooling Type'] else 'Number of Suppliers'
    
    agg_dict = {
        'Tooling': 'nunique', count_col: 'nunique',
        'Gain_Hours': 'sum', 'Loss_Hours': 'sum',
        'Shots_Gained': 'sum', 'Shots_Lost': 'sum',
        'Financial_Gain': 'sum', 'Financial_Loss': 'sum',
        'Expected_Hours': 'sum', 'Used_Hours': 'sum'
    }
    
    base = df.groupby(group_col).agg(agg_dict).reset_index()
    
    base['Net Efficiency %'] = np.where(base['Used_Hours'] > 0, (base['Expected_Hours'] / base['Used_Hours']) * 100, np.nan)
    base['Net Hours'] = base['Gain_Hours'] - base['Loss_Hours']
    base['Net Shots'] = base['Shots_Gained'] - base['Shots_Lost']
    base['Net Financial'] = base['Financial_Gain'] - base['Financial_Loss']
    
    eff_slice = df.groupby([group_col, 'Tolerance_Status'])[['Expected_Hours', 'Used_Hours']].sum().reset_index()
    eff_slice['Eff'] = np.where(eff_slice['Used_Hours'] > 0, (eff_slice['Expected_Hours'] / eff_slice['Used_Hours']) * 100, np.nan)
    
    eff_pivot = eff_slice.pivot(index=group_col, columns='Tolerance_Status', values='Eff').reset_index()
    for st_col in ['Fast', 'Slow', 'Neutral']:
        if st_col not in eff_pivot.columns: eff_pivot[st_col] = np.nan
    eff_pivot.rename(columns={'Fast': 'Fast %', 'Slow': 'Slow %', 'Neutral': 'Within %'}, inplace=True)
    
    merged = pd.merge(base, eff_pivot, on=group_col, how='left')
    merged.rename(columns={'Tooling': 'Number of Tools', count_col: count_label}, inplace=True)
    
    if widget_type == 'Net Hours':
        merged.rename(columns={'Gain_Hours': 'Hours Gained', 'Loss_Hours': 'Hours Lost'}, inplace=True)
        res = merged[[group_col, 'Number of Tools', count_label, 'Hours Gained', 'Hours Lost', 'Net Hours']].copy()
        for c in ['Hours Gained', 'Hours Lost', 'Net Hours']:
            res[c] = res[c].apply(format_hm)
        return res
        
    elif widget_type == 'Net Shots':
        merged.rename(columns={'Shots_Gained': 'Shots Gained', 'Shots_Lost': 'Shots Lost'}, inplace=True)
        res = merged[[group_col, 'Number of Tools', count_label, 'Shots Gained', 'Shots Lost', 'Net Shots']].copy()
        for c in ['Shots Gained', 'Shots Lost', 'Net Shots']:
            res[c] = res[c].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "0")
        return res
        
    elif widget_type == 'Net Financial':
        merged.rename(columns={'Financial_Gain': 'Gain', 'Financial_Loss': 'Lost'}, inplace=True)
        res = merged[[group_col, 'Number of Tools', count_label, 'Gain', 'Lost', 'Net Financial']].copy()
        for c in ['Gain', 'Lost', 'Net Financial']:
            res[c] = res[c].apply(lambda x: f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}")
        return res
        
    elif widget_type == 'Efficiency':
        res = merged[[group_col, 'Number of Tools', count_label, 'Fast %', 'Slow %', 'Within %', 'Net Efficiency %']].copy()
        for c in ['Fast %', 'Slow %', 'Within %', 'Net Efficiency %']:
            res[c] = res[c].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        return res
        
    return pd.DataFrame()


drill_options = ["(No Selection)"] + \
                ["Widget: Net Hours", "Widget: Net Shots", "Widget: Net Financial", "Widget: Efficiency"] + \
                [f"Supplier: {s}" for s in filtered_df['Supplier'].unique()] + \
                [f"Tooling Type: {t}" for t in filtered_df['Tooling Type'].unique()] + \
                [f"Product: {p}" for p in filtered_df['Product'].unique()]

drill_target = st.selectbox(
    "Simulate a Click on a Widget or Name to Drill Down:", 
    options=drill_options,
    help="Since native HTML clicks aren't supported in standard Streamlit without custom plugins, select a widget or entity here to view its drill-down analysis."
)

if drill_target != "(No Selection)":
    
    # ----------------------------------------------------
    # BRANCH A: WIDGET-BASED DRILL-DOWN WITH TABS & SUMMARY TOTALS
    # ----------------------------------------------------
    if drill_target.startswith("Widget:"):
        widget_name = drill_target.replace("Widget: ", "")
        st.markdown(f"### Drill-Down Details: `{widget_name}`")
        
        # Calculate consistent global totals for the selected widget
        if widget_name == 'Net Hours':
            val_gain = format_hm(filtered_df['Gain_Hours'].sum())
            val_lost = format_hm(filtered_df['Loss_Hours'].sum())
            val_net = format_hm(filtered_df['Gain_Hours'].sum() - filtered_df['Loss_Hours'].sum())
        elif widget_name == 'Net Shots':
            val_gain = f"{int(filtered_df['Shots_Gained'].sum()):,}"
            val_lost = f"{int(filtered_df['Shots_Lost'].sum()):,}"
            val_net = f"{int(filtered_df['Shots_Gained'].sum() - filtered_df['Shots_Lost'].sum()):,}"
        elif widget_name == 'Net Financial':
            gain_fin = filtered_df['Financial_Gain'].sum()
            loss_fin = filtered_df['Financial_Loss'].sum()
            net_fin_calc = gain_fin - loss_fin
            val_gain = f"${gain_fin:,.0f}"
            val_lost = f"${loss_fin:,.0f}"
            val_net = f"-${abs(net_fin_calc):,.0f}" if net_fin_calc < 0 else f"${net_fin_calc:,.0f}"
        elif widget_name == 'Efficiency':
            eff_fast_val = calc_weighted_eff(filtered_df[filtered_df['Tolerance_Status'] == 'Fast'])
            eff_slow_val = calc_weighted_eff(filtered_df[filtered_df['Tolerance_Status'] == 'Slow'])
            eff_net_val = calc_weighted_eff(filtered_df)
            val_gain = f"+{eff_fast_val:.2f}%" if pd.notna(eff_fast_val) else "N/A"
            val_lost = f"-{eff_slow_val:.2f}%" if pd.notna(eff_slow_val) else "N/A"
            val_net = f"{eff_net_val:.2f}%" if pd.notna(eff_net_val) else "N/A"

        # Summary Total Section (Globally applicable to all 3 tabs beneath it)
        sm1, sm2, sm3 = st.columns(3)
        sm1.metric("Total Gain", val_gain)
        sm2.metric("Total Lost", val_lost)
        sm3.metric("Total Net", val_net)
        
        st.markdown("<hr style='border-color: #2d3748; margin-top: 1rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)
        
        tab_supp, tab_tool, tab_prod = st.tabs(["View By Supplier", "View By Tooling Type", "View By Product"])
        
        with tab_supp:
            df_supp = get_widget_drilldown_table(filtered_df, 'Supplier', widget_name)
            st.dataframe(df_supp, use_container_width=True, hide_index=True)
            
        with tab_tool:
            df_tool = get_widget_drilldown_table(filtered_df, 'Tooling Type', widget_name)
            st.dataframe(df_tool, use_container_width=True, hide_index=True)
            
        with tab_prod:
            df_prod = get_widget_drilldown_table(filtered_df, 'Product', widget_name)
            st.dataframe(df_prod, use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # BRANCH B: ENTITY-BASED DRILL-DOWN (SUPPLIER/TOOL/PRODUCT)
    # ----------------------------------------------------
    else:
        st.markdown(f"### Drill-Down Details: `{drill_target}`")
        
        if drill_target.startswith("Supplier:"):
            entity = drill_target.replace("Supplier: ", "")
            df_drill = filtered_df[filtered_df["Supplier"] == entity].copy()
        elif drill_target.startswith("Tooling Type:"):
            entity = drill_target.replace("Tooling Type: ", "")
            df_drill = filtered_df[filtered_df["Tooling Type"] == entity].copy()
        elif drill_target.startswith("Product:"):
            entity = drill_target.replace("Product: ", "")
            df_drill = filtered_df[filtered_df["Product"] == entity].copy()
        
        drill_eff = calc_weighted_eff(df_drill)
        drill_gain_h = df_drill['Gain_Hours'].sum()
        drill_loss_h = df_drill['Loss_Hours'].sum()
        drill_net_fin = df_drill['Financial_Gain'].sum() - df_drill['Financial_Loss'].sum()
        
        dkpi1, dkpi2, dkpi3, dkpi4 = st.columns(4)
        dkpi1.metric("Overall Cycle Time Efficiency %", f"{drill_eff:.1f}%" if pd.notna(drill_eff) else "N/A")
        dkpi2.metric("Total Hours Gained (Fast)", format_hm(drill_gain_h))
        dkpi3.metric("Total Hours Lost (Slow)", format_hm(drill_loss_h))
        dkpi4.metric("Savings Opportunity (Net)", f"${drill_net_fin:,.0f}")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        t_col1, t_col2 = st.columns(2, gap="large")
        with t_col1:
            st.markdown("**Historical Trend: Cycle Time Efficiency % over Time**")
            trend_df = df_drill.groupby('Date')[['Expected_Hours', 'Used_Hours']].sum().reset_index()
            trend_df['Efficiency_%'] = np.where(trend_df['Used_Hours'] > 0, (trend_df['Expected_Hours'] / trend_df['Used_Hours']) * 100, 0)
            
            fig_dt = px.line(trend_df, x='Date', y='Efficiency_%', markers=True)
            fig_dt.add_hline(y=100, line_dash="dash", line_color="#94a3b8", annotation_text="100% Benchmark")
            fig_dt.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, title='', tickfont=dict(color='#94a3b8')),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Cycle Time Efficiency %', tickfont=dict(color='#e2e8f0')),
                margin=dict(l=0, r=20, t=10, b=10), height=300
            )
            st.plotly_chart(fig_dt, use_container_width=True)
            
        with t_col2:
            st.markdown("**Production Variance: Fast vs Slow Distribution**")
            var_df = df_drill.groupby('Tolerance_Status')['Total_Shots'].sum().reset_index()
            var_colors = {'Fast': '#5cb85c', 'Slow': '#d9534f', 'Neutral': '#f8fafc'}
            fig_dv = px.bar(var_df, x='Tolerance_Status', y='Total_Shots', color='Tolerance_Status', color_discrete_map=var_colors)
            fig_dv.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title='Classification', tickfont=dict(color='#94a3b8')),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Total Production Shots', tickfont=dict(color='#e2e8f0')),
                margin=dict(l=0, r=20, t=10, b=10), height=300, showlegend=False
            )
            st.plotly_chart(fig_dv, use_container_width=True)

        st.markdown("**Detailed Benchmark & Operations Breakdown**")
        display_df = df_drill[['Date', 'Plant', 'Tooling', 'Product', 'ACT', 'Actual_CT', 'Efficiency_%', 'Tolerance_Status', 'Financial_Gain', 'Financial_Loss']].copy()
        display_df.rename(columns={'ACT': 'Approved CT (s)', 'Actual_CT': 'Actual CT (s)', 'Efficiency_%': 'Cycle Time Efficiency %', 'Tolerance_Status': 'Status', 'Financial_Gain': 'Gain ($)', 'Financial_Loss': 'Lost ($)'}, inplace=True)
        display_df = display_df.sort_values(by='Date', ascending=False)
        
        st.dataframe(
            display_df.style.format({
                'Approved CT (s)': "{:.1f}", 
                'Actual CT (s)': "{:.1f}", 
                'Cycle Time Efficiency %': "{:.1f}%",
                'Gain ($)': "${:.0f}",
                'Lost ($)': "${:.0f}"
            }), 
            use_container_width=True,
            hide_index=True
        )