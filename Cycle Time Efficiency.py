import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 6. DIALOGS & POPUPS 
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
    
    cols = ['Tooling ID', 'Supplier', 'Plant', 'Time Period', 'Part', 'Part Name', 'Product', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
    df_detail = df_detail[[c for c in cols if c in df_detail.columns]]
    st.dataframe(df_detail, use_container_width=True, hide_index=True, column_config=detail_col_config)

    st.markdown("<br>", unsafe_allow_html=True)
    c_dr, c_btn = st.columns([3, 1])
    with c_dr:
        tool_sel = st.selectbox("Select a Tooling ID to view details:", ["(No Selection)"] + sorted(df_detail['Tooling ID'].unique().tolist()), key=f"wd_tool_{status_type}")
    with c_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        view_clicked = st.button("View Tool Details", key=f"wd_btn_{status_type}")
        
    if tool_sel != "(No Selection)" and view_clicked:
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

@st.dialog("Entity Performance Details", width="large")
def entity_drilldown_dialog(entity_type, entity_name):
    render_entity_details(entity_type, entity_name)

@st.dialog("Total Toolings Detail Breakdown", width="large")
def ranking_tooling_drilldown_dialog(entity_type, entity_name):
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
        cols = ['Tooling ID', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
        df_detail = df_detail[[c for c in cols if c in df_detail.columns]]
        st.dataframe(df_detail, use_container_width=True, hide_index=True, column_config=detail_col_config)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            tool_sel = st.selectbox("Select a Tooling ID to view details:", ["(No Selection)"] + sorted(df_sub['Tooling'].unique().tolist()), key=f"rk_tool_{entity_name.replace(' ', '_')}")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            view_clicked = st.button("View Tool Details", key=f"rk_btn_{entity_name.replace(' ', '_')}")
            
        if tool_sel != "(No Selection)" and view_clicked:
            st.markdown("<hr>", unsafe_allow_html=True)
            render_entity_details("Tooling", tool_sel)
    else:
        st.info("No toolings found.")

@st.dialog("Total Toolings Breakdown", width="large")
def total_toolings_dialog(supplier_name, df_subset):
    st.markdown(f"### Tooling Details for Supplier: `{supplier_name}`")
    supp_df = df_subset[df_subset['Supplier'] == supplier_name]
    comp_rows = [compute_comprehensive_row(name, group, 'Tooling ID') for name, group in supp_df.groupby('Tooling')]
    if comp_rows:
        df_detail = pd.DataFrame(comp_rows)
        df_detail.sort_values(by='CT Weighted Average Efficiency', ascending=True, inplace=True)
        cols = ['Tooling ID', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
        df_detail = df_detail[[c for c in cols if c in df_detail.columns]]
        st.dataframe(df_detail, use_container_width=True, hide_index=True, column_config=detail_col_config)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            tool_sel = st.selectbox("Select Tooling ID to view details:", ["(No Selection)"] + sorted(supp_df['Tooling'].unique().tolist()), key=f"sp_tool_{supplier_name.replace(' ', '_')}")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            view_clicked = st.button("View Tool Details", key=f"sp_btn_{supplier_name.replace(' ', '_')}")
            
        if tool_sel != "(No Selection)" and view_clicked:
            st.markdown("<hr>", unsafe_allow_html=True)
            render_entity_details("Tooling", tool_sel)
    else:
        st.info("No toolings found.")

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
    
    agg.sort_values(by='Overall Efficiency %', ascending=True, inplace=True)
    agg.insert(0, 'Rank', range(1, len(agg) + 1))
    
    agg['Performance Status'] = agg.apply(lambda r: "Within" if r['Net Financial'] >= 0 else ("Slow" if r['Net Financial'] > -1000 and r['Overall Efficiency %'] >= 85 else "Fast"), axis=1)
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
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Net Hours Gained</span><span class="metric-value text-green">{disp_gained_hrs}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Net Shots Gained</span><span class="metric-value text-green">{disp_gained_shots}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Financial Gain</span><span class="metric-value text-green">{disp_gained_fin}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Efficiency Gain</span><span class="metric-value text-green">{disp_eff_fast}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Parts Gained</span><span class="metric-value text-green">{parts_gained:,}</span></div>', 
        f'<div class="metric-row"><span class="metric-label">Tools Gained</span><span class="metric-value text-green">{tools_gained:,}</span></div>', 
        '</div>'
    )
    col_gain.markdown(html_gain, unsafe_allow_html=True)
    if col_gain.button("View Gained Details", use_container_width=True): widget_drilldown_dialog("Gained")
    
    html_loss = build_html(
        '<div class="dash-card" style="border-top: 4px solid #d9534f;">', 
        '<div class="kpi-title-container"><span class="kpi-title" style="color: #d9534f;">Lost (Slow Performance)</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Net Hours Lost</span><span class="metric-value text-red">{disp_lost_hrs}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Net Shots Lost</span><span class="metric-value text-red">{disp_lost_shots}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Financial Loss</span><span class="metric-value text-red">{disp_lost_fin}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Efficiency Loss</span><span class="metric-value text-red">{disp_eff_slow}</span></div>', 
        f'<div class="metric-row" style="margin-bottom: 8px;"><span class="metric-label">Parts Lost</span><span class="metric-value text-red">{parts_lost:,}</span></div>', 
        f'<div class="metric-row"><span class="metric-label">Tools Lost</span><span class="metric-value text-red">{tools_lost:,}</span></div>', 
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
        
        fast_df = grouped[grouped['Efficiency_%'] > 105].sort_values('Efficiency_%', ascending=False).head(3)
        slow_df = grouped[grouped['Efficiency_%'] < 95].sort_values('Efficiency_%', ascending=True).head(3)
        
        combined = pd.concat([fast_df, slow_df]).drop_duplicates()
        if combined.empty: return combined
        
        combined['Performance Status'] = combined.apply(lambda r: "Within" if r['Net Financial'] >= 0 else ("Slow" if r['Net Financial'] > -1000 and r['Efficiency_%'] >= 85 else "Fast"), axis=1)
        combined.sort_values('Efficiency_%', ascending=True, inplace=True)
        return combined

    def build_combined_plotly_vbar(df, x_col, y_col):
        if df.empty: return None
        fig = go.Figure()
        colors = {"Within": "#5cb85c", "Slow": "#eab308", "Fast": "#d9534f"}
        for status in ["Within", "Slow", "Fast"]:
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
        for status in ["Within", "Slow", "Fast"]:
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
                    hovertemplate=hover_template
                ))

        fig_comp.add_trace(go.Scatter(
            x=comp_grouped[group_col],
            y=comp_grouped['Total Shots'],
            mode='lines+markers',
            name='Shot Count',
            line=dict(color='#38bdf8', width=2),
            marker=dict(size=6),
            yaxis='y2',
            hovertemplate="Shot Count: %{y:,}<extra></extra>"
        ))

        top_margin = 170 
        chart_height = 450 

        fig_comp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title='', tickfont=dict(color='#e2e8f0', size=13)),
            yaxis=dict(showgrid=True, gridcolor='#334155', title='Cycle Time Efficiency %', tickfont=dict(color='#94a3b8')),
            yaxis2=dict(title='Shot Count', overlaying='y', side='right', showgrid=False, tickfont=dict(color='#38bdf8'), title_font=dict(color='#38bdf8')),
            margin=dict(l=0, r=20, t=top_margin, b=10), height=chart_height,
            legend_title_text='',
            title=chart_title
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        display_comp = comp_grouped.copy()
        display_comp = display_comp[[c for c in display_comp.columns if not c.startswith('Hover_')]]
        
        if group_col == 'Tooling ID':
            desired_cols = ['Tooling ID', 'Supplier', 'Plant', 'Time Period', 'Part', 'Part Name', 'Product', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
        else:
            desired_cols = ['Supplier', 'Total Toolings', 'Time Period', 'Part', 'Part Name', 'Product', 'Hourly Rate', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
            
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
                
            if drill_tool != "(No Selection)" and view_clicked:
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
        
        fig = px.bar(
            df_rank, 
            x=category, 
            y='Overall Efficiency %', 
            color='Performance Status',
            color_discrete_map={"Within": "#5cb85c", "Slow": "#eab308", "Fast": "#d9534f"},
            text='Overall Efficiency %'
        )
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=20, t=10, b=10), height=400, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#334155'), legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_rank, use_container_width=True, hide_index=True, column_config=common_ranking_col_config)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_dr, c_btn = st.columns([3, 1])
        with c_dr:
            drill_item = st.selectbox("Select to view 'Total Toolings' breakdown:", ["(No Selection)"] + df_rank[category].tolist(), key=f"rank_drill_{category}")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if drill_item != "(No Selection)" and st.button("View Toolings", key=f"btn_rank_{category}"):
                ranking_tooling_drilldown_dialog(category, drill_item)

    with r_supp: show_ranking_tab('Supplier')
    with r_tool: show_ranking_tab('Tooling Type')
    with r_prod: show_ranking_tab('Product')
    with r_part: show_ranking_tab('Part')