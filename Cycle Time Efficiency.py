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

# Strict Operational Tolerance Color Logic
# Applied automatically to charts and visualizations
COLOR_MAP = {
    "Below Tolerance": "#FF4B4B",
    "Within Tolerance": "#00CC96",
    "Above Tolerance": "#FFAA00"
}

# High-Contrast, Enterprise CSS
# Built to support both Light and Dark mode dynamically via CSS variables
st.markdown("""
    <style>
    /* Metric Container Styling */
    .metric-container {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 1rem;
    }
    /* Metric Value Styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-color);
    }
    /* Metric Label Styling */
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-color);
        opacity: 0.85;
    }
    /* Hide Streamlit Header */
    header {visibility: hidden;}
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
    
    # 4. Efficiency & Variance
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
def render_analysis_tab(global_filtered_df, data_subset, tolerance_label, metric_col_gain_loss, cost_col_gain_loss):
    """
    Renders the standardized layout for analysis tabs including new 
    trend stability, benchmark contexts, and drill-through capabilities.
    """
    if data_subset.empty:
        st.write(f"No products operating {tolerance_label.lower()} based on current filters.")
        return

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
    
    # --- Trend Stability Analysis ---
    st.subheader("Trend Stability Analysis")
    
    # Calculate Trend Metrics
    max_date = data_subset['Date'].max()
    d7_data = data_subset[data_subset['Date'] >= max_date - timedelta(days=7)]
    d30_data = data_subset[data_subset['Date'] >= max_date - timedelta(days=30)]
    
    d7_trend = d7_data['Variance_%'].mean() if not d7_data.empty else 0
    d30_trend = d30_data['Variance_%'].mean() if not d30_data.empty else 0
    
    # Stability Score (0-100 scale based on standard deviation of variance)
    std_dev = data_subset['Variance_%'].std()
    std_dev = 0 if pd.isna(std_dev) else std_dev
    stability_score = max(0, min(100, 100 - (std_dev * 5))) # Scaled for visibility
    
    consistency = "High" if stability_score >= 80 else "Medium" if stability_score >= 50 else "Low"

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    t_col1.metric("7-Day Trend (Avg Variance)", f"{d7_trend:+.2f}%")
    t_col2.metric("30-Day Trend (Avg Variance)", f"{d30_trend:+.2f}%")
    t_col3.metric("Stability Score", f"{stability_score:.0f}/100")
    t_col4.metric("Consistency Indicator", consistency)

    trend_grouping = st.selectbox("View historical trend by:", ["Supplier", "Product", "Plant", "Toolmaker"], key=f"trend_grp_{tolerance_label}")
    
    unique_entities = data_subset[trend_grouping].dropna().unique().tolist()
    # Default to top 3 entities by volume to prevent visual clutter
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
        
        fig_trend = px.bar(
            trend_data, 
            x='Date', 
            y='Variance_%', 
            color=trend_grouping,
            barmode='group'
        )
        
        # Clean layout: move legend to the top, unify hover tooltips
        fig_trend.update_layout(
            height=320, 
            margin=dict(t=10, b=10, l=10, r=10), 
            yaxis_title="Variance from ACT (%)",
            xaxis_title="",
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="right", 
                x=1,
                title=""
            ),
            hovermode="x unified"
        )
        st.plotly_chart(fig_trend, use_container_width=True, key=f"trend_chart_{tolerance_label}")
    else:
        st.info("Please select at least one entity to display the trend graph.")

    st.markdown("---")

    # --- Benchmark Context ---
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

    # Calculate Global Context Benchmarks
    benchmark_df = global_filtered_df.groupby(perspective_col).agg({'Efficiency_%': 'mean'}).reset_index()
    
    best_peer_idx = benchmark_df['Efficiency_%'].idxmax()
    best_peer = benchmark_df.loc[best_peer_idx, perspective_col]
    median_eff = benchmark_df['Efficiency_%'].median()
    
    # Calculate specific Supplier/Commodity averages across the global filtered set
    global_supplier_avg = global_filtered_df['Efficiency_%'].mean() # Default to global if not specific
    global_commodity_avg = global_filtered_df['Efficiency_%'].mean()
    
    if len(global_filtered_df['Supplier'].unique()) == 1:
        global_supplier_avg = global_filtered_df['Efficiency_%'].mean()
    if len(global_filtered_df['Commodity'].unique()) == 1:
        global_commodity_avg = global_filtered_df['Efficiency_%'].mean()

    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    b_col1.metric("Best Performing Peer", best_peer)
    b_col2.metric("Median Benchmark", f"{median_eff:.1f}%")
    b_col3.metric("Global Supplier Average", f"{global_supplier_avg:.1f}%")
    b_col4.metric("Global Commodity Average", f"{global_commodity_avg:.1f}%")

    fig_bench = px.bar(
        benchmark_df.sort_values('Efficiency_%', ascending=True), 
        x='Efficiency_%', y=perspective_col, orientation='h'
    )
    fig_bench.update_traces(marker_color='#3b82f6') # High contrast blue
    fig_bench.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Average Efficiency (%)", yaxis_title="")
    st.plotly_chart(fig_bench, use_container_width=True, key=f"bench_chart_{tolerance_label}")

    st.markdown("---")

    # --- Drill-Through Capability ---
    st.subheader("Detailed Drill-Through")
    drill_target = st.selectbox(
        "Select Tooling for Operational Drill-Through:", 
        options=data_subset['Tooling'].unique(),
        key=f"drill_{tolerance_label}"
    )
    
    if drill_target:
        tool_data = data_subset[data_subset['Tooling'] == drill_target].sort_values('Date')
        
        st.markdown(f"**Operational Analysis: {drill_target}**")
        d_col1, d_col2 = st.columns(2)
        
        with d_col1:
            fig_tool_trend = px.line(
                tool_data, x='Date', y='Actual_CT', 
                title="Historical Cycle Time Trend",
                markers=True
            )
            # Add ACT Reference Line
            act_val = tool_data['ACT'].iloc[0]
            fig_tool_trend.add_hline(y=act_val, line_dash="dash", line_color="rgba(128,128,128,0.5)", annotation_text="Approved CT")
            fig_tool_trend.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_tool_trend, use_container_width=True, key=f"tool_trend_{tolerance_label}")
            
        with d_col2:
            fig_tool_var = px.bar(
                tool_data, x='Date', y='Variance_%',
                title="Cycle Variance per Run",
                color='Tolerance_Status',
                color_discrete_map=COLOR_MAP
            )
            fig_tool_var.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_tool_var, use_container_width=True, key=f"tool_var_{tolerance_label}")
            
        st.markdown("**Production Runs History**")
        st.dataframe(
            tool_data[[
                'Date', 'Product', 'Part', 'Supplier', 'ACT', 'Actual_CT', 
                'Total_Shots', 'Variance_%', 'Tolerance_Status', 'Efficiency_%'
            ]].sort_values('Date', ascending=False),
            use_container_width=True
        )

# ------------------------------------------
# TAB 1: MACRO SUMMARY DASHBOARD
# ------------------------------------------
with tab_summary:
    # 1. High-Level KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Overall Average Efficiency", f"{filtered_df['Efficiency_%'].mean():.1f}%")
    kpi2.metric("Savings Opportunity (Faster)", f"${filtered_df['Financial_Gain'].sum():,.0f}")
    kpi3.metric("Production Loss (Slower)", f"${filtered_df['Financial_Loss'].sum():,.0f}")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Performance Summaries Layout
    col_supp, col_comm, col_prod = st.columns(3)

    with col_supp:
        st.markdown("**Supplier Performance**")
        supp_summary = filtered_df.groupby('Supplier').agg({
            'Financial_Gain': 'sum',
            'Efficiency_%': 'mean'
        }).reset_index().sort_values('Efficiency_%', ascending=True)
        
        fig_supp = px.bar(supp_summary, x='Efficiency_%', y='Supplier', orientation='h')
        fig_supp.update_traces(marker_color='#2563eb')
        fig_supp.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Efficiency %", yaxis_title="")
        st.plotly_chart(fig_supp, use_container_width=True)

    with col_comm:
        st.markdown("**Commodity Performance**")
        comm_summary = filtered_df.groupby('Commodity').agg({
            'Financial_Gain': 'sum',
            'Efficiency_%': 'mean'
        }).reset_index().sort_values('Efficiency_%', ascending=True)
        
        fig_comm = px.bar(comm_summary, x='Efficiency_%', y='Commodity', orientation='h')
        fig_comm.update_traces(marker_color='#3b82f6')
        fig_comm.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Efficiency %", yaxis_title="")
        st.plotly_chart(fig_comm, use_container_width=True)

    with col_prod:
        st.markdown("**Product Performance**")
        prod_summary = filtered_df.groupby('Product').agg({
            'Financial_Gain': 'sum',
            'Efficiency_%': 'mean'
        }).reset_index().sort_values('Efficiency_%', ascending=True)
        
        fig_prod = px.bar(prod_summary, x='Efficiency_%', y='Product', orientation='h')
        fig_prod.update_traces(marker_color='#60a5fa')
        fig_prod.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Efficiency %", yaxis_title="")
        st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown("---")

    # 3. Global Tolerance Distribution (Heatmap & Scatter)
    col_dist1, col_dist2 = st.columns(2)
    with col_dist1:
        st.markdown("**Tolerance Distribution by Commodity**")
        status_pivot = pd.crosstab(filtered_df['Commodity'], filtered_df['Tolerance_Status'], normalize='index') * 100
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
        fig_scatter.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="rgba(128,128,128,0.5)", dash="dash"))
        fig_scatter.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), showlegend=True)
        st.plotly_chart(fig_scatter, use_container_width=True)


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