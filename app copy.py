import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import calendar
import base64
from datetime import datetime
warnings.filterwarnings('ignore')
st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")

def load_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

@st.cache_data
def load_data_purchase():
    grn_data = pd.read_csv(os.path.join("data", "grn_data.csv"))
    lpo_data = pd.read_csv(os.path.join("data", "lpo_data.csv"))
    lpo_grn_gross_amount = pd.read_csv(os.path.join("data", "lpo_grn_gross_amount.csv"))
    lpo_grn_net_values = pd.read_csv(os.path.join("data", "lpo_grn_net_values.csv"))
    employee_strength_data = pd.read_csv(os.path.join("data","employee_strength_data.csv"))
    

    # Get current year
    current_year = datetime.now().year
    last_10_year = current_year - 9   # includes current year

    # Ensure Year is integer before filtering
    grn_data['Year'] = grn_data['Year'].astype(int)
    lpo_data['Year'] = lpo_data['Year'].astype(int)

    # Filter last 10 years
    grn_data = grn_data[grn_data['Year'] >= last_10_year]
    lpo_data = lpo_data[lpo_data['Year'] >= last_10_year]

    grn_data['Year']=grn_data['Year'].astype('str')
    lpo_data['Year']=lpo_data['Year'].astype('str')
    return grn_data, lpo_data, lpo_grn_gross_amount, lpo_grn_net_values,employee_strength_data  


def load_data_hr():
    total_employee_strength_data = pd.read_csv(os.path.join("data","total_employee_strength_data.csv"))
    in_out_strength = pd.read_csv(os.path.join("data","in_out_strength.csv"))
    visa_expiry=pd.read_csv(os.path.join("data","visa_expiry.csv"))
    total_employee_strength_data['MONTH'] = total_employee_strength_data['MONTH'].str.strip().str.upper()
    in_out_strength.columns = in_out_strength.columns.str.strip().str.title()
    return total_employee_strength_data,in_out_strength,visa_expiry

load_css('style.css')

with st.sidebar:
    main_menu = st.radio(
        "Select Module",
        ["🛒Purchase", "👥HR"]
    )

