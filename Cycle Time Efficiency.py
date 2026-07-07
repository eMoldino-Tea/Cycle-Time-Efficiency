import streamlit as st
import streamlit.components.v1 as components
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

/* Hide Streamlit Defaults Safely */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background-color: transparent !important;}

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

/* Streamlit Native Container Overrides */
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
.text-yellow { color: #eab308 !important; }
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
.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #ffffff;
    margin-top: 1rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #2d3748;
}

/* Tab Overrides */
[data-testid="stTabs"] button {
    font-size: 1.1rem;
    font-weight: 600;
}

/* Ensure buttons align perfectly regardless of text wrap */
[data-testid="stButton"] button {
    min-height: 3.5rem;
}

/* Print formatting: Hide sidebar and specific UI elements during PDF export */
@media print {
    [data-testid="stSidebar"], header, footer, button, [data-testid="stToolbar"], .stDeployButton, [data-testid="stHeader"] {
        display: none !important;
    }
    html, body, .stApp, section.main, .main, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
        background-color: transparent !important;
        overflow: visible !important;
        height: auto !important;
        max-height: none !important;
        position: static !important;
        display: block !important;
    }
    .block-container {
        padding: 10mm !important;
        max-width: 100% !important;
        overflow: visible !important;
        position: static !important;
    }
    /* Force all tabs to display in print */
    [data-baseweb="tab-panel"], div[role="tabpanel"], .stTabs [role="tabpanel"] {
        display: block !important;
        visibility: visible !important;
        position: static !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
        opacity: 1 !important;
        width: 100% !important;
        page-break-after: always !important;
    }
    /* Hide tab buttons */
    [data-baseweb="tab-list"], div[role="tablist"] {
        display: none !important;
    }
    /* Prevent squishing and cutting across page breaks */
    .element-container, .stVerticalBlock, .dash-card, [data-testid="stVerticalBlockBorderWrapper"], div.stPlotlyChart {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
        overflow: visible !important;
    }
    /* Force tables to expand to full height for printing */
    div[data-testid="stDataFrame"], div[data-testid="stDataFrame"] > div, div[data-testid="stDataFrame"] iframe {
        max-height: none !important;
        height: auto !important;
        overflow: visible !important;
        position: static !important;
    }
    /* Fix Plotly charts shrinking */
    .js-plotly-plot, .plotly, .js-plotly-plot .plot-container {
        width: 100% !important;
        height: auto !important;
        min-height: 350px !important;
        overflow: visible !important;
    }
    /* Ensure Modals/Dialogs expand properly */
    div[role="dialog"] {
        position: static !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
        transform: none !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    div[data-testid="stModal"] {
        position: static !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
    }
    div[data-testid="stModalBackdrop"] {
        position: static !important;
        background-color: transparent !important;
    }
    h1, h2, h3, .panel-title, .section-title, .dash-header {
        page-break-after: avoid !important;
        break-after: avoid !important;
    }
    @page {
        size: landscape;
        margin: 10mm;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. MATHEMATICALLY STRICT DATA LOADING
# ==========================================
@st.cache_data
def load_base_data():
    np.random.seed(42)
    
    T_GAIN_HRS = 15.2 
    T_LOSS_HRS = 3.0833333333333335 
    T_GAIN_SHOTS = 12553725
    T_LOSS_SHOTS = 5342431
    T_FIN_GAIN = 1688
    T_FIN_LOSS = 1712
    
    T_USED_FAST_MINS = 7337 
    T_USED_SLOW_MINS = 1457 
    
    N_FAST = 300
    N_SLOW = 150
    N_WITHIN = 600

    def generate_blended(f_items, s_items, w_items, counts):
        arr = np.concatenate([
            np.random.choice(f_items, counts[0]),
            np.random.choice(s_items, counts[1]),
            np.random.choice(w_items, counts[2])
        ])
        np.random.shuffle(arr)
        return arr

    sup_f_items = ['Foxconn', 'Jabil', 'Flex']
    sup_s_items = ['Sanmina', 'Pegatron', 'Celestica']
    sup_w_items = ['Supplier Alpha', 'Neutral Corp']
    
    suppliers_f = generate_blended(sup_f_items, sup_s_items, sup_w_items, (260, 16, 24))
    suppliers_s = generate_blended(sup_f_items, sup_s_items, sup_w_items, (16, 120, 14))
    suppliers_w = generate_blended(sup_f_items, sup_s_items, sup_w_items, (32, 8, 560))

    tt_f_items = ['Injection Molding', 'High Pressure Die Casting', 'Progressive Stamping']
    tt_s_items = ['Thermoforming', 'Blow Molding', 'Vacuum Forming']
    tt_w_items = ['Compression Molding', 'Rubber Molding', 'Silicone Molding']
    
    tooling_f = generate_blended(tt_f_items, tt_s_items, tt_w_items, (260, 16, 24))
    tooling_s = generate_blended(tt_f_items, tt_s_items, tt_w_items, (16, 120, 14))
    tooling_w = generate_blended(tt_f_items, tt_s_items, tt_w_items, (32, 8, 560))

    prod_f_items = ['Product X248', 'Product X277', 'Product X418']
    prod_s_items = ['Product X620D', 'Product V15', 'Product V12']
    prod_w_items = ['Product Y99', 'Product Z11']
    
    products_f = generate_blended(prod_f_items, prod_s_items, prod_w_items, (260, 16, 24))
    products_s = generate_blended(prod_f_items, prod_s_items, prod_w_items, (16, 120, 14))
    products_w = generate_blended(prod_f_items, prod_s_items, prod_w_items, (32, 8, 560))

    p_fast = [f"Part-{i:03d}" for i in range(1, 9)]
    p_slow = [f"Part-{i:03d}" for i in range(9, 17)]
    p_within = [f"Part-{i:03d}" for i in range(17, 25)]

    parts_f = generate_blended(p_fast, p_slow, p_within, (260, 16, 24))
    parts_s = generate_blended(p_fast, p_slow, p_within, (16, 120, 14))
    parts_w = generate_blended(p_fast, p_slow, p_within, (32, 8, 560))
    
    toolings_f = [f"TL-{np.random.randint(1, 15):03d}" for _ in range(N_FAST)]
    toolings_s = [f"TL-{np.random.randint(15, 25):03d}" for _ in range(N_SLOW)]
    toolings_w = [f"TL-{np.random.randint(25, 41):03d}" for _ in range(N_WITHIN)]

    b_sup_f = {'Foxconn': 1.6, 'Jabil': 0.9, 'Flex': 0.5}
    b_tool_f = {'Injection Molding': 1.4, 'High Pressure Die Casting': 1.0, 'Progressive Stamping': 0.6}
    b_prod_f = {'Product X248': 1.25, 'Product X277': 1.05, 'Product X418': 0.7}
    w_gain_f = np.array([b_sup_f.get(s, 1.0) * b_tool_f.get(t, 1.0) * b_prod_f.get(p, 1.0) for s, t, p in zip(suppliers_f, tooling_f, products_f)])
    w_gain_f /= w_gain_f.sum() 
    w_used_f = np.random.uniform(0.9, 1.1, N_FAST)
    w_used_f /= w_used_f.sum() 
    
    b_sup_s = {'Sanmina': 1.6, 'Pegatron': 0.9, 'Celestica': 0.5}
    b_tool_s = {'Thermoforming': 1.4, 'Blow Molding': 1.0, 'Vacuum Forming': 0.6}
    b_prod_s = {'Product X620D': 1.25, 'Product V15': 1.05, 'Product V12': 0.7}
    w_loss_s = np.array([b_sup_s.get(s, 1.0) * b_tool_s.get(t, 1.0) * b_prod_s.get(p, 1.0) for s, t, p in zip(suppliers_s, tooling_s, products_s)])
    w_loss_s /= w_loss_s.sum() 
    w_used_s = np.random.uniform(0.9, 1.1, N_SLOW)
    w_used_s /= w_used_s.sum() 

    def exact_distribute(target_int, weights):
        floored = np.floor(weights * target_int).astype(int)
        remainder = int(target_int - floored.sum())
        if remainder > 0:
            fractions = (weights * target_int) - floored
            indices = np.argsort(fractions)[::-1]
            for i in range(remainder):
                floored[indices[i]] += 1
        return floored

    gain_mins = exact_distribute(912, w_gain_f) 
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
        'Product': products_f,
        'Part': parts_f,
        'Tooling': toolings_f
    })
    df_fast['Expected_Hours'] = df_fast['Used_Hours'] + df_fast['Gain_Hours']

    loss_mins = exact_distribute(185, w_loss_s) 
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
        'Product': products_s,
        'Part': parts_s,
        'Tooling': toolings_s
    })
    df_slow['Expected_Hours'] = df_slow['Used_Hours'] - df_slow['Loss_Hours']
    
    df_within = pd.DataFrame({
        'Tolerance_Status': ['Within'] * N_WITHIN,
        'Gain_Hours': 0.0,
        'Loss_Hours': 0.0,
        'Shots_Gained': 0.0,
        'Shots_Lost': 0.0,
        'Expected_Hours': np.random.uniform(0.1, 0.4, N_WITHIN),
        'Base_Fin_Gain': 0.0,
        'Base_Fin_Loss': 0.0,
        'Supplier': suppliers_w,
        'Tooling Type': tooling_w,
        'Product': products_w,
        'Part': parts_w,
        'Tooling': toolings_w
    })
    df_within['Used_Hours'] = df_within['Expected_Hours']
    
    data = pd.concat([df_fast, df_slow, df_within], ignore_index=True)
    
    data['Total_Shots'] = data['Shots_Gained'] + data['Shots_Lost']
    data.loc[data['Tolerance_Status'] == 'Within', 'Total_Shots'] = np.random.randint(100, 1000, N_WITHIN)
    data['ACT'] = (data['Expected_Hours'] * 3600) / data['Total_Shots']
    data['Actual_CT'] = (data['Used_Hours'] * 3600) / data['Total_Shots']
    data['Efficiency_%'] = np.where(data['Used_Hours'] > 0, (data['Expected_Hours'] / data['Used_Hours']) * 100, 0)
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=89)
    date_offsets = np.random.randint(0, 90, len(data))
    data['Date'] = [start_date + timedelta(days=int(x)) for x in date_offsets]
    
    data['OEM Business Division'] = np.random.choice(['NA Auto', 'EU Consumer', 'APAC Enterprise', 'LATAM Industrial'], len(data))
    data['Toolmaker'] = np.random.choice(['TM-A', 'TM-B', 'TM-C', 'TM-D'], len(data))
    data['Plant'] = np.random.choice(['Plant 1 (MX)', 'Plant 2 (DE)', 'Plant 3 (CN)', 'Plant 4 (VN)'], len(data))
    
    part_names_pool = [
        'Unused', 'Housing Top', 'Housing Bottom', 'Display Lens', 'Battery Bracket',
        'Main Chassis', 'Camera Frame', 'Speaker Grill', 'Mic Mesh', 'Antenna Band',
        'Haptic Motor', 'USB Port', 'Power Key', 'Volume Key', 'SIM Slot',
        'Bezel', 'Rear Glass', 'Cooling Pad', 'EMI Shield', 'Biometric Scanner',
        'IR Sensor', 'Flash Module', 'Charging Coil', 'NFC Tag', 'Vapor Chamber'
    ]
    data['Part Name'] = data['Part'].apply(lambda x: part_names_pool[int(x.split('-')[1])])
    
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

filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### Financial Parameters")
labor_rate = st.sidebar.number_input("Labor Rate ($/hour)", min_value=0.0, value=40.0, step=1.0)
machine_rate = st.sidebar.number_input("Machine Rate ($/hour)", min_value=0.0, value=180.0, step=1.0)
combined_rate = labor_rate + machine_rate

rate_scalar = combined_rate / 220.0
filtered_df['Active_Rate'] = combined_rate
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
# 5. GLOBAL CALCULATIONS & HELPERS
# ==========================================
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
eff_within = calc_weighted_eff(filtered_df[filtered_df['Tolerance_Status'] == 'Within'])

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

disp_eff_fast = f"+{eff_fast:.2f}%" if pd.notna(eff_fast) else "N/A"
disp_eff_slow = f"-{abs(100 - eff_slow):.2f}%" if pd.notna(eff_slow) else "N/A" 

def build_html(*lines):
    return "".join(line.strip() for line in lines)

def export_pdf_ui():
    components.html(
        """
        <div style="text-align: right; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <button onclick="printApp()" style="background-color: #1e293b; color: #f8fafc; border: 1px solid #475569; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600;">
                Export to PDF
            </button>
        </div>
        <script>
        function printApp() {
            const p = window.parent;
            const d = p.document;
            const panels = d.querySelectorAll('[role="tabpanel"]');
            
            // Unhide all tabs globally before printing
            panels.forEach(tp => {
                tp.setAttribute('data-print-original-display', tp.style.display || '');
                tp.style.display = 'block';
                tp.style.visibility = 'visible';
                tp.style.height = 'auto';
                tp.style.position = 'static';
                tp.style.opacity = '1';
            });
            
            // Dispatch resize so Plotly draws the SVG layers fully 
            p.dispatchEvent(new Event('resize'));
            
            // Wait for charts to redraw, open print modal, then revert
            setTimeout(() => {
                p.print();
                panels.forEach(tp => {
                    tp.style.display = tp.getAttribute('data-print-original-display');
                    tp.style.visibility = '';
                    tp.style.height = '';
                    tp.style.position = '';
                    tp.style.opacity = '';
                });
                p.dispatchEvent(new Event('resize'));
            }, 1200);
        }
        </script>
        """,
        height=50
    )

