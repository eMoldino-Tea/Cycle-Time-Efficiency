import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
# CSS is fully left-aligned to prevent Streamlit from rendering it as a Markdown code block
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
    padding: 15px 20px !important;
    border: 1px solid #2d3748 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1) !important;
    margin-bottom: 20px !important;
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

/* Color Tokens (Muted for better eye comfort) */
.text-green { color: #5cb85c !important; }
.text-red { color: #d9534f !important; }
.text-neutral { color: #f8fafc !important; }

/* Panel Specific Styles */
.panel-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 24px;
}
.col-header {
    font-size: 0.8rem;
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
    background-color: #2d3748;
    height: 6px;
    border-radius: 3px;
    overflow: hidden;
}
.bar-fill-green {
    height: 100%;
    background-color: #5cb85c;
    border-radius: 3px;
}
.bar-fill-red {
    height: 100%;
    background-color: #d9534f;
    border-radius: 3px;
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
    
    # Updated logic for classification thresholds (Fast > 105, Slow < 95, Neutral 95-105)
    def categorize_shot(row):
        if row['Actual_CT'] < (row['ACT'] * 0.95):
            return "Below Tolerance" # Fast
        elif row['Actual_CT'] > (row['ACT'] * 1.05):
            return "Above Tolerance" # Slow
        else:
            return "Within Tolerance" # Neutral
            
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
st.markdown('<div class="dash-header">Cycle Time Efficiency</div>', unsafe_allow_html=True)

gained_hrs = filtered_df['Gain_Hours'].sum()
lost_hrs = filtered_df['Loss_Hours'].sum()
gained_shots = filtered_df['Shots_Gained'].sum()
lost_shots = filtered_df['Shots_Lost'].sum()
gained_fin = filtered_df['Financial_Gain'].sum()
lost_fin = filtered_df['Financial_Loss'].sum()

# Classify Efficiency rules (Fast > 105, Slow < 95, Neutral 95-105)
eff_fast = filtered_df[filtered_df['Efficiency_%'] > 105]['Efficiency_%'].mean()
eff_slow = filtered_df[filtered_df['Efficiency_%'] < 95]['Efficiency_%'].mean()
eff_within = filtered_df[(filtered_df['Efficiency_%'] >= 95) & (filtered_df['Efficiency_%'] <= 105)]['Efficiency_%'].mean()

def format_hm(hours_float):
    if pd.isna(hours_float): return "0H 0M"
    h = int(abs(hours_float))
    m = int((abs(hours_float) - h) * 60)
    return f"{h}H {m}M"

# ==========================================
# 6. SECTION 1: KPI SUMMARY CARDS
# ==========================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

def build_html(*lines):
    return "".join(line.strip() for line in lines)

html_kpi1 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container"><span class="kpi-title">Net Hours</span><span class="kpi-icon">ℹ️</span></div>',
    '<div class="metric-row"><span class="metric-label">Gained</span><span class="metric-value text-green">15H 12M</span></div>',
    '<div class="metric-row"><span class="metric-label">Lost</span><span class="metric-value text-red">3H 5M</span></div>',
    '</div>'
)
kpi1.markdown(html_kpi1, unsafe_allow_html=True)

html_kpi2 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container"><span class="kpi-title">Net Shots</span><span class="kpi-icon">ℹ️</span></div>',
    '<div class="metric-row"><span class="metric-label">Gained</span><span class="metric-value text-green">12,553,725</span></div>',
    '<div class="metric-row"><span class="metric-label">Lost</span><span class="metric-value text-red">5,342,431</span></div>',
    '</div>'
)
kpi2.markdown(html_kpi2, unsafe_allow_html=True)

html_kpi3 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container"><span class="kpi-title">Net Financial</span><span class="kpi-icon">ℹ️</span></div>',
    '<div class="metric-row"><span class="metric-label">Financial Gain</span><span class="metric-value text-green">$1,688</span></div>',
    '<div class="metric-row"><span class="metric-label">Financial Loss</span><span class="metric-value text-red">-$1,712</span></div>',
    '</div>'
)
kpi3.markdown(html_kpi3, unsafe_allow_html=True)