if main_menu == "🛒Purchase":
    # Define Purchase tabs
    report_title("Purchase Dashboard")
    tab1, tab2, tab3,tab4 = st.tabs([
        "📊 LPO Yearly Dashboard",
        "🌍 GRN Yearly Dashboard",
        "📈 GRN Monthly Dashboard",
        "📈 LPO Monthly Dashboard"
    ])

    grn_data, lpo_data, lpo_grn_gross_amount, lpo_grn_net_values, employee_strength_data  = load_data_purchase()

    total_lpo = lpo_data["Amount"].sum()
    total_grn = grn_data["Amount"].sum()
    difference = total_lpo - total_grn

    with tab1:
        col1P, Col1AP, col2P = st.columns([1.4, 5, 3])

        with col2P.popover("⚙️ Show Filters"):

            # --- Ensure numeric Year ---
            lpo_data['Year'] = lpo_data['Year'].astype(int)

            # --- Sorted unique years ---
            year_list = sorted(lpo_data['Year'].unique())

            # --- Use select_slider for year range ---
            start_year, end_year = st.select_slider(
                "Select Year Range",
                options=year_list,
                value=(year_list[0], year_list[-1])
            )

        view_option = st.radio("Select View", ["Yearly", "Monthly"], horizontal=True)

        if view_option == "Yearly":
                lpo_pur_year = lpo_data.groupby('Year')['Amount'].sum().reset_index()
                lpo_pur_year['Year'] = lpo_pur_year['Year'].astype(int).astype(str)
                lpo_pur_year['Amount'] = (lpo_pur_year['Amount'] / 1_000_000).round(1)

                # Bar chart
                fig_bar = px.bar(
                    lpo_pur_year, 
                    x='Year', 
                    y='Amount',
                    text_auto=True,
                    title='LPO Value OMR (in millions) - Yearly',
                   # color_discrete_sequence=["#90EE90"]  # light green
                )
                fig_bar.update_xaxes(
                    tickmode='array', 
                    tickvals=lpo_pur_year['Year'], 
                    ticktext=lpo_pur_year['Year']
                )
                fig_bar.update_yaxes(tickformat=",")

                # Pie chart
                fig_pie = px.pie(
                    lpo_pur_year, 
                    names='Year', 
                    values='Amount',
                    title='Net Amount LPO',
                    hole=0.4,   # donut style
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig_pie.update_traces(textinfo='percent+label')

        elif view_option == "Monthly":
                lpo_pur_month = lpo_data.groupby(['Year', 'Month'])['Amount'].sum().reset_index()
                lpo_pur_month['Amount'] = (lpo_pur_month['Amount'] / 1_000_000).round(1)
                lpo_pur_month['MonthName'] = lpo_pur_month['Month'].apply(lambda x: calendar.month_abbr[int(x)])
                lpo_pur_month['MonthName'] = pd.Categorical(
                    lpo_pur_month['MonthName'],
                    categories=[calendar.month_abbr[i] for i in range(1, 13)],
                    ordered=True             )
                
                lpo_pur_month['YearMonth'] = lpo_pur_month['Year'].astype(str) + "-" + lpo_pur_month['MonthName'].astype(str)

                # Stacked bar chart
                fig_bar = px.bar(
                    lpo_pur_month,
                    x='Year',
                    y='Amount',
                    color='MonthName',
                    text='Amount',
                    title='LPO Value OMR (in millions) - Yearly (Stacked by Month)',
                    barmode='stack'
                )
                fig_bar.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Amount (in millions)",
                    barmode='stack'
                )

                # Pie chart
                fig_pie = px.pie(
                    lpo_pur_month, 
                    names='YearMonth', 
                    values='Amount',
                    title='Net Amount LPO (Monthly)',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig_pie.update_traces(textinfo='percent+label')

            # Display charts
        col1, col2 = st.columns([3,2])
        with col1:
                clicked = st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
                st.plotly_chart(fig_pie, use_container_width=True)

        lpo_pur_year_month = lpo_data.groupby(['Year', 'Month'])['Amount'].sum().reset_index()

                    # Convert numeric months to names
        if lpo_pur_year_month['Month'].dtype != object:
                        lpo_pur_year_month['Month'] = lpo_pur_year_month['Month'].apply(lambda x: calendar.month_abbr[int(x)])

        lpo_pur_year_month['YearMonth'] = lpo_pur_year_month['Year'].astype(str) + "-" + lpo_pur_year_month['Month']

        lpo_pur_year_month['Amount'] = (lpo_pur_year_month['Amount'] / 1_000_000).round(1)
                    # Sort
                    # Create bar chart
        fig_bar2 = px.bar(
                        lpo_pur_year_month, 
                        x='YearMonth', 
                        y='Amount',
                        text_auto=True
                    )
        fig_bar2.update_yaxes(tickformat=",") 

                #st.subheader("LPO Monthly Summary", divider="blue")
                #st.plotly_chart(fig_bar2, use_container_width=True)


            

    total_grn = grn_data["Amount"].sum()
    with tab2:
                col3,col3a,col4=st.columns([1.4,5,3])
                col3.metric("GRN Amount", f"{total_grn/1_000_000:,.2f} M")
                with col4.popover("⚙️ Show Filters"):
                    col1, col2 = st.columns([1, 1])
                    grn_data['Year'] = grn_data['Year'].astype(int)

                    year_list1 = sorted(grn_data['Year'].unique())
                        # --- Year Filter ---
                    start_year, end_year = st.select_slider(
                    "Select Year Range",
                    options=year_list1,
                    value=(year_list1[0], year_list1[-1]),
                    key="grn_year_slider"  # unique key
                    )


                

    grn_pur_year = grn_data.groupby('Year')['Amount'].sum().reset_index()
    if grn_pur_year['Year'].dtype != object:
                grn_pur_year['Year'] = grn_pur_year['Year'].apply(lambda x: str(int(x)))

            # Sort the DataFrame in descending order based on TOTALAMOUNT
    grn_pur_year = grn_pur_year.sort_values(by='Amount', ascending=False)
    grn_pur_year['Year'] = grn_pur_year['Year'].astype(int).astype(str)
    grn_pur_year['Amount'] = (grn_pur_year['Amount'] / 1_000_000).round(1)

                # Create the bar chart using Plotly
    fig_bar1 = px.bar(grn_pur_year, 
                                x='Year', 
                                y='Amount',
                                text_auto=True,
                                title='GRN Value OMR (in millions)- Yearly',
                                    color_discrete_sequence=["#006400"])
                # Show all year labels
    fig_bar1.update_xaxes(
                    tickmode='array', 
                    tickvals=grn_pur_year['Year'], 
                    ticktext=grn_pur_year['Year']
                )
    fig_bar.update_yaxes(tickformat=",")

    with tab2:
            fig_bar1.update_layout(
                autosize=True,
                height=500   # 👈 match the CSS height
            )
        # --- New Pie Chart ---
            fig_pie1 = px.pie(
                    grn_pur_year, 
                    names='Year', 
                    values='Amount',
                    title='Net Amount GRN',
                    hole=0.4,   # donut style
                    color_discrete_sequence=px.colors.sequential.Greens  # gradient green
            )
            fig_pie1.update_traces(textinfo='percent+label')

            fig_pie1.update_layout(
                    autosize=True,
                    height=500   # 👈 match the CSS height
                )
            col1, col2 = st.columns([3,2])
            with col1:
                    st.plotly_chart(fig_bar1, use_container_width=True)
            with col2:
                    st.plotly_chart(fig_pie1, use_container_width=True)

    grn_pur_year_month = grn_data.groupby(['Year', 'Month'])['Amount'].sum().reset_index()

        # Convert numeric months to names
    if grn_pur_year_month['Month'].dtype != object:
            grn_pur_year_month['Month'] = grn_pur_year_month['Month'].apply(lambda x: calendar.month_abbr[int(x)])

        # Combine for display
    grn_pur_year_month['YearMonth'] = grn_pur_year_month['Year'].astype(str) + "-" + grn_pur_year_month['Month']
    grn_pur_year_month['Amount'] = (grn_pur_year_month['Amount'] / 1_000_000).round(1)
        # Sort
        #grn_pur_year_month = grn_pur_year_month.sort_values(by='Amount', ascending=False)

        # Create bar chart
    fig_bar2 = px.bar(
            grn_pur_year_month, 
            x='YearMonth', 
            y='Amount',
            text_auto=True,  color_discrete_sequence=["#006400"],title = "GRN Monthly Summary"
        )
    fig_bar2.update_yaxes(tickformat=",") 

        
    fig_bar2.update_layout(
                autosize=True,
                height=500   # 👈 match the CSS height
            )

    with tab3:
        st.plotly_chart(fig_bar2, use_container_width=True)

    pur_year_month = lpo_data.groupby(['Year', 'Month'])['Amount'].sum().reset_index()

        # Convert numeric months to names
    if pur_year_month['Month'].dtype != object:
            pur_year_month['Month'] = pur_year_month['Month'].apply(lambda x: calendar.month_abbr[int(x)])

        # Combine for display
    pur_year_month['YearMonth'] = pur_year_month['Year'].astype(str) + "-" + pur_year_month['Month']
    pur_year_month['Amount'] = (pur_year_month['Amount'] / 1_000_000).round(1)
        # Sort
        #grn_pur_year_month = grn_pur_year_month.sort_values(by='Amount', ascending=False)

        # Create bar chart
    fig_bar3 = px.bar(
            pur_year_month, 
            x='YearMonth', 
            y='Amount',
            text_auto=True,  color_discrete_sequence=["#006400"],title = "LPO Monthly Summary"
        )
    fig_bar3.update_yaxes(tickformat=",") 

        
    fig_bar3.update_layout(
                autosize=True,
                height=500   # 👈 match the CSS height
            )

    with tab4:
        st.plotly_chart(fig_bar3, use_container_width=True)

elif main_menu == "👥HR":
    # Define HR tab
    report_title("HR Dashboard")
    tab10,tab11,tab12,tab13 = st.tabs(["👥Yearly Strength","👥Monthly Strength ","🔃In and Out","📑Visa Expiry"])
    
    with tab10:
        # Put HR charts, filters, metrics here
        total_employee_strength_data,in_out_strength,visa_expiry=load_data_hr()

       
        col3P,col33P=st.columns([1.5,3])
        with col3P.expander("⚙️ Show Filters"):
                col1, col2 = st.columns([1, 1])

                selected_year_strength = col1.multiselect('Choose the Year',sorted(total_employee_strength_data['YEAR'].unique()))

                if not selected_year_strength:total_employee_strength_data = total_employee_strength_data.copy()
                else:
                    total_employee_strength_data = total_employee_strength_data[total_employee_strength_data['YEAR'].isin(selected_year_strength)]

        total_employee_strength_data["STRENGTH"] = (total_employee_strength_data["STRENGTH"].astype(str).str.replace(",", "").astype(int))
        
        yearly_strength=total_employee_strength_data[total_employee_strength_data['MONTH']=='DECEMBER']
        yearly_strength = yearly_strength[total_employee_strength_data["YEAR"] >= 2013]
        yearly_strength = (yearly_strength.groupby('YEAR')['STRENGTH'].sum().reset_index())
            
        if "selected_year" not in st.session_state:
            st.session_state.selected_year = None
        if st.session_state.selected_year is None:
             
            fig_hr = px.bar(yearly_strength,
            x="YEAR",
            y="STRENGTH",
            text_auto=True,
            title = "Total Employee Strenght - Yearly",
            color_discrete_sequence=["#006400"] )
        
            fig_hr.update_xaxes(
            tickmode='array', 
            tickvals=yearly_strength['YEAR'], 
            ticktext=yearly_strength['YEAR'])

        else:
        # Show monthly chart for selected year
            monthly_strength = (total_employee_strength_data[total_employee_strength_data['YEAR'] == st.session_state.selected_year]
            .groupby('MONTH')['STRENGTH'].sum().reset_index())

            month_order = ["JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE","JULY",
                    "AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"]
            monthly_strength['MONTH'] = pd.Categorical(monthly_strength['MONTH'], categories=month_order, ordered=True)
            monthly_strength = monthly_strength.sort_values('MONTH')

            fig_hr = px.bar(
            monthly_strength,
            x="MONTH",
            y="STRENGTH",
            text_auto=True,
            title=f"Total Employee Strength - Monthly ({st.session_state.selected_year})",
            color_discrete_sequence=["#03fc98"]
        )

        with tab10:# ---- Show chart with click handling ----
            clicked = st.plotly_chart(fig_hr, use_container_width=True, key="employee_strength", on_select="rerun")

    # Capture clickData
    if clicked and clicked["selection"]["points"]:
        clicked_year = clicked["selection"]["points"][0].get("x")
        if st.session_state.selected_year is None and clicked_year:
            st.session_state.selected_year = int(clicked_year)
            st.rerun()

    # Add a "Back" button for going back to yearly view
    if st.session_state.selected_year is not None:
        if st.button("⬅ Back to Yearly View"):
            st.session_state.selected_year = None
            st.rerun()
        fig_hr.update_layout(
            autosize=True,
            height=500   # 👈 match the CSS height
        )

     # Always render chart here (position fixed)
        with chart_placeholder:
             st.bar_chart(lpo_data, x="YearMonth", y="Amount")  # example chart
    

   
    # Filter only LABOUR
    labour_data = total_employee_strength_data[total_employee_strength_data["EMPMAINCAT"] == "LABOUR"]
    

    # Group by YEAR & MM (MM is numeric month)
    monthly_labour_strength = (
        labour_data.groupby(["YEAR", "MM"])["STRENGTH"]
        .sum()
        .reset_index()
    )

    # Ensure MM is zero-padded (01, 02, … 12)
    monthly_labour_strength["MM"] = monthly_labour_strength["MM"].astype(str).str.zfill(2)
    monthly_labour_strength = monthly_labour_strength[monthly_labour_strength["YEAR"] >= 2013]

    # Create YearMonth column (YYYY-MM)
    monthly_labour_strength["YearMonth"] = monthly_labour_strength["YEAR"].astype(str) + "-" + monthly_labour_strength["MM"]

    # Sort by YearMonth
    monthly_labour_strength = monthly_labour_strength.sort_values(by="YearMonth")

    # Plot
    fig_labour = px.bar(
        monthly_labour_strength,
        x="YearMonth",      # X-axis = Year-Month
        y="STRENGTH",       # Y-axis = Labour Strength
        text_auto=True,title = "Monthly LABOUR Strength",
         color_discrete_sequence=["#006400"] )
  

    # Layout
    fig_labour.update_layout(
        xaxis_title="Year-Month",
        yaxis_title="LABOUR Strength"
    )

    fig_labour.update_layout(
            autosize=True,
            height=500   # 👈 match the CSS height
        )
    with tab11:
        col4P,col44P=st.columns([1.5,3])
        with col4P.expander("⚙️ Show Filters"):
                    col1, col2 = st.columns([1, 1])

                    selected_mon_strength = col1.multiselect('Choose the Year',sorted(monthly_labour_strength['YEAR'].unique()))

                    if not selected_mon_strength:monthly_labour_strength = monthly_labour_strength.copy()
                    else:
                        monthly_labour_strength = monthly_labour_strength[monthly_labour_strength['YEAR'].isin(selected_mon_strength)]
    with tab11:
          st.plotly_chart(fig_labour, use_container_width=True)

    in_out_strength = in_out_strength[in_out_strength["Year"] >= 2013]

    # Convert year to int
    in_out_strength["Year"] = in_out_strength["Year"].astype(int)

    # Group
    in_out_strength = (
        in_out_strength.groupby(["Year","Type"])["Total_Strength"].sum().reset_index()
    )

    # Sort by Year
    in_out_strength = in_out_strength.sort_values("Year")

    # --- Create bar chart ---
    fig_in_out = px.bar(
        in_out_strength,
        x="Year",
        y="Total_Strength",
        color="Type",  # IN vs OUT
        barmode="group", text_auto=True,
        title="Yearly Employee Strength (IN vs OUT)",
        text="Total_Strength",color_discrete_sequence=["#006400", "#90EE90"]
    )
    fig_in_out.update_layout(
            autosize=True,
            height=500   # 👈 match the CSS height
        )
    # Better layout
    fig_in_out.update_traces(textposition="outside")
    fig_in_out.update_xaxes(type='category')  # force discrete x-axis

    with tab12:
        st.plotly_chart(fig_in_out, use_container_width=True)
        
        # Remove any trailing spaces in column names
    visa_expiry.columns = visa_expiry.columns.str.strip()

    # Filter for years > 2013 and < 2026
    visa_expiry = visa_expiry[(visa_expiry['Expiry_Year'] > 2023) & (visa_expiry['Expiry_Year'] < 2026)]

    # Create Year_Month column
    visa_expiry['Year_Month'] = visa_expiry['Expiry_Year'].astype(str) + '-' + visa_expiry['Expiry_Month'].astype(str).str.zfill(2)

    # Optional: sort by Year_Month
    visa_expiry = visa_expiry.sort_values(by=['Expiry_Year', 'Expiry_Month'])

    staff_data = visa_expiry[visa_expiry['Employee_Type'] == "STAFF"]
    worker_data = visa_expiry[visa_expiry['Employee_Type'] == "LABOUR"]


    # Plot
    fig_visa = px.bar(
        visa_expiry,
        x='Year_Month',
        y='Total_by_Month',
        color='Employee_Type', text_auto=True,
        title='Visa Expiry Report',color_discrete_sequence=["#006400", "#90EE90","#228B22"]
    )

    fig_staff_visa = px.bar(
        staff_data,
        x='Year_Month',
        y='Total_by_Month',
        color='Employee_Type', text_auto=True,
        title='Visa Expiry - Staff',color_discrete_sequence=["#006400", "#90EE90","#228B22"]
    )

    fig_worker_visa = px.bar(
        worker_data,
        x='Year_Month',
        y='Total_by_Month',
        color='Employee_Type', text_auto=True,
        title='Visa Expiry - Workers',color_discrete_sequence=["#006400", "#90EE90","#228B22"]
    )
    #fig_visa.update_layout(autosize=True,height=500  )
    
    with tab13:
        st.plotly_chart(fig_visa, use_container_width=True)

    with tab13:
        col1A, col2A = st.columns([1,1])
        with col1A:
            st.plotly_chart(fig_staff_visa, use_container_width=True)
        with col2A:
            st.plotly_chart(fig_worker_visa, use_container_width=True)