def compute_comprehensive_row(name, group, group_col):
    tot_shots = group['Total_Shots'].sum()
    parts_prod = tot_shots * 1.67
    act = np.average(group['ACT'], weights=group['Total_Shots']) if tot_shots > 0 else 0
    wact = np.average(group['Actual_CT'], weights=group['Total_Shots']) if tot_shots > 0 else 0
    ct_diff = wact - act 
    
    tot_exp_hrs = group['Expected_Hours'].sum()
    tot_act_hrs = group['Used_Hours'].sum()

    fast_grp = group[group['Tolerance_Status']=='Fast']
    slow_grp = group[group['Tolerance_Status']=='Slow']
    neu_grp = group[group['Tolerance_Status']=='Within']

    fast_shots = fast_grp['Total_Shots'].sum()
    slow_shots = slow_grp['Total_Shots'].sum()
    neu_shots = neu_grp['Total_Shots'].sum()

    fast_pct = (fast_shots/tot_shots*100) if tot_shots > 0 else 0
    slow_pct = (slow_shots/tot_shots*100) if tot_shots > 0 else 0
    neu_pct = (neu_shots/tot_shots*100) if tot_shots > 0 else 0

    wact_fast = np.average(fast_grp['Actual_CT'], weights=fast_grp['Total_Shots']) if fast_shots > 0 else 0
    wact_slow = np.average(slow_grp['Actual_CT'], weights=slow_grp['Total_Shots']) if slow_shots > 0 else 0

    exp_fast = fast_grp['Expected_Hours'].sum()
    exp_slow = slow_grp['Expected_Hours'].sum()
    act_fast = fast_grp['Used_Hours'].sum()
    act_slow = slow_grp['Used_Hours'].sum()

    hrs_gain = group['Gain_Hours'].sum()
    hrs_lost = group['Loss_Hours'].sum()
    shots_gain = group['Shots_Gained'].sum()
    shots_lost = group['Shots_Lost'].sum()
    fin_gain = group['Financial_Gain'].sum()
    fin_loss = group['Financial_Loss'].sum()
    net_fin = fin_gain - fin_loss

    ct_eff_fast = (exp_fast/act_fast*100) if act_fast > 0 else np.nan
    ct_eff_slow = (exp_slow/act_slow*100) if act_slow > 0 else np.nan
    ct_eff_wt = (tot_exp_hrs/tot_act_hrs*100) if tot_act_hrs > 0 else np.nan

    # 3-color strict mapping
    if pd.isna(ct_eff_wt):
        perf_status = 'Within'
    elif ct_eff_wt > 105:
        perf_status = 'Fast'
    elif ct_eff_wt < 95:
        perf_status = 'Slow'
    else:
        perf_status = 'Within'

    row = {
        group_col: name,
        'Time Period': f"{start_date.date()} to {end_date.date()}",
        'Part': group['Part'].iloc[0] if not group.empty else "",
        'Product': group['Product'].iloc[0] if not group.empty else "",
        'Part Name': group['Part Name'].iloc[0] if not group.empty else "",
        'Hourly Rate': group['Active_Rate'].iloc[0] if not group.empty else 0,
        'Total Shots': tot_shots,
        'Parts Produced': parts_prod,
        'ACT': act,
        'Actual Average CT (WACT)': wact,
        'CT Difference': ct_diff,
        'Total Expected Hours': tot_exp_hrs,
        'Total Actual Hours': tot_act_hrs,
        'Fast Shots (%)': fast_pct,
        'Slow Shots (%)': slow_pct,
        'Within Shots (%)': neu_pct,
        'WACT (Fast)': wact_fast,
        'WACT (Slow)': wact_slow,
        'Expected Hours (Fast)': exp_fast,
        'Expected Hours (Slow)': exp_slow,
        'Actual Hours (Fast)': act_fast,
        'Actual Hours (Slow)': act_slow,
        'Hours Gained': hrs_gain,
        'Hours Lost': hrs_lost,
        'Shots Gained': shots_gain,
        'Shots Lost': shots_lost,
        'Financial Gain': fin_gain,
        'Financial Loss': fin_loss,
        'Net Financial': net_fin,
        'CT Efficiency of Fast Hours': ct_eff_fast,
        'CT Efficiency of Slow Hours': ct_eff_slow,
        'CT Weighted Average Efficiency': ct_eff_wt,
        'Performance Status': perf_status
    }
    
    if group_col == 'Tooling ID':
        row['Supplier'] = group['Supplier'].iloc[0] if not group.empty else ""
        row['Plant'] = group['Plant'].iloc[0] if not group.empty else ""
    elif group_col == 'Supplier':
        row['Total Toolings'] = group['Tooling'].nunique()

    return pd.Series(row)

# Strict detailed column config mappings
detail_col_config = {
    "Total Shots": st.column_config.NumberColumn(format="%d"),
    "Parts Produced": st.column_config.NumberColumn(format="%d"),
    "ACT": st.column_config.NumberColumn(format="%.2f"),
    "Actual Average CT (WACT)": st.column_config.NumberColumn(format="%.2f"),
    "CT Difference": st.column_config.NumberColumn(format="%.2f"),
    "Total Expected Hours": st.column_config.NumberColumn(format="%.2f"),
    "Total Actual Hours": st.column_config.NumberColumn(format="%.2f"),
    "Fast Shots (%)": st.column_config.NumberColumn(format="%.2f%%"),
    "Slow Shots (%)": st.column_config.NumberColumn(format="%.2f%%"),
    "Within Shots (%)": st.column_config.NumberColumn(format="%.2f%%"),
    "WACT (Fast)": st.column_config.NumberColumn(format="%.2f"),
    "WACT (Slow)": st.column_config.NumberColumn(format="%.2f"),
    "Expected Hours (Fast)": st.column_config.NumberColumn(format="%.2f"),
    "Expected Hours (Slow)": st.column_config.NumberColumn(format="%.2f"),
    "Actual Hours (Fast)": st.column_config.NumberColumn(format="%.2f"),
    "Actual Hours (Slow)": st.column_config.NumberColumn(format="%.2f"),
    "Hours Gained": st.column_config.NumberColumn(format="%.2f"),
    "Hours Lost": st.column_config.NumberColumn(format="%.2f"),
    "Shots Gained": st.column_config.NumberColumn(format="%d"),
    "Shots Lost": st.column_config.NumberColumn(format="%d"),
    "Financial Gain": st.column_config.NumberColumn(format="$%.0f"),
    "Financial Loss": st.column_config.NumberColumn(format="$%.0f"),
    "Net Financial": st.column_config.NumberColumn(format="$%.0f"),
    "CT Efficiency of Fast Hours": st.column_config.NumberColumn(format="%.2f%%"),
    "CT Efficiency of Slow Hours": st.column_config.NumberColumn(format="%.2f%%"),
    "CT Weighted Average Efficiency": st.column_config.NumberColumn(format="%.2f%%")
}


