import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import calendar
import base64
from datetime import datetime

import data.data_load as data_load
import src.purchase.purchase_db as purchase_db
import src.hr.hr_db as hr_db
import src.sales as sales_db
import src.finance as finance_db
import utils.login_page as login
import src.global_params as params
from email.mime.text import MIMEText

# -----------------------------------------------------------
# BASIC SETUP
# -----------------------------------------------------------
warnings.filterwarnings('ignore')
st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

# -----------------------------------------------------------
# SESSION STATE INITIALIZATION (FIRST!)
# -----------------------------------------------------------
if "USERS" not in st.session_state:
    st.session_state.USERS = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "main_menu" not in st.session_state:
    st.session_state.main_menu = "👥 HR"

# -----------------------------------------------------------
# DEV LOGIN BYPASS USING QUERY STRING (?sessionid=1)
# -----------------------------------------------------------
try:
    qp = st.query_params
    session_id = qp.get("sessionid")

    # Works for ALL Streamlit versions
    if session_id and str(session_id) == "1" and not st.session_state.logged_in:
        st.session_state.logged_in = True
        st.session_state.username = "dev_bypass"
        st.session_state.role = "admin"
        st.session_state.main_menu = "👥 HR"
        st.rerun()

except Exception as e:
    st.write("Query param error:", e)

# -----------------------------------------------------------
# LOAD CSS
# -----------------------------------------------------------
def load_css(file_name: str):
    try:
        with open(file_name) as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    except FileNotFoundError:
        pass

load_css("style.css")

# -----------------------------------------------------------
# DEV DEBUG (OPTIONAL)
# -----------------------------------------------------------
if os.environ.get("DEV_SHOW_QUERY_DEBUG", "0") == "10":
    with st.sidebar:
        st.markdown("**DEV DEBUG**")
        st.write("query_params:", st.query_params)
        dbg = {
            k: v if isinstance(v, (str, int, float, bool)) else type(v).__name__
            for k, v in st.session_state.items()
        }
        st.write("session_state:", dbg)

# -----------------------------------------------------------
# MAIN APPLICATION CLASS
# -----------------------------------------------------------
class InfowayApp:

    def __init__(self):
        pass

    # -------------------------------------------------------
    # DASHBOARD UI
    # -------------------------------------------------------
    def dashboard(self):

        # ---------------- SIDEBAR ----------------
        with st.sidebar:
            st.markdown(
                """
                <div style='text-align:left;'>
                    <marquee style='color:green; font-size:24px; font-weight:bold;'>
                        Welcome to Al Adarak!
                    </marquee>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("""
                <style>
                div.stButton > button {
                    width: 150px;
                    height: 45px;
                    font-size: 16px;
                    margin: 5px 0;
                }
                </style>
            """, unsafe_allow_html=True)

            if st.button("👥 HR"):
                st.session_state.main_menu = "👥 HR"

            if st.button("🧾 Sales"):
                st.session_state.main_menu = "🧾 Sales"

            if st.button("💰 Finance"):
                st.session_state.main_menu = "💰 Finance"

            if st.button("🛒 Purchase"):
                st.session_state.main_menu = "🛒 Purchase"

            if st.button("Global Parameter"):
                st.session_state.main_menu = "Global Parameter"

            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.role = ""
                st.success("Logout Successfully")
                st.rerun()

        # ---------------- MAIN CONTENT ----------------

        if st.session_state.main_menu == "👥 HR":
            total_emp, in_out, visa_exp, emp_strength, dept, employee = data_load.load_data_hr()
            hr_db.hr_dashboard(total_emp, in_out, visa_exp, emp_strength, dept, employee)

        elif st.session_state.main_menu == "🛒 Purchase":
            grn_data, lpo_data, gross_amt, net_values, Purchase = data_load.load_data_purchase()
            purchase_db.purchase_dashboard(grn_data, lpo_data, gross_amt, net_values, Purchase)

        elif st.session_state.main_menu == "🧾 Sales":
            sales = data_load.load_data_sales()
            sales_db.sales_dashboard(sales)

        elif st.session_state.main_menu == "💰 Finance":
            ledger, cash, bank, cy_py_exp, cy_py_inc, fin = data_load.load_data_finance()
            finance_db.finance_dashboard(ledger, cash, bank, cy_py_exp, cy_py_inc, fin)

        elif st.session_state.main_menu == "Global Parameter":
            GP_COMP, GP_PROJ, GP_YEAR, GP_CATEGORY = data_load.load_data_global_param()
            params.global_params(GP_COMP, GP_PROJ, GP_YEAR, GP_CATEGORY)

        else:
            st.info("Please select a module from the sidebar.")

    # -------------------------------------------------------
    # APP RUNNER
    # -------------------------------------------------------
    def run(self):

        if st.session_state.logged_in:
            role = st.session_state.role.lower().strip()

            if role in ["admin", "user", "viewer", "manager"]:
                self.dashboard()
            else:
                st.warning("No dashboard available for this role.")
        else:
            login.login()

# -----------------------------------------------------------
# RUN APP
# -----------------------------------------------------------
if __name__ == "__main__":
    app = InfowayApp()
    app.run()