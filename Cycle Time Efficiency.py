import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Cycle Time Efficiency Analytics",
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
.css-18ni7ap {visibility: hidden;} /* Hide top padding */
.block-container {padding-top: 2rem !important; padding-bottom: 2rem !important;}

/* Title Header */
.dash-header {
    font-size: 1.75rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 1.5rem;
    letter-spacing: 0.5px;
}

/* Dashboard Card Global Styles */
.dash-card {
    background-color: #1a1d26;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #2d3748;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}
.dash-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
    border-color: #4a5568;
}

/* KPI Card Typography */
.kpi-title-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}
.kpi-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #cbd5e1;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.kpi-icon {
    color: #475569;
    font-size: 1.2rem;
}

/* Metric Rows */
.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-size: 1.1rem;
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
.text-green { color: #10b981 !important; }
.text-red { color: #ef4444 !important; }
.text-neutral { color: #f8fafc !important; }

/* Panel Specific Styles */
.panel-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 20px;
}
.panel-split {
    display: flex;
    gap: 24px;
}
.panel-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0; /* Prevents flex blowout */
}
.col-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-bottom: 8px;
    margin-bottom: 16px;
    border-bottom: 1px solid #334155;
}

/* Ranking Items & Progress Bars */
.rank-item {
    margin-bottom: 16px;
}
.rank-text-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    font-size: 0.9rem;
}
.rank-name {
    color: #e2e8f0;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 10px;
}
.bar-bg {
    width: 100%;
    background-color: #334155;
    height: 4px;
    border-radius: 2px;
    overflow: hidden;
}
.bar-fill-green {
    height: 100%;
    background-color: #10b981;
    border-radius: 2px;
}
.bar-fill-red {
    height: 100%;
    background-color: #ef4444;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA LOADING & PROCESSING
# ==========================================
@st.cache_data
def load_base_data():
    """Generates base mock data ensuring proper Tooling Types for the new UI"""
    np.random.seed(42)
    n_rows = 2500
    
    tooling_types = [
        'Injection Molding', 'Blow Molding', 'Compression Molding', 'Rubber Molding', 
        'Silicone Molding', 'Simple Blanking Stamping', 'Forming Stamping', 'Compound Stamping', 
        'Progressive Stamping', 'Tandem Stamping', 'Transfer Stamping', 'High Pressure Die Casting', 
        'Vacuum Forming', 'Thermoforming'
    ]
    
    data = pd.DataFrame({
        'Date': [datetime.today() - timedelta(days=int(x)) for x in np.random.randint(0, 90, n_rows)],
        'OEM Business Division': np.random.choice(['NA Auto', 'EU Consumer', 'APAC Enterprise', 'LATAM Industrial'], n_rows),
        'Supplier': np.random.choice(['Supplier Alpha', 'Foxconn', 'Jabil', 'Flex', 'Sanmina', 'Pegatron', 'Celestica'], n_rows),
        'Toolmaker': np.random.choice(['TM-A', 'TM-B', 'TM-C', 'TM-D'], n_rows),
        'Plant': np.random.choice(['Plant 1 (MX)', 'Plant 2 (DE)', 'Plant 3 (CN)', 'Plant 4 (VN)'], n_rows),
        'Tooling Type': np.random.choice(tooling_types, n_rows),
        'Product': np.random.choice(['Product X248', 'Product X277', 'Product X418', 'Product X620D', 'Product V15', 'Product V12'], n_rows),
        'Part': [f"Part-{np.random.randint(100, 999)}" for _ in range(n_rows)],
        'Tooling': [f"TL-{np.random.randint(1000, 9999)}" for _ in range(n_rows)],
        'ACT': np.random.uniform(15.0, 60.0, n_rows),
        'Total_Shots': np.random.randint(5000, 50000, n_rows)
    })

    # Add realistic variance 
    variance_multiplier = np.random.normal(1.0, 0.08, n_rows)
    data['Actual_CT'] = data['ACT'] * variance_multiplier
    
    # Core Logic
    data['Expected_Hours'] = (data['ACT'] * data['Total_Shots']) / 3600
    data['Used_Hours'] = (data['Actual_CT'] * data['Total_Shots']) / 3600
    data['Hours_Diff'] = data['Expected_Hours'] - data['Used_Hours']
    
    def categorize_shot(row):
        if row['Actual_CT'] < (row['ACT'] * 0.95):
            return "Below Tolerance"
        elif row['Actual_CT'] > (row['ACT'] * 1.05):
            return "Above Tolerance"
        else:
            return "Within Tolerance"
            
    data['Tolerance_Status'] = data.apply(categorize_shot, axis=1)
    
    data['Gain_Hours'] = np.where(data['Tolerance_Status'] == 'Below Tolerance', data['Hours_Diff'], 0)
    data['Loss_Hours'] = np.where(data['Tolerance_Status'] == 'Above Tolerance', -data['Hours_Diff'], 0)
    
    data['Shots_Gained'] = np.where(data['ACT'] > 0, (data['Gain_Hours'] * 3600) / data['ACT'], 0)
    data['Shots_Lost'] = np.where(data['ACT'] > 0, (data['Loss_Hours'] * 3600) / data['ACT'], 0)
    
    data['Efficiency_%'] = (data['Expected_Hours'] / data['Used_Hours']) * 100
    
    return data

df = load_base_data()

# ==========================================
# 4. SIDEBAR FILTERS & FINANCIALS
# ==========================================
st.sidebar.markdown("### Financial Parameters")
labor_rate = st.sidebar.number_input("Labor Rate ($/hour)", min_value=0.0, value=40.0, step=1.0)
machine_rate = st.sidebar.number_input("Machine Rate ($/hour)", min_value=0.0, value=180.0, step=1.0)
combined_rate = labor_rate + machine_rate

# Dynamically apply financial logic
df['Financial_Gain'] = df['Gain_Hours'] * combined_rate
df['Financial_Loss'] = df['Loss_Hours'] * combined_rate

st.sidebar.markdown("---")
st.sidebar.markdown("### Master Filter")

selected_oem = st.sidebar.multiselect("OEM Business Division", options=df['OEM Business Division'].unique())
filtered_df = df[df['OEM Business Division'].isin(selected_oem)] if selected_oem else df

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
st.markdown('<div class="dash-header">Manufacturing Performance: Cycle Time Efficiency</div>', unsafe_allow_html=True)

gained_hrs = filtered_df['Gain_Hours'].sum()
lost_hrs = filtered_df['Loss_Hours'].sum()
gained_shots = filtered_df['Shots_Gained'].sum()
lost_shots = filtered_df['Shots_Lost'].sum()
gained_fin = filtered_df['Financial_Gain'].sum()
lost_fin = filtered_df['Financial_Loss'].sum()

eff_fast = filtered_df[filtered_df['Tolerance_Status'] == 'Below Tolerance']['Efficiency_%'].mean()
eff_slow = filtered_df[filtered_df['Tolerance_Status'] == 'Above Tolerance']['Efficiency_%'].mean()
eff_within = filtered_df[filtered_df['Tolerance_Status'] == 'Within Tolerance']['Efficiency_%'].mean()

def format_hm(hours_float):
    if pd.isna(hours_float): return "0H 0M"
    h = int(abs(hours_float))
    m = int((abs(hours_float) - h) * 60)
    return f"{h}H {m}M"

# ==========================================
# 6. SECTION 1: KPI SUMMARY CARDS
# ==========================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

with kpi1:
    st.markdown(f"""
<div class="dash-card">
    <div class="kpi-title-container">
        <span class="kpi-title">Net Hours</span>
        <span class="kpi-icon">ℹ️</span>
    </div>
    <div class="metric-row">
        <span class="metric-label">Gained</span>
        <span class="metric-value text-green">{format_hm(gained_hrs)}</span>
    </div>
    <div class="metric-row">
        <span class="metric-label">Lost</span>
        <span class="metric-value text-red">{format_hm(lost_hrs)}</span>
    </div>
</div>
""", unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
<div class="dash-card">
    <div class="kpi-title-container">
        <span class="kpi-title">Net Shots</span>
        <span class="kpi-icon">ℹ️</span>
    </div>
    <div class="metric-row">
        <span class="metric-label">Gained</span>
        <span class="metric-value text-green">{int(gained_shots):,}</span>
    </div>
    <div class="metric-row">
        <span class="metric-label">Lost</span>
        <span class="metric-value text-red">{int(lost_shots):,}</span>
    </div>
</div>
""", unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
<div class="dash-card">
    <div class="kpi-title-container">
        <span class="kpi-title">Net Financial</span>
        <span class="kpi-icon">ℹ️</span>
    </div>
    <div class="metric-row">
        <span class="metric-label">Financial Gain</span>
        <span class="metric-value text-green">${gained_fin:,.0f}</span>
    </div>
    <div class="metric-row">
        <span class="metric-label">Financial Loss</span>
        <span class="metric-value text-red">-${lost_fin:,.0f}</span>
    </div>
</div>
""", unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
<div class="dash-card">
    <div class="kpi-title-container">
        <span class="kpi-title">Efficiency</span>
        <span class="kpi-icon">ℹ️</span>
    </div>
    <div class="metric-row" style="margin-bottom: 8px;">
        <span class="metric-label">Fast</span>
        <span class="metric-value text-green">{f"+{eff_fast:.2f}%" if pd.notna(eff_fast) else "N/A"}</span>
    </div>
    <div class="metric-row" style="margin-bottom: 8px;">
        <span class="metric-label">Slow</span>
        <span class="metric-value text-red">{f"-{abs(eff_slow):.2f}%" if pd.notna(eff_slow) else "N/A"}</span>
    </div>
    <div class="metric-row">
        <span class="metric-label">Within</span>
        <span class="metric-value text-neutral">{f"{eff_within:.2f}%" if pd.notna(eff_within) else "N/A"}</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. SECTION 2: PERFORMANCE ANALYTICS
# ==========================================
def generate_panel_html(df, group_col, title):
    grouped = df.groupby(group_col)['Efficiency_%'].mean().reset_index()
    grouped = grouped.dropna(subset=['Efficiency_%'])
    
    fastest = grouped.sort_values('Efficiency_%', ascending=False).head(3)
    slowest = grouped.sort_values('Efficiency_%', ascending=True).head(3)
    
    max_fast = fastest['Efficiency_%'].max() if not fastest.empty else 100
    max_slow = slowest['Efficiency_%'].max() if not slowest.empty else 100
    
    html_parts = []
    html_parts.append('<div class="dash-card">')
    html_parts.append(f'<div class="panel-title">{title}</div>')
    html_parts.append('<div class="panel-split">')
    
    # Left: Fastest
    html_parts.append('<div class="panel-col">')
    html_parts.append('<div class="col-header text-green">Top 3 Fastest</div>')
    
    for _, row in fastest.iterrows():
        name = row[group_col]
        eff = row['Efficiency_%']
        bar_w = min(100, (eff / (max_fast + 0.001)) * 100)
        html_parts.append(f"""
<div class="rank-item">
    <div class="rank-text-row">
        <span class="rank-name" title="{name}">{name}</span>
        <span class="metric-value text-green">{eff:.1f}%</span>
    </div>
    <div class="bar-bg"><div class="bar-fill-green" style="width: {bar_w}%;"></div></div>
</div>
""")
        
    html_parts.append('</div>')
    
    # Right: Slowest
    html_parts.append('<div class="panel-col">')
    html_parts.append('<div class="col-header text-red">Top 3 Slowest</div>')
    
    for _, row in slowest.iterrows():
        name = row[group_col]
        eff = row['Efficiency_%']
        bar_w = min(100, (eff / (max_slow + 0.001)) * 100)
        html_parts.append(f"""
<div class="rank-item">
    <div class="rank-text-row">
        <span class="rank-name" title="{name}">{name}</span>
        <span class="metric-value text-red">{eff:.1f}%</span>
    </div>
    <div class="bar-bg"><div class="bar-fill-red" style="width: {bar_w}%;"></div></div>
</div>
""")
        
    html_parts.append('</div>')
    html_parts.append('</div>')
    html_parts.append('</div>')
    
    return "".join(html_parts)

# Render Panels
panel1, panel2, panel3 = st.columns(3, gap="medium")

with panel1:
    st.markdown(generate_panel_html(filtered_df, 'Supplier', 'Supplier Performance'), unsafe_allow_html=True)
    
with panel2:
    st.markdown(generate_panel_html(filtered_df, 'Tooling Type', 'Tooling Type Performance'), unsafe_allow_html=True)
    
with panel3:
    st.markdown(generate_panel_html(filtered_df, 'Product', 'Product Performance'), unsafe_allow_html=True)