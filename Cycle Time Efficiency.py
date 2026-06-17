<!-- ... existing code ... -->
# ==========================================
# 6. HELPER RENDERERS (To prevent nested dialog error)
# ==========================================
def render_entity_details(entity_type, entity_name):
    st.markdown(f"### Detailed Analysis: `{entity_name}`")
    df_drill = filtered_df[filtered_df[entity_type] == entity_name].copy()
<!-- ... existing code ... -->
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
                    st.session_state[f"st_red_{entity_type}_{entity_name}"] = tool_sel
                if st.session_state.get(f"st_red_{entity_type}_{entity_name}") == tool_sel:
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
        cols = ['Tooling ID', 'Total Shots', 'Parts Produced', 'ACT', 'Actual Average CT (WACT)', 'CT Difference', 'Total Expected Hours', 'Total Actual Hours', 'Fast Shots (%)', 'Slow Shots (%)', 'Within Shots (%)', 'WACT (Fast)', 'WACT (Slow)', 'Expected Hours (Fast)', 'Expected Hours (Slow)', 'Actual Hours (Fast)', 'Actual Hours (Slow)', 'Hours Gained', 'Hours Lost', 'Shots Gained', 'Shots Lost', 'Financial Gain', 'Financial Loss', 'Net Financial', 'CT Efficiency of Fast Hours', 'CT Efficiency of Slow Hours', 'CT Weighted Average Efficiency', 'Performance Status']
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
# ... existing code ...
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
# ... existing code ...
    st.markdown("<br>", unsafe_allow_html=True)
    c_dr, c_btn = st.columns([3, 1])
    with c_dr:
        drill_item = st.selectbox("Select to view 'Total Toolings' breakdown:", ["(No Selection)"] + df_rank[category].tolist(), key=f"all_ent_drill_{category}")
    with c_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        view_clicked = st.button("View Toolings", key=f"btn_all_ent_{category}")
        
    if drill_item != "(No Selection)":
        if view_clicked:
            st.session_state[f"st_all_ent_{category}"] = drill_item
        if st.session_state.get(f"st_all_ent_{category}") == drill_item:
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
# ... existing code ...
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
# ... existing code ...
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
# ... existing code ...