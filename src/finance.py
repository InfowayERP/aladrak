import streamlit as st
import plotly.express as px
import pandas as pd
import io
import os
import warnings
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

def finance_dashboard(Ledger,cash,bank,cy_py_expense,cy_py_income,fin):
    report_title("Finance Dashboard")
    tab1, tab2, tab3= st.tabs([
        "📊 Financial Overview",
        "💵 Income & Expense",
        "🏦 Cash & Bank",
    ])
      
    total_income_cy = cy_py_income['CY_AMOUNT'].sum()
    total_income_py = cy_py_income['PY_AMOUNT'].sum()
    total_expense_cy = cy_py_expense['CM_AMOUNT'].sum()
    total_expense_py = cy_py_expense['PY_AMOUNT'].sum()
    total_asset = fin['TOTAL_ASSETAMT'].sum()
    total_liablity = fin['TOTAL_LIABILTYAMT'].sum()
    total_liablity=total_liablity*-1
    netbook_value = total_asset-total_liablity

    CY_PL = total_income_cy+total_expense_cy
    PY_PL = total_income_py+total_expense_py

    total_cash = cash['PRMCLOSING'].sum()
    total_bank = bank['PRMCLOSING'].sum()

    receivable = fin[fin['CATEGORY'] == 5]
    receivable = receivable['TOTAL_AMT'].sum()

    payable = fin[fin['CATEGORY'] == 4]
    payable = payable['TOTAL_AMT'].sum()

    today = datetime.today()
    current_month = today.month
    current_year = today.year

    with tab1:       
        col1, col2, col3, col4 ,col5= st.columns(5)
        col1.metric("Total Asset Value", f"{total_asset:,.0f}")
        col2.metric("Receivables", f"{receivable :,.0f}")
        col3.metric("Cash Book", f"{total_cash:,.0f}")
        col4.metric(f':inbox_tray: {current_year} - Revenue(OMR)', f"{int(total_income_cy):,}")
        col5.metric(f':outbox_tray: {current_year-1} - Revenue(OMR)', f"{int(total_income_py):,}")

        col1a, col1b, col1c, col1d ,col1e= st.columns(5)
        col1a.metric("Total Liability Value", f"{total_liablity:,.0f}")
        col1b.metric("Payables", f"{payable :,.0f}")
        col1c.metric("Bank Book", f"{total_bank:,.0f}")
        col1d.metric(f':inbox_tray: {current_year} - Expense(OMR)', f"{int(total_expense_cy):,}")
        col1e.metric(f':outbox_tray: {current_year-1} - Expense(OMR)', f"{int(total_expense_py):,}")

        col2a, col2b, col2c, col2d ,col2e= st.columns(5)
        col2a.metric("Total Net Value", f"{netbook_value:,.0f}")
        col2d.metric(f':inbox_tray: {current_year} - Profit/Loss(OMR)', f"{int(CY_PL):,}")
        col2e.metric(f':outbox_tray: {current_year-1} - Profit/Loss(OMR)', f"{int(PY_PL):,}") 
        
        company_summary = fin.groupby(['BRANCHCODE'])[['TOTAL_ASSETAMT', 'TOTAL_LIABILTYAMT']].sum().reset_index()
        company_summary['TOTAL_LIABILTYAMT'] = company_summary['TOTAL_LIABILTYAMT'] * -1
        company_summary['NET_VALUE'] = company_summary['TOTAL_ASSETAMT'] - company_summary['TOTAL_LIABILTYAMT']

        fig_comp = px.bar(
            company_summary,
            x='BRANCHCODE',
            y=['TOTAL_ASSETAMT', 'TOTAL_LIABILTYAMT','NET_VALUE'],
            barmode='group',
            title=f"Company Wise Financial Summary", 
            labels={'value': 'Amount(OMR)', 'variable': 'Company'},
            text_auto=True, color_discrete_sequence=["#006400", "#90EE90","#228B22"]  
        )

        fig_comp.update_traces(
            texttemplate='%{y:,.0f}',  # show full numbers without decimals
             textposition='outside',
             cliponaxis=False 
        )
        fig_comp.update_layout(
            xaxis_title="BRANCHCODE",
            yaxis_title="Amount (OMR)",
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            margin=dict(t=80, b=60)
        )
        fig_comp.update_yaxes(showticklabels=False)

      
        st.plotly_chart(fig_comp, use_container_width=True)

        

    with tab2:
        top_accounts = (cy_py_income.groupby('ACCOUNTNAME')['CY_AMOUNT'].sum().reset_index().sort_values('CY_AMOUNT', ascending=False).head(10))
        top_accounts['ACCOUNTNAME'] = (top_accounts['ACCOUNTNAME'].astype(str).str.title().apply(lambda x: x if len(x) <= 20 else x[:17] + '...'))
        col2a, col2b= st.columns(2)
        fig_top_income = px.bar(
            top_accounts,
            x='ACCOUNTNAME',
            y='CY_AMOUNT',
            text='CY_AMOUNT',labels={'value': 'Amount', 'variable': 'ACCOUNT'},
            title='Top 10 Income Accounts', color_discrete_sequence=px.colors.sequential.Greens[::-1]
        )

        fig_top_income.update_traces(
            texttemplate='%{y:,.0f}',  # show full numbers without decimals
            textposition='outside', textfont_size=8 
        )
        fig_top_income.update_layout(
            xaxis_title="Account",   # X-axis label
            yaxis_title="Amount (OMR)",   # Y-axis label
            xaxis_tickangle=-45,autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            height=350
            )
        
        fig_top_income.update_layout(xaxis_tickangle=-45)
        fig_top_income.update_yaxes(showticklabels=False)
        with col2a:
            st.plotly_chart(fig_top_income, use_container_width=True)

        top_companies = (cy_py_income.groupby('COMPANYCODE')['CY_AMOUNT'].sum().reset_index().sort_values('CY_AMOUNT', ascending=False).head(10))
        fig_top_companies = px.bar(
            top_companies,
            x='COMPANYCODE',
            y='CY_AMOUNT',
            text='CY_AMOUNT',
            title='Top 10 Companies by Income (CY)', color_discrete_sequence=px.colors.sequential.Greens[::-1]
        )

        fig_top_companies.update_traces(
            texttemplate='%{y:,.0f}',  # show full numbers without decimals
            textposition='outside'
        )

        fig_top_companies.update_layout(
            xaxis_title="Company Code",   # X-axis label
            yaxis_title="Amount (OMR)",   # Y-axis label
            xaxis_tickangle=-45,autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            height=350
            )
        fig_top_companies.update_yaxes(showticklabels=False)
        with col2b:
            st.plotly_chart(fig_top_companies, use_container_width=True)

        col3a, col3b= st.columns(2)
        monthly_trend = cy_py_income.groupby(['VCHSHORTMONTH'])[['CY_AMOUNT', 'PY_AMOUNT']].sum().reset_index()
        monthly_trend['MONTH_NAME'] = monthly_trend['VCHSHORTMONTH'].apply(lambda x: calendar.month_abbr[int(x)])
        monthly_trend['MONTH_ORDER'] = monthly_trend['VCHSHORTMONTH']
        monthly_trend = monthly_trend.sort_values('MONTH_ORDER')
        
        fig_trend = px.bar(
            monthly_trend,
            x='MONTH_NAME',
            y=['CY_AMOUNT', 'PY_AMOUNT'],
            barmode='group',
            title=f"{current_year} v/s {current_year-1} Income Monthly Trend ", 
            labels={'value': 'Amount', 'variable': 'Year'},
            text_auto=True, color_discrete_sequence=["#006400", "#90EE90","#228B22"]  
        )

        fig_trend.update_traces(
            texttemplate='%{y:,.0f}',  # show full numbers without decimals
            textposition='outside'
        )
        fig_trend.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount (OMR)",
            uniformtext_minsize=8,
            uniformtext_mode='hide', margin=dict(l=10, r=10, t=40, b=10),
            height=350
        )
        fig_trend.update_yaxes(showticklabels=False)

        with col3a:
            st.plotly_chart(fig_trend, use_container_width=True)

        monthly_trend_exp = cy_py_expense.groupby(['VCHMONTHNO'])[['CY_AMOUNT', 'PY_AMOUNT']].sum().reset_index()

        monthly_trend_exp = cy_py_expense.groupby(['VCHMONTHNO'])[['CY_AMOUNT', 'PY_AMOUNT']].sum().reset_index()

        # --- Define month order ---
        month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

        # --- Ensure consistent case ---
        monthly_trend_exp['VCHMONTHNO'] = monthly_trend_exp['VCHMONTHNO'].str.title().str.strip()

        # --- Ordered category for sorting ---
        monthly_trend_exp['MONTH_ORDER'] = pd.Categorical(
            monthly_trend_exp['VCHMONTHNO'],
            categories=month_order,
            ordered=True
        )
        monthly_trend_exp = monthly_trend_exp.sort_values('MONTH_ORDER')
        
        fig_trend_exp = px.bar(
            monthly_trend_exp,
            x='MONTH_ORDER',
            y=['CY_AMOUNT', 'PY_AMOUNT'],
            barmode='group',
            title=f"{current_year} v/s {current_year-1} Expense Monthly Trend", 
            labels={'value': 'Amount', 'variable': 'Year'},
            text_auto=True, color_discrete_sequence=["#006400", "#90EE90","#228B22"]  
        )
        fig_trend_exp.update_xaxes(categoryorder='array', categoryarray=month_order)
        fig_trend_exp.update_traces(
            texttemplate='%{y:,.0f}',  # show full numbers without decimals
            textposition='outside'
        )
        fig_trend_exp.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount (OMR)",
            uniformtext_minsize=8,
            uniformtext_mode='hide', margin=dict(l=10, r=10, t=40, b=10),
            height=350
        )
        fig_trend_exp.update_yaxes(showticklabels=False)

        with col3b:
            st.plotly_chart(fig_trend_exp, use_container_width=True)

       


    with tab3:

        col3a, col3b= st.columns(2)
        with col3a:
            balances = pd.DataFrame({
                'Type': ['Cash', 'Bank'],
                'Amount': [total_cash, total_bank]
            })
            fig1 = px.bar(
                balances, x='Type', y='Amount', text='Amount',
                color='Type', title='Cash vs Bank Balance', color_discrete_sequence=px.colors.sequential.Greens[::-1]
            )
            fig1.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig1.update_layout(
                autosize=True,
                margin=dict(l=10, r=10, t=40, b=10),
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)
       

        with col3b:
            cash['ACCOUNTNAME'] = (cash['ACCOUNTNAME'].astype(str).str.title().apply(lambda x: x if len(x) <= 20 else x[:17] + '...')
)
            fig_cash = px.bar(cash.melt(id_vars='ACCOUNTNAME', value_vars=['PRVYCLOSINGM', 'PRMCLOSING', 'TODAYAMT']),
                x='ACCOUNTNAME',
                y='value',
                color='variable',
                barmode='group',
                title='Cash Account Balances Comparison',
                labels={'value': 'Amount (OMR)', 'variable': 'Period'},
                text_auto=True, color_discrete_sequence=["#006400", "#90EE90","#228B22"]  
            )
            fig_cash.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
            fig_cash.update_layout(height=300)
            st.plotly_chart(fig_cash, use_container_width=True)   
        col4a, col4b= st.columns(2)     

        with col4a:           
            summary = pd.DataFrame({
                'Category': ['Cash', 'Bank'],
                'Prev Year': [cash['PRVYCLOSINGM'].sum(), bank['PRVYCLOSING'].sum()],
                'Prev Month': [cash['PRMCLOSING'].sum(), bank['PRMCLOSING'].sum()],
                'Today': [cash['TODAYAMT'].sum(), bank['TODAYAMT'].sum()]
            })
            summary = summary.melt(id_vars='Category', var_name='Period', value_name='Amount')   
            fig_summary = px.bar(summary, x='Category', y='Amount', color='Period',
                barmode='group', text_auto=True,
                title='Overall Cash vs Bank Trend', color_discrete_sequence=["#006400", "#90EE90","#228B22"]  
            )

            fig_summary.update_layout(height=300)
            st.plotly_chart(fig_summary, use_container_width=True)

        with col4b: 
            fig_cash_pie = px.pie(    cash,
            names='ACCOUNTNAME',
            values='TODAYAMT',
            title='Cash Distribution by Account',
            hole=0.4,  color_discrete_sequence=px.colors.sequential.Greens[::-1]    )


            fig_cash_pie.update_layout(height=300)
            st.plotly_chart(fig_cash_pie, use_container_width=True)