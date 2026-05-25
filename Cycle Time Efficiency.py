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

/* Ranking Items & Progress Bars */
.rank-item {
    margin-bottom: 16px;
}
.rank-text-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    font-size: 0.95rem;
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
# 3. DATA LOADING & PROCESSING
# ==========================================
@st.cache_data
def load_base_data():
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

    def get_base_mult(row):
        mult = 1.0
        # Systematic biases to push group averages into >105% and <95% thresholds
        
        # Suppliers
        if row['Supplier'] in ['Foxconn', 'Jabil', 'Flex']: mult -= 0.15
        elif row['Supplier'] in ['Sanmina', 'Pegatron', 'Celestica']: mult += 0.15
        
        # Tooling Types
        if row['Tooling Type'] in ['Injection Molding', 'High Pressure Die Casting', 'Progressive Stamping']: mult -= 0.12
        elif row['Tooling Type'] in ['Thermoforming', 'Blow Molding', 'Vacuum Forming']: mult += 0.12
        
        # Products
        if row['Product'] in ['Product X248', 'Product X277', 'Product X418']: mult -= 0.12
        elif row['Product'] in ['Product X620D', 'Product V15', 'Product V12']: mult += 0.12
        
        return mult
        
    base_mult = data.apply(get_base_mult, axis=1)
    variance_multiplier = np.random.normal(base_mult, 0.05)
    variance_multiplier = np.clip(variance_multiplier, 0.4, 2.0)
    
    data['Actual_CT'] = data['ACT'] * variance_multiplier
    
    data['Expected_Hours'] = (data['ACT'] * data['Total_Shots']) / 3600
    data['Used_Hours'] = (data['Actual_CT'] * data['Total_Shots']) / 3600
    data['Hours_Diff'] = data['Expected_Hours'] - data['Used_Hours']
    data['Efficiency_%'] = (data['Expected_Hours'] / data['Used_Hours']) * 100
    
    def categorize_shot(row):
        if row['Efficiency_%'] > 105: return "Fast"
        elif row['Efficiency_%'] < 95: return "Slow"
        else: return "Neutral"
            
    data['Tolerance_Status'] = data.apply(categorize_shot, axis=1)
    
    data['Gain_Hours'] = np.where(data['Tolerance_Status'] == 'Fast', data['Hours_Diff'], 0)
    data['Loss_Hours'] = np.where(data['Tolerance_Status'] == 'Slow', -data['Hours_Diff'], 0)
    
    data['Shots_Gained'] = np.where(data['ACT'] > 0, (data['Gain_Hours'] * 3600) / data['ACT'], 0)
    data['Shots_Lost'] = np.where(data['ACT'] > 0, (data['Loss_Hours'] * 3600) / data['ACT'], 0)
    
    return data

df = load_base_data()

# ==========================================
# 4. SIDEBAR FILTERS & FINANCIALS
# ==========================================
st.sidebar.markdown("### Financial Parameters")
labor_rate = st.sidebar.number_input("Labor Rate ($/hour)", min_value=0.0, value=40.0, step=1.0)
machine_rate = st.sidebar.number_input("Machine Rate ($/hour)", min_value=0.0, value=180.0, step=1.0)
combined_rate = labor_rate + machine_rate

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

eff_fast = filtered_df[filtered_df['Tolerance_Status'] == 'Fast']['Efficiency_%'].mean()
eff_slow = filtered_df[filtered_df['Tolerance_Status'] == 'Slow']['Efficiency_%'].mean()
eff_within = filtered_df[filtered_df['Tolerance_Status'] == 'Neutral']['Efficiency_%'].mean()

def format_hm(hours_float):
    if pd.isna(hours_float): return "0H 0M"
    h = int(abs(hours_float))
    m = int((abs(hours_float) - h) * 60)
    return f"{h}H {m}M"

def build_html(*lines):
    return "".join(line.strip() for line in lines)

# ==========================================
# 6. SECTION 1: KPI SUMMARY CARDS
# ==========================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

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

st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)


