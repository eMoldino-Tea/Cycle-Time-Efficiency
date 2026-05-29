import streamlit as st
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
    
    suppliers_f = np.tile(['Foxconn', 'Jabil', 'Flex'], 100)
    tooling_f = np.repeat(['Injection Molding', 'High Pressure Die Casting', 'Progressive Stamping'], 100)
    np.random.shuffle(tooling_f)
    products_f = np.tile(['Product X248', 'Product X277', 'Product X418'], 100)
    np.random.shuffle(products_f)
    
    suppliers_s = np.tile(['Sanmina', 'Pegatron', 'Celestica'], 50)
    tooling_s = np.repeat(['Thermoforming', 'Blow Molding', 'Vacuum Forming'], 50)
    np.random.shuffle(tooling_s)
    products_s = np.tile(['Product X620D', 'Product V15', 'Product V12'], 50)
    np.random.shuffle(products_s)
    
    b_sup_f = {'Foxconn': 1.6, 'Jabil': 0.9, 'Flex': 0.5}
    b_tool_f = {'Injection Molding': 1.4, 'High Pressure Die Casting': 1.0, 'Progressive Stamping': 0.6}
    b_prod_f = {'Product X248': 1.25, 'Product X277': 1.05, 'Product X418': 0.7}
    w_gain_f = np.array([b_sup_f[s] * b_tool_f[t] * b_prod_f[p] for s, t, p in zip(suppliers_f, tooling_f, products_f)])
    w_gain_f /= w_gain_f.sum() 
    w_used_f = np.random.uniform(0.9, 1.1, N_FAST)
    w_used_f /= w_used_f.sum() 
    
    b_sup_s = {'Sanmina': 1.6, 'Pegatron': 0.9, 'Celestica': 0.5}
    b_tool_s = {'Thermoforming': 1.4, 'Blow Molding': 1.0, 'Vacuum Forming': 0.6}
    b_prod_s = {'Product X620D': 1.25, 'Product V15': 1.05, 'Product V12': 0.7}
    w_loss_s = np.array([b_sup_s[s] * b_tool_s[t] * b_prod_s[p] for s, t, p in zip(suppliers_s, tooling_s, products_s)])
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
        'Product': products_f
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
        'Product': products_s
    })
    df_slow['Expected_Hours'] = df_slow['Used_Hours'] - df_slow['Loss_Hours']
    
    df_within = pd.DataFrame({
        'Tolerance_Status': ['Neutral'] * N_WITHIN,
        'Gain_Hours': 0.0,
        'Loss_Hours': 0.0,
        'Shots_Gained': 0.0,
        'Shots_Lost': 0.0,
        'Expected_Hours': np.random.uniform(5.0, 20.0, N_WITHIN),
        'Base_Fin_Gain': 0.0,
        'Base_Fin_Loss': 0.0,
        'Supplier': np.random.choice(['Supplier Alpha', 'Neutral Corp'], N_WITHIN),
        'Tooling Type': np.random.choice(['Compression Molding', 'Rubber Molding', 'Silicone Molding'], N_WITHIN),
        'Product': np.random.choice(['Product Y99', 'Product Z11'], N_WITHIN)
    })
    df_within['Used_Hours'] = df_within['Expected_Hours']
    
    data = pd.concat([df_fast, df_slow, df_within], ignore_index=True)
    
    data['Total_Shots'] = data['Shots_Gained'] + data['Shots_Lost']
    data.loc[data['Tolerance_Status'] == 'Neutral', 'Total_Shots'] = np.random.randint(5000, 50000, N_WITHIN)
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
    data['Part Name'] = np.random.choice(['Housing Top', 'Housing Bottom', 'Display Lens', 'Battery Bracket'], len(data))
    data['Part'] = [f"Part-{np.random.randint(1, 25):03d}" for _ in range(len(data))]
    data['Tooling'] = [f"TL-{np.random.randint(1, 40):03d}" for _ in range(len(data))]
    
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
eff_within = calc_weighted_eff(filtered_df[filtered_df['Tolerance_Status'] == 'Neutral'])

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
fin_sign = "-$" if net_fin < 0 else "$"
disp_net_fin = f"{fin_sign}{abs(net_fin):,.0f}"

