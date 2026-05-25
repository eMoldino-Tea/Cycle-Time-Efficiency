import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Cycle Time Efficiency Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
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
# 3. DASHBOARD HEADER
# ==========================================
st.markdown('<div class="dash-header">Manufacturing Performance: Cycle Time Efficiency</div>', unsafe_allow_html=True)

# ==========================================
# 4. SECTION 1: KPI SUMMARY CARDS
# ==========================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

with kpi1:
    st.markdown("""
    <div class="dash-card">
        <div class="kpi-title-container">
            <span class="kpi-title">Net Hours</span>
            <span class="kpi-icon">ℹ️</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Gained</span>
            <span class="metric-value text-green">15H 12M</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Lost</span>
            <span class="metric-value text-red">3H 5M</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown("""
    <div class="dash-card">
        <div class="kpi-title-container">
            <span class="kpi-title">Net Shots</span>
            <span class="kpi-icon">ℹ️</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Gained</span>
            <span class="metric-value text-green">12,553,725</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Lost</span>
            <span class="metric-value text-red">5,342,431</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown("""
    <div class="dash-card">
        <div class="kpi-title-container">
            <span class="kpi-title">Net Financial</span>
            <span class="kpi-icon">ℹ️</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Financial Gain</span>
            <span class="metric-value text-green">$1,688</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Financial Loss</span>
            <span class="metric-value text-red">-$1,712</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown("""
    <div class="dash-card">
        <div class="kpi-title-container">
            <span class="kpi-title">Efficiency</span>
            <span class="kpi-icon">ℹ️</span>
        </div>
        <div class="metric-row" style="margin-bottom: 8px;">
            <span class="metric-label">Fast</span>
            <span class="metric-value text-green">+112.43%</span>
        </div>
        <div class="metric-row" style="margin-bottom: 8px;">
            <span class="metric-label">Slow</span>
            <span class="metric-value text-red">-87.30%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Within</span>
            <span class="metric-value text-neutral">100.00%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# ==========================================
# 5. SECTION 2: PERFORMANCE ANALYTICS
# ==========================================
panel1, panel2, panel3 = st.columns(3, gap="medium")

# Panel 1: Supplier Performance
with panel1:
    st.markdown("""
    <div class="dash-card">
        <div class="panel-title">Supplier Performance</div>
        <div class="panel-split">
            <!-- Left: Fastest -->
            <div class="panel-col">
                <div class="col-header text-green">Top 3 Fastest</div>
                
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Foxconn</span><span class="metric-value text-green">118.2%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 100%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Jabil</span><span class="metric-value text-green">114.5%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 85%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Flex</span><span class="metric-value text-green">109.1%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 60%;"></div></div>
                </div>
            </div>
            
            <!-- Right: Slowest -->
            <div class="panel-col">
                <div class="col-header text-red">Top 3 Slowest</div>
                
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Sanmina</span><span class="metric-value text-red">76.4%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 100%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Pegatron</span><span class="metric-value text-red">82.1%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 75%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Celestica</span><span class="metric-value text-red">88.9%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 45%;"></div></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Panel 2: Tooling Type Performance
with panel2:
    st.markdown("""
    <div class="dash-card">
        <div class="panel-title">Tooling Type Performance</div>
        <div class="panel-split">
            <!-- Left: Fastest -->
            <div class="panel-col">
                <div class="col-header text-green">Top 3 Fastest</div>
                
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name" title="Injection Molding">Injection Molding</span><span class="metric-value text-green">115.8%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 100%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name" title="High Pressure Die Casting">High Pressure Die Casting</span><span class="metric-value text-green">112.3%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 80%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name" title="Progressive Stamping">Progressive Stamping</span><span class="metric-value text-green">108.7%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 55%;"></div></div>
                </div>
            </div>
            
            <!-- Right: Slowest -->
            <div class="panel-col">
                <div class="col-header text-red">Top 3 Slowest</div>
                
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name" title="Thermoforming">Thermoforming</span><span class="metric-value text-red">81.2%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 100%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name" title="Blow Molding">Blow Molding</span><span class="metric-value text-red">84.5%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 85%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name" title="Vacuum Forming">Vacuum Forming</span><span class="metric-value text-red">89.4%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 50%;"></div></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Panel 3: Product Performance
with panel3:
    st.markdown("""
    <div class="dash-card">
        <div class="panel-title">Product Performance</div>
        <div class="panel-split">
            <!-- Left: Fastest -->
            <div class="panel-col">
                <div class="col-header text-green">Top 3 Fastest</div>
                
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Product X248</span><span class="metric-value text-green">121.0%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 100%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Product X418</span><span class="metric-value text-green">116.4%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 75%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Product X277</span><span class="metric-value text-green">107.5%</span></div>
                    <div class="bar-bg"><div class="bar-fill-green" style="width: 35%;"></div></div>
                </div>
            </div>
            
            <!-- Right: Slowest -->
            <div class="panel-col">
                <div class="col-header text-red">Top 3 Slowest</div>
                
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Product X620D</span><span class="metric-value text-red">78.3%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 100%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Product V15</span><span class="metric-value text-red">83.9%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 65%;"></div></div>
                </div>
                <div class="rank-item">
                    <div class="rank-text-row"><span class="rank-name">Product V12</span><span class="metric-value text-red">89.1%</span></div>
                    <div class="bar-bg"><div class="bar-fill-red" style="width: 40%;"></div></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)