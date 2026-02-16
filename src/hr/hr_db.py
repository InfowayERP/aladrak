import streamlit as st
import plotly.express as px
import pandas as pd
import io
import os
import warnings
import calendar
import base64
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

def hr_dashboard(total_employee_strength_data,in_out_strength,visa_expiry,employee_strength_data,department,employee):
    report_title("HR Dashboard")
    tab10,tab11,tab12,tab13,tab14 = st.tabs(["👥Yearly Strength","👥Monthly Strength ","🔃In and Out","📑Visa Expiry","🏢Department-wise"])
    
    with tab10:
        # Put HR charts, filters, metrics here
        # --- Ensure numeric Year first ---
        total_employee_strength_data["YEAR"] = total_employee_strength_data["YEAR"].astype(int)

        total_employee_strength_data = total_employee_strength_data[total_employee_strength_data["YEAR"] >= 2013]
   

        col3P,col33P,col34P,col35P=st.columns([1,1,1,1])
       
        with col3P:
    # --- Ensure numeric Year ---
            total_employee_strength_data["YEAR"] = total_employee_strength_data["YEAR"].astype(int)

            # --- Sorted unique years ---
            year_list = sorted(total_employee_strength_data["YEAR"].unique())

            # --- Use select_slider for year range ---
            start_year, end_year = st.select_slider(
                "Select Year Range",
                options=year_list,
                value=(year_list[0], year_list[-1]),
                key="year_range_slider"
            )

            # --- Company multiselect ---
            with col33P:
                with st.popover("🏢 Select Company"):

                    # ---- Fetch default companies (JSON → list) ----
                    param_data = ltrd.get_all_params()
                    companies_default_list = json.loads(param_data[0][0])  # adjust if employee-strength has a separate default list

                    # Company list
                    company_list = sorted(
                        total_employee_strength_data["COMPANY"].unique().tolist()
                    )

                    st.write("Select Company:")

                    # Select All + Clear All buttons
                    c1, c2 = st.columns([0.3, 0.7])

                    with c1:
                        select_company = st.button(
                            "✔ Select All",
                            key="select_all_emp_strength",
                            use_container_width=True
                        )

                    with c2:
                        clear_company = st.button(
                            "✖ Clear All",
                            key="clear_all_emp_strength",
                            use_container_width=True
                        )

                    selected_companies = []

                    # Checkbox loop with select/clear/default logic
                    for comp in company_list:
                        key = f"chk_emp_strength_{comp}"

                        # 🔹 Initialize default selection (only once)
                        if key not in st.session_state:
                            st.session_state[key] = comp in companies_default_list

                        # Clear All logic
                        if clear_company:
                            st.session_state[key] = False

                        # Select All logic
                        if select_company:
                            st.session_state[key] = True

                        # Render checkbox
                        checked = st.checkbox(comp, key=key)

                        if checked:
                            selected_companies.append(comp)

            # --- Filtering logic ---
            if selected_companies:
                filtered_employee_data = total_employee_strength_data[
                    total_employee_strength_data["COMPANY"].isin(selected_companies)
                ]
            else:
                filtered_employee_data = total_employee_strength_data
            # --- Employee Main Category multiselect ---
            with col35P:
                with st.popover("👷‍♂️ Select Employee Category"):

                    emp_cat_list = sorted(
                        total_employee_strength_data["EMPMAINCAT"].dropna().unique().tolist()
                    )
                    selected_emp_cats = []

                    st.write("Select Employee Category:")

                    # --- Buttons Row ---
                    e1, e2 = st.columns([0.3, 0.3])
                    with e1:
                        clear_emp_cat = st.button(
                            "✖ Clear All",
                            key="clear_all_emp_cat",
                            use_container_width=True
                        )
                    with e2:
                        select_all_emp_cat = st.button(
                            "✔ Select All",
                            key="select_all_emp_cat",
                            use_container_width=True
                        )

                    # --- Checkboxes with select/clear logic ---
                    for cat in emp_cat_list:
                        key = f"chk_emp_cat_{cat}"

                        # Clear all
                        if clear_emp_cat:
                            st.session_state[key] = False

                        # Select all
                        if select_all_emp_cat:
                            st.session_state[key] = True

                        # Render checkbox
                        if st.checkbox(cat, key=key):
                            selected_emp_cats.append(cat)

            # -------- APPLY FILTERS --------
            filtered_data = total_employee_strength_data[
                (total_employee_strength_data["YEAR"] >= start_year) &
                (total_employee_strength_data["YEAR"] <= end_year)
            ].copy()

            if selected_companies:
                filtered_data = filtered_data[filtered_data["COMPANY"].isin(selected_companies)]

            if selected_emp_cats:
                filtered_data = filtered_data[filtered_data["EMPMAINCAT"].isin(selected_emp_cats)]

            # Convert datatypes after filtering (not before)
            filtered_data["STRENGTH"] = (
                filtered_data["STRENGTH"].astype(str).str.replace(",", "").astype(int)
            )

            # --- Yearly strength (use filtered data only for DECEMBER) ---
            yearly_strength = filtered_data[filtered_data["MONTH"] == "DECEMBER"]
            yearly_strength = yearly_strength.groupby("YEAR")["STRENGTH"].sum().reset_index()

            with col34P:
                st.download_button(
                    "📥 Download Excel",
                    data=export_excel(yearly_strength),
                    file_name=f"yearly_strength_{start_year}_{end_year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            with col3P:
                st.caption("ℹ️ Tip: Click on any year bar to view the month-wise report.")

        # --- Chart Logic (same as before) ---
        yearly_strength = yearly_strength.groupby("YEAR")["STRENGTH"].sum().reset_index()

        if "selected_year" not in st.session_state:
            st.session_state.selected_year = None

        if st.session_state.selected_year is None:
            fig_hr = px.bar(
                yearly_strength,
                x="YEAR",
                y="STRENGTH",
                text_auto=True,
                title=f"Total Employee Strength - Yearly ({start_year}-{end_year})",
                color_discrete_sequence=["#006400"]
            )

            fig_hr.update_xaxes(
                tickmode="array",
                tickvals=yearly_strength["YEAR"],
                ticktext=yearly_strength["YEAR"]
            )
            fig_hr.update_traces(
                hovertemplate="<b>Year:</b> %{x}<br><b>Strength:</b> %{y}<br><i>Click bar for month-wise view</i><extra></extra>"
            )

        else:
            monthly_strength = (
                filtered_data[filtered_data["YEAR"] == st.session_state.selected_year]
                .groupby("MONTH")["STRENGTH"]
                .sum()
                .reset_index()
            )

            month_order = [
                "JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE",
                "JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"
            ]
            monthly_strength["MONTH"] = pd.Categorical(monthly_strength["MONTH"], categories=month_order, ordered=True)
            monthly_strength = monthly_strength.sort_values("MONTH")

            fig_hr = px.bar(
                monthly_strength,
                x="MONTH",
                y="STRENGTH",
                text_auto=True,
                title=f"Total Employee Strength - Monthly ({st.session_state.selected_year})",
                color_discrete_sequence=["#000064"]
            )

        clicked = st.plotly_chart(fig_hr, use_container_width=True, key="employee_strength", on_select="rerun")

        # --- Handle click and back navigation ---
        if clicked and clicked["selection"]["points"]:
            clicked_year = clicked["selection"]["points"][0].get("x")
            if st.session_state.selected_year is None and clicked_year:
                st.session_state.selected_year = int(clicked_year)
                st.rerun()

        if st.session_state.selected_year is not None:
            col1, col2 = st.columns([1, 10])
            if col1.button("⬅ Back to Yearly View"):
                st.session_state.selected_year = None
                st.rerun()
            fig_hr.update_layout(autosize=True, height=500)
        # Always render chart here (position fixed)
        #chart_placeholder = st.empty()
        #chart_placeholder.plotly_chart(fig_hr, use_container_width=True)
        

    with tab11:
        # --- Filter only LABOUR ---
        labour_data = total_employee_strength_data[total_employee_strength_data["EMPMAINCAT"] == "LABOUR"]

        # --- Group by YEAR, MM, and Companyname ---
        monthly_labour_strength = (
            labour_data.groupby(["YEAR", "MM", "COMPANY"])["STRENGTH"]
            .sum()
            .reset_index()
        )

        # --- Ensure MM is zero-padded (01–12) ---
        monthly_labour_strength["MM"] = monthly_labour_strength["MM"].astype(str).str.zfill(2)
        monthly_labour_strength = monthly_labour_strength[monthly_labour_strength["YEAR"] >= 2013]

        # --- Create YearMonth column ---
        monthly_labour_strength["YearMonth"] = monthly_labour_strength["YEAR"].astype(str) + "-" + monthly_labour_strength["MM"]

        # --- Sort by YearMonth ---
        monthly_labour_strength = monthly_labour_strength.sort_values(by="YearMonth")

        # --- Layout columns ---
        col4P, col44P, col4Q, col44p = st.columns([2, 2, 2, 2])

        with col4P:
            # --- Year Range Slider ---
            monthly_labour_strength['YEAR'] = monthly_labour_strength['YEAR'].astype(int)
            year_list = sorted(monthly_labour_strength['YEAR'].unique())

            # Get current year
            current_year = dt.datetime.now().year
            default_start = default_end = current_year if current_year in year_list else year_list[0]

            start_year, end_year = st.select_slider(
                "Select Year Range",
                options=year_list,
                value=(default_start, default_end)
            )

        with col4Q:
            with st.popover("🏢 Select Company"):

                # ---- Fetch default companies (JSON → list) ----
                param_data = ltrd.get_all_params()
                companies_default_list = json.loads(param_data[0][0])

                company_list = sorted(monthly_labour_strength["COMPANY"].unique())

                st.write("Select Company:")

                # Select All + Clear All buttons
                c1, c2 = st.columns([0.3, 0.7])

                with c1:
                    select_company = st.button(
                        "✔ Select All",
                        key="select_all_monthly_labour",
                        use_container_width=True
                    )

                with c2:
                    clear_company = st.button(
                        "✖ Clear All",
                        key="clear_all_monthly_labour",
                        use_container_width=True
                    )

                selected_companies = []

                for comp in company_list:
                    key = f"chk_monthly_labour_{comp}"

                    # 🔹 Initialize default selection (once)
                    if key not in st.session_state:
                        st.session_state[key] = comp in companies_default_list

                    # Clear all
                    if clear_company:
                        st.session_state[key] = False

                    # Select all
                    if select_company:
                        st.session_state[key] = True

                    # Checkbox
                    if st.checkbox(comp, key=key):
                        selected_companies.append(comp)
        # --- Apply Filters ---
        monthly_labour_strength_filtered = monthly_labour_strength[
            (monthly_labour_strength["YEAR"] >= start_year) &
            (monthly_labour_strength["YEAR"] <= end_year)
        ]

        if selected_companies:
            monthly_labour_strength_filtered = monthly_labour_strength_filtered[
                monthly_labour_strength_filtered["COMPANY"].isin(selected_companies)
            ]


        # --- Plot ---
        fig_labour = px.bar(
            monthly_labour_strength_filtered,
            x="YearMonth",
            y="STRENGTH",
            color_discrete_sequence=px.colors.sequential.Greens[::-1],
            text_auto=True,
            title=f"Monthly LABOUR Strength ({start_year}-{end_year})",
        )

        fig_labour.update_layout(
            xaxis_title="Year-Month",
            yaxis_title="LABOUR Strength",
            autosize=True,
            height=500
        )

        with col44P:
            st.download_button(
                "📥 Download Excel",
                data=export_excel(monthly_labour_strength_filtered),
                file_name=f"Monthly_Labour_Strength_{start_year}_{end_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.plotly_chart(fig_labour, use_container_width=True)
       
    with tab12:
    # --- Clean and prepare data ---
        in_out_strength["Year"] = pd.to_numeric(in_out_strength["Year"], errors="coerce")
        in_out_strength = in_out_strength.dropna(subset=["Year"])
        in_out_strength = in_out_strength[in_out_strength["Year"] >= 2013]

        # Standardize columns
        in_out_strength.columns = in_out_strength.columns.str.strip()

        # --- Handle missing columns safely ---
        if "Companyname" not in in_out_strength.columns:
            in_out_strength["Companyname"] = "Unknown"
        if "EMPMAINCAT" not in in_out_strength.columns:
            in_out_strength["EMPMAINCAT"] = "Unknown"

        # Convert year to int
        in_out_strength["Year"] = in_out_strength["Year"].astype(int)

        # --- Group data ---
        in_out_strength_grouped = (
            in_out_strength.groupby(["Year", "Type", "Companyname", "EMPMAINCAT"])["Total_Strength"]
            .sum()
            .reset_index()
        )

        in_out_strength_grouped = in_out_strength_grouped.sort_values("Year")

        # --- Layout ---
        col5P, col5B, col54b, col54P = st.columns([1, 1, 1, 1])

        with col5P:
            year_list = sorted(in_out_strength_grouped["Year"].unique())
            start_year, end_year = st.select_slider(
                "Select Year Range",
                options=year_list,
                value=(year_list[0], year_list[-1]),
                key="year_range_slider_in_out",
            )

        with col5B:
            with st.popover("🏢 Company Filter"):

                # ---- Fetch default companies (JSON → list) ----
                param_data = ltrd.get_all_params()
                companies_default_list = json.loads(param_data[0][0])

                # Company list
                company_list = sorted(
                    in_out_strength_grouped["Companyname"].unique()
                )

                st.write("Select Company:")

                # Select All + Clear All buttons
                c1, c2 = st.columns([0.3, 0.7])

                with c1:
                    select_company = st.button(
                        "✔ Select All",
                        key="select_all_in_out_company",
                        use_container_width=True
                    )

                with c2:
                    clear_company = st.button(
                        "✖ Clear All",
                        key="clear_all_in_out_company",
                        use_container_width=True
                    )

                selected_companies = []

                # Checkbox list
                for comp in company_list:
                    key = f"chk_in_out_{comp}"

                    # 🔹 Initialize default selection (once)
                    if key not in st.session_state:
                        st.session_state[key] = comp in companies_default_list

                    # Clear All
                    if clear_company:
                        st.session_state[key] = False

                    # Select All
                    if select_company:
                        st.session_state[key] = True

                    if st.checkbox(comp, key=key):
                        selected_companies.append(comp)

        with col54b:
            with st.popover("👷‍♂️ Category Filter"):

                empcat_list = sorted(in_out_strength_grouped["EMPMAINCAT"].dropna().unique())
                selected_empcat = []

                st.write("Select Category:")

                # --- Buttons Row ---
                c1, c2 = st.columns([0.3, 0.3])
                with c1:
                    clear_empcat = st.button(
                        "✖ Clear All",
                        key="clear_all_inout_empcat",
                        use_container_width=True
                    )
                with c2:
                    select_all_empcat = st.button(
                        "✔ Select All",
                        key="select_all_inout_empcat",
                        use_container_width=True
                    )

                # --- Checkboxes with Select/Clear logic ---
                for cat in empcat_list:
                    key = f"chk_inout_empcat_{cat}"

                    # Clear All action
                    if clear_empcat:
                        st.session_state[key] = False

                    # Select All action
                    if select_all_empcat:
                        st.session_state[key] = True

                    # Render checkbox
                    if st.checkbox(cat, key=key):
                        selected_empcat.append(cat)
                in_out_strength_filtered = in_out_strength_grouped[
            (in_out_strength_grouped["Year"] >= start_year)
            & (in_out_strength_grouped["Year"] <= end_year)
        ]

        if selected_companies:
            in_out_strength_filtered = in_out_strength_filtered[
                in_out_strength_filtered["Companyname"].isin(selected_companies)
            ]

        if selected_empcat:
            in_out_strength_filtered = in_out_strength_filtered[
                in_out_strength_filtered["EMPMAINCAT"].isin(selected_empcat)
            ]
        in_out_strength_agg = (in_out_strength_filtered.groupby(["Year", "Type"], as_index=False)["Total_Strength"].sum())
        with col54P:
            st.download_button(
                "📥 Download Excel",
                data=export_excel(in_out_strength_agg),
                file_name=f"in_out_strength_{start_year}_{end_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # --- Create bar chart ---
        fig_in_out = px.bar(
        in_out_strength_agg,
        x="Year",
        y="Total_Strength",
        color="Type",
        barmode="group",
        text_auto=True,
        title=f"Yearly Employee Strength (IN vs OUT) ({start_year}-{end_year})",
        # ❌ removed facet_col
        color_discrete_sequence=["#006400", "#90EE90"],
        )

        fig_in_out.update_layout(autosize=True, height=500)
        fig_in_out.update_traces(textposition="outside")
        fig_in_out.update_xaxes(type="category")

        st.plotly_chart(fig_in_out, use_container_width=True)
            
        # Remove any trailing spaces in column names
    
    #fig_visa.update_layout(autosize=True,height=500  )
    
    with tab13:
        visa_expiry.columns = visa_expiry.columns.str.strip().str.lower()

        # --- Clean data ---
        if "employee_type" in visa_expiry.columns:
            visa_expiry["employee_type"] = visa_expiry["employee_type"].str.strip().str.upper()

        # Convert month names to numbers
        month_map = {
            "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
            "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
            "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
        }
        visa_expiry["expiry_month"] = visa_expiry["expiry_month"].str.strip().str.upper().map(month_map)

        # Filter for years 2023–2025
        visa_expiry = visa_expiry[
            (visa_expiry["expiry_year"] > 2022) & (visa_expiry["expiry_year"] < 2026)
        ]

        # Ensure Companyname column exists
        if "companyname" not in visa_expiry.columns:
            visa_expiry["companyname"] = "Unknown"

        # Normalize column case back for display
        visa_expiry.rename(columns=str.title, inplace=True)

        # Create Year_Month column
        visa_expiry["Year_Month"] = (
            visa_expiry["Expiry_Year"].astype(int).astype(str)
            + "-"
            + visa_expiry["Expiry_Month"].astype(int).astype(str).str.zfill(2)
        )
        visa_expiry = visa_expiry.sort_values(by=["Expiry_Year", "Expiry_Month"])

        # --- Layout ---
        col6P, col64P, col65P, col66P = st.columns([2, 4, 4, 2])

        # --- Year Range Filter ---
        with col6P:
            visa_expiry["Expiry_Year"] = visa_expiry["Expiry_Year"].astype(int)
            year_list = sorted(visa_expiry["Expiry_Year"].unique())
            start_year, end_year = st.select_slider(
                "Select Year Range",
                options=year_list,
                value=(year_list[0], year_list[-1]),
            )

        # --- Company Filter ---
        with col64P:
            with st.popover("🏢 Choose Company"):

                # ---- Fetch default companies (JSON → list) ----
                param_data = ltrd.get_all_params()
                companies_default_list = json.loads(param_data[0][0])  # company defaults

                # Company list
                company_list = sorted(visa_expiry["Companyname"].unique())

                st.write("Select Company:")

                # Select All + Clear All buttons
                c1, c2 = st.columns([0.3, 0.7])

                with c1:
                    select_company = st.button(
                        "✔ Select All",
                        key="select_all_visa_company",
                        use_container_width=True
                    )

                with c2:
                    clear_company = st.button(
                        "✖ Clear All",
                        key="clear_all_visa_company",
                        use_container_width=True
                    )

                selected_comp = []

                # Checkbox list with Select / Clear / Default logic
                for comp in company_list:
                    key = f"chk_visa_{comp}"

                    # 🔹 Initialize default selection (ONLY once)
                    if key not in st.session_state:
                        st.session_state[key] = comp in companies_default_list

                    # Clear All
                    if clear_company:
                        st.session_state[key] = False

                    # Select All
                    if select_company:
                        st.session_state[key] = True

                    # Render checkbox
                    if st.checkbox(comp, key=key):
                        selected_comp.append(comp)


        # --- Apply Company + Year Filters ---
        if selected_comp:
            visa_expiry_filtered = visa_expiry[
                (visa_expiry["Companyname"].isin(selected_comp))
                & (visa_expiry["Expiry_Year"] >= start_year)
                & (visa_expiry["Expiry_Year"] <= end_year)
            ]
        else:
            visa_expiry_filtered = visa_expiry[
                (visa_expiry["Expiry_Year"] >= start_year)
                & (visa_expiry["Expiry_Year"] <= end_year)
            ]


        # --- Employee Category Filter ---
        with col65P:
            with st.popover("👥 Employee Category"):

                empcat_list = sorted(visa_expiry["Employee_Category"].dropna().unique())
                selected_emp_types = []

                st.write("Select Employee Category:")

                # --- Buttons Row ---
                c1, c2 = st.columns([0.3, 0.3])
                with c1:
                    clear_empcat = st.button(
                        "✖ Clear All",
                        key="clear_all_visa_emp_cat",
                        use_container_width=True
                    )
                with c2:
                    select_all_empcat = st.button(
                        "✔ Select All",
                        key="select_all_visa_emp_cat",
                        use_container_width=True
                    )

                # --- Checkboxes with Select/Clear logic ---
                for cat in empcat_list:
                    key = f"chk_visa_emp_cat_{cat}"

                    # Clear all logic
                    if clear_empcat:
                        st.session_state[key] = False

                    # Select all logic
                    if select_all_empcat:
                        st.session_state[key] = True

                    # Render checkbox state
                    if st.checkbox(cat, key=key):
                        selected_emp_types.append(cat)

                if selected_emp_types:
                    visa_expiry_filtered = visa_expiry_filtered[
                        visa_expiry_filtered["Employee_Category"].isin(selected_emp_types)
                    ]
        # --- Download Button ---
        with col66P:
            st.download_button(
                "📥 Download Excel",
                data=export_excel(visa_expiry_filtered),
                file_name=f"visa_expiry_{start_year}_{end_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            # --- Chart ---
            fig_visa = px.bar(
            visa_expiry_filtered,
            x="Year_Month",
            y="Total_By_Month",   # <-- FIXED HERE
            color="Employee_Category",
            text_auto=True,
            title=f"Visa Expiry Report ({start_year}-{end_year})",
            color_discrete_sequence=["#006400", "#90EE90", "#228B22"],    )

        st.plotly_chart(fig_visa, use_container_width=True)


    with tab14:
    # --- Base group (Removed YEAR from grouping) ---
        dept_yearly = department.groupby(["EMPDEPT", "COMPANYNAME"])["TOTAL"].sum().reset_index()

        col14A, col14B,col14C, col14D, col14E, col14F = st.columns([1,1, 1, 1, 1, 1])

       
        with col14A:
            with st.popover("🏢 Select Company"):

                # ---- Fetch default companies (JSON → list) ----
                param_data = ltrd.get_all_params()
                companies_default_list = json.loads(param_data[0][0])  # company defaults

                company_list = sorted(department["COMPANYNAME"].unique())
                selected_companies = []

                st.write("Select Company:")
                c1, c2 = st.columns([0.3, 0.7])

                with c1:
                    select_company = st.button(
                        "✔ Select All",
                        key="select_all_department_company",
                        use_container_width=True
                    )

                with c2:
                    clear_company = st.button(
                        "✖ Clear All",
                        key="clear_all_department_company",
                        use_container_width=True
                    )

                for comp in company_list:
                    key = f"chk_department_{comp}"

                    # 🔹 Initialize default selection (only once)
                    if key not in st.session_state:
                        st.session_state[key] = comp in companies_default_list

                    if clear_company:
                        st.session_state[key] = False

                    if select_company:
                        st.session_state[key] = True

                    if st.checkbox(comp, key=key):
                        selected_companies.append(comp)

        with col14B:
            with st.popover("👥 Employee Category"):

                emp_cat_list = sorted(department["NCATEGORY"].dropna().unique())
                selected_emp_cats = []

                st.write("Select Employee Category:")
                e1, e2 = st.columns([0.3, 0.3])

                with e1:
                    select_emp_cat = st.button(
                        "✔ Select All",
                        key="select_all_emp_categories",
                        use_container_width=True
                    )
                with e2:
                    clear_emp_cat = st.button(
                        "✖ Clear All",
                        key="clear_all_emp_categories",
                        use_container_width=True
                    )

                for cat in emp_cat_list:
                    key = f"dept_chk_emp_cat_{cat}"   # <-- updated key

                    if clear_emp_cat:
                        st.session_state[key] = False
                    if select_emp_cat:
                        st.session_state[key] = True

                    if st.checkbox(cat, key=key):
                        selected_emp_cats.append(cat)

        # =======================================================================
        # APPLY FILTERS
        # =======================================================================
        dept_yearly_filtered = dept_yearly.copy()
        department_selected = department.copy()

        if selected_companies:
            dept_yearly_filtered = dept_yearly_filtered[
                dept_yearly_filtered["COMPANYNAME"].isin(selected_companies)
            ]
            department_selected = department_selected[
                department_selected["COMPANYNAME"].isin(selected_companies)
            ]

        if selected_emp_cats:
            dept_yearly_filtered = dept_yearly_filtered[
                dept_yearly_filtered["EMPDEPT"].isin(
                    department_selected[
                        department_selected["NCATEGORY"].isin(selected_emp_cats)
                    ]["EMPDEPT"].unique()
                )
            ]
            department_selected = department_selected[
                department_selected["NCATEGORY"].isin(selected_emp_cats)
            ]

        # =======================================================================
        # METRICS
        # =======================================================================
        with col14C:
            total_employees = department_selected["TOTAL"].sum()
            st.metric(label="👥 Total Employees", value=total_employees)

        nationality_grouped = (
            department_selected.groupby("CATEGORY")["TOTAL"].sum().reset_index()
        )

        total_omani = nationality_grouped.loc[
            nationality_grouped["CATEGORY"] == "Omani", "TOTAL"
        ].sum()

        total_expat = nationality_grouped.loc[
            nationality_grouped["CATEGORY"] == "Expat", "TOTAL"
        ].sum()

        with col14D:
            st.metric(label="👥 Total Omani Employees", value=int(total_omani))

        with col14E:
            st.metric(label="🌍 Total Expat Employees", value=int(total_expat))

    
        with col14F:
            st.download_button(
                "📥 Download Excel",
                data=export_excel(dept_yearly_filtered),
                file_name="dept_yearly.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # =======================================================================
        # CHART
        # =======================================================================
        col14a, col14b = st.columns([5, 0.10])
        with col14a:

            dept_yearly_filtered["EMPDEPT"] = dept_yearly_filtered["EMPDEPT"].apply(
                lambda x: "<br>".join([x[i:i + 12] for i in range(0, len(x), 12)])
            )

            dept_yearly_sum = dept_yearly_filtered.groupby("EMPDEPT", as_index=False)["TOTAL"].sum()

            fig_dept_yearly = px.bar(
                dept_yearly_sum,
                x="EMPDEPT",
                y="TOTAL",
                text_auto=True,
                title="Department-wise Employee Strength",
                color_discrete_sequence=px.colors.sequential.Greens[::-1]
            )

            st.plotly_chart(fig_dept_yearly, use_container_width=True)