disp_eff_fast = f"+{eff_fast:.2f}%" if pd.notna(eff_fast) else "N/A"
disp_eff_slow = f"-{abs(100 - eff_slow):.2f}%" if pd.notna(eff_slow) else "N/A" 
disp_eff_within = f"{eff_within:.0f}%" if pd.notna(eff_within) else "N/A"

def build_html(*lines):
    return "".join(line.strip() for line in lines)

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
    neu_grp = group[group['Tolerance_Status']=='Neutral']

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

    perf_status = 'Faster' if net_fin > 0 else 'Slower'

    row = {
        group_col: name,
        'Time Period': f"{start_date.date()} to {end_date.date()}",
        'Part': group['Part'].iloc[0] if not group.empty else "",
        'Part Name': group['Part Name'].iloc[0] if not group.empty else "",
        'Product': group['Product'].iloc[0] if not group.empty else "",
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

def format_comprehensive_table(df_display, group_col):
    for col in ['ACT', 'Actual Average CT (WACT)', 'CT Difference', 'WACT (Fast)', 'WACT (Slow)', 'Hours Gained', 'Hours Lost']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "0.00")
    for col in ['Total Expected Hours', 'Total Actual Hours', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "0.00")
    for col in ['Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    for col in ['Total Shots', 'Parts Produced', 'Shots Gained', 'Shots Lost']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"{int(round(x)):,}" if pd.notna(x) else "0")
    for col in ['Hourly Rate', 'Financial Gain', 'Financial Loss', 'Net Financial']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"-${abs(x):,.0f}" if pd.notna(x) and x < 0 else (f"${x:,.0f}" if pd.notna(x) else "$0"))
    
    if group_col == 'Tooling ID':
        cols = ['Tooling ID', 'Supplier', 'Plant', 'Time Period', 'Part', 'Part Name', 'Product', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
    else:
        cols = ['Supplier', 'Total Toolings', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
    return df_display[[c for c in cols if c in df_display.columns]]


# ==========================================
# 6. DIALOGS & POPUPS (Streamlit >1.34)
# ==========================================
@st.dialog("Widget Breakdown Details", width="large")
def widget_drilldown_dialog(widget_name):
    def get_widget_drilldown_table(df, group_col, widget_type):
        if df.empty: return pd.DataFrame()
        count_col = 'Product' if group_col in ['Supplier', 'Tooling Type'] else 'Supplier'
        count_label = 'Number of Products' if group_col in ['Supplier', 'Tooling Type'] else 'Number of Suppliers'
        agg_dict = {'Tooling': 'nunique', count_col: 'nunique', 'Gain_Hours': 'sum', 'Loss_Hours': 'sum', 'Shots_Gained': 'sum', 'Shots_Lost': 'sum', 'Financial_Gain': 'sum', 'Financial_Loss': 'sum', 'Expected_Hours': 'sum', 'Used_Hours': 'sum'}
        base = df.groupby(group_col).agg(agg_dict).reset_index()
        base['Net Efficiency %'] = np.where(base['Used_Hours'] > 0, (base['Expected_Hours'] / base['Used_Hours']) * 100, np.nan)
        base['Net Hours'] = base['Gain_Hours'] - base['Loss_Hours']
        base['Net Shots'] = base['Shots_Gained'] - base['Shots_Lost']
        base['Net Financial'] = base['Financial_Gain'] - base['Financial_Loss']
        eff_slice = df.groupby([group_col, 'Tolerance_Status'])[['Expected_Hours', 'Used_Hours']].sum().reset_index()
        eff_slice['Eff'] = np.where(eff_slice['Used_Hours'] > 0, (eff_slice['Expected_Hours'] / eff_slice['Used_Hours']) * 100, np.nan)
        eff_pivot = eff_slice.pivot(index=group_col, columns='Tolerance_Status', values='Eff').reset_index()
        for st_col in ['Fast', 'Slow', 'Neutral']:
            if st_col not in eff_pivot.columns: eff_pivot[st_col] = np.nan
        eff_pivot.rename(columns={'Fast': 'Fast %', 'Slow': 'Slow %', 'Neutral': 'Within %'}, inplace=True)
        merged = pd.merge(base, eff_pivot, on=group_col, how='left')
        merged.rename(columns={'Tooling': 'Number of Tools', count_col: count_label}, inplace=True)
        if widget_type == 'Net Hours':
            merged.rename(columns={'Gain_Hours': 'Hours Gained', 'Loss_Hours': 'Hours Lost'}, inplace=True)
            res = merged[[group_col, 'Number of Tools', count_label, 'Hours Gained', 'Hours Lost', 'Net Hours']].copy()
            for c in ['Hours Gained', 'Hours Lost', 'Net Hours']: res[c] = res[c].apply(format_hm)
            return res
        elif widget_type == 'Net Shots':
            merged.rename(columns={'Shots_Gained': 'Shots Gained', 'Shots_Lost': 'Shots Lost'}, inplace=True)
            res = merged[[group_col, 'Number of Tools', count_label, 'Shots Gained', 'Shots Lost', 'Net Shots']].copy()
            for c in ['Shots Gained', 'Shots Lost', 'Net Shots']: res[c] = res[c].apply(lambda x: f"{int(round(x)):,}" if pd.notna(x) else "0")
            return res
        elif widget_type == 'Net Financial':
            merged.rename(columns={'Financial_Gain': 'Gain', 'Financial_Loss': 'Lost'}, inplace=True)
            res = merged[[group_col, 'Number of Tools', count_label, 'Gain', 'Lost', 'Net Financial']].copy()
            for c in ['Gain', 'Lost', 'Net Financial']: res[c] = res[c].apply(lambda x: f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}")
            return res
        elif widget_type == 'Efficiency':
            res = merged[[group_col, 'Number of Tools', count_label, 'Fast %', 'Slow %', 'Within %', 'Net Efficiency %']].copy()
            for c in ['Fast %', 'Slow %', 'Within %', 'Net Efficiency %']: res[c] = res[c].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            return res
        return pd.DataFrame()

    st.markdown(f"### Breakdowns for `{widget_name}`")
    tab_s, tab_t, tab_p = st.tabs(["By Supplier", "By Tooling Type", "By Product"])
    with tab_s: st.dataframe(get_widget_drilldown_table(filtered_df, 'Supplier', widget_name), use_container_width=True, hide_index=True)
    with tab_t: st.dataframe(get_widget_drilldown_table(filtered_df, 'Tooling Type', widget_name), use_container_width=True, hide_index=True)
    with tab_p: st.dataframe(get_widget_drilldown_table(filtered_df, 'Product', widget_name), use_container_width=True, hide_index=True)

@st.dialog("Entity Performance Details", width="large")
def entity_drilldown_dialog(entity_type, entity_name):
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
        fig_dt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=20, t=10, b=10), height=300)
        st.plotly_chart(fig_dt, use_container_width=True)
        
    with t_col2:
        st.markdown("**Efficiency Distribution**")
        drill_total_shots = df_drill['Total_Shots'].sum()
        rng = np.random.RandomState(abs(hash(entity_name)) % 10000)
        fast_sim = int(drill_total_shots * rng.uniform(0.25, 0.40))
        slow_sim = int(drill_total_shots * rng.uniform(0.15, 0.30))
        within_sim = drill_total_shots - fast_sim - slow_sim
        var_df = pd.DataFrame({'Tolerance_Status': ['Fast', 'Slow', 'Within Efficiency'], 'Total_Shots': [fast_sim, slow_sim, within_sim]})
        fig_dv = px.pie(var_df, names='Tolerance_Status', values='Total_Shots', color='Tolerance_Status', color_discrete_map={'Fast': '#5cb85c', 'Slow': '#d9534f', 'Within Efficiency': '#f8fafc'}, hole=0.4)
        fig_dv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=20, t=10, b=10), height=300)
        st.plotly_chart(fig_dv, use_container_width=True)

    st.markdown("**Detailed Benchmark & Operations Breakdown**")
    # Generates identical comprehensive metrics mapped dynamically so math remains perfectly sound
    comprehensive_rows = [compute_comprehensive_row(name, group, 'Tooling ID') for name, group in df_drill.groupby('Tooling')]
    if comprehensive_rows:
        df_comp_table = pd.DataFrame(comprehensive_rows)
        df_comp_display = format_comprehensive_table(df_comp_table, 'Tooling ID')
        st.dataframe(df_comp_display, use_container_width=True, hide_index=True)
    else:
        st.info("No detailed breakdown available.")

