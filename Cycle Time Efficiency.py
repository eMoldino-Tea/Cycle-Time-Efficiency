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
    T_GAIN_HRS = 15.2 # 15H 12M
    T_LOSS_HRS = 3.0833333333333335 # 3H 5M
    T_GAIN_SHOTS = 12553725
    T_LOSS_SHOTS = 5342431
    T_FIN_GAIN = 1688
    T_FIN_LOSS = 1712
    
    # 2. DERIVE REQUIRED BASE HOURS TO HIT EXACT EFFICIENCY %
    # 112.43% => Gain is 12.43% of Used => Used = Gain / 0.1243
    T_USED_FAST_MINS = 7337 # 15.2 / 0.1243 * 60
    # 87.30% => Loss is 12.70% of Used => Used = Loss / 0.1270
    T_USED_SLOW_MINS = 1457 # 3.0833 / 0.127 * 60
    
    # 3. ROW DISTRIBUTION (Balanced Entity Assignments)
    N_FAST = 300
    N_SLOW = 150
    N_WITHIN = 600
    
    suppliers_f = np.tile(['Foxconn', 'Jabil', 'Flex'], 100)
    tooling_f = np.repeat(['Injection Molding', 'High Pressure Die Casting', 'Progressive Stamping'], 100)
    np.random.shuffle(tooling_f)
    products_f = np.tile(['Product X248', 'Product X277', 'Product X418'], 100)
    np.random.shuffle(products_f)
    
    suppliers_s = np.tile(['Sanmina', 'Pegatron', 'Celestica'], 50)
    tooling_s = np.repeat(['Thermoforming', 'Blow Molding', 'Vacuum Forming'], 50)
    np.random.shuffle(tooling_s)
    products_s = np.tile(['Product X620D', 'Product V15', 'Product V12'], 50)
    np.random.shuffle(products_s)
    
    # Unique weighting maps to ensure charts look beautifully distinct from each other
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

    # Helper: Enforce exact integer distribution (no rounding float loss)
    def exact_distribute(target_int, weights):
        floored = np.floor(weights * target_int).astype(int)
        remainder = int(target_int - floored.sum())
        if remainder > 0:
            fractions = (weights * target_int) - floored
            indices = np.argsort(fractions)[::-1]
            for i in range(remainder):
                floored[indices[i]] += 1
        return floored

    # 4. Generate FASTER dataframe
    gain_mins = exact_distribute(912, w_gain_f) # 15H 12M = 912 mins
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
        'Product': products_f
    })
    df_fast['Expected_Hours'] = df_fast['Used_Hours'] + df_fast['Gain_Hours']

    # 5. Generate SLOWER dataframe
    loss_mins = exact_distribute(185, w_loss_s) # 3H 5M = 185 mins
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
        'Product': products_s
    })
    df_slow['Expected_Hours'] = df_slow['Used_Hours'] - df_slow['Loss_Hours']
    
    # 6. Generate NEUTRAL dataframe
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
    
    # 7. Finalize formulas mapped to AI Spec
    data['Total_Shots'] = data['Shots_Gained'] + data['Shots_Lost']
    data.loc[data['Tolerance_Status'] == 'Neutral', 'Total_Shots'] = np.random.randint(5000, 50000, N_WITHIN)
    data['ACT'] = (data['Expected_Hours'] * 3600) / data['Total_Shots']
    data['Actual_CT'] = (data['Used_Hours'] * 3600) / data['Total_Shots']
    data['Efficiency_%'] = np.where(data['Used_Hours'] > 0, (data['Expected_Hours'] / data['Used_Hours']) * 100, 0)
    
    # Lock dates within strict 90 days to guarantee default filter loads 100% of rows
    end_date = datetime.today()
    start_date = end_date - timedelta(days=89)
    date_offsets = np.random.randint(0, 90, len(data))
    data['Date'] = [start_date + timedelta(days=int(x)) for x in date_offsets]
    
    # Adjusted Cardinality for Tooling and Part to ensure realistic comparison overlaps
    data['OEM Business Division'] = np.random.choice(['NA Auto', 'EU Consumer', 'APAC Enterprise', 'LATAM Industrial'], len(data))
    data['Toolmaker'] = np.random.choice(['TM-A', 'TM-B', 'TM-C', 'TM-D'], len(data))
    data['Plant'] = np.random.choice(['Plant 1 (MX)', 'Plant 2 (DE)', 'Plant 3 (CN)', 'Plant 4 (VN)'], len(data))
    data['Part'] = [f"Part-{np.random.randint(1, 25):03d}" for _ in range(len(data))]
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

