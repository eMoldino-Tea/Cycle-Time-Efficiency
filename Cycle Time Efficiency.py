import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Cycle Time Efficiency V3",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Strict Operational Tolerance Color Logic (V3 Requirement)
# Applied to charts/visuals, hidden from text/UI explanations
COLOR_MAP = {
    "Below Tolerance": "#FF4B4B",
    "Within Tolerance": "#00CC96",
    "Above Tolerance": "#FFAA00"
}

# Clean, Enterprise CSS without decorative elements
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 12px;
        box-shadow: none;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 600;
        color: #333333;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #666666;
    }
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING & AI TEAM LOGIC
# ==========================================
@st.cache_data
def load_and_process_data():
    """
    Generates mock data and applies the 'AI Team Calculation Logic'.
    In production, replace the generation block with your Snowflake/DB query.
    """
    np.random.seed(42)
    n_rows = 2500
    
    # Generate Base Data to reflect the documents & new filter requirements
    data = pd.DataFrame({
        'Date': [datetime.today() - timedelta(days=int(x)) for x in np.random.randint(0, 90, n_rows)],
        'OEM Business Division': np.random.choice(['NA Auto', 'EU Consumer', 'APAC Enterprise', 'LATAM Industrial'], n_rows),
        'Supplier': np.random.choice(['Supplier Alpha', 'Supplier Beta', 'Supplier Gamma', 'Supplier Delta', 'Supplier Epsilon'], n_rows),
        'Toolmaker': np.random.choice(['TM-A', 'TM-B', 'TM-C', 'TM-D'], n_rows),
        'Plant': np.random.choice(['Plant 1 (MX)', 'Plant 2 (DE)', 'Plant 3 (CN)', 'Plant 4 (VN)'], n_rows),
        'Commodity': np.random.choice(['Injection Molding', 'Stamping', 'Die Casting'], n_rows),
        'Product': np.random.choice(['Product X248', 'Product X277', 'Product X418', 'Product X620D'], n_rows),
        'Tooling': [f"TL-{np.random.randint(1000, 9999)}" for _ in range(n_rows)],
        'ACT': np.random.uniform(15.0, 60.0, n_rows), # Approved Cycle Time (seconds)
        'Total_Shots': np.random.randint(5000, 50000, n_rows),
        'Hourly_Rate': np.random.uniform(40, 120, n_rows) # Combined Labor + Machine rate
    })
    
    # Map parts based on commodity to ensure valid, logical benchmarking
    commodity_part_map = {
        'Injection Molding': ['Housing-A', 'Main Body X620D', 'Brush Housing', 'Filter Chamber'],
        'Stamping': ['Metal-Base', 'Vortex Plate', 'Soleplate', 'End Cap'],
        'Die Casting': ['Engine-Block', 'Drive Housing', 'Manifold', 'Motor Bucket']
    }
    data['Part'] = data.apply(lambda row: np.random.choice(commodity_part_map[row['Commodity']]), axis=1)

    # Generate Actual CT with realistic variance around the ACT
    variance_multiplier = np.random.normal(1.0, 0.08, n_rows)
    data['Actual_CT'] = data['ACT'] * variance_multiplier
    
    # ---------------------------------------------------------
    # AI TEAM CALCULATION LOGIC (Source of Truth calculations)
    # ---------------------------------------------------------
    
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
    
    # 3. Gain / Loss Hours (Floored at zero per category)
    data['Gain_Hours'] = np.where(data['Tolerance_Status'] == 'Below Tolerance', data['Hours_Diff'], 0)
    data['Loss_Hours'] = np.where(data['Tolerance_Status'] == 'Above Tolerance', -data['Hours_Diff'], 0)
    
    # 4. Financial Gain / Loss
    data['Financial_Gain'] = data['Gain_Hours'] * data['Hourly_Rate']
    data['Financial_Loss'] = data['Loss_Hours'] * data['Hourly_Rate']
    data['Net_Financial'] = data['Financial_Gain'] - data['Financial_Loss']
    
    # 5. Efficiency Calculation
    data['Efficiency_%'] = (data['Expected_Hours'] / data['Used_Hours']) * 100
    
    # 6. Trend & Consistency Mocks
    # Create stability scores based on standard deviation of cycle time variance
    data['Variance_%'] = ((data['Actual_CT'] - data['ACT']) / data['ACT']) * 100
    
    return data

df = load_and_process_data()

# ==========================================
# 3. GLOBAL MASTER FILTER (SIDEBAR)
# ==========================================
st.sidebar.title("Master Filter")

# 1. OEM Business Division
oem_options = df['OEM Business Division'].unique()
selected_oem = st.sidebar.multiselect("OEM Business Division", options=oem_options)
filtered_df = df[df['OEM Business Division'].isin(selected_oem)] if selected_oem else df

