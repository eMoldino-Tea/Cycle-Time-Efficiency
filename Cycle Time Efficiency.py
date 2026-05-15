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
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Strict Operational Tolerance Color Logic (V3 Requirement)
COLOR_MAP = {
    "Below Tolerance": "#FF4B4B",  # Red - Tool runs faster (Quality Risk)
    "Within Tolerance": "#00CC96", # Green - Acceptable/Compliant
    "Above Tolerance": "#FFAA00"   # Yellow - Tool runs slower (Inefficiency/Loss)
}

# Custom CSS for an Enterprise Analytics Look
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 1px 2px 5px rgba(0,0,0,0.05);
    }
    .red-text { color: #FF4B4B !important; font-weight: bold; }
    .green-text { color: #00CC96 !important; font-weight: bold; }
    .yellow-text { color: #FFAA00 !important; font-weight: bold; }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING & AI TEAM LOGIC
# ==========================================
@st.cache_data
def load_and_process_data():
    """
    Generates mock data and applies the 'AI Team Calculation Logic' from the provided PDF.
    In production, replace the generation block with your Snowflake/DB query.
    """
    np.random.seed(42)
    n_rows = 1500
    
    # Generate Base Data to reflect the documents
    data = pd.DataFrame({
        # FIX: Cast the numpy int to a standard Python int to avoid timedelta TypeError
        'Date': [datetime.today() - timedelta(days=int(x)) for x in np.random.randint(0, 180, n_rows)],
        'Region': np.random.choice(['NA', 'EU', 'APAC', 'LATAM'], n_rows),
        'Supplier': np.random.choice(['Jabil', 'Flex', 'Foxconn', 'Pegatron', 'Sanmina'], n_rows),
        'Commodity': np.random.choice(['Injection Molding', 'Stamping', 'Die Casting'], n_rows),
        'Project': np.random.choice(['X248', 'X277', 'X418', 'X620D'], n_rows),
        'Tool': [f"TL-{np.random.randint(1000, 9999)}" for _ in range(n_rows)],
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
    # FASTER if CT < ACT * 0.95 | SLOWER if CT > ACT * 1.05 | WITHIN otherwise
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
    # Efficiency = (Expected Hours / Actual Hours) * 100
    data['Efficiency_%'] = (data['Expected_Hours'] / data['Used_Hours']) * 100
    
    return data

df = load_and_process_data()

# ==========================================
# 3. SIDEBAR: BENCHMARK-SAFE FILTERS
# ==========================================
st.sidebar.markdown("### 📊 Benchmarking Flow")
st.sidebar.caption("Filter sequentially to ensure valid performance comparisons.")

# 1. Commodity (Highest Level ensures Apples-to-Apples)
selected_commodity = st.sidebar.selectbox("1. Commodity (Required)", options=df['Commodity'].unique())
filtered_df = df[df['Commodity'] == selected_commodity]

# 2. Part (Filtered strictly by selected Commodity)
part_options = ["All Parts"] + list(filtered_df['Part'].unique())
selected_part = st.sidebar.selectbox("2. Part (Optional)", options=part_options)
if selected_part != "All Parts":
    filtered_df = filtered_df[filtered_df['Part'] == selected_part]

# 3. Supplier (Filtered strictly by selected Part)
supplier_options = ["All Suppliers"] + list(filtered_df['Supplier'].unique())
selected_supplier = st.sidebar.selectbox("3. Supplier (Optional)", options=supplier_options)
if selected_supplier != "All Suppliers":
    filtered_df = filtered_df[filtered_df['Supplier'] == selected_supplier]

st.sidebar.divider()
st.sidebar.markdown("""
**Operational Color Standard:**
* 🔴 **Red (<95% ACT):** Below Tolerance. Running too fast. Indicates process instability or unapproved conditions.
* 🟢 **Green (±5% ACT):** Within Tolerance. Stable and compliant.
* 🟡 **Yellow (>105% ACT):** Above Tolerance. Running too slow. Indicates inefficiency and cost loss.
""")

# ==========================================
# 4. DASHBOARD TABS & ROUTING
# ==========================================
st.title("⚙️ Cycle Time Efficiency V3")
st.markdown(f"**Current Context:** Commodity: `{selected_commodity}` | Part: `{selected_part}` | Supplier: `{selected_supplier}`")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Macro Summary Dashboard", 
    "🔴 Below Tolerance (Too Fast)", 
    "🟡 Above Tolerance (Too Slow)", 
    "🟢 Within Tolerance", 
    "🔍 Detailed Filter & Deep Dive"
])

# ------------------------------------------
# TAB 1: MACRO SUMMARY DASHBOARD
# ------------------------------------------
with tab1:
    st.subheader("Executive Overview")
    
    # AI Team Logic KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    avg_efficiency = filtered_df['Efficiency_%'].mean()
    total_financial_gain = filtered_df['Financial_Gain'].sum()
    total_financial_loss = filtered_df['Financial_Loss'].sum()
    total_net = total_financial_gain - total_financial_loss
    
    kpi1.metric("Overall Weighted Avg Efficiency", f"{avg_efficiency:.1f}%")
    kpi2.metric("Savings Opportunity (Gain)", f"${total_financial_gain:,.0f}")
    kpi3.metric("Production Loss (Inefficiency)", f"${total_financial_loss:,.0f}")
    kpi4.metric("Net Financial Impact", f"${total_net:,.0f}")
    
    st.divider()
    
    colA, colB = st.columns([1, 2])
    
    with colA:
        st.markdown("#### Operational Tolerance Distribution")
        status_counts = filtered_df['Tolerance_Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        # Ensures strict adherence to color logic across charts
        fig_pie = px.pie(status_counts, values='Count', names='Status', 
                         color='Status', color_discrete_map=COLOR_MAP, hole=0.4)
        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with colB:
        st.markdown("#### Cycle Time Efficiency Rankings by Supplier")
        supplier_perf = filtered_df.groupby('Supplier').agg({
            'Efficiency_%': 'mean',
            'Net_Financial': 'sum'
        }).reset_index().sort_values(by='Efficiency_%', ascending=True)
        
        # Color coding the bars based on threshold rules
        supplier_perf['Color'] = np.where(supplier_perf['Efficiency_%'] > 105, COLOR_MAP['Below Tolerance'], 
                                 np.where(supplier_perf['Efficiency_%'] < 95, COLOR_MAP['Above Tolerance'], 
                                          COLOR_MAP['Within Tolerance']))
        
        fig_bar = px.bar(supplier_perf, x='Efficiency_%', y='Supplier', orientation='h',
                         hover_data=['Net_Financial'])
        fig_bar.update_traces(marker_color=supplier_perf['Color'])
        fig_bar.add_vline(x=100, line_dash="dash", line_color="black", annotation_text="Target (100%)")
        fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Efficiency (%)")
        st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------
# TAB 2: BELOW TOLERANCE (RED)
# ------------------------------------------
with tab2:
    st.markdown("### <span class='red-text'>🔴 Products Running Below Approved Cycle Time</span>", unsafe_allow_html=True)
    st.error("**Risk Alert:** These products are operating faster than ACT. While yielding monetary gains, this flags potential unapproved operating conditions, tool wear risks, or quality instability.")
    
    red_df = filtered_df[filtered_df['Tolerance_Status'] == 'Below Tolerance'].copy()
    
    if not red_df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Tools Flagged", len(red_df['Tool'].unique()))
        c2.metric("Total Hours Saved", f"{red_df['Gain_Hours'].sum():,.1f} h")
        c3.metric("Cost Gain (Opportunity)", f"${red_df['Financial_Gain'].sum():,.2f}")
        
        st.dataframe(red_df[['Supplier', 'Project', 'Part', 'Tool', 'ACT', 'Actual_CT', 'Gain_Hours', 'Financial_Gain']].style.format({
            "ACT": "{:.2f}s", "Actual_CT": "{:.2f}s", "Gain_Hours": "{:.1f}h", "Financial_Gain": "${:,.2f}"
        }), use_container_width=True)
    else:
        st.success("No products are running faster than the tolerance threshold.")

# ------------------------------------------
# TAB 3: ABOVE TOLERANCE (YELLOW)
# ------------------------------------------
with tab3:
    st.markdown("### <span class='yellow-text'>🟡 Products Running Above Approved Cycle Time</span>", unsafe_allow_html=True)
    st.warning("**Inefficiency Alert:** These products are operating slower than ACT. These represent lost production time, excess cycle time, and direct monetary loss.")
    
    yellow_df = filtered_df[filtered_df['Tolerance_Status'] == 'Above Tolerance'].copy()
    
    if not yellow_df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Tools Flagged", len(yellow_df['Tool'].unique()))
        c2.metric("Total Hours Lost", f"{yellow_df['Loss_Hours'].sum():,.1f} h")
        c3.metric("Cost Lost", f"${yellow_df['Financial_Loss'].sum():,.2f}")
        
        st.dataframe(yellow_df[['Supplier', 'Project', 'Part', 'Tool', 'ACT', 'Actual_CT', 'Loss_Hours', 'Financial_Loss']].style.format({
            "ACT": "{:.2f}s", "Actual_CT": "{:.2f}s", "Loss_Hours": "{:.1f}h", "Financial_Loss": "${:,.2f}"
        }), use_container_width=True)
    else:
        st.success("No products are running slower than the tolerance threshold.")

# ------------------------------------------
# TAB 4: WITHIN TOLERANCE (GREEN)
# ------------------------------------------
with tab4:
    st.markdown("### <span class='green-text'>🟢 Products Running Within Tolerance</span>", unsafe_allow_html=True)
    st.success("**Operational Stability:** These tools are operating safely within the ±5% Approved Cycle Time tolerance range, representing high process compliance.")
    
    green_df = filtered_df[filtered_df['Tolerance_Status'] == 'Within Tolerance'].copy()
    
    if not green_df.empty:
        st.metric("Stable Tools", len(green_df['Tool'].unique()))
        st.dataframe(green_df[['Supplier', 'Project', 'Part', 'Tool', 'ACT', 'Actual_CT', 'Efficiency_%']].style.format({
            "ACT": "{:.2f}s", "Actual_CT": "{:.2f}s", "Efficiency_%": "{:.1f}%"
        }), use_container_width=True)
    else:
        st.info("No products fall perfectly within the tolerance range.")

# ------------------------------------------
# TAB 5: DEEP DIVE & EXPORT
# ------------------------------------------
with tab5:
    st.markdown("### 🔍 Advanced Filter & Deep Dive")
    st.write("Use granular filters to isolate specific dimensions and export data.")
    
    dd_col1, dd_col2, dd_col3, dd_col4 = st.columns(4)
    
    with dd_col1:
        dates = pd.to_datetime(filtered_df['Date'])
        date_range = st.date_input("Date Range", [dates.min(), dates.max()])
    with dd_col2:
        selected_projects = st.multiselect("Project", options=filtered_df['Project'].unique())
    with dd_col3:
        selected_regions = st.multiselect("Region", options=filtered_df['Region'].unique())
    with dd_col4:
        selected_tools = st.multiselect("Specific Tool", options=filtered_df['Tool'].unique())

    # Apply Detailed Filters
    deep_dive_df = filtered_df.copy()
    
    if len(date_range) == 2:
        deep_dive_df = deep_dive_df[(deep_dive_df['Date'].dt.date >= date_range[0]) & (deep_dive_df['Date'].dt.date <= date_range[1])]
    if selected_projects:
        deep_dive_df = deep_dive_df[deep_dive_df['Project'].isin(selected_projects)]
    if selected_regions:
        deep_dive_df = deep_dive_df[deep_dive_df['Region'].isin(selected_regions)]
    if selected_tools:
        deep_dive_df = deep_dive_df[deep_dive_df['Tool'].isin(selected_tools)]

    # Heatmap visualization
    st.markdown("#### Cycle Time Deviations (ACT vs Actual CT)")
    fig_scatter = px.scatter(deep_dive_df, x='ACT', y='Actual_CT', color='Tolerance_Status', 
                             color_discrete_map=COLOR_MAP, hover_data=['Tool', 'Supplier', 'Part', 'Efficiency_%'])
    
    # Adding the 1:1 Reference Line
    max_val = max(deep_dive_df['ACT'].max() if not deep_dive_df.empty else 60, 
                  deep_dive_df['Actual_CT'].max() if not deep_dive_df.empty else 60)
    fig_scatter.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, 
                          line=dict(color="rgba(0,0,0,0.3)", dash="dash"))
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("#### Tabular Data")
    st.dataframe(deep_dive_df.sort_values(by="Date", ascending=False), use_container_width=True)
    
    csv = deep_dive_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='cycle_time_efficiency_export.csv',
        mime='text/csv',
    )