@st.dialog("Total Toolings Breakdown", width="large")
def total_toolings_dialog(supplier_name, df_subset):
    st.markdown(f"### Tooling Details for Supplier: `{supplier_name}`")
    supp_df = df_subset[df_subset['Supplier'] == supplier_name]
    comprehensive_rows = [compute_comprehensive_row(name, group, 'Tooling ID') for name, group in supp_df.groupby('Tooling')]
    if comprehensive_rows:
        df_comp_table = pd.DataFrame(comprehensive_rows)
        df_comp_display = format_comprehensive_table(df_comp_table, 'Tooling ID')
        st.dataframe(df_comp_display, use_container_width=True, hide_index=True)
    else:
        st.info("No toolings found.")

@st.dialog("Total Toolings Detail Breakdown", width="large")
def ranking_tooling_drilldown_dialog(entity_type, entity_name):
    st.markdown(f"### Tooling Details for {entity_type}: `{entity_name}`")
    df_sub = filtered_df[filtered_df[entity_type] == entity_name]
    
    comp_rows = [compute_comprehensive_row(name, group, 'Tooling ID') for name, group in df_sub.groupby('Tooling')]
    if comp_rows:
        df_detail = pd.DataFrame(comp_rows)
        cols = [
            'Tooling ID', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 
            'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 
            'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 
            'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 
            'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 
            'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 
            'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status'
        ]
        df_detail = df_detail[[c for c in cols if c in df_detail.columns]]
        
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
        
        st.dataframe(df_detail, use_container_width=True, hide_index=True, column_config=detail_col_config)
    else:
        st.info("No toolings found.")

