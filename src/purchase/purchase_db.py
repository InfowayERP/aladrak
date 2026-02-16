import streamlit as st
import plotly.express as px
import pandas as pd
import io
import os
import warnings
import calendar
import base64
import numpy as np
import datetime as dt
import data.sqlite_reader as ltrd
import json


def export_excel(df, sheet_name1="Data"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name1)
    return output.getvalue()

def report_title(report_name):
    # Load local image and convert to base64
    image_path = "images/Aladrak.png"  # Adjust the path to your image
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .dashboard-header {{
            display: flex;
            align-items: center;
            justify-content: space-between; /* push text left, image right */
            font-size: 2rem;
            font-weight: 700;
            color: green;  /* text in blue */
            padding: 0.3rem 2rem;
            border-radius: 12px;
            background: rgb(226, 252, 231);
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
            margin-bottom: 0.5rem;
        }}
        .dashboard-header img {{
            height: 40px; /* adjust size */
            width: auto;
        }}
        </style>

        <div class="dashboard-header">
            <span>{report_name}</span>
            <img src="data:image/png;base64,{img_base64}" alt="Logo">
        </div>
        """,
        unsafe_allow_html=True
    )

def purchase_dashboard(grn_data, lpo_data, lpo_grn_gross_amount, lpo_grn_net_values,Purchase):
    report_title("Purchase Dashboard")
    tab1, tab2, tab3,tab4,tab5 = st.tabs([
        "📊 LPO Dashboard",
        "🌍 GRN Dashboard",
        "🏗️ Projectwise Net Purchase","💼Supplier Summary","🏢Facility wise purchase"
    ])

    

    total_lpo = lpo_data["Amount"].sum()
    total_grn = grn_data["Amount"].sum()
    difference = total_lpo - total_grn

  

    with tab1:
      

        col1P, Col1AP,Col1AQ, col2PP,cole,col2P = st.columns([0.25,0.25,0.25,0.25,0.25,0.25])
        
        with cole:
        
             view_option = st.radio(
            "Select View",
            ["Yearly", "Monthly"],
            horizontal=True,
            key="lpo_view_mode"
        )

        if view_option == "Yearly":
            with col1P:
                lpo_data['Year'] = lpo_data['Year'].astype(int)
                year_list = sorted(lpo_data['Year'].unique())

                start_year, end_year = st.select_slider(
                    "Select Year Range",
                    options=year_list,
                    value=(year_list[0], year_list[-1]),
                    key="year_range_main"
                )
            
            with col2PP:
                with st.popover("🏢 Choose Company"):

                    param_data = ltrd.get_all_params()

                    # Convert stored JSON string → list
                    companies_default_list = json.loads(param_data[0][0])

                    # Company list to display
                    company_list = sorted(lpo_data['Companyname'].unique())

                    st.write("Select Company:")

                    small_col1, small_col2 = st.columns([0.3, 0.7])

                    with small_col1:
                        select_all = st.button("✔ Select All", use_container_width=True)

                    with small_col2:
                        clear_all = st.button("✖ Clear All", use_container_width=True)

                    selected_comp = []

                    # --- Loop through companies ---
                    for comp in company_list:
                        key = f"chk_{comp}"

                        # 🔹 Initialize default selection only once
                        if key not in st.session_state:
                            st.session_state[key] = comp in companies_default_list

                        # Clear all
                        if clear_all:
                            st.session_state[key] = False

                        # Select all
                        if select_all:
                            st.session_state[key] = True

                        checked = st.checkbox(comp, key=key)

                        if checked:
                            selected_comp.append(comp)

            if selected_comp:
                lpo_data_filtered = lpo_data[
                    (lpo_data['Companyname'].isin(selected_comp)) &
                    (lpo_data['Year'] >= start_year) &
                    (lpo_data['Year'] <= end_year)
                ]
            else:
                lpo_data_filtered = lpo_data[
                    (lpo_data['Year'] >= start_year) &
                    (lpo_data['Year'] <= end_year)
                ]

            lpo_pur_year = lpo_data_filtered.groupby('Year')['Amount'].sum().reset_index()
            lpo_pur_year['Year'] = lpo_pur_year['Year'].astype(int).astype(str)
            lpo_pur_year_kpi=lpo_pur_year['Amount'].sum()
            lpo_pur_year_export = lpo_pur_year.copy()
            lpo_pur_year['Amount'] = (lpo_pur_year['Amount'] / 1_000_000).round(1)

            with Col1AP:
                Col1AP.metric("LPO Amount", f"{lpo_pur_year_kpi/1_000_000:,.2f} M")

            fig_bar = px.bar(
                lpo_pur_year,
                x='Year',
                y='Amount',
                text_auto=True,
                title=f'LPO Value OMR (in millions) - Yearly({start_year}-{end_year})',
                color_discrete_sequence=["#006400"]
            )

            fig_bar.update_xaxes(
                tickmode='array',
                tickvals=lpo_pur_year['Year'],
                ticktext=lpo_pur_year['Year']
            )
            fig_bar.update_yaxes(tickformat=",")

            with Col1AQ:
                st.download_button(label="📥Excel",
                    data=export_excel(lpo_pur_year_export),
                    file_name=f"lpo_pur_year_{start_year}_{end_year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            col1, col2 = st.columns([5, 0.25])
            with col1:
                st.plotly_chart(fig_bar, use_container_width=True)

        else:

           
            current_year = dt.datetime.now().year

            with col2PP:
                with st.popover("🏢 Choose Company"):

                    # Fetch default companies (JSON string → list)
                    param_data = ltrd.get_all_params()
                    companies_default_list = json.loads(param_data[0][0])

                    company_list = sorted(lpo_data['Companyname'].unique())
                    st.write("Select Company:")

                    # Buttons layout
                    small_c1, small_c2 = st.columns([0.3, 0.7])

                    with small_c1:
                        select_all_m = st.button("✔ Select All (M)", use_container_width=True)

                    with small_c2:
                        clear_all_m = st.button("✖ Clear All (M)", use_container_width=True)

                    selected_comp_m = []

                    # --- Loop through companies ---
                    for comp in company_list:
                        key = f"chk_m_{comp}"

                        # 🔹 Initialize default selection (ONLY ONCE)
                        if key not in st.session_state:
                            st.session_state[key] = comp in companies_default_list

                        # ---- Clear All Logic ----
                        if clear_all_m:
                            st.session_state[key] = False

                        # ---- Select All Logic ----
                        if select_all_m:
                            st.session_state[key] = True

                        # Checkbox
                        checked = st.checkbox(comp, key=key)

                        # Collect selected companies
                        if checked:
                            selected_comp_m.append(comp)
            with col1P:
                month_list = list(range(1, 13))
                month_dict = {i: calendar.month_abbr[i] for i in month_list}

                start_m, end_m = st.select_slider(
                    "Select Month Range",
                    options=month_list,
                    value=(1, 12),
                    format_func=lambda x: month_dict[x],
                    key="month_range_main"
                )

            with Col1AP:
                year_list = sorted(lpo_data["Year"].dropna().unique())

                selected_year = st.selectbox(
                    "Select Year",
                    year_list,
                    index=len(year_list)-1,   # Default to latest available year
                    key="lpo_year_main"
                )

            # ---- FILTER DATA FOR SELECTED YEAR ----
            df_current = lpo_data[lpo_data["Year"] == str(selected_year)].copy()

            df_current["Month"] = pd.to_numeric(df_current["Month"], errors="coerce")
            df_current = df_current.dropna(subset=["Month"])
            df_current["Month"] = df_current["Month"].astype(int)

            # Company Filter
            if selected_comp_m:
                df_current = df_current[df_current["Companyname"].isin(selected_comp_m)]

            # Month Filter
            df_current = df_current[
                (df_current["Month"] >= start_m) &
                (df_current["Month"] <= end_m)
            ]

            # Validate
            if df_current.empty:
                st.warning("⚠ No data found for selected filters.")
                st.stop()

            # Month Name column
            df_current["Month_Name"] = df_current["Month"].apply(lambda x: calendar.month_abbr[x])

            # Month sorting
            month_order = {calendar.month_abbr[i]: i for i in range(1, 13)}
            monthly_summary = df_current.groupby("Month_Name")["Amount"].sum().reset_index()
            monthly_summary["Month_Order"] = monthly_summary["Month_Name"].map(month_order)
            monthly_summary = monthly_summary.sort_values("Month_Order")
            monthly_summary["Amount_Million"] = (monthly_summary["Amount"] / 1_000_000).round(2)

            # ---- CHART ----
            fig_bar_month = px.bar(
                monthly_summary,
                x='Month_Name',
                y='Amount_Million',
                text='Amount_Million',
                color_discrete_sequence=px.colors.sequential.Greens[::-1],
                title=f"Monthly LPO (in Millions) – {selected_year}",
                labels={"Month_Name": "Month", "Amount_Million": "Amount"}
            )
            fig_bar_month.update_traces(texttemplate='%{text}M')

            st.plotly_chart(fig_bar_month, use_container_width=True)


        lpo_pur_year_month = lpo_data.groupby(['Year', 'Month'])['Amount'].sum().reset_index()

                    # Convert numeric months to names
        if lpo_pur_year_month['Month'].dtype != object:
                        lpo_pur_year_month['Month'] = lpo_pur_year_month['Month'].apply(lambda x: calendar.month_abbr[int(x)])

        lpo_pur_year_month['YearMonth'] = lpo_pur_year_month['Year'].astype(str) + "-" + lpo_pur_year_month['Month']

        lpo_pur_year_month['Amount'] = (lpo_pur_year_month['Amount'] / 1_000_000).round(1)

        fig_bar2 = px.bar( lpo_pur_year_month, x='YearMonth',y='Amount', text_auto=True)
        fig_bar2.update_yaxes(tickformat=",") 

    

    with tab2:

        col3, col3a, col3b, col3f, col3c, col3g = st.columns([1,1,1,1,1,1])

        # -------------------------
        # VIEW MODE : Yearly / Monthly  (SAME AS TAB1)
        # -------------------------
        with col3g:
            view_option_grn = st.radio(
                "Select View",
                ["Yearly", "Monthly"],
                horizontal=True,
                key="grn_view_mode"
            )

        
        grn_data['Year'] = pd.to_numeric(grn_data['Year'], errors="coerce")

        year_list1 = sorted(grn_data['Year'].dropna().astype(int).unique())

        if not year_list1:
            st.error("❌ No valid years found in GRN data.")
            st.stop()

        if view_option_grn == "Yearly":

            with col3:
                start_year, end_year = st.select_slider(
                    "Select Year Range",
                    options=year_list1,
                    value=(year_list1[0], year_list1[-1]),
                    key="grn_year_range_main"
                )

           
            with col3b:
                with st.popover("🏢 Choose Company"):

                    # Fetch default companies (JSON string → list)
                    param_data = ltrd.get_all_params()
                    companies_default_list = json.loads(param_data[0][0])  # or use a specific list for GRN if different

                    company_list = sorted(grn_data['Companyname'].unique())
                    st.write("Select Company:")

                    small_col1, small_col2 = st.columns([0.3, 0.7])

                    with small_col1:
                        select_all_m_grn = st.button("✔ Select All", key="select_all_m_grn", use_container_width=True)

                    with small_col2:
                        clear_all_m_grn = st.button("✖ Clear All", key="clear_all_m_grn", use_container_width=True)

                    selected_comp_grn = []

                    # --- Loop through companies ---
                    for comp in company_list:
                        key = f"chk_grn_{comp}"

                        # 🔹 Initialize default selection (only once)
                        if key not in st.session_state:
                            st.session_state[key] = comp in companies_default_list

                        # Clear all logic
                        if clear_all_m_grn:
                            st.session_state[key] = False

                        # Select all logic
                        if select_all_m_grn:
                            st.session_state[key] = True

                        # Checkbox
                        checked = st.checkbox(comp, key=key)

                        if checked:
                            selected_comp_grn.append(comp)

            if selected_comp_grn:
                grn_data_filtered = grn_data[
                    (grn_data['Companyname'].isin(selected_comp_grn)) &
                    (grn_data['Year'] >= start_year) &
                    (grn_data['Year'] <= end_year)
                ]
            else:
                grn_data_filtered = grn_data[
                    (grn_data['Year'] >= start_year) &
                    (grn_data['Year'] <= end_year)
                ]
            
            grn_pur_year = grn_data_filtered.groupby('Year')['Amount'].sum().reset_index()
            grn_total = grn_pur_year['Amount'].sum()

            grn_pur_year['Year'] = grn_pur_year['Year'].astype(str)
            grn_pur_year_export = grn_pur_year.copy()
            grn_pur_year['Amount'] = (grn_pur_year['Amount'] / 1_000_000).round(1)
            

            col3a.metric("GRN Amount", f"{grn_total/1_000_000:,.2f} M")

            # DOWNLOAD
            with col3f:
                st.download_button(
                    label="📥 Download Excel",
                    data=export_excel(grn_pur_year_export),
                    file_name=f"grn_year_{start_year}_{end_year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # CHART
            fig_bar1 = px.bar(
                grn_pur_year,
                x='Year', y='Amount',
                text_auto=True,
                title=f'GRN Value (in Millions) - {start_year} to {end_year}',
                color_discrete_sequence=["#006400"]
            )
            fig_bar1.update_xaxes(type="category")
            fig_bar1.update_xaxes(tickmode="linear", dtick=1)

            fig_bar1.update_layout(xaxis_tickangle=0)

            st.plotly_chart(fig_bar1, use_container_width=True)

        else:

            current_year = dt.datetime.now().year

          
            with col3b:
                with st.popover("🏢 Choose Company"):

                    # Fetch default companies (JSON string → list)
                    param_data = ltrd.get_all_params()
                    companies_default_list = json.loads(param_data[0][0])  # adjust if GRN has a separate default list

                    company_list = sorted(grn_data['Companyname'].unique())
                    st.write("Select Company:")

                    # Buttons layout
                    small_c1, small_c2 = st.columns([0.3, 0.7])

                    with small_c1:
                        select_all_m_grn = st.button(
                            "✔ Select All", key="select_all_m_grn_year", use_container_width=True
                        )

                    with small_c2:
                        clear_all_m_grn = st.button(
                            "✖ Clear All", key="clear_all_m_grn_year", use_container_width=True
                        )

                    selected_comp_m_grn = []

                    # --- Loop through companies ---
                    for comp in company_list:
                        key = f"chk_m_grn_{comp}"

                        # 🔹 Initialize default selection (only once)
                        if key not in st.session_state:
                            st.session_state[key] = comp in companies_default_list

                        # ---- Clear All Logic ----
                        if clear_all_m_grn:
                            st.session_state[key] = False

                        # ---- Select All Logic ----
                        if select_all_m_grn:
                            st.session_state[key] = True

                        # Checkbox
                        checked = st.checkbox(comp, key=key)

                        # Collect selected
                        if checked:
                            selected_comp_m_grn.append(comp)
           
            with col3:
                month_list = list(range(1, 13))
                month_dict = {i: calendar.month_abbr[i] for i in month_list}

                start_m, end_m = st.select_slider(
                    "Select Month Range",
                    options=month_list,
                    value=(1, 12),
                    format_func=lambda x: month_dict[x],
                    key="grn_month_range_main"
                )
            with col3f:
                year_list = sorted(grn_data["Year"].dropna().unique())

                selected_year = st.selectbox(
                    "Select Year",
                    year_list,
                    index=len(year_list)-1,   # default to latest year
                    key="grn_year_main"
                )

            # ---- Filter Data for Selected Year ----
            df_grn_curr = grn_data[grn_data['Year'] == selected_year].copy()

            df_grn_curr["Month"] = pd.to_numeric(df_grn_curr["Month"], errors="coerce")
            df_grn_curr = df_grn_curr.dropna(subset=["Month"])
            df_grn_curr["Month"] = df_grn_curr["Month"].astype(int)

            if selected_comp_m_grn:
                df_grn_curr = df_grn_curr[df_grn_curr["Companyname"].isin(selected_comp_m_grn)]

            df_grn_curr = df_grn_curr[
                (df_grn_curr["Month"] >= start_m) &
                (df_grn_curr["Month"] <= end_m)
            ]

            if df_grn_curr.empty:
                st.warning("⚠ No data found for selected company/month range.")
                st.stop()

            df_grn_curr["Month_Name"] = df_grn_curr["Month"].apply(lambda x: calendar.month_abbr[x])
            month_order = {calendar.month_abbr[i]: i for i in range(1, 13)}

            monthly_grn = df_grn_curr.groupby("Month_Name")["Amount"].sum().reset_index()
            monthly_grn["Month_Order"] = monthly_grn["Month_Name"].map(month_order)
            monthly_grn = monthly_grn.sort_values("Month_Order")
            monthly_grn["Amount_Million"] = (monthly_grn["Amount"] / 1_000_000).round(2)

            fig_grn_month = px.bar(
                monthly_grn,
                x="Month_Name", y="Amount_Million",
                text="Amount_Million",
                color_discrete_sequence=px.colors.sequential.Greens[::-1],
                title=f"Monthly GRN (in Millions) – {selected_year}",
            )
            fig_grn_month.update_traces(texttemplate='%{text}M')

            st.plotly_chart(fig_grn_month, use_container_width=True)
    
        
    with tab3:
        top_projects = lpo_grn_net_values.copy()
        top_projects2 = lpo_grn_net_values.copy()

        col3, col3a, col3b, col3c, col3d, col3e = st.columns([1, 1, 1, 1, 1, 1])

        # --------------- COMPANY FILTER ---------------
        with col3a:
            with st.popover("🏢 Choose Company"):

                # Fetch default companies (JSON string → list)
                param_data = ltrd.get_all_params()
                companies_default_list = json.loads(param_data[0][0])  # adjust if this popover has a separate default list

                company_list = sorted(lpo_grn_net_values["Companyname"].unique())
                st.write("Select Company:")

                # Buttons layout
                c1, c2 = st.columns([0.3, 0.7])

                with c1:
                    select_company = st.button(
                        "✔ Select All",
                        key="select_all_company",
                        use_container_width=True
                    )

                with c2:
                    clear_company = st.button(
                        "✖ Clear All",
                        key="clear_all_company",
                        use_container_width=True
                    )

                selected_companies = []

                # --- Loop through companies ---
                for comp in company_list:
                    key = f"chk_lpo_grn_{comp}"

                    # 🔹 Initialize default selection (only once)
                    if key not in st.session_state:
                        st.session_state[key] = comp in companies_default_list

                    # ---- Clear all logic ----
                    if clear_company:
                        st.session_state[key] = False

                    # ---- Select all logic ----
                    if select_company:
                        st.session_state[key] = True

                    # Checkbox
                    checked = st.checkbox(comp, key=key)

                    # Collect selected companies
                    if checked:
                        selected_companies.append(comp)
        # --------------- PROJECT FILTER ---------------
        with col3b:
            with st.popover("📂 Choose Project"):

                # ---- Step 1: Apply company filter first ----
                if selected_companies:
                    temp_df = lpo_grn_net_values[
                        lpo_grn_net_values["Companyname"].isin(selected_companies)
                    ]
                else:
                    temp_df = lpo_grn_net_values

                project_list = sorted(temp_df["Project"].unique())
                st.write("Select Project:")

                # ---- Fetch default projects (JSON → list) ----
                param_data = ltrd.get_all_params()
                default_project_list = json.loads(param_data[0][1])  # project defaults

                # --- Small buttons row ---
                p1, p2 = st.columns([0.2, 0.2])

                with p1:
                    clear_project = st.button(
                        "✖ Clear",
                        key="clear_all_project",
                        use_container_width=True
                    )

                with p2:
                    select_all_project = st.button(
                        "✔ Select All",
                        key="select_all_project",
                        use_container_width=True
                    )

                selected_projects = []

                # ---- Step 2: Build checkboxes with logic ----
                for proj in project_list:
                    key = f"chk_lpo_grn_proj_{proj}"

                    # 🔹 Initialize default selection ONCE
                    if key not in st.session_state:
                        st.session_state[key] = proj in default_project_list

                    # Clear all logic
                    if clear_project:
                        st.session_state[key] = False

                    # Select all logic
                    if select_all_project:
                        st.session_state[key] = True

                    # Render checkbox
                    if st.checkbox(proj, key=key):
                        selected_projects.append(proj)

        # ---------------- APPLY FINAL FILTER ----------------
        filtered_projects = lpo_grn_net_values.copy()

        if selected_companies:
            filtered_projects = filtered_projects[
                filtered_projects["Companyname"].isin(selected_companies)
            ]

        if selected_projects:
            filtered_projects = filtered_projects[
                filtered_projects["Project"].isin(selected_projects)
            ]

        # --------------- REMOVE TOP-N LOGIC ---------------
        # Show ALL filtered projects instead of top N
        top_projects = filtered_projects.sort_values(by="PO_Value", ascending=False)

        # --------------- CONVERT VALUES TO MILLIONS ---------------
        for df in [top_projects, top_projects2]:
            df['PO_Value'] = (df['PO_Value'] / 1_000_000).round(1)
            df['GRN_Value'] = (df['GRN_Value'] / 1_000_000).round(1)

        # --------------- DOWNLOAD EXCEL BUTTON ---------------
        with col3c:
            st.download_button(
                label="📥 Download Excel",
                data=export_excel(top_projects),
                file_name=f"projects_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # --------------- BAR CHART ---------------
        fig_bar5 = px.bar(
            top_projects,
            x='Project',
            y=['PO_Value', 'GRN_Value'],
            text_auto=True,
            title=f'Main Projects',
            color_discrete_map={"PO_Value": "#006400", "GRN_Value": "#90EE90"},
        )

        fig_bar5.update_layout(
            autosize=True,
            height=500,
            xaxis_title='Project',
            yaxis_title='Amount (OMR in Millions)',
            barmode='group'
        )

        st.plotly_chart(fig_bar5, use_container_width=True, key="top_projects_chart")
        
                        
       
    with tab4:

        # --- Convert YEARLY safely
        Purchase['YEAR'] = pd.to_numeric(Purchase['YEAR'], errors='coerce')
        Purchase = Purchase.dropna(subset=['YEAR'])
        Purchase['YEAR'] = Purchase['YEAR'].astype(int)
        Purchase['MONTH'] = Purchase['MONTH'].astype(str).str.strip().str.upper()

        today = dt.datetime.today()
        cm = today.month
        cy = today.year
        py = cy - 1

        if cm == 1:
            pm_year = cy - 1
            pm_month = 12
        else:
            pm_year = cy
            pm_month = cm - 1

        # --- UI layout
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        # --- Company filter first
        with col1:
            with st.popover("🏢 Choose Company"):

                # Fetch default companies/branches (JSON string → list)
                param_data = ltrd.get_all_params()
                companies_default_list = json.loads(param_data[0][0])  # adjust if this popover has a separate default list

                # Company / Branch list
                company_list = sorted(Purchase["BRANCHNAME"].unique())
                st.write("Select Company:")

                # --- Select All + Clear All buttons ---
                c1, c2 = st.columns([0.3, 0.7])

                with c1:
                    select_company = st.button(
                        "✔ Select All",
                        key="select_all_purchase",
                        use_container_width=True
                    )

                with c2:
                    clear_company = st.button(
                        "✖ Clear All",
                        key="clear_all_purchase",
                        use_container_width=True
                    )

                selected_companies = []

                # --- Loop through companies/branches ---
                for comp in company_list:
                    key = f"chk_purchase_{comp}"

                    # 🔹 Initialize default selection (only once)
                    if key not in st.session_state:
                        st.session_state[key] = comp in companies_default_list

                    # ---- Clear all logic ----
                    if clear_company:
                        st.session_state[key] = False

                    # ---- Select all logic ----
                    if select_company:
                        st.session_state[key] = True

                    # Checkbox
                    checked = st.checkbox(comp, key=key)

                    # Collect selected companies/branches
                    if checked:
                        selected_companies.append(comp)

            # --- Filtering logic ---
            if selected_companies:
                filtered_purchase = Purchase[
                    Purchase["BRANCHNAME"].isin(selected_companies)
                ]
            else:
                filtered_purchase = Purchase
        # --- Year range filter
        with col2:
            year_list = sorted(Purchase["YEAR"].unique())
            selected_year_range = st.select_slider(
                "Select Year Range",
                options=year_list,
                value=(year_list[0], year_list[-1]),  # default full range
                key="purchase_year_range_filter_7"
            )
            start_year, end_year = selected_year_range

        # --- Top N selector
        with col3:
            top_n_suppliers = st.slider(
                "Number of Top Suppliers",
                min_value=5,
                max_value=50,
                value=20,
                step=5,
                key="top_n_suppliers_slider_6"
            )
        
        Purchase_filtered = Purchase.copy()

        if selected_companies:
            Purchase_filtered = Purchase_filtered[Purchase_filtered["BRANCHNAME"].isin(selected_companies)]

        if selected_year_range:
            Purchase_filtered = Purchase_filtered[
                (Purchase_filtered["YEAR"] >= start_year) &
                (Purchase_filtered["YEAR"] <= end_year)
            ]

        # --- Calculate KPIs based on filtered data
        cy_amount = Purchase_filtered.loc[Purchase_filtered['YEAR'] == cy, 'AMOUNT_OMR'].sum()
        py_amount = Purchase_filtered.loc[Purchase_filtered['YEAR'] == py, 'AMOUNT_OMR'].sum()
        cm_amount = Purchase_filtered.loc[
            (Purchase_filtered['YEAR'] == cy) & (Purchase_filtered['MONTH'] == str(cm)),
            'AMOUNT_OMR'
        ].sum()
        pm_amount = Purchase_filtered.loc[
            (Purchase_filtered['YEAR'] == pm_year) & (Purchase_filtered['MONTH'] == str(pm_month)),
            'AMOUNT_OMR'
        ].sum()

        # --- Supplier-wise summary (based on filtered data)
        supplierwise_pur = Purchase_filtered.groupby('VENDORNAME')['AMOUNT_OMR'].sum().reset_index()
        supplierwise_pur = supplierwise_pur.sort_values(by='AMOUNT_OMR', ascending=False)

        # --- Top N suppliers (dynamic)
        top_suppliers = supplierwise_pur.head(top_n_suppliers)
        top_suppliers['AMOUNT_OMR'] = top_suppliers['AMOUNT_OMR'].apply(np.int64)
        top_suppliers['VENDOR_NAME'] = top_suppliers['VENDORNAME'].apply(
            lambda x: '<br>'.join([x[i:i+12] for i in range(0, len(x), 12)])
        )
        top_suppliers_export = top_suppliers.copy()  # for Excel export
        
        top_suppliers['AMOUNT_OMR'] = (top_suppliers['AMOUNT_OMR'] / 1_000_000).round(1)
        
        with col4:
            st.download_button(
                label="📥 Download Excel",
                data=export_excel(top_suppliers_export),
                file_name=f"top_{top_n_suppliers}_suppliers_{start_year}_{end_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # --- Chart
        company_label = ", ".join(selected_companies) if selected_companies else "All Companies"
        
        fig_bar = px.bar(
            top_suppliers,
            x='VENDOR_NAME',
            y='AMOUNT_OMR',
            title=f"Top {top_n_suppliers} Suppliers ({start_year}–{end_year})",
            text_auto=True,
            color_discrete_sequence=["#006400"]
        )

        fig_bar.update_yaxes(tickformat=",")
        fig_bar.update_layout(
            xaxis_title="Supplier",
            yaxis_title="Amount (OMR)"
        )

        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab5:
        top_projects = lpo_grn_net_values.copy()

        col3, col3a, col3b, col3c, col3d, col3e = st.columns([1, 1, 1, 1, 1, 1])

       
        with col3a:
            with st.popover("🏢 Choose Company"):

                # Fetch default companies (JSON string → list)
                param_data = ltrd.get_all_params()
                companies_default_list = json.loads(param_data[0][0])  # adjust if a separate default list is needed

                company_list = sorted(lpo_grn_net_values["Companyname"].unique())
                selected_companies = []

                st.write("Select Company:")

                # Select All + Clear All buttons
                c1, c2 = st.columns([0.3, 0.7])

                with c1:
                    select_company = st.button(
                        "✔ Select All",
                        key="select_all_company_tab5",
                        use_container_width=True
                    )

                with c2:
                    clear_company = st.button(
                        "✖ Clear All",
                        key="clear_all_company_tab5",
                        use_container_width=True
                    )

                # Checkboxes with select/clear logic
                for comp in company_list:
                    key = f"chk_lpo_grn_tab5_{comp}"

                    # 🔹 Initialize default selection (only once)
                    if key not in st.session_state:
                        st.session_state[key] = comp in companies_default_list

                    # Clear all logic
                    if clear_company:
                        st.session_state[key] = False

                    # Select all logic
                    if select_company:
                        st.session_state[key] = True

                    # Checkbox
                    checked = st.checkbox(comp, key=key)

                    if checked:
                        selected_companies.append(comp)

        # Apply company filter
        if selected_companies:
            filtered_projects = lpo_grn_net_values[
                lpo_grn_net_values["Companyname"].isin(selected_companies)
            ]
        else:
            filtered_projects = lpo_grn_net_values

        
        with col3b:
            with st.popover("📂 Choose Project"):

                # Fetch default projects (JSON string → list)
                param_data = ltrd.get_all_params()
                default_project_list = json.loads(param_data[0][1])  # assuming projects are stored in index [1]

                project_list = sorted(filtered_projects["Project"].unique())
                selected_projects = []

                st.write("Select Project:")

                # --- Buttons Row ---
                p1, p2 = st.columns([0.3, 0.3])

                with p1:
                    clear_project = st.button(
                        "✖ Clear All",
                        key="clear_all_project_tab5",
                        use_container_width=True
                    )

                with p2:
                    select_all_project = st.button(
                        "✔ Select All",
                        key="select_all_project_tab5",
                        use_container_width=True
                    )

                # --- Checkboxes with state logic ---
                for proj in project_list:
                    key = f"chk_lpo_grn_proj_tab5_{proj}"

                    # 🔹 Initialize default selection (ONLY once)
                    if key not in st.session_state:
                        st.session_state[key] = proj in default_project_list

                    # Clear all
                    if clear_project:
                        st.session_state[key] = False

                    # Select all
                    if select_all_project:
                        st.session_state[key] = True

                    # Render checkbox
                    if st.checkbox(proj, key=key):
                        selected_projects.append(proj)
        # -------- APPLY PROJECT FILTER --------
        if selected_projects:
            filtered_projects = filtered_projects[
                filtered_projects["Project"].isin(selected_projects)
            ]
        
        top_projects = filtered_projects.sort_values(by="PO_Value", ascending=False)
        top_projects_export=top_projects.copy()  # to avoid SettingWithCopyWarning

        # Convert to millions
        for df in [top_projects, top_projects2]:
            df['PO_Value'] = (df['PO_Value'] / 1_000_000).round(1)
            df['GRN_Value'] = (df['GRN_Value'] / 1_000_000).round(1)

       
        with col3c:
            st.download_button(
                label="📥 Download Excel",
                data=export_excel(top_projects_export),
                file_name=f"top_projects_tab5_left_{start_year}_{end_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_button_tab5_left"
            )

      
        fig_bar5 = px.bar(
            top_projects,
            x='Project',
            y=['PO_Value', 'GRN_Value'],
            text_auto=True,
            title='Main Facilities',
            color_discrete_map={"PO_Value": "#006400", "GRN_Value": "#90EE90"},
        )

        fig_bar5.update_layout(
            autosize=True,
            height=500,
            xaxis_title='Project',
            yaxis_title='Amount (OMR in Millions)',
            barmode='group'
        )

        st.plotly_chart(fig_bar5, use_container_width=True, key="top_projects_chart_tab5_left")