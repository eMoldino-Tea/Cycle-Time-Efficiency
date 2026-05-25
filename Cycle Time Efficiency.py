import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import textwrap

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Cycle Time Efficiency V3",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Strict Operational Tolerance Color Logic
COLOR_MAP = {
    "Below Tolerance": "#00CC96", # Green mapping for dashboards (Fast/Positive)
    "Within Tolerance": "#0f172a", # Black/Neutral
    "Above Tolerance": "#FF4B4B"   # Red mapping for dashboards (Slow/Negative)
}

# High-Contrast, Enterprise CSS tailored for Power BI / Tableau aesthetic
# Note: Flush-left alignment is required so Streamlit doesn't parse this as a code block.
st.markdown("""
<style>
/* Force Enterprise Background for the App */
.stApp {
    background-color: #f5f6f8;
}

/* Hide Streamlit Header */
header {visibility: hidden;}

/* Dashboard KPI & Panel Cards */
.dash-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    border: 1px solid #f1f5f9;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    color: #334155;
    height: 100%;
}
.dash-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* KPI Card Specifics */
.kpi-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 20px;
    font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.kpi-icon {
    color: #94a3b8;
    font-size: 1.2rem;
    font-weight: 400;
}
.kpi-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-size: 1rem;
    font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.kpi-row:last-child {
    margin-bottom: 0;
}
.kpi-label {
    color: #64748b;
    font-weight: 600;
}
.kpi-val {
    font-weight: 700;
}

/* Text Colors */
.text-green { color: #00CC96 !important; }
.text-red { color: #FF4B4B !important; }
.text-black { color: #0f172a !important; }

/* Clean Divider */
hr {
    margin-top: 1rem;
    margin-bottom: 1rem;
    border-color: rgba(128, 128, 128, 0.2);
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING & BASE LOGIC
# ==========================================
@st.cache_data
def load_base_data():
    """
    Generates core mock data WITHOUT financial impact. 
    Financial impact is calculated dynamically based on UI inputs.
    """
    np.random.seed(42)
    n_rows = 2500
    
    data = pd.DataFrame({
        'Date': [datetime.today() - timedelta(days=int(x)) for x in np.random.randint(0, 90, n_rows)],
        'OEM Business Division': np.random.choice(['NA Auto', 'EU Consumer', 'APAC Enterprise', 'LATAM Industrial'], n_rows),
        'Supplier': np.random.choice(['Supplier Alpha', 'Supplier Beta', 'Supplier Gamma', 'Supplier Delta', 'Supplier Epsilon'], n_rows),
        'Toolmaker': np.random.choice(['TM-A', 'TM-B', 'TM-C', 'TM-D'], n_rows),
        'Plant': np.random.choice(['Plant 1 (MX)', 'Plant 2 (DE)', 'Plant 3 (CN)', 'Plant 4 (VN)'], n_rows),
        'Commodity': np.random.choice(['Injection Molding', 'Stamping', 'Die Casting'], n_rows),
        'Product': np.random.choice(['Product X248', 'Product X277', 'Product X418', 'Product X620D'], n_rows),
        'Tooling': [f"TL-{np.random.randint(1000, 9999)}" for _ in range(n_rows)],
        'ACT': np.random.uniform(15.0, 60.0, n_rows),
        'Total_Shots': np.random.randint(5000, 50000, n_rows)
    })
    
    commodity_part_map = {
        'Injection Molding': ['Housing-A', 'Main Body X620D', 'Brush Housing', 'Filter Chamber'],
        'Stamping': ['Metal-Base', 'Vortex Plate', 'Soleplate', 'End Cap'],
        'Die Casting': ['Engine-Block', 'Drive Housing', 'Manifold', 'Motor Bucket']
    }
    data['Part'] = data.apply(lambda row: np.random.choice(commodity_part_map[row['Commodity']]), axis=1)

    variance_multiplier = np.random.normal(1.0, 0.08, n_rows)
    data['Actual_CT'] = data['ACT'] * variance_multiplier
    
    # 1. Expected vs Used Machine Hours
    data['Expected_Hours'] = (data['ACT'] * data['Total_Shots']) / 3600
    data['Used_Hours'] = (data['Actual_CT'] * data['Total_Shots']) / 3600
    data['Hours_Diff'] = data['Expected_Hours'] - data['Used_Hours']
    
    # 2. Shot Classification (Tolerance Band: 5%)
    def categorize_shot(row):
        if row['Actual_CT'] < (row['ACT'] * 0.95):
            return "Below Tolerance"
        elif row['Actual_CT'] > (row['ACT'] * 1.05):
            return "Above Tolerance"
        else:
            return "Within Tolerance"
            
    data['Tolerance_Status'] = data.apply(categorize_shot, axis=1)
    
    # 3. Gain / Loss Hours
    data['Gain_Hours'] = np.where(data['Tolerance_Status'] == 'Below Tolerance', data['Hours_Diff'], 0)
    data['Loss_Hours'] = np.where(data['Tolerance_Status'] == 'Above Tolerance', -data['Hours_Diff'], 0)
    
    # 4. Gained / Lost Shots
    data['Shots_Gained'] = np.where(data['ACT'] > 0, (data['Gain_Hours'] * 3600) / data['ACT'], 0)
    data['Shots_Lost'] = np.where(data['ACT'] > 0, (data['Loss_Hours'] * 3600) / data['ACT'], 0)
    
    # 5. Efficiency & Variance
    data['Efficiency_%'] = (data['Expected_Hours'] / data['Used_Hours']) * 100
    data['Variance_%'] = ((data['Actual_CT'] - data['ACT']) / data['ACT']) * 100
    
    return data

df = load_base_data()

# ==========================================
# 3. GLOBAL MASTER FILTER & FINANCIAL INPUTS
# ==========================================
st.sidebar.markdown("### Financial Parameters")
labor_rate = st.sidebar.number_input("Labor Rate ($/hour)", min_value=0.0, value=40.0, step=1.0)
machine_rate = st.sidebar.number_input("Machine Rate ($/hour)", min_value=0.0, value=180.0, step=1.0)
combined_rate = labor_rate + machine_rate

# Dynamically apply financial logic based on sidebar inputs
df['Financial_Gain'] = df['Gain_Hours'] * combined_rate
df['Financial_Loss'] = df['Loss_Hours'] * combined_rate
df['Net_Financial'] = df['Financial_Gain'] - df['Financial_Loss']

st.sidebar.markdown("---")
st.sidebar.markdown("### Master Filter")

oem_options = df['OEM Business Division'].unique()
selected_oem = st.sidebar.multiselect("OEM Business Division", options=oem_options)
filtered_df = df[df['OEM Business Division'].isin(selected_oem)] if selected_oem else df

supplier_options = filtered_df['Supplier'].unique()
selected_supplier = st.sidebar.multiselect("Supplier", options=supplier_options)
filtered_df = filtered_df[filtered_df['Supplier'].isin(selected_supplier)] if selected_supplier else filtered_df

toolmaker_options = filtered_df['Toolmaker'].unique()
selected_toolmaker = st.sidebar.multiselect("Toolmaker", options=toolmaker_options)
filtered_df = filtered_df[filtered_df['Toolmaker'].isin(selected_toolmaker)] if selected_toolmaker else filtered_df

plant_options = filtered_df['Plant'].unique()
selected_plant = st.sidebar.multiselect("Plant", options=plant_options)
filtered_df = filtered_df[filtered_df['Plant'].isin(selected_plant)] if selected_plant else filtered_df

product_options = filtered_df['Product'].unique()
selected_product = st.sidebar.multiselect("Product", options=product_options)
filtered_df = filtered_df[filtered_df['Product'].isin(selected_product)] if selected_product else filtered_df

part_options = filtered_df['Part'].unique()
selected_part = st.sidebar.multiselect("Part", options=part_options)
filtered_df = filtered_df[filtered_df['Part'].isin(selected_part)] if selected_part else filtered_df

tooling_options = filtered_df['Tooling'].unique()
selected_tooling = st.sidebar.multiselect("Tooling", options=tooling_options)
filtered_df = filtered_df[filtered_df['Tooling'].isin(selected_tooling)] if selected_tooling else filtered_df

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ==========================================
# 4. DASHBOARD TABS
# ==========================================
tab_summary, tab_below, tab_above, tab_within = st.tabs([
    "Summary Dashboard", 
    "Below Tolerance Analysis", 
    "Above Tolerance Analysis", 
    "Within Tolerance Analysis"
])

# ------------------------------------------
# HELPER FUNCTION: RENDER ANALYSIS TABS (TABS 2-4)
# ------------------------------------------
def render_analysis_tab(global_filtered_df, data_subset, tolerance_label, metric_col_gain_loss, cost_col_gain_loss):
    if data_subset.empty:
        st.write(f"No products operating {tolerance_label.lower()} based on current filters.")
        return

    col1, col2, col3, col4 = st.columns(4)
    avg_variance = data_subset['Variance_%'].mean()
    total_hours = data_subset[metric_col_gain_loss].sum() if metric_col_gain_loss else 0
    total_cost = data_subset[cost_col_gain_loss].sum() if cost_col_gain_loss else 0
    
    col1.metric("Tools Flagged", len(data_subset['Tooling'].unique()))
    col2.metric("Average Variance", f"{avg_variance:+.2f}%")
    if metric_col_gain_loss:
        col3.metric("Total Hours Impact", f"{total_hours:,.1f} h")
    if cost_col_gain_loss:
        col4.metric("Financial Impact", f"${total_cost:,.0f}")

    st.markdown("---")
    st.subheader("Trend Stability Analysis")
    
    max_date = data_subset['Date'].max()
    d7_data = data_subset[data_subset['Date'] >= max_date - timedelta(days=7)]
    d30_data = data_subset[data_subset['Date'] >= max_date - timedelta(days=30)]
    
    d7_trend = d7_data['Variance_%'].mean() if not d7_data.empty else 0
    d30_trend = d30_data['Variance_%'].mean() if not d30_data.empty else 0
    
    std_dev = data_subset['Variance_%'].std()
    std_dev = 0 if pd.isna(std_dev) else std_dev
    stability_score = max(0, min(100, 100 - (std_dev * 5))) 
    consistency = "High" if stability_score >= 80 else "Medium" if stability_score >= 50 else "Low"

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    t_col1.metric("7-Day Trend (Avg Variance)", f"{d7_trend:+.2f}%")
    t_col2.metric("30-Day Trend (Avg Variance)", f"{d30_trend:+.2f}%")
    t_col3.metric("Stability Score", f"{stability_score:.0f}/100")
    t_col4.metric("Consistency Indicator", consistency)

    trend_grouping = st.selectbox("View historical trend by:", ["Supplier", "Product", "Plant", "Toolmaker"], key=f"trend_grp_{tolerance_label}")
    unique_entities = data_subset[trend_grouping].dropna().unique().tolist()
    top_entities = data_subset[trend_grouping].value_counts().head(3).index.tolist()
    
    selected_trend_entities = st.multiselect(
        f"Select specific {trend_grouping}(s) to display:",
        options=unique_entities,
        default=top_entities,
        key=f"trend_sel_{tolerance_label}"
    )

    if selected_trend_entities:
        filtered_trend_data = data_subset[data_subset[trend_grouping].isin(selected_trend_entities)]
        trend_data = filtered_trend_data.groupby(['Date', trend_grouping])['Variance_%'].mean().reset_index()
        fig_trend = px.bar(trend_data, x='Date', y='Variance_%', color=trend_grouping, barmode='group')
        fig_trend.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), yaxis_title="Variance from ACT (%)", xaxis_title="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""), hovermode="x unified")
        st.plotly_chart(fig_trend, use_container_width=True, key=f"trend_chart_{tolerance_label}")
    else:
        st.info("Please select at least one entity to display the trend graph.")

    st.markdown("---")
    st.subheader("Benchmark Context")
    perspective = st.radio("Select Benchmark Perspective:", ["Commodity Perspective", "Part Perspective", "Supplier Perspective"], horizontal=True, key=f"perspective_{tolerance_label}")
    
    perspective_col = "Commodity" if perspective == "Commodity Perspective" else "Part" if perspective == "Part Perspective" else "Supplier"
    benchmark_df = global_filtered_df.groupby(perspective_col).agg({'Efficiency_%': 'mean'}).reset_index()
    
    best_peer_idx = benchmark_df['Efficiency_%'].idxmax()
    best_peer = benchmark_df.loc[best_peer_idx, perspective_col]
    median_eff = benchmark_df['Efficiency_%'].median()
    
    global_supplier_avg = global_filtered_df['Efficiency_%'].mean()
    global_commodity_avg = global_filtered_df['Efficiency_%'].mean()
    
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    b_col1.metric("Best Performing Peer", best_peer)
    b_col2.metric("Median Benchmark", f"{median_eff:.1f}%")
    b_col3.metric("Global Supplier Average", f"{global_supplier_avg:.1f}%")
    b_col4.metric("Global Commodity Average", f"{global_commodity_avg:.1f}%")

    fig_bench = px.bar(benchmark_df.sort_values('Efficiency_%', ascending=True), x='Efficiency_%', y=perspective_col, orientation='h')
    fig_bench.update_traces(marker_color='#3b82f6')
    fig_bench.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Average Efficiency (%)", yaxis_title="")
    st.plotly_chart(fig_bench, use_container_width=True, key=f"bench_chart_{tolerance_label}")

    st.markdown("---")
    st.subheader("Detailed Drill-Through")
    drill_target = st.selectbox("Select Tooling for Operational Drill-Through:", options=data_subset['Tooling'].unique(), key=f"drill_{tolerance_label}")
    
    if drill_target:
        tool_data = data_subset[data_subset['Tooling'] == drill_target].sort_values('Date')
        st.markdown(f"**Operational Analysis: {drill_target}**")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            fig_tool_trend = px.line(tool_data, x='Date', y='Actual_CT', title="Historical Cycle Time Trend", markers=True)
            fig_tool_trend.add_hline(y=tool_data['ACT'].iloc[0], line_dash="dash", line_color="rgba(128,128,128,0.5)", annotation_text="Approved CT")
            fig_tool_trend.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_tool_trend, use_container_width=True, key=f"tool_trend_{tolerance_label}")
        with d_col2:
            color_m = {"Below Tolerance": "#FF4B4B", "Within Tolerance": "#00CC96", "Above Tolerance": "#FFAA00"}
            fig_tool_var = px.bar(tool_data, x='Date', y='Variance_%', title="Cycle Variance per Run", color='Tolerance_Status', color_discrete_map=color_m)
            fig_tool_var.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_tool_var, use_container_width=True, key=f"tool_var_{tolerance_label}")
            
        st.markdown("**Production Runs History**")
        st.dataframe(tool_data[['Date', 'Product', 'Part', 'Supplier', 'ACT', 'Actual_CT', 'Total_Shots', 'Variance_%', 'Tolerance_Status', 'Efficiency_%']].sort_values('Date', ascending=False), use_container_width=True)

# ------------------------------------------
# TAB 1: MACRO SUMMARY DASHBOARD
# ------------------------------------------
with tab_summary:
    # ----------------------------------------------------
    # SECTION 1: KPI SUMMARY WIDGETS
    # ----------------------------------------------------
    # Pre-calculate Metrics
    gained_hrs = filtered_df['Gain_Hours'].sum()
    lost_hrs = filtered_df['Loss_Hours'].sum()
    
    gained_shots = filtered_df['Shots_Gained'].sum()
    lost_shots = filtered_df['Shots_Lost'].sum()
    
    gained_fin = filtered_df['Financial_Gain'].sum()
    lost_fin = filtered_df['Financial_Loss'].sum()
    
    eff_fast = filtered_df[filtered_df['Tolerance_Status'] == 'Below Tolerance']['Efficiency_%'].mean()
    eff_slow = filtered_df[filtered_df['Tolerance_Status'] == 'Above Tolerance']['Efficiency_%'].mean()
    eff_within = filtered_df[filtered_df['Tolerance_Status'] == 'Within Tolerance']['Efficiency_%'].mean()

    # Formatter for hours/minutes layout
    def format_hm(hours_float):
        if pd.isna(hours_float): return "0H 0M"
        h = int(abs(hours_float))
        m = int((abs(hours_float) - h) * 60)
        return f"{h}H {m}M"
    
    # Clean HTML construction (no deep indents to prevent Markdown code-block parsing)
    kpi_html = f"""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; margin-bottom: 32px; margin-top: 10px;">
    <div class="dash-card">
        <div class="kpi-title">Net Hours <span class="kpi-icon">&#9432;</span></div>
        <div class="kpi-row">
            <span class="kpi-label">Gained</span>
            <span class="kpi-val text-green">{format_hm(gained_hrs)}</span>
        </div>
        <div class="kpi-row">
            <span class="kpi-label">Lost</span>
            <span class="kpi-val text-red">{format_hm(lost_hrs)}</span>
        </div>
    </div>
    <div class="dash-card">
        <div class="kpi-title">Net Shots <span class="kpi-icon">&#9432;</span></div>
        <div class="kpi-row">
            <span class="kpi-label">Gained</span>
            <span class="kpi-val text-green">{int(gained_shots):,}</span>
        </div>
        <div class="kpi-row">
            <span class="kpi-label">Lost</span>
            <span class="kpi-val text-red">{int(lost_shots):,}</span>
        </div>
    </div>
    <div class="dash-card">
        <div class="kpi-title">Net Financial <span class="kpi-icon">&#9432;</span></div>
        <div class="kpi-row">
            <span class="kpi-label">Financial Gain</span>
            <span class="kpi-val text-green">${gained_fin:,.0f}</span>
        </div>
        <div class="kpi-row">
            <span class="kpi-label">Financial Loss</span>
            <span class="kpi-val text-red">-${lost_fin:,.0f}</span>
        </div>
    </div>
    <div class="dash-card">
        <div class="kpi-title">Efficiency <span class="kpi-icon">&#9432;</span></div>
        <div class="kpi-row">
            <span class="kpi-label">Fast</span>
            <span class="kpi-val text-green">{f"+{eff_fast:.2f}%" if pd.notna(eff_fast) else "N/A"}</span>
        </div>
        <div class="kpi-row">
            <span class="kpi-label">Slow</span>
            <span class="kpi-val text-red">{f"-{eff_slow:.2f}%" if pd.notna(eff_slow) else "N/A"}</span>
        </div>
        <div class="kpi-row">
            <span class="kpi-label">Within</span>
            <span class="kpi-val text-black">{f"{eff_within:.2f}%" if pd.notna(eff_within) else "N/A"}</span>
        </div>
    </div>
</div>
"""
    st.markdown(kpi_html, unsafe_allow_html=True)
    
    # ----------------------------------------------------
    # SECTION 2: PERFORMANCE ANALYSIS (PANELS)
    # ----------------------------------------------------
    
    def generate_panel_html(df, group_col, title):
        grouped = df.groupby(group_col)['Efficiency_%'].mean().reset_index()
        grouped = grouped.dropna(subset=['Efficiency_%'])
        
        fastest = grouped.sort_values('Efficiency_%', ascending=False).head(5)
        slowest = grouped.sort_values('Efficiency_%', ascending=True).head(5)
        
        max_fast = fastest['Efficiency_%'].max() if not fastest.empty else 100
        max_slow = slowest['Efficiency_%'].max() if not slowest.empty else 100
        
        # Built securely without indents to bypass the Streamlit markdown parsing bug
        html_parts = []
        html_parts.append('<div class="dash-card">')
        html_parts.append(f'<div style="font-size:1.15rem; font-weight:700; color:#1e293b; margin-bottom: 24px; font-family:\'Segoe UI\', sans-serif;">{title}</div>')
        html_parts.append('<div style="display:flex; gap:32px; flex: 1;">')
        
        # Fastest Side
        html_parts.append('<div style="flex:1; display:flex; flex-direction:column;">')
        html_parts.append('<div style="color:#00CC96; font-weight:700; font-size:0.8rem; margin-bottom:16px; border-bottom:1px solid #e2e8f0; padding-bottom:8px; text-transform:uppercase; letter-spacing:0.5px;">Top 5 Fastest</div>')
        
        for _, row in fastest.iterrows():
            name = row[group_col]
            eff = row['Efficiency_%']
            bar_w = min(100, (eff / (max_fast + 0.001)) * 100)
            html_parts.append('<div style="margin-bottom:16px;">')
            html_parts.append(f'<div style="display:flex; justify-content:space-between; margin-bottom:6px; font-size:0.9rem; font-family:\'Segoe UI\', sans-serif;"><span style="color:#475569; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;" title="{name}">{name}</span><span class="text-green" style="font-weight:700;">{eff:.1f}%</span></div>')
            html_parts.append(f'<div style="width:100%; background-color:#f1f5f9; height:6px; border-radius:3px;"><div style="width: {bar_w}%; background-color:#00CC96; height:100%; border-radius:3px;"></div></div>')
            html_parts.append('</div>')
            
        html_parts.append('</div>')
        
        # Slowest Side
        html_parts.append('<div style="flex:1; display:flex; flex-direction:column;">')
        html_parts.append('<div style="color:#FF4B4B; font-weight:700; font-size:0.8rem; margin-bottom:16px; border-bottom:1px solid #e2e8f0; padding-bottom:8px; text-transform:uppercase; letter-spacing:0.5px;">Top 5 Slowest</div>')
        
        for _, row in slowest.iterrows():
            name = row[group_col]
            eff = row['Efficiency_%']
            bar_w = min(100, (eff / (max_slow + 0.001)) * 100)
            html_parts.append('<div style="margin-bottom:16px;">')
            html_parts.append(f'<div style="display:flex; justify-content:space-between; margin-bottom:6px; font-size:0.9rem; font-family:\'Segoe UI\', sans-serif;"><span style="color:#475569; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;" title="{name}">{name}</span><span class="text-red" style="font-weight:700;">{eff:.1f}%</span></div>')
            html_parts.append(f'<div style="width:100%; background-color:#f1f5f9; height:6px; border-radius:3px;"><div style="width: {bar_w}%; background-color:#FF4B4B; height:100%; border-radius:3px;"></div></div>')
            html_parts.append('</div>')
            
        html_parts.append('</div></div></div>')
        return "".join(html_parts)

    # Render Grid Panels
    col_supp, col_tool, col_prod = st.columns(3)
    
    with col_supp:
        st.markdown(generate_panel_html(filtered_df, 'Supplier', 'Supplier Performance'), unsafe_allow_html=True)
        
    with col_tool:
        st.markdown(generate_panel_html(filtered_df, 'Commodity', 'Tooling Type Performance'), unsafe_allow_html=True)
        
    with col_prod:
        st.markdown(generate_panel_html(filtered_df, 'Product', 'Product Performance'), unsafe_allow_html=True)


# ------------------------------------------
# TAB 2: BELOW TOLERANCE ANALYSIS
# ------------------------------------------
with tab_below:
    below_df = filtered_df[filtered_df['Tolerance_Status'] == 'Below Tolerance'].copy()
    render_analysis_tab(
        global_filtered_df=filtered_df,
        data_subset=below_df, 
        tolerance_label="Below Tolerance", 
        metric_col_gain_loss="Gain_Hours", 
        cost_col_gain_loss="Financial_Gain"
    )

# ------------------------------------------
# TAB 3: ABOVE TOLERANCE ANALYSIS
# ------------------------------------------
with tab_above:
    above_df = filtered_df[filtered_df['Tolerance_Status'] == 'Above Tolerance'].copy()
    render_analysis_tab(
        global_filtered_df=filtered_df,
        data_subset=above_df, 
        tolerance_label="Above Tolerance", 
        metric_col_gain_loss="Loss_Hours", 
        cost_col_gain_loss="Financial_Loss"
    )

# ------------------------------------------
# TAB 4: WITHIN TOLERANCE ANALYSIS
# ------------------------------------------
with tab_within:
    within_df = filtered_df[filtered_df['Tolerance_Status'] == 'Within Tolerance'].copy()
    render_analysis_tab(
        global_filtered_df=filtered_df,
        data_subset=within_df, 
        tolerance_label="Within Tolerance", 
        metric_col_gain_loss=None,
        cost_col_gain_loss=None
    )