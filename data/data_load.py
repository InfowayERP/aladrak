import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import calendar
import base64
import data.sqlqueries as sq
import data.sqlreader as sr
from datetime import datetime
warnings.filterwarnings('ignore')

def load_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def load_data_purchase():
   # grn_data = pd.read_csv(os.path.join("data", "grn_data.csv"))
    grn_data = sr.fetch_sql_data(sq.MV_GRN_DATA)
    #lpo_data = pd.read_csv(os.path.join("data", "lpo_data.csv"))
    lpo_data = sr.fetch_sql_data(sq.MV_LPODATA)
    #lpo_grn_gross_amount = pd.read_csv(os.path.join("data", "lpo_grn_gross_amount.csv"))
    lpo_grn_gross_amount = sr.fetch_sql_data(sq.MV_LPO_GRN_DATA)
    lpo_grn_net_values = sr.fetch_sql_data(sq.MV_LPO_GRN_NETVALUE)
   # lpo_grn_net_values = pd.read_csv(os.path.join("data", "lpo_grn_net_values.csv"))
    Purchase = sr.fetch_sql_data(sq.PURCHASE)
    
    

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
    return grn_data, lpo_data, lpo_grn_gross_amount, lpo_grn_net_values ,Purchase
 
def load_data_sales():
    sales=sr.fetch_sql_data(sq.SALES)

    return sales

def load_data_finance():
    Ledger = sr.fetch_sql_data(sq.LEDGER)
    cash = sr.fetch_sql_data(sq.CASH)
    bank = sr.fetch_sql_data(sq.BANK)
    cy_py_income = sr.fetch_sql_data(sq.CY_PY_INCOME)
    cy_py_expense = sr.fetch_sql_data(sq.CY_PY_EXPENSE)
    fin = sr.fetch_sql_data(sq.FIN)

    return Ledger,cash,bank,cy_py_expense,cy_py_income,fin

def load_data_hr():
    #total_employee_strength_data = pd.read_csv(os.path.join("data","total_employee_strength_data.csv"))
    total_employee_strength_data = sr.fetch_sql_data(sq.MV_EMPSTRENGTH)
   # in_out_strength = pd.read_csv(os.path.join("data","in_out_strength.csv"))
    in_out_strength = sr.fetch_sql_data(sq.MV_INOUT_STRENGTH)

    #visa_expiry=pd.read_csv(os.path.join("data","visa_expiry.csv"))
    visa_expiry=sr.fetch_sql_data(sq.MV_VISA_EXPIRY)

    department=sr.fetch_sql_data(sq.MV_DEPTSTRENGTH)

    employee = sr.fetch_sql_data(sq.EMPLOYEE)
    
   # employee_strength_data = pd.read_csv(os.path.join("data","employee_strength_data.csv"))
    employee_strength_data = sr.fetch_sql_data(sq.MV_EMPSTRENGTH)
    total_employee_strength_data['MONTH'] = total_employee_strength_data['MONTH'].str.strip().str.upper()
    in_out_strength.columns = in_out_strength.columns.str.strip().str.title()
    
    return total_employee_strength_data,in_out_strength,visa_expiry,employee_strength_data,department,employee

def load_data_global_param():
    return (
        sr.fetch_sql_data(sq.GP_COMPANY) ,
        sr.fetch_sql_data(sq.GP_PROJECT),
        sr.fetch_sql_data(sq.GP_YEAR) ,
        sr.fetch_sql_data(sq.GP_EMPCATEGORY) 
    )