# ==========================================
# 6. HELPER RENDERERS (To prevent nested dialog error)
# ==========================================
def render_entity_details(entity_type, entity_name):
    st.markdown(f"### Detailed Analysis: `{entity_name}`")
    df_drill = filtered_df[filtered_df[entity_type] == entity_name].copy()
    if df_drill.empty:
        st.warning("No data found.")
        return

    drill_eff = calc_weighted_eff(df_drill)
    drill_gain_h = df_drill['Gain_Hours'].sum()
    drill_loss_h = df_drill['Loss_Hours'].sum()
    drill_net_fin = df_drill['Financial_Gain'].sum() - df_drill['Financial_Loss'].sum()
    drill_fin_sign = "-$" if drill_net_fin < 0 else "$"
    
    dkpi1, dkpi2, dkpi3, dkpi4 = st.columns(4)
    dkpi1.metric("Overall Cycle Time Efficiency %", f"{drill_eff:.1f}%" if pd.notna(drill_eff) else "N/A")
    dkpi2.metric("Total Hours Gained (Fast)", format_hm(drill_gain_h))
    dkpi3.metric("Total Hours Lost (Slow)", format_hm(drill_loss_h))
    dkpi4.metric("Net Financial", f"{drill_fin_sign}{abs(drill_net_fin):,.0f}")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    t_col1, t_col2 = st.columns(2, gap="large")
    with t_col1:
        st.markdown("**Historical Trend: Cycle Time Efficiency %**")
        trend_df = df_drill.groupby('Date')[['Expected_Hours', 'Used_Hours']].sum().reset_index()
        trend_df['Efficiency_%'] = np.where(trend_df['Used_Hours'] > 0, (trend_df['Expected_Hours'] / trend_df['Used_Hours']) * 100, 0)
        fig_dt = px.line(trend_df, x='Date', y='Efficiency_%', markers=True)
        fig_dt.add_hline(y=100, line_dash="dash", line_color="#94a3b8")
        fig_dt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=20, t=10, b=10), height=300, legend_title_text='')
        st.plotly_chart(fig_dt, use_container_width=True)
        
    with t_col2:
        st.markdown("**Efficiency Distribution**")
        fast_sim = df_drill[df_drill['Tolerance_Status'] == 'Fast']['Total_Shots'].sum()
        slow_sim = df_drill[df_drill['Tolerance_Status'] == 'Slow']['Total_Shots'].sum()
        within_sim = df_drill[df_drill['Tolerance_Status'] == 'Within']['Total_Shots'].sum()
        var_df = pd.DataFrame({'Tolerance_Status': ['Within', 'Slow', 'Fast'], 'Total_Shots': [within_sim, slow_sim, fast_sim]})
        
        fig_dv = px.pie(var_df, names='Tolerance_Status', values='Total_Shots', color='Tolerance_Status', color_discrete_map={'Within': '#5cb85c', 'Slow': '#eab308', 'Fast': '#d9534f'}, hole=0.4)
        fig_dv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=20, t=10, b=10), height=300, legend_title_text='')
        st.plotly_chart(fig_dv, use_container_width=True)

    st.markdown("**Detailed Benchmark & Operations Breakdown**")
    comp_rows = [compute_comprehensive_row(name, group, 'Tooling ID') for name, group in df_drill.groupby('Tooling')]
    if comp_rows:
        df_comp_table = pd.DataFrame(comp_rows)
        df_comp_table.sort_values(by='CT Weighted Average Efficiency', ascending=True, inplace=True)
        cols = ['Tooling ID', 'Supplier', 'Plant', 'Time Period', 'Part', 'Product', 'Part Name', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
        df_comp_table = df_comp_table[[c for c in cols if c in df_comp_table.columns]]
        st.dataframe(df_comp_table, use_container_width=True, hide_index=True, column_config=detail_col_config)
        
        if entity_type != 'Tooling':
            st.markdown("<br>", unsafe_allow_html=True)
            c_dr, c_btn = st.columns([3, 1])
            with c_dr:
                tool_sel = st.selectbox("Select a Tooling ID to view details:", ["(No Selection)"] + sorted(df_comp_table['Tooling ID'].unique().tolist()), key=f"red_tool_{entity_type}_{str(entity_name).replace(' ', '_')}")
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                view_clicked = st.button("View Tool Details", key=f"red_btn_{entity_type}_{str(entity_name).replace(' ', '_')}")
                
            if tool_sel != "(No Selection)":
                if view_clicked:
                    st.session_state[f"st_red_{entity_type}_{str(entity_name).replace(' ', '_')}"] = tool_sel
                if st.session_state.get(f"st_red_{entity_type}_{str(entity_name).replace(' ', '_')}") == tool_sel:
                    st.markdown("<hr>", unsafe_allow_html=True)
                    render_entity_details("Tooling", tool_sel)
    else:
        st.info("No detailed breakdown available.")

def render_ranking_tooling_drilldown(entity_type, entity_name):
    st.markdown(f"### Tooling Details for {entity_type}: `{entity_name}`")
    df_sub = filtered_df[filtered_df[entity_type] == entity_name]
    
    tot_tools = df_sub['Tooling'].nunique()
    tot_parts = df_sub['Part'].nunique()
    net_fin = df_sub['Financial_Gain'].sum() - df_sub['Financial_Loss'].sum()
    status_word = "losing" if net_fin < 0 else "gaining"
    st.markdown(f"*{entity_name} has **{tot_tools} tools**, making **{tot_parts} distinct parts**, and is {status_word} **${abs(net_fin):,.0f}** overall.*")
    
    comp_rows = [compute_comprehensive_row(name, group, 'Tooling ID') for name, group in df_sub.groupby('Tooling')]
    if comp_rows:
        df_detail = pd.DataFrame(comp_rows)
        df_detail.sort_values(by='CT Weighted Average Efficiency', ascending=True, inplace=True)
        cols = ['Tooling ID', 'Supplier', 'Plant', 'Time Period', 'Part', 'Product', 'Part Name', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
        df_detail = df_detail[[c for c in cols if c in df_detail.columns]]
        st.dataframe(df_detail, use_container_width=True, hide_index=True, column_config=detail_col_config)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            tool_sel = st.selectbox("Select a Tooling ID to view details:", ["(No Selection)"] + sorted(df_sub['Tooling'].unique().tolist()), key=f"rk_tool_inline_{entity_name.replace(' ', '_')}")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            view_clicked = st.button("View Tool Details", key=f"rk_btn_inline_{entity_name.replace(' ', '_')}")
            
        if tool_sel != "(No Selection)":
            if view_clicked:
                st.session_state[f"st_rk_inline_{entity_name}"] = tool_sel
            if st.session_state.get(f"st_rk_inline_{entity_name}") == tool_sel:
                st.markdown("<hr>", unsafe_allow_html=True)
                render_entity_details("Tooling", tool_sel)
    else:
        st.info("No toolings found.")

# ==========================================
# 7. DIALOGS & POPUPS 
# ==========================================
@st.dialog("Widget Breakdown Details", width="large")
def widget_drilldown_dialog(status_type):
    st.markdown(f"### {status_type} Performance Breakdown")
    target_status = 'Fast' if status_type == 'Gained' else 'Slow'
    df_sub = filtered_df[filtered_df['Tolerance_Status'] == target_status]
    
    if df_sub.empty:
        st.info(f"No {status_type.lower()} data available.")
        return
    
    comp_rows = [compute_comprehensive_row(name, group, 'Tooling ID') for name, group in df_sub.groupby('Tooling')]
    df_detail = pd.DataFrame(comp_rows)
    df_detail.sort_values(by='CT Weighted Average Efficiency', ascending=True, inplace=True)
    
    cols = ['Tooling ID', 'Supplier', 'Plant', 'Time Period', 'Part', 'Product', 'Part Name', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
    df_detail = df_detail[[c for c in cols if c in df_detail.columns]]
    st.dataframe(df_detail, use_container_width=True, hide_index=True, column_config=detail_col_config)

    st.markdown("<br>", unsafe_allow_html=True)
    c_dr, c_btn = st.columns([3, 1])
    with c_dr:
        tool_sel = st.selectbox("Select a Tooling ID to view details:", ["(No Selection)"] + sorted(df_detail['Tooling ID'].unique().tolist()), key=f"wd_tool_{status_type}")
    with c_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        view_clicked = st.button("View Tool Details", key=f"wd_btn_{status_type}")
        
    if tool_sel != "(No Selection)":
        if view_clicked:
            st.session_state[f"st_wd_{status_type}"] = tool_sel
        if st.session_state.get(f"st_wd_{status_type}") == tool_sel:
            st.markdown("<hr>", unsafe_allow_html=True)
            render_entity_details("Tooling", tool_sel)

@st.dialog("All Entity Performance", width="large")
def see_all_entities_dialog(category):
    st.markdown(f"### Complete {category} Performance")
    df_rank = generate_ranking_table_data(filtered_df, category)
    
    if df_rank.empty:
        st.info("No data available.")
        return

    fig = px.bar(
        df_rank, 
        x=category, 
        y='Overall Efficiency %', 
        color='Performance Status',
        color_discrete_map={"Within": "#5cb85c", "Slow": "#eab308", "Fast": "#d9534f"},
        text='Overall Efficiency %',
        title=f"All {category}s (Sorted Worst to Best)"
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#334155'), margin=dict(l=0, r=20, t=40, b=10), height=400, legend_title_text='')
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_rank, use_container_width=True, hide_index=True, column_config=common_ranking_col_config)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c_dr, c_btn = st.columns([3, 1])
    with c_dr:
        drill_item = st.selectbox("Select to view 'Total Toolings' breakdown:", ["(No Selection)"] + df_rank[category].tolist(), key=f"all_ent_drill_{category}")
    with c_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        view_clicked = st.button("View Toolings", key=f"btn_all_ent_{category}")
        
    if drill_item != "(No Selection)":
        if view_clicked:
            st.session_state[f"st_modal_ent_{category}"] = drill_item
        if st.session_state.get(f"st_modal_ent_{category}") == drill_item:
            st.markdown("<hr>", unsafe_allow_html=True)
            render_ranking_tooling_drilldown(category, drill_item)

@st.dialog("Entity Performance Details", width="large")
def entity_drilldown_dialog(entity_type, entity_name):
    render_entity_details(entity_type, entity_name)

@st.dialog("Total Toolings Detail Breakdown", width="large")
def ranking_tooling_drilldown_dialog(entity_type, entity_name):
    render_ranking_tooling_drilldown(entity_type, entity_name)

@st.dialog("Total Toolings Breakdown", width="large")
def total_toolings_dialog(supplier_name, df_subset):
    st.markdown(f"### Tooling Details for Supplier: `{supplier_name}`")
    supp_df = df_subset[df_subset['Supplier'] == supplier_name]
    comp_rows = [compute_comprehensive_row(name, group, 'Tooling ID') for name, group in supp_df.groupby('Tooling')]
    if comp_rows:
        df_detail = pd.DataFrame(comp_rows)
        df_detail.sort_values(by='CT Weighted Average Efficiency', ascending=True, inplace=True)
        cols = ['Tooling ID', 'Supplier', 'Plant', 'Time Period', 'Part', 'Product', 'Part Name', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
        df_detail = df_detail[[c for c in cols if c in df_detail.columns]]
        st.dataframe(df_detail, use_container_width=True, hide_index=True, column_config=detail_col_config)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            tool_sel = st.selectbox("Select Tooling ID to view details:", ["(No Selection)"] + sorted(supp_df['Tooling'].unique().tolist()), key=f"sp_tool_{supplier_name.replace(' ', '_')}")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            view_clicked = st.button("View Tool Details", key=f"sp_btn_{supplier_name.replace(' ', '_')}")
            
        if tool_sel != "(No Selection)":
            if view_clicked:
                st.session_state[f"st_sp_{supplier_name}"] = tool_sel
            if st.session_state.get(f"st_sp_{supplier_name}") == tool_sel:
                st.markdown("<hr>", unsafe_allow_html=True)
                render_entity_details("Tooling", tool_sel)
    else:
        st.info("No toolings found.")

def generate_ranking_table_data(df, col):
    def _agg_func(x):
        res = {
            'Total Toolings': x['Tooling'].nunique(),
            'Hours Gained': x['Gain_Hours'].sum(),
            'Hours Lost': x['Loss_Hours'].sum(),
            'Net Hours': x['Gain_Hours'].sum() - x['Loss_Hours'].sum(),
            'Shots Gained': x['Shots_Gained'].sum(),
            'Shots Lost': x['Shots_Lost'].sum(),
            'Net Shots': x['Shots_Gained'].sum() - x['Shots_Lost'].sum(),
            'Financial Gained': x['Financial_Gain'].sum(),
            'Financial Lost': x['Financial_Loss'].sum(),
            'Net Financial': x['Financial_Gain'].sum() - x['Financial_Loss'].sum(),
            'Overall Efficiency %': calc_weighted_eff(x)
        }
        if col == 'Part':
            res['Product'] = x['Product'].iloc[0] if not x.empty else ""
        return pd.Series(res)

    agg = df.groupby(col).apply(_agg_func).reset_index()
    
    agg.sort_values(by='Overall Efficiency %', ascending=True, inplace=True)
    agg.insert(0, 'Rank', range(1, len(agg) + 1))

    if col == 'Part' and 'Product' in agg.columns:
        col_order = list(agg.columns)
        col_order.remove('Product')
        part_idx = col_order.index('Part')
        col_order.insert(part_idx + 1, 'Product')
        agg = agg[col_order]
    
    agg['Performance Status'] = agg['Overall Efficiency %'].apply(lambda x: 'Fast' if pd.notna(x) and x > 105 else ('Slow' if pd.notna(x) and x < 95 else 'Within'))
    return agg

common_ranking_col_config = {
    "Hours Gained": st.column_config.NumberColumn(format="%.2f"),
    "Hours Lost": st.column_config.NumberColumn(format="%.2f"),
    "Net Hours": st.column_config.NumberColumn(format="%.2f"),
    "Shots Gained": st.column_config.NumberColumn(format="%d"),
    "Shots Lost": st.column_config.NumberColumn(format="%d"),
    "Net Shots": st.column_config.NumberColumn(format="%d"),
    "Financial Gained": st.column_config.NumberColumn(format="$%.0f"),
    "Financial Lost": st.column_config.NumberColumn(format="$%.0f"),
    "Net Financial": st.column_config.NumberColumn(format="$%.0f"),
    "Overall Efficiency %": st.column_config.NumberColumn(format="%.2f%%")
}

# ==========================================
# 8. MAIN UI LAYOUT
# ==========================================
st.markdown('<div class="dash-header">Cycle Time Efficiency</div>', unsafe_allow_html=True)

filter_dict = {
    "OEM Business Division": selected_oem,
    "Supplier": selected_supplier,
    "Toolmaker": selected_toolmaker,
    "Plant": selected_plant,
    "Tooling Type": selected_tooling_type,
    "Product": selected_product,
    "Part": selected_part,
    "Tooling": selected_tooling
}

filter_tags = []
for name, vals in filter_dict.items():
    if vals:
        val_str = ", ".join([str(v) for v in vals])
        filter_tags.append(
            f"<div style='display: inline-block; background-color: #1e293b; border: 1px solid #475569; color: #e2e8f0; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; margin: 0 8px 8px 0;'>"
            f"<strong style='color: #94a3b8; font-weight: 600;'>{name}:</strong> {val_str}"
            f"</div>"
        )

filters_html = "".join(filter_tags) if filter_tags else "<div style='color: #64748b; font-style: italic; font-size: 0.9rem; padding-top: 4px;'>None (All data included)</div>"

summary_html = f"""
<div style="background-color: #1a1d26; border: 1px solid #2d3748; border-radius: 12px; padding: 16px 24px 8px 24px; margin-bottom: 24px; box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);">
    <div style="display: flex; flex-wrap: wrap; gap: 24px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #2d3748;">
        <div style="font-size: 0.95rem; color: #e2e8f0;"><strong style="color: #94a3b8;">Date Range:</strong> {start_date.date()} to {end_date.date()}</div>
        <div style="font-size: 0.95rem; color: #e2e8f0;"><strong style="color: #94a3b8;">Financial Parameters:</strong> Labor ${labor_rate:.2f}/hr &nbsp;|&nbsp; Machine ${machine_rate:.2f}/hr</div>
    </div>
    <div style="display: flex; align-items: flex-start;">
        <div style="font-size: 0.9rem; font-weight: 600; color: #94a3b8; margin-right: 12px; padding-top: 5px; white-space: nowrap;">Filters:</div>
        <div style="display: flex; flex-wrap: wrap; flex: 1;">
            {filters_html}
        </div>
    </div>
</div>
"""
st.markdown(summary_html, unsafe_allow_html=True)

tab_overview, tab_comp, tab_rankings = st.tabs(["Overview Summary", "Comparison Analysis", "Full Rankings & Details"])

# ----------------------------------------------------
# TAB 1: OVERVIEW SUMMARY
# ----------------------------------------------------
with tab_overview:
    export_pdf_ui()
    col_gain, col_loss = st.columns(2, gap="large")
    
    parts_gained = filtered_df[filtered_df['Tolerance_Status'] == 'Fast']['Part'].nunique()
    tools_gained = filtered_df[filtered_df['Tolerance_Status'] == 'Fast']['Tooling'].nunique()
    
    parts_lost = filtered_df[filtered_df['Tolerance_Status'] == 'Slow']['Part'].nunique()
    tools_lost = filtered_df[filtered_df['Tolerance_Status'] == 'Slow']['Tooling'].nunique()
    
    html_gain = build_html(
        '<div class="dash-card" style="border-top: 4px solid #5cb85c;">', 
        '<div class="kpi-title-container"><span class="kpi-title" style="color: #5cb85c;">Gained (Fast Performance)</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Number of Fast Tools</span><span class="metric-value text-green">{tools_gained:,}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Hours Gained</span><span class="metric-value text-green">{disp_gained_hrs}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Shots Gained</span><span class="metric-value text-green">{disp_gained_shots}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Parts Gained</span><span class="metric-value text-green">{parts_gained:,}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Financial Gain</span><span class="metric-value text-green">{disp_gained_fin}</span></div>', 
        f'<div class="metric-row"><span class="metric-label">Efficiency Gain</span><span class="metric-value text-green">{disp_eff_fast}</span></div>', 
        '</div>'
    )
    col_gain.markdown(html_gain, unsafe_allow_html=True)
    if col_gain.button("View Gained Details", use_container_width=True): widget_drilldown_dialog("Gained")
    
    html_loss = build_html(
        '<div class="dash-card" style="border-top: 4px solid #d9534f;">', 
        '<div class="kpi-title-container"><span class="kpi-title" style="color: #d9534f;">Lost (Slow Performance)</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Number of Slow Tools</span><span class="metric-value text-red">{tools_lost:,}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Hours Lost</span><span class="metric-value text-red">{disp_lost_hrs}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Shots Lost</span><span class="metric-value text-red">{disp_lost_shots}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Parts Lost</span><span class="metric-value text-red">{parts_lost:,}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Financial Loss</span><span class="metric-value text-red">{disp_lost_fin}</span></div>', 
        f'<div class="metric-row"><span class="metric-label">Efficiency Loss</span><span class="metric-value text-red">{disp_eff_slow}</span></div>', 
        '</div>'
    )
    col_loss.markdown(html_loss, unsafe_allow_html=True)
    if col_loss.button("View Lost Details", use_container_width=True): widget_drilldown_dialog("Lost")

    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    def get_combined_stats(df, category):
        if df.empty: return pd.DataFrame()
        grouped = df.groupby(category).apply(lambda x: pd.Series({
            'Expected_Hours': x['Expected_Hours'].sum(),
            'Used_Hours': x['Used_Hours'].sum(),
            'Financial_Gain': x['Financial_Gain'].sum(),
            'Financial_Loss': x['Financial_Loss'].sum()
        })).reset_index()
        grouped['Efficiency_%'] = np.where(grouped['Used_Hours'] > 0, (grouped['Expected_Hours'] / grouped['Used_Hours']) * 100, 0)
        grouped['Net Financial'] = grouped['Financial_Gain'] - grouped['Financial_Loss']
        
        fast_df = grouped[grouped['Efficiency_%'] > 105].sort_values('Efficiency_%', ascending=False).head(3).copy()
        fast_df['Performance Status'] = 'Fast'
        
        slow_df = grouped[grouped['Efficiency_%'] < 95].sort_values('Efficiency_%', ascending=True).head(3).copy()
        slow_df['Performance Status'] = 'Slow'
        
        combined = pd.concat([fast_df, slow_df]).drop_duplicates()
        if combined.empty: return combined
        
        combined.sort_values('Efficiency_%', ascending=True, inplace=True)
        return combined

    def build_combined_plotly_vbar(df, x_col, y_col):
        if df.empty: return None
        fig = go.Figure()
        colors = {"Within": "#5cb85c", "Slow": "#eab308", "Fast": "#d9534f"}
        for status in ["Slow", "Fast"]:
            df_sub = df[df['Performance Status'] == status]
            if not df_sub.empty:
                fig.add_trace(go.Bar(
                    x=df_sub[x_col], y=df_sub[y_col] - 100, base=100,
                    marker_color=colors[status], name=status, text=df_sub[y_col],
                    texttemplate='%{text:.1f}%', textposition='outside'
                ))
        y_range = [min(94, df[y_col].min() * 0.95), max(106, df[y_col].max() * 1.05)]
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#334155', range=y_range, title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8')), xaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)), margin=dict(l=55, r=10, t=20, b=30), height=300, legend_title_text='')
        return fig
        
    def build_combined_plotly_hbar(df, x_col, y_col):
        if df.empty: return None
        fig = go.Figure()
        colors = {"Within": "#5cb85c", "Slow": "#eab308", "Fast": "#d9534f"}
        for status in ["Slow", "Fast"]:
            df_sub = df[df['Performance Status'] == status]
            if not df_sub.empty:
                fig.add_trace(go.Bar(
                    y=df_sub[y_col], x=df_sub[x_col] - 100, base=100, orientation='h',
                    marker_color=colors[status], name=status, text=df_sub[x_col],
                    texttemplate='%{text:.1f}%', textposition='outside'
                ))
        x_range = [min(94, df[x_col].min() * 0.95), max(106, df[x_col].max() * 1.05)]
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#334155', visible=True, range=x_range, title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8')), yaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)), margin=dict(l=0, r=40, t=10, b=30), height=300, legend_title_text='')
        return fig

    def build_combined_plotly_bubble(df, x_col, y_col):
        if df.empty: return None
        df['Bubble_Size'] = abs(df[x_col] - 100)
        df['Bubble_Size'] = df['Bubble_Size'].clip(lower=0.5)
        x_range = [min(94, df[x_col].min() * 0.97), max(106, df[x_col].max() * 1.03)]
        fig = px.scatter(df, x=x_col, y=y_col, size='Bubble_Size', text=x_col, size_max=25, color='Performance Status', color_discrete_map={"Within": "#5cb85c", "Slow": "#eab308", "Fast": "#d9534f"})
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='middle right', marker=dict(line=dict(width=1.5, color='#ffffff')))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#334155', title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8'), range=x_range), yaxis=dict(showgrid=True, gridcolor='#334155', title='', tickfont=dict(color='#e2e8f0', size=13)), margin=dict(l=0, r=40, t=10, b=40), height=300, legend_title_text='')
        return fig

    with st.container(border=True):
        st.markdown('<div class="panel-title">Supplier Performance (Top 3 Fastest & Slowest)</div>', unsafe_allow_html=True)
        supp_combined = get_combined_stats(filtered_df, 'Supplier')
        if not supp_combined.empty:
            fig_supp = build_combined_plotly_vbar(supp_combined, 'Supplier', 'Efficiency_%')
            st.plotly_chart(fig_supp, use_container_width=True, key="supp_combined")
        else:
            st.info("No data available.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            drill_s = st.selectbox("Select Supplier to view details:", ["(No Selection)"] + sorted(filtered_df['Supplier'].unique().tolist()), key="overview_supp_drill")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if drill_s != "(No Selection)" and st.button("View Details", key="btn_ov_supp"):
                entity_drilldown_dialog("Supplier", drill_s)
        
        if st.button("See All Suppliers", use_container_width=True): see_all_entities_dialog('Supplier')

    with st.container(border=True):
        st.markdown('<div class="panel-title">Tooling Type Performance (Top 3 Fastest & Slowest)</div>', unsafe_allow_html=True)
        tool_combined = get_combined_stats(filtered_df, 'Tooling Type')
        if not tool_combined.empty:
            fig_tool = build_combined_plotly_hbar(tool_combined, 'Efficiency_%', 'Tooling Type')
            st.plotly_chart(fig_tool, use_container_width=True, key="tool_combined")
        else:
            st.info("No data available.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            drill_tt = st.selectbox("Select Tooling Type to view details:", ["(No Selection)"] + sorted(filtered_df['Tooling Type'].unique().tolist()), key="overview_tt_drill")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if drill_tt != "(No Selection)" and st.button("View Details", key="btn_ov_tt"):
                entity_drilldown_dialog("Tooling Type", drill_tt)
        
        if st.button("See All Tooling Types", use_container_width=True): see_all_entities_dialog('Tooling Type')

    with st.container(border=True):
        st.markdown('<div class="panel-title">Product Performance (Top 3 Fastest & Slowest)</div>', unsafe_allow_html=True)
        prod_combined = get_combined_stats(filtered_df, 'Product')
        if not prod_combined.empty:
            fig_prod = build_combined_plotly_bubble(prod_combined, 'Efficiency_%', 'Product')
            st.plotly_chart(fig_prod, use_container_width=True, key="prod_combined")
        else:
            st.info("No data available.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            drill_prod = st.selectbox("Select Product to view details:", ["(No Selection)"] + sorted(filtered_df['Product'].unique().tolist()), key="overview_prod_drill")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if drill_prod != "(No Selection)" and st.button("View Details", key="btn_ov_prod"):
                entity_drilldown_dialog("Product", drill_prod)
        
        if st.button("See All Products", use_container_width=True): see_all_entities_dialog('Product')

    with st.container(border=True):
        st.markdown('<div class="panel-title">Part Performance (Top 3 Fastest & Slowest)</div>', unsafe_allow_html=True)
        part_combined = get_combined_stats(filtered_df, 'Part')
        if not part_combined.empty:
            fig_part = build_combined_plotly_bubble(part_combined, 'Efficiency_%', 'Part')
            st.plotly_chart(fig_part, use_container_width=True, key="part_combined")
        else:
            st.info("No data available.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            drill_part = st.selectbox("Select Part to view details:", ["(No Selection)"] + sorted(filtered_df['Part'].unique().tolist()), key="overview_part_drill")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if drill_part != "(No Selection)" and st.button("View Details", key="btn_ov_part"):
                entity_drilldown_dialog("Part", drill_part)
        
        if st.button("See All Parts", use_container_width=True): see_all_entities_dialog('Part')


# ----------------------------------------------------
# TAB 2: COMPARISON ANALYSIS
# ----------------------------------------------------
with tab_comp:
    export_pdf_ui()
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Compare performance of tools producing the same part, or suppliers producing the same part.</p>", unsafe_allow_html=True)

    comp_mode = st.radio("Select Comparison Mode:", ["Part Comparison (tools making the same part)", "Supplier Comparison (tools making the same part from different suppliers)"], horizontal=True)

    parts_available = sorted(filtered_df['Part'].unique())
    if len(parts_available) > 0:
        if "Part Comparison" in comp_mode:
            comp_target = st.selectbox("Select a Part to compare its Tools:", parts_available)
            comp_df = filtered_df[filtered_df['Part'] == comp_target]
            group_col = 'Tooling ID'
        else:
            comp_target = st.selectbox("Select a Part to compare across Suppliers:", parts_available)
            comp_df = filtered_df[filtered_df['Part'] == comp_target]
            group_col = 'Supplier'
    else:
        comp_target = None
        comp_df = pd.DataFrame()

    if comp_target and not comp_df.empty:
        df_group_col = 'Tooling' if group_col == 'Tooling ID' else 'Supplier'
        comprehensive_rows = [compute_comprehensive_row(name, group, group_col) for name, group in comp_df.groupby(df_group_col)]
        comp_grouped = pd.DataFrame(comprehensive_rows)
        comp_grouped.sort_values(by='CT Weighted Average Efficiency', ascending=True, inplace=True) 

        if group_col == 'Tooling ID':
            num_toolings = comp_grouped['Tooling ID'].nunique()
            suppliers_inv = comp_grouped['Supplier'].dropna().unique()
            suppliers_str = ", ".join(suppliers_inv)
            num_suppliers = len(suppliers_inv)
            min_eff = comp_grouped['CT Weighted Average Efficiency'].min()
            max_eff = comp_grouped['CT Weighted Average Efficiency'].max()
            best_p = comp_grouped.iloc[-1]['Tooling ID']
            worst_p = comp_grouped.iloc[0]['Tooling ID']
            
            chart_title = (
                f"Cycle Time Efficiency % by Tooling<br>"
                f"<br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Number of Toolings: {num_toolings}</span><br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Number of Suppliers: {num_suppliers} ({suppliers_str})</span><br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Efficiency Range: {min_eff:.2f}% - {max_eff:.2f}%</span><br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Best Performer: {best_p} | Worst Performer: {worst_p}</span>"
            )
            custom_data = ['Tooling ID', 'Hover_CT_Eff', 'Hover_Net_Fin', 'Supplier']
            hover_template = "Tooling ID: %{customdata[0]}<br>Supplier: %{customdata[3]}<br>CT Efficiency: %{customdata[1]}<br>Net Financial: %{customdata[2]}<extra></extra>"
        else:
            num_toolings = comp_grouped['Total Toolings'].sum()
            suppliers_inv = comp_grouped['Supplier'].dropna().unique()
            suppliers_str = ", ".join(suppliers_inv)
            num_suppliers = len(suppliers_inv)
            min_eff = comp_grouped['CT Weighted Average Efficiency'].min()
            max_eff = comp_grouped['CT Weighted Average Efficiency'].max()
            best_p = comp_grouped.iloc[-1]['Supplier']
            worst_p = comp_grouped.iloc[0]['Supplier']
            
            chart_title = (
                f"Cycle Time Efficiency % by Supplier<br>"
                f"<br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Number of Toolings: {num_toolings}</span><br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Number of Suppliers: {num_suppliers} ({suppliers_str})</span><br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Efficiency Range: {min_eff:.2f}% - {max_eff:.2f}%</span><br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Best Performer: {best_p} | Worst Performer: {worst_p}</span>"
            )
            custom_data = ['Supplier', 'Hover_CT_Eff', 'Hover_Net_Fin', 'Total Toolings']
            hover_template = "Supplier: %{customdata[0]}<br>Total Toolings: %{customdata[3]}<br>CT Efficiency: %{customdata[1]}<br>Net Financial: %{customdata[2]}<extra></extra>"

        comp_grouped['Hover_CT_Eff'] = comp_grouped['CT Weighted Average Efficiency'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        comp_grouped['Hover_Net_Fin'] = comp_grouped['Net Financial'].apply(lambda x: f"-${abs(x):.1f}" if pd.notna(x) and x < 0 else f"${x:.1f}" if pd.notna(x) else "$0.0")

        fig_comp = go.Figure()
        colors = {"Within": "#5cb85c", "Slow": "#eab308", "Fast": "#d9534f"}

        for status in ["Within", "Slow", "Fast"]:
            df_sub = comp_grouped[comp_grouped['Performance Status'] == status]
            if not df_sub.empty:
                fig_comp.add_trace(go.Bar(
                    x=df_sub[group_col],
                    y=df_sub['CT Weighted Average Efficiency'],
                    marker_color=colors[status],
                    name=status,
                    text=df_sub['CT Weighted Average Efficiency'],
                    texttemplate='%{text:.2f}%',
                    textposition='outside',
                    customdata=df_sub[custom_data],
                    hovertemplate=hover_template,
                    showlegend=True
                ))
            else:
                fig_comp.add_trace(go.Bar(
                    x=[comp_grouped[group_col].iloc[0]] if not comp_grouped.empty else [None],
                    y=[None],
                    marker_color=colors[status],
                    name=status,
                    showlegend=True,
                    hoverinfo='skip'
                ))

        fig_comp.add_trace(go.Scatter(
            x=comp_grouped[group_col],
            y=comp_grouped['Total Shots'],
            mode='lines+markers',
            name='Shot count (volume)',
            line=dict(color='#94a3b8', width=2),
            marker=dict(size=6, color='#94a3b8'),
            yaxis='y2',
            hovertemplate="Shot count (volume): %{y:,}<extra></extra>"
        ))

        top_margin = 170 
        chart_height = 450 

        fig_comp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                type='category', 
                categoryorder='array',
                categoryarray=comp_grouped[group_col].tolist(),
                showgrid=False, 
                title='', 
                tickfont=dict(color='#e2e8f0', size=13)
            ),
            yaxis=dict(showgrid=True, gridcolor='#334155', title='Cycle Time Efficiency %', tickfont=dict(color='#94a3b8')),
            yaxis2=dict(title='Shot count (volume)', overlaying='y', side='right', showgrid=False, tickfont=dict(color='#94a3b8'), title_font=dict(color='#94a3b8')),
            margin=dict(l=0, r=60, t=top_margin, b=10), height=chart_height,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            legend_title_text='',
            title=chart_title
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        display_comp = comp_grouped.copy()
        display_comp = display_comp[[c for c in display_comp.columns if not c.startswith('Hover_')]]
        
        if group_col == 'Tooling ID':
            desired_cols = ['Tooling ID', 'Supplier', 'Plant', 'Time Period', 'Part', 'Product', 'Part Name', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
        else:
            desired_cols = ['Supplier', 'Total Toolings', 'Time Period', 'Part', 'Product', 'Part Name', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
            
        display_comp = display_comp[[c for c in desired_cols if c in display_comp.columns]]
        
        st.dataframe(display_comp, use_container_width=True, hide_index=True, column_config=detail_col_config)

        if group_col == 'Supplier':
            st.markdown("<br>", unsafe_allow_html=True)
            c_sup, c_btn = st.columns([3, 1])
            with c_sup:
                drill_supp = st.selectbox("Simulate a click on a 'Total Toolings' count to view breakdown:", ["(No Selection)"] + sorted(comp_grouped['Supplier'].unique().tolist()))
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if drill_supp != "(No Selection)" and st.button("View Toolings"): total_toolings_dialog(drill_supp, comp_df)
                
        elif group_col == 'Tooling ID':
            st.markdown("<br>", unsafe_allow_html=True)
            c_tool, c_btn = st.columns([3, 1])
            with c_tool:
                drill_tool = st.selectbox("Select a Tooling ID to view details:", ["(No Selection)"] + sorted(comp_grouped['Tooling ID'].unique().tolist()), key="comp_part_tool_drill")
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                view_clicked = st.button("View Tooling Details", key="btn_comp_part_tool")
                
            if drill_tool != "(No Selection)":
                if view_clicked:
                    st.session_state["st_comp_part_tool"] = drill_tool
                if st.session_state.get("st_comp_part_tool") == drill_tool:
                    st.markdown("<hr>", unsafe_allow_html=True)
                    render_entity_details("Tooling", drill_tool)

    elif comp_target:
        st.info(f"No data available for the selected {comp_target}.")

# ----------------------------------------------------
# TAB 3: FULL RANKINGS & DETAILS
# ----------------------------------------------------
with tab_rankings:
    export_pdf_ui()
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Complete list and ranking of all Suppliers, Tooling Types, Products, and Parts (Macro -> Detail Hierarchy).</p>", unsafe_allow_html=True)
    
    r_supp, r_tool, r_prod, r_part = st.tabs(["All Suppliers", "All Tooling Types", "All Products", "All Parts"])

    def show_ranking_tab(category):
        df_rank = generate_ranking_table_data(filtered_df, category)
        if df_rank.empty:
            st.info("No data available.")
            return

        worst_row = df_rank.iloc[0]
        best_row = df_rank.iloc[-1]
        
        st.markdown(f"### {category} Overview")
        c1, c2 = st.columns(2)
        c1.markdown(f"""
        <div style="background-color: #1e293b; padding: 16px; border-radius: 8px; border-left: 4px solid #5cb85c; height: 100%;">
            <div style="font-size: 0.9rem; color: #94a3b8;">Fastest Performer</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #ffffff;">{best_row[category]}</div>
            <div style="font-size: 1rem; color: #5cb85c;">{best_row['Overall Efficiency %']:.2f}% | +${best_row['Financial Gained']:,.0f} Gained</div>
        </div>
        """, unsafe_allow_html=True)

        c2.markdown(f"""
        <div style="background-color: #1e293b; padding: 16px; border-radius: 8px; border-left: 4px solid #d9534f; height: 100%;">
            <div style="font-size: 0.9rem; color: #94a3b8;">Slowest Performer</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #ffffff;">{worst_row[category]}</div>
            <div style="font-size: 1rem; color: #d9534f;">{worst_row['Overall Efficiency %']:.2f}% | -${abs(worst_row['Financial Lost']):,.0f} Lost</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        fig = go.Figure()
        colors = {"Within": "#5cb85c", "Slow": "#eab308", "Fast": "#d9534f"}

        for status in ["Within", "Slow", "Fast"]:
            df_sub = df_rank[df_rank['Performance Status'] == status]
            if not df_sub.empty:
                fig.add_trace(go.Bar(
                    x=df_sub[category],
                    y=df_sub['Overall Efficiency %'],
                    marker_color=colors[status],
                    name=status,
                    text=df_sub['Overall Efficiency %'],
                    texttemplate='%{text:.2f}%',
                    textposition='outside',
                    showlegend=True
                ))
            else:
                fig.add_trace(go.Bar(
                    x=[df_rank[category].iloc[0]] if not df_rank.empty else [None],
                    y=[None],
                    marker_color=colors[status],
                    name=status,
                    showlegend=True,
                    hoverinfo='skip'
                ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(l=0, r=20, t=10, b=10), 
            height=400, 
            xaxis=dict(
                type='category', 
                categoryorder='array',
                categoryarray=df_rank[category].tolist(),
                showgrid=False
            ), 
            yaxis=dict(showgrid=True, gridcolor='#334155'), 
            legend_title_text='',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_rank, use_container_width=True, hide_index=True, column_config=common_ranking_col_config)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            drill_item = st.selectbox("Select to view 'Total Toolings' breakdown:", ["(No Selection)"] + df_rank[category].tolist(), key=f"rank_drill_{category}")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            view_clicked = st.button("View Toolings", key=f"btn_rank_{category}")
            
        if drill_item != "(No Selection)" and view_clicked:
            ranking_tooling_drilldown_dialog(category, drill_item)

    with r_supp: show_ranking_tab('Supplier')
    with r_tool: show_ranking_tab('Tooling Type')
    with r_prod: show_ranking_tab('Product')
    with r_part: show_ranking_tab('Part')