# ==========================================
# 7. SECTION 2: PERFORMANCE ANALYTICS
# ==========================================
def get_aggregated_stats(df, category):
    grouped = df.groupby(category)['Efficiency_%'].mean().reset_index()
    fast_df = grouped[grouped['Efficiency_%'] > 105].sort_values('Efficiency_%', ascending=False).head(3)
    slow_df = grouped[grouped['Efficiency_%'] < 95].sort_values('Efficiency_%', ascending=True).head(3)
    return fast_df, slow_df

# --- ROW 1: SUPPLIER PERFORMANCE (HTML PROGRESS BARS) ---
with st.container(border=True):
    st.markdown('<div class="panel-title">Supplier Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    
    supp_fast, supp_slow = get_aggregated_stats(filtered_df, 'Supplier')
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Suppliers</div>', unsafe_allow_html=True)
        html_fast = []
        if not supp_fast.empty:
            for _, row in supp_fast.iterrows():
                name, eff = row['Supplier'], row['Efficiency_%']
                bar_width = min(100, (eff / 130.0) * 100)
                html_fast.append(f"""
                <div class="rank-item">
                    <div class="rank-text-row">
                        <span class="rank-name" title="{name}">{name}</span>
                        <span class="metric-value text-green" title="Cycle Time Efficiency %">{eff:.1f}%</span>
                    </div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: {bar_width:.1f}%;"></div></div>
                </div>
                """.strip())
            st.markdown("".join(html_fast), unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #64748b;'>No suppliers performing >105% Efficiency.</span>", unsafe_allow_html=True)
        
    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Suppliers</div>', unsafe_allow_html=True)
        html_slow = []
        if not supp_slow.empty:
            for _, row in supp_slow.iterrows():
                name, eff = row['Supplier'], row['Efficiency_%']
                bar_width = min(100, (eff / 100.0) * 100)
                html_slow.append(f"""
                <div class="rank-item">
                    <div class="rank-text-row">
                        <span class="rank-name" title="{name}">{name}</span>
                        <span class="metric-value text-red" title="Cycle Time Efficiency %">{eff:.1f}%</span>
                    </div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: {bar_width:.1f}%;"></div></div>
                </div>
                """.strip())
            st.markdown("".join(html_slow), unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #64748b;'>No suppliers performing <95% Efficiency.</span>", unsafe_allow_html=True)


# --- ROW 2: TOOLING TYPE PERFORMANCE (PLOTLY HORIZONTAL BAR CHARTS) ---
def build_plotly_bar(df, x_col, y_col, color, max_range):
    if df.empty: return None
    df_sorted = df.sort_values(x_col, ascending=True)
    fig = px.bar(df_sorted, x=x_col, y=y_col, orientation='h', text=x_col)
    fig.update_traces(
        marker_color=color, 
        texttemplate='%{text:.1f}%', 
        textposition='outside', 
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Cycle Time Efficiency %: %{x:.1f}%<extra></extra>"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Cycle Time Efficiency %",
        xaxis=dict(showgrid=False, visible=True, range=[0, max_range], title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8')),
        yaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)),
        margin=dict(l=0, r=40, t=10, b=30),
        height=220
    )
    return fig

with st.container(border=True):
    st.markdown('<div class="panel-title">Tooling Type Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    
    tool_fast, tool_slow = get_aggregated_stats(filtered_df, 'Tooling Type')
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Tooling Types</div>', unsafe_allow_html=True)
        fig_fast = build_plotly_bar(tool_fast, 'Efficiency_%', 'Tooling Type', '#5cb85c', 140)
        if fig_fast: st.plotly_chart(fig_fast, use_container_width=True, key="bar_fast")
        else: st.markdown("<span style='color: #64748b;'>No tooling types >105% Efficiency.</span>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Tooling Types</div>', unsafe_allow_html=True)
        fig_slow = build_plotly_bar(tool_slow, 'Efficiency_%', 'Tooling Type', '#d9534f', 110)
        if fig_slow: st.plotly_chart(fig_slow, use_container_width=True, key="bar_slow")
        else: st.markdown("<span style='color: #64748b;'>No tooling types <95% Efficiency.</span>", unsafe_allow_html=True)


# --- ROW 3: PRODUCT PERFORMANCE (PLOTLY BUBBLE CHARTS) ---
def build_plotly_bubble(df, x_col, y_col, color, x_range):
    if df.empty: return None
    df['Bubble_Size'] = 1
    fig = px.scatter(df, x=x_col, y=y_col, size='Bubble_Size', text=x_col)
    fig.update_traces(
        marker_color=color, 
        texttemplate='%{text:.1f}%', 
        textposition='middle right', 
        marker=dict(line=dict(width=1.5, color='#ffffff'), sizeref=0.05),
        hovertemplate="<b>%{y}</b><br>Cycle Time Efficiency %: %{x:.1f}%<extra></extra>"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Cycle Time Efficiency %",
        xaxis=dict(showgrid=True, gridcolor='#334155', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8'), range=x_range),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='', tickfont=dict(color='#e2e8f0', size=13)),
        margin=dict(l=0, r=40, t=10, b=40),
        height=240,
        showlegend=False
    )
    return fig

with st.container(border=True):
    st.markdown('<div class="panel-title">Product Performance</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    
    prod_fast, prod_slow = get_aggregated_stats(filtered_df, 'Product')
    
    with col_left:
        st.markdown('<div class="col-header text-green">Top 3 Fastest Products</div>', unsafe_allow_html=True)
        fig_pfast = build_plotly_bubble(prod_fast, 'Efficiency_%', 'Product', '#5cb85c', [90, 140])
        if fig_pfast: st.plotly_chart(fig_pfast, use_container_width=True, key="bubble_fast")
        else: st.markdown("<span style='color: #64748b;'>No products >105% Efficiency.</span>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="col-header text-red">Top 3 Slowest Products</div>', unsafe_allow_html=True)
        fig_pslow = build_plotly_bubble(prod_slow, 'Efficiency_%', 'Product', '#d9534f', [60, 105])
        if fig_pslow: st.plotly_chart(fig_pslow, use_container_width=True, key="bubble_slow")
        else: st.markdown("<span style='color: #64748b;'>No products <95% Efficiency.</span>", unsafe_allow_html=True)


# ==========================================
# 8. SECTION 3: INTERACTIVE DRILL-DOWN ANALYSIS
# ==========================================
st.markdown('<div class="section-title">Interactive Drill-Down Analysis</div>', unsafe_allow_html=True)

# Simulated Click Interaction for Streamlit UI constraint
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
    
    st.markdown(f"### Drill-Down Details: `{drill_target}`")
    
    # Filter drill-down logic based on selection type
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
        # If a global widget is selected, show global drill-down
        df_drill = filtered_df.copy()
    
    drill_eff = df_drill['Efficiency_%'].mean()
    drill_gain_h = df_drill['Gain_Hours'].sum()
    drill_loss_h = df_drill['Loss_Hours'].sum()
    drill_net_fin = df_drill['Financial_Gain'].sum() - df_drill['Financial_Loss'].sum()
    
    dkpi1, dkpi2, dkpi3, dkpi4 = st.columns(4)
    dkpi1.metric("Overall Cycle Time Efficiency %", f"{drill_eff:.1f}%")
    dkpi2.metric("Total Hours Gained (Fast)", format_hm(drill_gain_h))
    dkpi3.metric("Total Hours Lost (Slow)", format_hm(drill_loss_h))
    dkpi4.metric("Savings Opportunity (Net)", f"${drill_net_fin:,.0f}")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    t_col1, t_col2 = st.columns(2, gap="large")
    with t_col1:
        st.markdown("**Historical Trend: Cycle Time Efficiency % over Time**")
        trend_df = df_drill.groupby('Date')['Efficiency_%'].mean().reset_index()
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
    display_df.rename(columns={'ACT': 'Approved CT (s)', 'Actual_CT': 'Actual CT (s)', 'Efficiency_%': 'Cycle Time Efficiency %', 'Tolerance_Status': 'Status'}, inplace=True)
    display_df = display_df.sort_values(by='Date', ascending=False)
    
    st.dataframe(
        display_df.style.format({
            'Approved CT (s)': "{:.1f}", 
            'Actual CT (s)': "{:.1f}", 
            'Cycle Time Efficiency %': "{:.1f}%",
            'Financial_Gain': "${:.0f}",
            'Financial_Loss': "${:.0f}"
        }), 
        use_container_width=True,
        hide_index=True
    )