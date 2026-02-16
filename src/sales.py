import streamlit as st
import plotly.express as px
import pandas as pd
import io
import os
import warnings
import altair as alt
import calendar
import base64
from datetime import datetime

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

def sales_dashboard(Sales):
    report_title("Sales Dashboard")

    today = datetime.today()
    current_month = today.month
    current_year = today.year

    # ===== KPI Metrics =====
    current_month_sales = Sales[(Sales['DOCDT'].dt.month == current_month) &
                                (Sales['DOCDT'].dt.year == current_year)]['NET_AMOUNT'].sum()

    prev_month = 12 if current_month == 1 else current_month - 1
    prev_year = current_year - 1 if current_month == 1 else current_year

    prev_month_sales = Sales[(Sales['DOCDT'].dt.month == prev_month) &
                             (Sales['DOCDT'].dt.year == prev_year)]['NET_AMOUNT'].sum()

    py_sales = Sales[(Sales['DOCDT'].dt.month == current_month) &
                     (Sales['DOCDT'].dt.year == current_year - 1)]['NET_AMOUNT'].sum()

    cy_sales = Sales[Sales['DOCDT'].dt.year == current_year]['NET_AMOUNT'].sum()

    col1, col2, col3, col4 ,col5= st.columns(5)
    col1.metric("Current Month Sales", f"{current_month_sales:,.0f}")
    col2.metric("Current Year Sales", f"{cy_sales:,.0f}")
    col3.metric("Previous Month Sales", f"{prev_month_sales:,.0f}")
    col4.metric("Previous Year Sales", f"{py_sales:,.0f}")

    # ===== Company Filter =====
    selected_comp = col5.multiselect('🏢 Choose Company', sorted(Sales['COMPANY_NAME'].unique()))
    if selected_comp:
        Sales = Sales[Sales['COMPANY_NAME'].isin(selected_comp)]
    col1a, col2a = st.columns(2)

    with col1a:
        today = datetime.today()
        cy = today.year
        py = cy - 1

        Sales['DOCDT'] = pd.to_datetime(Sales['DOCDT'], errors='coerce')

# --- Add a YEAR column ---
        Sales['YEARLY'] = Sales['DOCDT'].dt.year

        # --- Filter for current and previous year ---
        sales_filtered = Sales[Sales['YEARLY'].isin([cy, py])]
        # Filter only the two years
        sales_filtered = Sales[Sales['YEARLY'].isin([cy, py])]

        company_sales = (
        sales_filtered.groupby(['YEARLY', 'COMPANY_NAME'])['NET_AMOUNT']
        .sum()
        .reset_index()    )

        # Round NET_AMOUNT to 2 decimal places
        company_sales['NET_AMOUNT'] = company_sales['NET_AMOUNT'].round(2)

        # Clean company names for better wrapping
        company_sales['Company'] = company_sales['COMPANY_NAME'].apply(
            lambda x: '<br>'.join([x[i:i+12] for i in range(0, len(x), 12)])
        )
        
        # Create bar chart with grouped bars
        company_sales['YEARLY'] = company_sales['YEARLY'].astype(str)

        color_map = {
            str(py): '#90EE90',   # Light Green for Previous Year
            str(cy): '#006400'    # Dark Green for Current Year
        }

        fig_bar2 = px.bar(
            company_sales,
            x='Company',
            y='NET_AMOUNT',
            color='YEARLY',
            color_discrete_map=color_map,  # Different color for CY and PY
            barmode='group',
            text_auto=True,
            title=f'Company Wise Sales Comparison ({py} vs {cy})'
              )
        fig_bar2.update_layout(
            xaxis_title='Company',
            yaxis_title='Amount (OMR)',
            font=dict(size=16),  # Change font size for overall text
            title_font=dict(size=20),  # Title font size
            xaxis=dict(
                tickangle=45,  # Rotate x-axis labels to avoid overlap
                tickfont=dict(size=10),  # Increase size of x-axis labels
            ),
            yaxis=dict(
                showticklabels=False,
                tickfont=dict(size=10),
                  tickformat=',',  # Increase size of y-axis labels
            )
        )


        fig_bar2.update_traces(texttemplate='%{y:,.0f}', textposition='auto',textfont=dict(size=16, color='black', family='Arial'))

        # Layout customization
        fig_bar2.update_layout(
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            height=350,
            xaxis_tickangle=-45
        )

        # Show chart in Streamlit
        st.plotly_chart(fig_bar2, use_container_width=True)
    
        # ===== Product Group Wise =====
       
    with col2a:
        top_customers = Sales[Sales['DOCDT'].dt.year == current_year]
        top_customers = (Sales.groupby('CUSTOMERNAME')['NET_AMOUNT']
                        .sum().reset_index()
                        .sort_values('NET_AMOUNT', ascending=False)
                        .head(10))
        top_customers['CUSTOMER_NAME'] = top_customers['CUSTOMERNAME'].apply(
            lambda x: '<br>'.join([x[i:i+12] for i in range(0, len(x), 12)])
        )
        fig_bar1 = px.bar(
            top_customers,
            x='CUSTOMER_NAME',
            y='NET_AMOUNT',
            text_auto=True,
            title='CY Top 10 Customers',
            color_discrete_sequence=["#006400"]
        )

        fig_bar1.update_layout(
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            height=350,xaxis_title='Customer',
            yaxis_title='Amount (OMR)',
        )

        fig_bar1.update_traces(texttemplate='%{y:,.0f}', textposition='auto',textfont=dict(size=16, color='black', family='Arial'))
        st.plotly_chart(fig_bar1, use_container_width=True)


       
    col3a, col4a = st.columns(2)

    with col3a:
    
        product_group_sales = (Sales[Sales['DOCDT'].dt.year == current_year]
                            .groupby('PRODUCT_GROUP')['NET_AMOUNT']
                            .sum().reset_index())
        fig_pie1 = px.pie(
            product_group_sales,
            names='PRODUCT_GROUP',
            values='NET_AMOUNT',
            title='CY Product Group Wise Sales',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Greens[::-1]
        )
        fig_pie1.update_traces(textinfo='percent+label')

        fig_pie1.update_layout(
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            height=350,xaxis_title='Product Group',
            yaxis_title='Amount (OMR)',
        )

        st.plotly_chart(fig_pie1, use_container_width=True)
     
    with col4a:
       
            
    # ===== Monthly Sales Chart =====
        monthly_sales = (Sales[Sales['DOCDT'].dt.year == current_year]
                        .groupby(Sales['DOCDT'].dt.month)['NET_AMOUNT']
                        .sum().reset_index())
        monthly_sales.columns = ['Month', 'Sales']
        monthly_sales['Month'] = monthly_sales['Month'].apply(lambda x: datetime(1900, x, 1).strftime('%b'))
        month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

        fig_bar = px.bar(
            monthly_sales,
            x='Month',
            y='Sales',
            text_auto=True,
            title='📊 CY Monthly Sales Summary',
            color_discrete_sequence=["#006400"]
        )
        fig_bar.update_xaxes(categoryorder='array', categoryarray=month_order)
        fig_bar.update_layout(
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            height=350
        )
        fig_bar.update_traces(texttemplate='%{y:,.0f}', textposition='auto',textfont=dict(size=16, color='black', family='Arial'))

        st.plotly_chart(fig_bar, use_container_width=True)