html_kpi4 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container"><span class="kpi-title">Efficiency</span><span class="kpi-icon">ℹ️</span></div>',
    f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Fast</span><span class="metric-value text-green">{f"+{eff_fast:.2f}%" if pd.notna(eff_fast) else "N/A"}</span></div>',
    f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Slow</span><span class="metric-value text-red">{f"{eff_slow:.2f}%" if pd.notna(eff_slow) else "N/A"}</span></div>',
    f'<div class="metric-row"><span class="metric-label">Within</span><span class="metric-value text-neutral">{f"{eff_within:.2f}%" if pd.notna(eff_within) else "100%"}</span></div>',
    '</div>'
)
kpi4.markdown(html_kpi4, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. SECTION 2: MIXED PERFORMANCE ANALYTICS
# ==========================================
# Static Placeholder Data enforcing Classification Rules (Fast > 105%, Slow < 95%)
MOCK_DATA = {
    "Supplier": {
        "fast": [("Foxconn", 118.2), ("Jabil", 114.5), ("Flex", 109.1)],
        "slow": [("Sanmina", 76.4), ("Pegatron", 82.1), ("Celestica", 88.9)]
    },
    "Tooling Type": {
        "fast": [("Injection Molding", 115.8), ("High Pressure Die Casting", 112.3), ("Progressive Stamping", 108.7)],
        "slow": [("Thermoforming", 81.2), ("Blow Molding", 84.5), ("Vacuum Forming", 89.4)]
    },
    "Product": {
        "fast": [("Product X248", 121.0), ("Product X418", 116.4), ("Product X277", 107.5)],
        "slow": [("Product X620D", 78.3), ("Product V15", 83.9), ("Product V12", 89.1)]
    }
}

# --- Row 1: Supplier Performance (Ranked HTML Progress Bars) ---
with st.container(border=True):
    st.markdown('<div class="panel-title">Supplier Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Suppliers</div>', unsafe_allow_html=True)
        html_fast = []
        for name, eff in MOCK_DATA["Supplier"]["fast"]:
            bar_width = min(100, (eff / 125.0) * 100)
            html_fast.append(f"""
            <div class="rank-item">
                <div class="rank-text-row">
                    <span class="rank-name" title="{name}">{name}</span>
                    <span class="metric-value text-green">{eff:.1f}%</span>
                </div>
                <div class="bar-bg"><div class="bar-fill-green" style="width: {bar_width:.1f}%;"></div></div>
            </div>
            """.strip())
        st.markdown("".join(html_fast), unsafe_allow_html=True)
        
    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Suppliers</div>', unsafe_allow_html=True)
        html_slow = []
        for name, eff in MOCK_DATA["Supplier"]["slow"]:
            bar_width = min(100, (eff / 100.0) * 100)
            html_slow.append(f"""
            <div class="rank-item">
                <div class="rank-text-row">
                    <span class="rank-name" title="{name}">{name}</span>
                    <span class="metric-value text-red">{eff:.1f}%</span>
                </div>
                <div class="bar-bg"><div class="bar-fill-red" style="width: {bar_width:.1f}%;"></div></div>
            </div>
            """.strip())
        st.markdown("".join(html_slow), unsafe_allow_html=True)


# --- Row 2: Tooling Type Performance (Plotly Horizontal Bar Charts) ---
def build_plotly_bar(df, x_col, y_col, color, max_range):
    fig = px.bar(df, x=x_col, y=y_col, orientation='h', text=x_col)
    fig.update_traces(marker_color=color, texttemplate='%{text:.1f}%', textposition='outside', cliponaxis=False)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, visible=False, range=[0, max_range]),
        yaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)),
        margin=dict(l=0, r=40, t=10, b=10),
        height=180
    )
    return fig

with st.container(border=True):
    st.markdown('<div class="panel-title">Tooling Type Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    
    # Form DataFrames from Mock Data & sort ascending so highest value is at the top of the Plotly y-axis
    df_tool_fast = pd.DataFrame(MOCK_DATA["Tooling Type"]["fast"], columns=["Tooling Type", "Efficiency_%"]).sort_values("Efficiency_%", ascending=True)
    df_tool_slow = pd.DataFrame(MOCK_DATA["Tooling Type"]["slow"], columns=["Tooling Type", "Efficiency_%"]).sort_values("Efficiency_%", ascending=True)
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Tooling Types</div>', unsafe_allow_html=True)
        st.plotly_chart(build_plotly_bar(df_tool_fast, 'Efficiency_%', 'Tooling Type', '#5cb85c', 130), use_container_width=True, key="bar_fast")

    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Tooling Types</div>', unsafe_allow_html=True)
        st.plotly_chart(build_plotly_bar(df_tool_slow, 'Efficiency_%', 'Tooling Type', '#d9534f', 110), use_container_width=True, key="bar_slow")


# --- Row 3: Product Performance (Plotly Bubble/Scatter Charts) ---
def build_plotly_bubble(df, x_col, y_col, color, x_range):
    fig = px.scatter(df, x=x_col, y=y_col, size=x_col, text=x_col)
    fig.update_traces(
        marker_color=color, 
        texttemplate='%{text:.1f}%', 
        textposition='middle right', 
        marker=dict(line=dict(width=1.5, color='#ffffff'))
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#334155', title='Efficiency %', tickfont=dict(color='#94a3b8'), range=x_range),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='', tickfont=dict(color='#e2e8f0', size=13)),
        margin=dict(l=0, r=40, t=10, b=30),
        height=220
    )
    return fig

with st.container(border=True):
    st.markdown('<div class="panel-title">Product Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    
    df_prod_fast = pd.DataFrame(MOCK_DATA["Product"]["fast"], columns=["Product", "Efficiency_%"]).sort_values("Efficiency_%", ascending=True)
    df_prod_slow = pd.DataFrame(MOCK_DATA["Product"]["slow"], columns=["Product", "Efficiency_%"]).sort_values("Efficiency_%", ascending=True)
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Products</div>', unsafe_allow_html=True)
        st.plotly_chart(build_plotly_bubble(df_prod_fast, 'Efficiency_%', 'Product', '#5cb85c', [90, 140]), use_container_width=True, key="bubble_fast")

    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Products</div>', unsafe_allow_html=True)
        st.plotly_chart(build_plotly_bubble(df_prod_slow, 'Efficiency_%', 'Product', '#d9534f', [65, 100]), use_container_width=True, key="bubble_slow")