# 2. Supplier
supplier_options = filtered_df['Supplier'].unique()
selected_supplier = st.sidebar.multiselect("Supplier", options=supplier_options)
filtered_df = filtered_df[filtered_df['Supplier'].isin(selected_supplier)] if selected_supplier else filtered_df

# 3. Toolmaker
toolmaker_options = filtered_df['Toolmaker'].unique()
selected_toolmaker = st.sidebar.multiselect("Toolmaker", options=toolmaker_options)
filtered_df = filtered_df[filtered_df['Toolmaker'].isin(selected_toolmaker)] if selected_toolmaker else filtered_df

# 4. Plant
plant_options = filtered_df['Plant'].unique()
selected_plant = st.sidebar.multiselect("Plant", options=plant_options)
filtered_df = filtered_df[filtered_df['Plant'].isin(selected_plant)] if selected_plant else filtered_df

# 5. Product
product_options = filtered_df['Product'].unique()
selected_product = st.sidebar.multiselect("Product", options=product_options)
filtered_df = filtered_df[filtered_df['Product'].isin(selected_product)] if selected_product else filtered_df

# 6. Part
part_options = filtered_df['Part'].unique()
selected_part = st.sidebar.multiselect("Part", options=part_options)
filtered_df = filtered_df[filtered_df['Part'].isin(selected_part)] if selected_part else filtered_df

# 7. Tooling
tooling_options = filtered_df['Tooling'].unique()
selected_tooling = st.sidebar.multiselect("Tooling", options=tooling_options)
filtered_df = filtered_df[filtered_df['Tooling'].isin(selected_tooling)] if selected_tooling else filtered_df

# Stop execution if filtering returns empty dataframe
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ==========================================
# 4. DASHBOARD TABS
# ==========================================
st.title("Cycle Time Efficiency V3")

tab_summary, tab_below, tab_above, tab_within = st.tabs([
    "Summary Dashboard", 
    "Below Tolerance Analysis", 
    "Above Tolerance Analysis", 
    "Within Tolerance Analysis"
])

# ------------------------------------------
# HELPER FUNCTION: RENDER ANALYSIS TABS
# ------------------------------------------
def render_analysis_tab(data_subset, tolerance_label, metric_col_gain_loss, cost_col_gain_loss):
    """
    Renders the standardized layout for Below, Above, or Within Tolerance tabs.
    Includes page-level benchmark filters, trend analysis, and drill-throughs.
    """
    if data_subset.empty:
        st.write(f"No products operating {tolerance_label.lower()} based on current filters.")
        return

    # --- Page-Level Benchmark Filter ---
    st.subheader("Benchmark Context")
    perspective = st.radio(
        "Select Benchmark Perspective:",
        ["Commodity Perspective", "Part Perspective", "Supplier Perspective"],
        horizontal=True,
        key=f"perspective_{tolerance_label}"
    )
    
    perspective_col = "Commodity"
    if perspective == "Part Perspective":
        perspective_col = "Part"
    elif perspective == "Supplier Perspective":
        perspective_col = "Supplier"

    # --- Top KPIs & Context ---
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
    
    # --- Benchmark Comparison ---
    st.markdown(f"**Comparison by {perspective_col}**")
    
    # Calculate Benchmarks
    benchmark_df = data_subset.groupby(perspective_col).agg({
        'Efficiency_%': 'mean',
        'Variance_%': 'mean',
        'Tooling': 'nunique',
    }).reset_index().rename(columns={'Tooling': 'Active Tools'})
    
    # Summary of Benchmarks
    best_peer_idx = benchmark_df['Efficiency_%'].idxmax()
    best_peer = benchmark_df.loc[best_peer_idx, perspective_col]
    median_eff = benchmark_df['Efficiency_%'].median()
    avg_eff = benchmark_df['Efficiency_%'].mean()
    
    b_col1, b_col2, b_col3 = st.columns(3)
    b_col1.metric(f"Best Performing {perspective_col}", best_peer)
    b_col2.metric("Median Efficiency", f"{median_eff:.1f}%")
    b_col3.metric("Average Efficiency", f"{avg_eff:.1f}%")

    # Benchmark Ranked Chart
    fig_bench = px.bar(
        benchmark_df.sort_values('Efficiency_%', ascending=True), 
        x='Efficiency_%', y=perspective_col, orientation='h',
        color_discrete_sequence=['#4B5563']
    )
    fig_bench.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Average Efficiency (%)", yaxis_title="")
    st.plotly_chart(fig_bench, use_container_width=True)

    # --- Trend Stability Analysis ---
    st.subheader("Trend Stability Analysis")
    trend_grouping = st.selectbox("View trend by:", ["Supplier", "Product", "Plant", "Toolmaker"], key=f"trend_{tolerance_label}")
    
    trend_data = data_subset.groupby(['Date', trend_grouping])['Variance_%'].mean().reset_index()
    fig_trend = px.line(trend_data, x='Date', y='Variance_%', color=trend_grouping)
    fig_trend.update_layout(height=350, margin=dict(t=10, b=10, l=10, r=10), yaxis_title="Variance from ACT (%)")
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- Drill-Through Capability ---
    st.subheader("Detailed Drill-Through")
    with st.expander("Expand to view tool-level operations and historical runs"):
        st.dataframe(
            data_subset[[
                'Date', 'Product', 'Part', 'Supplier', 'Plant', 'Toolmaker', 'Tooling', 
                'ACT', 'Actual_CT', 'Variance_%', 'Tolerance_Status', 'Efficiency_%'
            ]].sort_values('Date', ascending=False),
            use_container_width=True
        )