# ==========================================
# 7. MAIN UI LAYOUT
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

tab_overview, tab_comp, tab_rankings = st.tabs(["Overview & Performance", "Comparison Analysis", "Full Rankings & Details"])

# ----------------------------------------------------
# TAB 1: OVERVIEW & PERFORMANCE
# ----------------------------------------------------
with tab_overview:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    html_kpi1 = build_html(
        '<div class="dash-card">', 
        f'<div class="kpi-title-container"><span class="kpi-title">Net Hours: {disp_net_hrs}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Gained</span><span class="metric-value text-green">{disp_gained_hrs}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Lost</span><span class="metric-value text-red">{disp_lost_hrs}</span></div>', 
        '<div class="metric-row" style="visibility: hidden;"><span class="metric-label">-</span><span class="metric-value">-</span></div>', 
        '</div>'
    )
    kpi1.markdown(html_kpi1, unsafe_allow_html=True)
    if kpi1.button("🔍 View Net Hours Details", use_container_width=True): widget_drilldown_dialog("Net Hours")

    html_kpi2 = build_html(
        '<div class="dash-card">', 
        f'<div class="kpi-title-container"><span class="kpi-title">Net Shots: {disp_net_shots}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Gained</span><span class="metric-value text-green">{disp_gained_shots}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Lost</span><span class="metric-value text-red">{disp_lost_shots}</span></div>', 
        '<div class="metric-row" style="visibility: hidden;"><span class="metric-label">-</span><span class="metric-value">-</span></div>', 
        '</div>'
    )
    kpi2.markdown(html_kpi2, unsafe_allow_html=True)
    if kpi2.button("🔍 View Net Shots Details", use_container_width=True): widget_drilldown_dialog("Net Shots")

    html_kpi3 = build_html(
        '<div class="dash-card">', 
        f'<div class="kpi-title-container"><span class="kpi-title">Net Financial: {disp_net_fin}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Gain</span><span class="metric-value text-green">{disp_gained_fin}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Lost</span><span class="metric-value text-red">{disp_lost_fin}</span></div>', 
        '<div class="metric-row" style="visibility: hidden;"><span class="metric-label">-</span><span class="metric-value">-</span></div>', 
        '</div>'
    )
    kpi3.markdown(html_kpi3, unsafe_allow_html=True)
    if kpi3.button("🔍 View Net Financial Details", use_container_width=True): widget_drilldown_dialog("Net Financial")

    html_kpi4 = build_html(
        '<div class="dash-card">', 
        '<div class="kpi-title-container"><span class="kpi-title">Efficiency</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Fast</span><span class="metric-value text-green">{disp_eff_fast}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Slow</span><span class="metric-value text-red">{disp_eff_slow}</span></div>', 
        f'<div class="metric-row"><span class="metric-label">Within</span><span class="metric-value text-neutral">{disp_eff_within}</span></div>', 
        '</div>'
    )
    kpi4.markdown(html_kpi4, unsafe_allow_html=True)
    if kpi4.button("🔍 View Efficiency Details", use_container_width=True): widget_drilldown_dialog("Efficiency")

    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    def get_aggregated_stats(df, category):
        grouped = df.groupby(category)[['Expected_Hours', 'Used_Hours']].sum().reset_index()
        grouped['Efficiency_%'] = np.where(grouped['Used_Hours'] > 0, (grouped['Expected_Hours'] / grouped['Used_Hours']) * 100, 0)
        fast_df = grouped[grouped['Efficiency_%'] > 105].sort_values('Efficiency_%', ascending=False).head(3)
        slow_df = grouped[grouped['Efficiency_%'] < 95].sort_values('Efficiency_%', ascending=True).head(3)
        return fast_df, slow_df

    def build_plotly_vbar(df, x_col, y_col, color, is_fast=True):
        if df.empty: return None
        df_sorted = df.sort_values(y_col, ascending=False if is_fast else True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_sorted[x_col], y=df_sorted[y_col] - 100, base=100, marker_color=color, text=df_sorted[y_col], texttemplate='%{text:.1f}%', textposition='outside'))
        if is_fast: y_range = [100, max(106, df[y_col].max() * 1.05)]
        else: y_range = [min(94, df[y_col].min() * 0.95), 100]
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#334155', range=y_range, title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8')), xaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)), margin=dict(l=55, r=10, t=20, b=30), height=240)
        return fig

    with st.container(border=True):
        st.markdown('<div class="panel-title">Supplier Performance</div>', unsafe_allow_html=True)
        col_left, col_right = st.columns(2, gap="large")
        supp_fast, supp_slow = get_aggregated_stats(filtered_df, 'Supplier')
        
        with col_left:
            st.markdown('<div class="col-header text-green">Top 3 Fastest Suppliers</div>', unsafe_allow_html=True)
            fig_sfast = build_plotly_vbar(supp_fast, 'Supplier', 'Efficiency_%', '#5cb85c', is_fast=True)
            if fig_sfast: st.plotly_chart(fig_sfast, use_container_width=True, key="supp_fast")
            else: st.markdown("<span style='color: #64748b;'>No suppliers >105% Efficiency.</span>", unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div class="col-header text-red">Top 3 Slowest Suppliers</div>', unsafe_allow_html=True)
            fig_sslow = build_plotly_vbar(supp_slow, 'Supplier', 'Efficiency_%', '#d9534f', is_fast=False)
            if fig_sslow: st.plotly_chart(fig_sslow, use_container_width=True, key="supp_slow")
            else: st.markdown("<span style='color: #64748b;'>No suppliers <95% Efficiency.</span>", unsafe_allow_html=True)
        
        drill_supp = st.selectbox("Select Supplier for Drill-Down", ["(Select)"] + filtered_df['Supplier'].unique().tolist(), key="sel_supp")
        if drill_supp != "(Select)" and st.button(f"🔍 Drill Down: {drill_supp}"):
            entity_drilldown_dialog("Supplier", drill_supp)

    def build_plotly_hbar(df, x_col, y_col, color, is_fast=True):
        if df.empty: return None
        df_sorted = df.sort_values(x_col, ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=df_sorted[y_col], x=df_sorted[x_col] - 100, base=100, orientation='h', marker_color=color, text=df_sorted[x_col], texttemplate='%{text:.1f}%', textposition='outside'))
        if is_fast: x_range = [100, max(106, df[x_col].max() * 1.05)]
        else: x_range = [min(94, df[x_col].min() * 0.95), 100]
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, visible=True, range=x_range, title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8')), yaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)), margin=dict(l=0, r=40, t=10, b=30), height=220)
        return fig

    with st.container(border=True):
        st.markdown('<div class="panel-title">Tooling Type Performance</div>', unsafe_allow_html=True)
        col_left, col_right = st.columns(2, gap="large")
        tool_fast, tool_slow = get_aggregated_stats(filtered_df, 'Tooling Type')
        
        with col_left:
            st.markdown('<div class="col-header text-green">Top 3 Fastest Tooling Types</div>', unsafe_allow_html=True)
            fig_tfast = build_plotly_hbar(tool_fast, 'Efficiency_%', 'Tooling Type', '#5cb85c', is_fast=True)
            if fig_tfast: st.plotly_chart(fig_tfast, use_container_width=True, key="bar_fast")
            else: st.markdown("<span style='color: #64748b;'>No tooling types >105% Efficiency.</span>", unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="col-header text-red">Top 3 Slowest Tooling Types</div>', unsafe_allow_html=True)
            fig_tslow = build_plotly_hbar(tool_slow, 'Efficiency_%', 'Tooling Type', '#d9534f', is_fast=False)
            if fig_tslow: st.plotly_chart(fig_tslow, use_container_width=True, key="bar_slow")
            else: st.markdown("<span style='color: #64748b;'>No tooling types <95% Efficiency.</span>", unsafe_allow_html=True)
            
        drill_tt = st.selectbox("Select Tooling Type for Drill-Down", ["(Select)"] + filtered_df['Tooling Type'].unique().tolist(), key="sel_tt")
        if drill_tt != "(Select)" and st.button(f"🔍 Drill Down: {drill_tt}"):
            entity_drilldown_dialog("Tooling Type", drill_tt)

    def build_plotly_bubble(df, x_col, y_col, color, is_fast=True):
        if df.empty: return None
        df['Bubble_Size'] = (df[x_col] - 100) if is_fast else (100 - df[x_col])
        df['Bubble_Size'] = df['Bubble_Size'].clip(lower=0.5)
        x_range = [100, max(106, df[x_col].max() * 1.03)] if is_fast else [min(94, df[x_col].min() * 0.97), 100]
        fig = px.scatter(df, x=x_col, y=y_col, size='Bubble_Size', text=x_col, size_max=25)
        fig.update_traces(marker_color=color, texttemplate='%{text:.1f}%', textposition='middle right', marker=dict(line=dict(width=1.5, color='#ffffff')))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#334155', title='Cycle Time Efficiency %', title_font=dict(size=12, color='#94a3b8'), tickfont=dict(color='#94a3b8'), range=x_range), yaxis=dict(showgrid=True, gridcolor='#334155', title='', tickfont=dict(color='#e2e8f0', size=13)), margin=dict(l=0, r=40, t=10, b=40), height=240, showlegend=False)
        return fig

    with st.container(border=True):
        st.markdown('<div class="panel-title">Product Performance</div>', unsafe_allow_html=True)
        col_left, col_right = st.columns(2, gap="large")
        prod_fast, prod_slow = get_aggregated_stats(filtered_df, 'Product')
        
        with col_left:
            st.markdown('<div class="col-header text-green">Top 3 Fastest Products</div>', unsafe_allow_html=True)
            fig_pfast = build_plotly_bubble(prod_fast, 'Efficiency_%', 'Product', '#5cb85c', is_fast=True)
            if fig_pfast: st.plotly_chart(fig_pfast, use_container_width=True, key="bubble_fast")
            else: st.markdown("<span style='color: #64748b;'>No products >105% Efficiency.</span>", unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="col-header text-red">Top 3 Slowest Products</div>', unsafe_allow_html=True)
            fig_pslow = build_plotly_bubble(prod_slow, 'Efficiency_%', 'Product', '#d9534f', is_fast=False)
            if fig_pslow: st.plotly_chart(fig_pslow, use_container_width=True, key="bubble_slow")
            else: st.markdown("<span style='color: #64748b;'>No products <95% Efficiency.</span>", unsafe_allow_html=True)
            
        drill_prod = st.selectbox("Select Product for Drill-Down", ["(Select)"] + filtered_df['Product'].unique().tolist(), key="sel_prod")
        if drill_prod != "(Select)" and st.button(f"🔍 Drill Down: {drill_prod}"):
            entity_drilldown_dialog("Product", drill_prod)


# ----------------------------------------------------
# TAB 2: COMPARISON ANALYSIS
# ----------------------------------------------------
with tab_comp:
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

        if group_col == 'Tooling ID':
            num_toolings = comp_grouped['Tooling ID'].nunique()
            num_suppliers = comp_grouped['Supplier'].nunique()
            chart_title = (
                f"Cycle Time Efficiency % by Tooling<br>"
                f"<br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Number of Toolings: {num_toolings}</span><br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Number of Suppliers: {num_suppliers}</span>"
            )
            hover_template = "Tooling ID: %{customdata[0]}<br>CT Efficiency: %{customdata[1]}<br>Net Financial: %{customdata[2]}<extra></extra>"
        else:
            num_toolings = comp_grouped['Total Toolings'].sum()
            num_suppliers = comp_grouped['Supplier'].nunique()
            chart_title = (
                f"Cycle Time Efficiency % by Supplier<br>"
                f"<br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Number of Toolings: {num_toolings}</span><br>"
                f"<span style='font-size: 16px; font-weight: 500; color: #cbd5e1;'>Number of Suppliers: {num_suppliers}</span>"
            )
            hover_template = "Supplier: %{customdata[0]}<br>CT Efficiency: %{customdata[1]}<br>Net Financial: %{customdata[2]}<extra></extra>"

        comp_grouped['Hover_CT_Eff'] = comp_grouped['CT Weighted Average Efficiency'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        comp_grouped['Hover_Net_Fin'] = comp_grouped['Net Financial'].apply(lambda x: f"-${abs(x):.1f}" if pd.notna(x) and x < 0 else f"${x:.1f}" if pd.notna(x) else "$0.0")

        fig_comp = px.bar(
            comp_grouped, 
            x=group_col, 
            y='CT Weighted Average Efficiency', 
            color='Net Financial',
            text='CT Weighted Average Efficiency',
            color_continuous_scale=['#d9534f', '#f8fafc', '#5cb85c'],
            title=chart_title,
            custom_data=[group_col, 'Hover_CT_Eff', 'Hover_Net_Fin']
        )
        fig_comp.update_traces(
            texttemplate='%{text:.2f}%', 
            textposition='outside',
            hovertemplate=hover_template
        )

        top_margin = 130 
        chart_height = 420 

        fig_comp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)),
            yaxis=dict(showgrid=True, gridcolor='#334155', title='Cycle Time Efficiency %', tickfont=dict(color='#94a3b8')),
            margin=dict(l=0, r=20, t=top_margin, b=10), height=chart_height,
            coloraxis_colorbar=dict(
                title=dict(text="Net Financial ($)", font=dict(color='#94a3b8')),
                tickfont=dict(color='#94a3b8')
            )
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        display_comp = format_comprehensive_table(comp_grouped, group_col)
        st.dataframe(display_comp, use_container_width=True, hide_index=True)

        if group_col == 'Supplier':
            st.markdown("<br>", unsafe_allow_html=True)
            c_sup, c_btn = st.columns([3, 1])
            with c_sup:
                drill_supp = st.selectbox(
                    "Select a Supplier to view 'Total Toolings' Breakdown:", 
                    options=["(No Selection)"] + sorted(comp_grouped['Supplier'].unique().tolist())
                )
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if drill_supp != "(No Selection)" and st.button("🔍 View Toolings"):
                    total_toolings_dialog(drill_supp, comp_df)

    elif comp_target:
        st.info(f"No data available for the selected {comp_target}.")

# ----------------------------------------------------
# TAB 3: FULL RANKINGS & DETAILS
# ----------------------------------------------------
with tab_rankings:
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Complete list and ranking of all Suppliers, Tooling Types, and Products.</p>", unsafe_allow_html=True)
    
    r_supp, r_tool, r_prod = st.tabs(["All Suppliers", "All Tooling Types", "All Products"])
    
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

    def generate_ranking_table_data(df, col):
        agg = df.groupby(col).apply(lambda x: pd.Series({
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
        })).reset_index()
        agg.sort_values(by='Overall Efficiency %', ascending=False, inplace=True)
        agg.insert(0, 'Rank', range(1, len(agg) + 1))
        return agg

    with r_supp:
        df_supp_rank = generate_ranking_table_data(filtered_df, 'Supplier')
        st.dataframe(df_supp_rank, use_container_width=True, hide_index=True, column_config=common_ranking_col_config)
        
        c_s_dr, c_s_btn = st.columns([3, 1])
        with c_s_dr:
            drill_s = st.selectbox("Simulate a click on 'Total Toolings' to view breakdown:", ["(No Selection)"] + df_supp_rank['Supplier'].tolist(), key="rank_drill_supp")
        with c_s_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if drill_s != "(No Selection)" and st.button("🔍 View Toolings", key="btn_rank_supp"):
                ranking_tooling_drilldown_dialog('Supplier', drill_s)

    with r_tool:
        df_tool_rank = generate_ranking_table_data(filtered_df, 'Tooling Type')
        st.dataframe(df_tool_rank, use_container_width=True, hide_index=True, column_config=common_ranking_col_config)
        
        c_t_dr, c_t_btn = st.columns([3, 1])
        with c_t_dr:
            drill_t = st.selectbox("Simulate a click on 'Total Toolings' to view breakdown:", ["(No Selection)"] + df_tool_rank['Tooling Type'].tolist(), key="rank_drill_tool")
        with c_t_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if drill_t != "(No Selection)" and st.button("🔍 View Toolings", key="btn_rank_tool"):
                ranking_tooling_drilldown_dialog('Tooling Type', drill_t)

    with r_prod:
        df_prod_rank = generate_ranking_table_data(filtered_df, 'Product')
        st.dataframe(df_prod_rank, use_container_width=True, hide_index=True, column_config=common_ranking_col_config)
        
        c_p_dr, c_p_btn = st.columns([3, 1])
        with c_p_dr:
            drill_p = st.selectbox("Simulate a click on 'Total Toolings' to view breakdown:", ["(No Selection)"] + df_prod_rank['Product'].tolist(), key="rank_drill_prod")
        with c_p_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if drill_p != "(No Selection)" and st.button("🔍 View Toolings", key="btn_rank_prod"):
                ranking_tooling_drilldown_dialog('Product', drill_p)