# Apply global time filter
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### Financial Parameters")
labor_rate = st.sidebar.number_input("Labor Rate ($/hour)", min_value=0.0, value=40.0, step=1.0)
machine_rate = st.sidebar.number_input("Machine Rate ($/hour)", min_value=0.0, value=180.0, step=1.0)
combined_rate = labor_rate + machine_rate

# Financial elasticity math: Base Rate * Multiplier applies dynamically across dashboard UI changes
rate_scalar = combined_rate / 220.0
filtered_df['Active_Rate'] = filtered_df['Base_Fin_Gain'] * rate_scalar
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
fin_sign = "-$" if net_fin < 0 else "$"
disp_net_fin = f"{fin_sign}{abs(net_fin):,.0f}"

disp_eff_fast = f"+{eff_fast:.2f}%" if pd.notna(eff_fast) else "N/A"
disp_eff_slow = f"-{abs(100 - eff_slow):.2f}%" if pd.notna(eff_slow) else "N/A" 
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
            res[c] = res[c].apply(lambda x: f"{int(round(x)):,}" if pd.notna(x) else "0")
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
            val_gain = f"{int(round(filtered_df['Shots_Gained'].sum())):,}"
            val_lost = f"{int(round(filtered_df['Shots_Lost'].sum())):,}"
            val_net = f"{int(round(filtered_df['Shots_Gained'].sum() - filtered_df['Shots_Lost'].sum())):,}"
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
            val_lost = f"-{abs(eff_slow_val):.2f}%" if pd.notna(eff_slow_val) else "N/A"
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
        else:
            df_drill = filtered_df.copy()
        
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
            st.markdown("**Efficiency Distribution**")
            
            # Simulate visually balanced distribution while mathematically tying to the exact entity total
            drill_total_shots = df_drill['Total_Shots'].sum() if not df_drill.empty else 15000
            rng = np.random.RandomState(abs(hash(drill_target)) % 10000)
            fast_sim = int(drill_total_shots * rng.uniform(0.25, 0.40))
            slow_sim = int(drill_total_shots * rng.uniform(0.15, 0.30))
            within_sim = drill_total_shots - fast_sim - slow_sim
            
            var_df = pd.DataFrame({
                'Tolerance_Status': ['Fast', 'Slow', 'Within Efficiency'],
                'Total_Shots': [fast_sim, slow_sim, within_sim]
            })
            var_colors = {'Fast': '#5cb85c', 'Slow': '#d9534f', 'Within Efficiency': '#f8fafc'}
            fig_dv = px.pie(var_df, names='Tolerance_Status', values='Total_Shots', color='Tolerance_Status', color_discrete_map=var_colors, hole=0.4)
            fig_dv.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=20, t=10, b=10), height=300,
                legend=dict(font=dict(color='#94a3b8'))
            )
            st.plotly_chart(fig_dv, use_container_width=True)

        st.markdown("**Detailed Benchmark & Operations Breakdown**")
        
        # Use exact suggested simulated data structure for drill down
        simulated_drilldown_df = pd.DataFrame([
            {
                'Tooling ID': 'T-001', 'Time Period': '2025-09-05 to 2025-09-09', 'Part': 'P-001', 'Part Name': 'Part A',
                'Product': 'ATSE', 'Supplier': 'IC', 'Hourly Rate': 220, 'Total Shots': 10912, 'Parts Produced': 18260,
                'ACT': 74.65, 'Actual Average CT (WACT)': 89.30, 'CT Difference': -14.65, 'Total Expected Hours': 18.18,
                'Total Actual Hours': 22.6, 'Fast Shots (%)': 2.11, 'Slow Shots (%)': 36.39, 'Within Shots (%)': 61.5,
                'WACT (Fast)': 34.37, 'WACT (Slow)': 99.88, 'Expected Hours (Fast)': 0.38, 'Expected Hours (Slow)': 6.62,
                'Actual Hours (Fast)': 0.22, 'Actual Hours (Slow)': 11.01, 'Hours Gained': 0.16, 'Hours Lost': 4.39,
                'Shots Gained': 23.39, 'Shots Lost': 735.29, 'Financial Gain': 65.8, 'Financial Loss': -930.61,
                'Net': 72.73, 'CT Efficiency of Fast Hours': 60.13, 'CT Efficiency of Slow Hours': 87.02,
                'CT Weighted Average Efficiency': 80.4, 'Performance Status': 'Slower'
            },
            {
                'Tooling ID': 'T-002', 'Time Period': '2025-09-11 to 2025-09-12', 'Part': 'P-002', 'Part Name': 'Part B',
                'Product': 'ATSE', 'Supplier': 'IC', 'Hourly Rate': 220, 'Total Shots': 8158, 'Parts Produced': 15505,
                'ACT': 59.59, 'Actual Average CT (WACT)': 69.18, 'CT Difference': -9.59, 'Total Expected Hours': 11.32,
                'Total Actual Hours': 13.49, 'Fast Shots (%)': 19.63, 'Slow Shots (%)': 76.2, 'Within Shots (%)': 4.17,
                'WACT (Fast)': 44.33, 'WACT (Slow)': 64.11, 'Expected Hours (Fast)': 2.22, 'Expected Hours (Slow)': 8.62,
                'Actual Hours (Fast)': 1.97, 'Actual Hours (Slow)': 11.06, 'Hours Gained': 0.25, 'Hours Lost': 2.44,
                'Shots Gained': 16.06, 'Shots Lost': 2155, 'Financial Gain': 536.8, 'Financial Loss': -481.8,
                'Net': 112.69, 'CT Efficiency of Fast Hours': 77.94, 'CT Efficiency of Slow Hours': 85.68,
                'CT Weighted Average Efficiency': 83.9, 'Performance Status': 'Slower'
            },
            {
                'Tooling ID': 'T-003', 'Time Period': '2025-09-18 to 2025-09-28', 'Part': 'P-003', 'Part Name': 'Part C',
                'Product': 'ATSE', 'Supplier': 'IC', 'Hourly Rate': 220, 'Total Shots': 12695, 'Parts Produced': 76222,
                'ACT': 7.08, 'Actual Average CT (WACT)': 12.16, 'CT Difference': -5.08, 'Total Expected Hours': 7.76,
                'Total Actual Hours': 9.55, 'Fast Shots (%)': 0.47, 'Slow Shots (%)': 99.53, 'Within Shots (%)': 0,
                'WACT (Fast)': 12.18, 'WACT (Slow)': 27.15, 'Expected Hours (Fast)': 0.04, 'Expected Hours (Slow)': 7.72,
                'Actual Hours (Fast)': 0.02, 'Actual Hours (Slow)': 9.53, 'Hours Gained': 0.02, 'Hours Lost': 1.81,
                'Shots Gained': 6.12, 'Shots Lost': 634.43, 'Financial Gain': 98.2, 'Financial Loss': -393.8,
                'Net': 200, 'CT Efficiency of Fast Hours': 81.01, 'CT Efficiency of Slow Hours': 81.57,
                'CT Weighted Average Efficiency': 81.2, 'Performance Status': 'Slower'
            },
            {
                'Tooling ID': 'T-004', 'Time Period': '2025-11-18 to 2025-11-18', 'Part': 'P-004', 'Part Name': 'Part D',
                'Product': 'ATSE', 'Supplier': 'IC', 'Hourly Rate': 220, 'Total Shots': 800, 'Parts Produced': 800,
                'ACT': 43, 'Actual Average CT (WACT)': 82.79, 'CT Difference': -39.79, 'Total Expected Hours': 9.56,
                'Total Actual Hours': 18.40, 'Fast Shots (%)': 100, 'Slow Shots (%)': 0, 'Within Shots (%)': 0,
                'WACT (Fast)': 43, 'WACT (Slow)': 82.79, 'Expected Hours (Fast)': 0, 'Expected Hours (Slow)': 9.56,
                'Actual Hours (Fast)': 0, 'Actual Hours (Slow)': 18.40, 'Hours Gained': 8.84, 'Hours Lost': 0,
                'Shots Gained': 800, 'Shots Lost': 0, 'Financial Gain': 1944.8, 'Financial Loss': -1944.8,
                'Net': 100, 'CT Efficiency of Fast Hours': 51.96, 'CT Efficiency of Slow Hours': 51.96,
                'CT Weighted Average Efficiency': 51.96, 'Performance Status': 'Slower'
            }
        ])
        
        st.dataframe(simulated_drilldown_df, use_container_width=True, hide_index=True)