# ------------------------------------------
# TAB 1: MACRO SUMMARY DASHBOARD
# ------------------------------------------
with tab_summary:
    # 1. High-Level KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Active Tooling", len(filtered_df['Tooling'].unique()))
    kpi2.metric("Overall Average Efficiency", f"{filtered_df['Efficiency_%'].mean():.1f}%")
    kpi3.metric("Savings Opportunity (Faster)", f"${filtered_df['Financial_Gain'].sum():,.0f}")
    kpi4.metric("Production Loss (Slower)", f"${filtered_df['Financial_Loss'].sum():,.0f}")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Performance Summaries Layout
    col_supp, col_comm, col_prod = st.columns(3)

    # Supplier Performance Summary
    with col_supp:
        st.markdown("**Supplier Performance**")
        supp_summary = filtered_df.groupby('Supplier').agg({
            'Financial_Gain': 'sum',
            'Efficiency_%': 'mean'
        }).reset_index().sort_values('Efficiency_%', ascending=True)
        
        fig_supp = px.bar(supp_summary, x='Efficiency_%', y='Supplier', orientation='h', color_discrete_sequence=['#1F2937'])
        fig_supp.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Efficiency %", yaxis_title="")
        st.plotly_chart(fig_supp, use_container_width=True)

    # Commodity Performance Summary
    with col_comm:
        st.markdown("**Commodity Performance**")
        comm_summary = filtered_df.groupby('Commodity').agg({
            'Financial_Gain': 'sum',
            'Efficiency_%': 'mean'
        }).reset_index().sort_values('Efficiency_%', ascending=True)
        
        fig_comm = px.bar(comm_summary, x='Efficiency_%', y='Commodity', orientation='h', color_discrete_sequence=['#4B5563'])
        fig_comm.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Efficiency %", yaxis_title="")
        st.plotly_chart(fig_comm, use_container_width=True)

    # Product Performance Summary
    with col_prod:
        st.markdown("**Product Performance**")
        prod_summary = filtered_df.groupby('Product').agg({
            'Financial_Gain': 'sum',
            'Efficiency_%': 'mean'
        }).reset_index().sort_values('Efficiency_%', ascending=True)
        
        fig_prod = px.bar(prod_summary, x='Efficiency_%', y='Product', orientation='h', color_discrete_sequence=['#9CA3AF'])
        fig_prod.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Efficiency %", yaxis_title="")
        st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown("---")

    # 3. Global Tolerance Distribution (Heatmap & Scatter)
    col_dist1, col_dist2 = st.columns(2)
    with col_dist1:
        st.markdown("**Tolerance Distribution by Commodity**")
        status_pivot = pd.crosstab(filtered_df['Commodity'], filtered_df['Tolerance_Status'], normalize='index') * 100
        # Reorder columns if they exist
        cols_order = [c for c in ["Below Tolerance", "Within Tolerance", "Above Tolerance"] if c in status_pivot.columns]
        status_pivot = status_pivot[cols_order]
        
        fig_heat = px.imshow(status_pivot, text_auto=".1f", aspect="auto", color_continuous_scale="Blues")
        fig_heat.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_dist2:
        st.markdown("**Actual CT vs Approved CT Distribution**")
        fig_scatter = px.scatter(
            filtered_df, x='ACT', y='Actual_CT', 
            color='Tolerance_Status', color_discrete_map=COLOR_MAP,
            hover_data=['Tooling', 'Supplier', 'Part']
        )
        max_val = max(filtered_df['ACT'].max(), filtered_df['Actual_CT'].max())
        fig_scatter.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="#d1d5db", dash="dash"))
        fig_scatter.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), showlegend=True)
        st.plotly_chart(fig_scatter, use_container_width=True)


# ------------------------------------------
# TAB 2: BELOW TOLERANCE ANALYSIS
# ------------------------------------------
with tab_below:
    below_df = filtered_df[filtered_df['Tolerance_Status'] == 'Below Tolerance'].copy()
    render_analysis_tab(
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
        data_subset=within_df, 
        tolerance_label="Within Tolerance", 
        metric_col_gain_loss=None, # Stable states do not generate gain/loss hours in this context
        cost_col_gain_loss=None
    )