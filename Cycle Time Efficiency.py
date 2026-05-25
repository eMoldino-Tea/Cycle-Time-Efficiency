import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Cycle Time Efficiency",
    layout="wide",
    initial_sidebar_state="collapsed"
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

/* Dashboard Card Global Styles */
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

/* Color Tokens */
.text-green { color: #10b981 !important; }
.text-red { color: #ef4444 !important; }
.text-neutral { color: #f8fafc !important; }

/* Panel Specific Styles */
.panel-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 24px;
}
.panel-split {
    display: flex;
    flex-direction: row;
    gap: 20px;
    flex-wrap: wrap;
    flex: 1;
}
.panel-col {
    flex: 1 1 calc(50% - 10px);
    display: flex;
    flex-direction: column;
    min-width: 140px;
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
    background-color: #10b981;
    border-radius: 3px;
}
.bar-fill-red {
    height: 100%;
    background-color: #ef4444;
    border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DASHBOARD TITLE
# ==========================================
st.markdown('<div class="dash-header">Cycle Time Efficiency</div>', unsafe_allow_html=True)

# ==========================================
# 4. SECTION 1: KPI SUMMARY CARDS
# ==========================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

# Helper function to build HTML blocks cleanly without indentation issues
def build_html(*lines):
    return "".join(line.strip() for line in lines)

# Card 1 - Net Hours
html_kpi1 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container">',
    '<span class="kpi-title">Net Hours</span>',
    '<span class="kpi-icon">ℹ️</span>',
    '</div>',
    '<div class="metric-row">',
    '<span class="metric-label">Gained</span>',
    '<span class="metric-value text-green">15H 12M</span>',
    '</div>',
    '<div class="metric-row">',
    '<span class="metric-label">Lost</span>',
    '<span class="metric-value text-red">3H 5M</span>',
    '</div>',
    '</div>'
)
kpi1.markdown(html_kpi1, unsafe_allow_html=True)

# Card 2 - Net Shots
html_kpi2 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container">',
    '<span class="kpi-title">Net Shots</span>',
    '<span class="kpi-icon">ℹ️</span>',
    '</div>',
    '<div class="metric-row">',
    '<span class="metric-label">Gained</span>',
    '<span class="metric-value text-green">12,553,725</span>',
    '</div>',
    '<div class="metric-row">',
    '<span class="metric-label">Lost</span>',
    '<span class="metric-value text-red">5,342,431</span>',
    '</div>',
    '</div>'
)
kpi2.markdown(html_kpi2, unsafe_allow_html=True)

# Card 3 - Net Financial
html_kpi3 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container">',
    '<span class="kpi-title">Net Financial</span>',
    '<span class="kpi-icon">ℹ️</span>',
    '</div>',
    '<div class="metric-row">',
    '<span class="metric-label">Financial Gain</span>',
    '<span class="metric-value text-green">$1,688</span>',
    '</div>',
    '<div class="metric-row">',
    '<span class="metric-label">Financial Loss</span>',
    '<span class="metric-value text-red">-$1,712</span>',
    '</div>',
    '</div>'
)
kpi3.markdown(html_kpi3, unsafe_allow_html=True)

# Card 4 - Efficiency
html_kpi4 = build_html(
    '<div class="dash-card">',
    '<div class="kpi-title-container">',
    '<span class="kpi-title">Efficiency</span>',
    '<span class="kpi-icon">ℹ️</span>',
    '</div>',
    '<div class="metric-row" style="margin-bottom: 8px;">',
    '<span class="metric-label">Fast</span>',
    '<span class="metric-value text-green">+112.43%</span>',
    '</div>',
    '<div class="metric-row" style="margin-bottom: 8px;">',
    '<span class="metric-label">Slow</span>',
    '<span class="metric-value text-red">-87.30%</span>',
    '</div>',
    '<div class="metric-row">',
    '<span class="metric-label">Within</span>',
    '<span class="metric-value text-neutral">100%</span>',
    '</div>',
    '</div>'
)
kpi4.markdown(html_kpi4, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# ==========================================
# 5. SECTION 2: PERFORMANCE ANALYTICS
# ==========================================
# Static Placeholder Data mapped to Efficiency Classification Rules
MOCK_DATA = {
    "Supplier": {
        "gain": [("Foxconn", 118.2), ("Jabil", 114.5), ("Flex", 109.1)],
        "loss": [("Sanmina", 76.4), ("Pegatron", 82.1), ("Celestica", 88.9)]
    },
    "Tooling Type": {
        "gain": [("Injection Molding", 115.8), ("High Pressure Die Casting", 112.3), ("Progressive Stamping", 108.7)],
        "loss": [("Thermoforming", 81.2), ("Blow Molding", 84.5), ("Vacuum Forming", 89.4)]
    },
    "Product": {
        "gain": [("Product X248", 121.0), ("Product X418", 116.4), ("Product X277", 107.5)],
        "loss": [("Product X620D", 78.3), ("Product V15", 83.9), ("Product V12", 89.1)]
    }
}

def render_panel(title, category_key):
    gain_list = MOCK_DATA[category_key]["gain"]
    loss_list = MOCK_DATA[category_key]["loss"]
    
    html_parts = []
    html_parts.append('<div class="dash-card">')
    html_parts.append(f'<div class="panel-title">{title}</div>')
    html_parts.append('<div class="panel-split">')
    
    # Left Side: Top 3 Gain
    html_parts.append('<div class="panel-col">')
    html_parts.append(f'<div class="col-header text-green">Top 3 Gain {category_key}s</div>')
    
    for name, eff in gain_list:
        # Scale progress bar relative to a max visualization boundary (e.g., 125%)
        bar_width = min(100, (eff / 125.0) * 100)
        html_parts.append(f"""
        <div class="rank-item">
            <div class="rank-text-row">
                <span class="rank-name" title="{name}">{name}</span>
                <span class="metric-value text-green">{eff:.1f}%</span>
            </div>
            <div class="bar-bg"><div class="bar-fill-green" style="width: {bar_w}%;"></div></div>
        </div>
        """.replace("{name}", name).replace("{eff:.1f}", f"{eff:.1f}").replace("{bar_w}", f"{bar_width:.1f}").strip())
        
    html_parts.append('</div>')
    
    # Right Side: Top 3 Loss
    html_parts.append('<div class="panel-col">')
    html_parts.append(f'<div class="col-header text-red">Top 3 Loss {category_key}s</div>')
    
    for name, eff in loss_list:
        # Scale progress bar relative to a max visualization boundary (e.g., 100%)
        bar_width = min(100, (eff / 100.0) * 100)
        html_parts.append(f"""
        <div class="rank-item">
            <div class="rank-text-row">
                <span class="rank-name" title="{name}">{name}</span>
                <span class="metric-value text-red">{eff:.1f}%</span>
            </div>
            <div class="bar-bg"><div class="bar-fill-red" style="width: {bar_w}%;"></div></div>
        </div>
        """.replace("{name}", name).replace("{eff:.1f}", f"{eff:.1f}").replace("{bar_w}", f"{bar_width:.1f}").strip())
        
    html_parts.append('</div>')
    html_parts.append('</div>')
    html_parts.append('</div>')
    
    return "".join(html_parts)

panel1, panel2, panel3 = st.columns(3, gap="medium")

with panel1:
    st.markdown(render_panel("Supplier Performance", "Supplier"), unsafe_allow_html=True)
    
with panel2:
    st.markdown(render_panel("Tooling Type Performance", "Tooling Type"), unsafe_allow_html=True)
    
with panel3:
    st.markdown(render_panel("Product Performance", "Product"), unsafe_allow_html=True)