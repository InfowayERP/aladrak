import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import calendar
import base64
from datetime import datetime
import data.sqlqueries as sq
import data.sqlreader as sr

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
    st.session_state.main_menu = None

if "user_perms" not in st.session_state:
    st.session_state.user_perms = None

# -----------------------------------------------------------
# DEV LOGIN BYPASS USING QUERY STRING (?sessionid=1)
# -----------------------------------------------------------
try:
    qp = st.query_params
    session_id = qp.get("sessionid")
    active_session=sr.fetch_sql_data(f"select username from axpertlog where sessionid = '{session_id}' and callfinished >= sysdate - (10/1440) ORDER BY callfinished DESC FETCH FIRST 1 ROW ONLY ")

    # Normalize session_id (Streamlit may return a list)
    if isinstance(session_id, (list, tuple)):
        session_id = session_id[0] if session_id else None

    # No sessionid -> normal login flow
    if session_id is None:
        pass
    else:
        # sessionid present
        if session_id in active_session['SESSIONID'].values:
            if not st.session_state.logged_in:
                username = active_session[active_session['SESSIONID'] == session_id]['USERNAME'].values[0]
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "admin"
                
                # Fetch and Cache Permissions
                try:
                    perms_df = sr.fetch_sql_data(f"select to_char(username) username,dashboardaccess,superuser,sales,finance,purchase,hr from dashboard_access where username <> 'admin' and username = '{username}'   union all select 'admin' username,'T' dashboardaccess,'T' superuser, 'T' sales,'T' finance,'T' purchase,'T' hr from dual where  'admin' = '{username}'")
                    if not perms_df.empty:
                        st.session_state.user_perms = perms_df.iloc[0].to_dict()
                except:
                    pass
                
                # Set Initial Menu if not set
                if st.session_state.main_menu is None and st.session_state.user_perms:
                    up = st.session_state.user_perms
                    if up.get('HR') == 'T': st.session_state.main_menu = "👥 HR"
                    elif up.get('SALES') == 'T': st.session_state.main_menu = "🧾 Sales"
                    elif up.get('FINANCE') == 'T': st.session_state.main_menu = "💰 Finance"
                    elif up.get('PURCHASE') == 'T': st.session_state.main_menu = "🛒 Purchase"
                    elif up.get('SUPERUSER') == 'T' or up.get('DASHBOARDACCESS') == 'T': 
                        st.session_state.main_menu = "User Access"
                
                st.rerun()
            # already logged in via bypass — continue normal flow
        else:
            # Present but invalid session id -> show error and stop further execution
            st.error("Oops! Session Out! or You are not having access to dashboard!")
            st.stop()

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
if os.environ.get("DEV_SHOW_QUERY_DEBUG", "0") == "100":
    with st.sidebar:
        st.write(active_session)
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

            def has_access(module):
                if st.session_state.user_perms is None: return False
                perms = st.session_state.user_perms
                key = module.upper().replace(" ", "")
                # Superuser always gets User Access Screen
                if key == 'DASHBOARDACCESS' and perms.get('SUPERUSER') == 'T':
                    return True
                # For modules, respect specific flags
                return perms.get(key) == 'T'

            # Menu Buttons - Only show if authorized
            if has_access('HR'):
                if st.button("👥 HR"):
                    st.session_state.main_menu = "👥 HR"

            if has_access('SALES'):
                if st.button("🧾 Sales"):
                    st.session_state.main_menu = "🧾 Sales"

            if has_access('FINANCE'):
                if st.button("💰 Finance"):
                    st.session_state.main_menu = "💰 Finance"

            if has_access('PURCHASE'):
                if st.button("🛒 Purchase"):
                    st.session_state.main_menu = "🛒 Purchase"

            if st.button("Global Parameter"):
                st.session_state.main_menu = "Global Parameter"

            if has_access('DASHBOARDACCESS'):
                if st.button("🔑 User Access"):
                    st.session_state.main_menu = "User Access"

            if session_id is None:
                if st.button("🚪 Logout"):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.role = ""
                    st.session_state.user_perms = None
                    st.session_state.main_menu = None
                    st.success("Logout Successfully")
                    st.rerun()

        # ---------------- MAIN CONTENT ----------------

        if st.session_state.main_menu == "👥 HR" and has_access('HR'):
            total_emp, in_out, visa_exp, emp_strength, dept, employee = data_load.load_data_hr()
            hr_db.hr_dashboard(total_emp, in_out, visa_exp, emp_strength, dept, employee)

        elif st.session_state.main_menu == "🛒 Purchase" and has_access('PURCHASE'):
            grn_data, lpo_data, gross_amt, net_values, Purchase = data_load.load_data_purchase()
            purchase_db.purchase_dashboard(grn_data, lpo_data, gross_amt, net_values, Purchase)

        elif st.session_state.main_menu == "🧾 Sales" and has_access('SALES'):
            sales = data_load.load_data_sales()
            sales_db.sales_dashboard(sales)
 
        elif st.session_state.main_menu == "💰 Finance" and has_access('FINANCE'):
            ledger, cash, bank, cy_py_exp, cy_py_inc, fin = data_load.load_data_finance()
            finance_db.finance_dashboard(ledger, cash, bank, cy_py_exp, cy_py_inc, fin)

        elif st.session_state.main_menu == "Global Parameter":
            GP_COMP, GP_PROJ, GP_YEAR, GP_CATEGORY = data_load.load_data_global_param()
            params.global_params(GP_COMP, GP_PROJ, GP_YEAR, GP_CATEGORY)

        elif st.session_state.main_menu == "User Access" and has_access('DASHBOARDACCESS'):
            self.user_access_screen()

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

    # -------------------------------------------------------
    # USER ACCESS MANAGEMENT SCREEN
    # -------------------------------------------------------
    def user_access_screen(self):
        def report_title_local(report_name):
            image_path = "images/Aladrak.png"
            try:
                with open(image_path, "rb") as f:
                    img_base64 = base64.b64encode(f.read()).decode()
            except FileNotFoundError:
                img_base64 = ""
                
            st.markdown(
                f"""
                <style>
                .dashboard-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    font-size: 2rem;
                    font-weight: 700;
                    color: green;
                    padding: 0.3rem 2rem;
                    border-radius: 12px;
                    background: rgb(226, 252, 231);
                    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
                    margin-bottom: 0.5rem;
                }}
                .dashboard-header img {{
                    height: 40px;
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

        report_title_local("User Access Management")
        
        # Add User Option
        with st.popover("➕ Add User"):
            st.markdown("### Add User from System")
            try:
                ax_users_df = sr.fetch_sql_data(sq.QR_AXUSERS_ONLY)
                if not ax_users_df.empty:
                    # Search Box for Add User
                    add_search = st.text_input("🔍 Search User to Add", key="add_user_search_box")
                    
                    user_list = ax_users_df['USERNAME'].tolist()
                    if add_search:
                        user_list = [u for u in user_list if add_search.lower() in u.lower()]
                    
                    if user_list:
                        user_to_add = st.selectbox("Select User to Add", options=user_list, key="select_user_to_add")
                        if st.button("Add User", type="primary"):
                            add_query = f"""
                            INSERT INTO dashboard_access (username, dashboardaccess, superuser, sales, finance, purchase, hr)
                            VALUES ('{user_to_add}', 'F', 'F', 'F', 'F', 'F', 'F')
                            """
                            try:
                                sr.run_sql_query(add_query)
                                st.success(f"User {user_to_add} added successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding user: {e}")
                    else:
                        st.warning(f"No system users match '{add_search}'")
                else:
                    st.info("All users from sys directory are already added.")
            except Exception as e:
                st.error(f"Error fetching sys users: {e}")

        # Fetch data
        try:
            df = sr.fetch_sql_data(sq.QR_DASHBOARD_ACCESS)
        except Exception as e:
            st.error(f"Error fetching access data: {e}")
            return

        if df.empty:
            st.info("No authorized users found. Use 'Add User' to add them.")
            return

        # Search Box
        search_query = st.text_input("🔍 Search Dashboard Users", placeholder="Enter username here...")
        
        if search_query:
            df = df[df['USERNAME'].str.contains(search_query, case=False, na=False)]

        if df.empty:
            st.warning(f"No dashboard users found matching '{search_query}'")
            return

        # User List and Edit logic
        for index, row in df.iterrows():
            username = row['USERNAME']
            with st.expander(f"👤 {username}"):
                cols = st.columns(6)
                
                # Helper to convert T/F to bool
                def to_bool(val):
                    return True if val == 'T' else False
                
                def from_bool(val):
                    return 'T' if val else 'F'

                dashboard_access = cols[0].checkbox("Dashboard", value=to_bool(row['DASHBOARDACCESS']), key=f"da_{username}")
                superuser = cols[1].checkbox("Superuser", value=to_bool(row['SUPERUSER']), key=f"su_{username}")
                sales = cols[2].checkbox("Sales", value=to_bool(row['SALES']), key=f"sa_{username}")
                finance = cols[3].checkbox("Finance", value=to_bool(row['FINANCE']), key=f"fi_{username}")
                purchase = cols[4].checkbox("Purchase", value=to_bool(row['PURCHASE']), key=f"pu_{username}")
                hr = cols[5].checkbox("HR", value=to_bool(row['HR']), key=f"hr_{username}")

                save_col, del_col = st.columns([1, 1])
                if save_col.button(f"Update", key=f"btn_{username}", type="primary"):
                    update_query = f"""
                    UPDATE dashboard_access 
                    SET DASHBOARDACCESS = '{from_bool(dashboard_access)}',
                        SUPERUSER = '{from_bool(superuser)}',
                        SALES = '{from_bool(sales)}',
                        FINANCE = '{from_bool(finance)}',
                        PURCHASE = '{from_bool(purchase)}',
                        HR = '{from_bool(hr)}'
                    WHERE USERNAME = '{username}'
                    """
                    try:
                        sr.run_sql_query(update_query)
                        # Update session state cache if we updated current user's perms
                        if username == st.session_state.username:
                            perms_df = sr.fetch_sql_data(f"SELECT * FROM dashboard_access WHERE username = '{username}'")
                            if not perms_df.empty:
                                st.session_state.user_perms = perms_df.iloc[0].to_dict()
                                
                        st.success(f"Updated permissions for {username}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating permissions: {e}")
                
                if del_col.button(f"Remove", key=f"del_{username}", type="secondary"):
                    delete_query = f"DELETE FROM dashboard_access WHERE USERNAME = '{username}'"
                    try:
                        sr.run_sql_query(delete_query)
                        st.warning(f"User {username} removed from dashboard access.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error removing user: {e}")

# -----------------------------------------------------------
# RUN APP
# -----------------------------------------------------------
if __name__ == "__main__":
    app = InfowayApp()
    app.run()