# ==========================================
# 9. COMPARISON ANALYSIS
# ==========================================
st.markdown('<div class="section-title">Comparison Analysis</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Compare performance of tools producing the same part, or suppliers producing the same part.</p>", unsafe_allow_html=True)

comp_mode = st.radio("Select Comparison Mode:", ["Part Comparison (tools making the same part)", "Supplier Comparison (tools making the same part from different suppliers)"], horizontal=True)

if "Part Comparison" in comp_mode:
    parts_available = sorted(filtered_df['Part'].unique())
    if len(parts_available) > 0:
        comp_target = st.selectbox("Select a Part to compare its Tools:", parts_available)
        comp_df = filtered_df[filtered_df['Part'] == comp_target]
        group_col = 'Tooling'
    else:
        comp_target = None
        comp_df = pd.DataFrame()
else:
    parts_available = sorted(filtered_df['Part'].unique())
    if len(parts_available) > 0:
        comp_target = st.selectbox("Select a Part to compare across Suppliers:", parts_available)
        comp_df = filtered_df[filtered_df['Part'] == comp_target]
        group_col = 'Supplier'
    else:
        comp_target = None
        comp_df = pd.DataFrame()

if comp_target and not comp_df.empty:
    # Build comparison data using established calculation functions to guarantee identical mathematical reconciliation
    comp_grouped = comp_df.groupby(group_col).apply(lambda x: pd.Series({
        'Total Shots': x['Total_Shots'].sum(),
        'Cycle Time Efficiency %': calc_weighted_eff(x),
        'Hours Gained': x['Gain_Hours'].sum(),
        'Hours Lost': x['Loss_Hours'].sum(),
        'Net Hours': x['Gain_Hours'].sum() - x['Loss_Hours'].sum(),
        'Net Financial': x['Financial_Gain'].sum() - x['Financial_Loss'].sum()
    })).reset_index()

    # Display comparison chart
    fig_comp = px.bar(
        comp_grouped, 
        x=group_col, 
        y='Cycle Time Efficiency %', 
        color='Net Financial',
        text='Cycle Time Efficiency %',
        color_continuous_scale=['#d9534f', '#f8fafc', '#5cb85c'],
        title=f"Cycle Time Efficiency % by {group_col} (Target: {comp_target})"
    )
    fig_comp.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_comp.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='Cycle Time Efficiency %', tickfont=dict(color='#94a3b8')),
        margin=dict(l=0, r=20, t=40, b=10), height=350,
        coloraxis_colorbar=dict(
            title=dict(text="Net Financial ($)", font=dict(color='#94a3b8')),
            tickfont=dict(color='#94a3b8')
        )
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # Display formatted comparison table
    display_comp = comp_grouped.copy()
    display_comp['Cycle Time Efficiency %'] = display_comp['Cycle Time Efficiency %'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    display_comp['Hours Gained'] = display_comp['Hours Gained'].apply(format_hm)
    display_comp['Hours Lost'] = display_comp['Hours Lost'].apply(format_hm)
    display_comp['Net Hours'] = display_comp['Net Hours'].apply(format_hm)
    display_comp['Net Financial'] = display_comp['Net Financial'].apply(lambda x: f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}")
    display_comp['Total Shots'] = display_comp['Total Shots'].apply(lambda x: f"{int(round(x)):,}")
    
    st.dataframe(display_comp, use_container_width=True, hide_index=True)
elif comp_target:
    st.info(f"No data available for the selected {comp_target}.")