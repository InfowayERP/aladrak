import streamlit as st
import os
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import hashlib
import random 
import smtplib
import base64
from email.mime.text import MIMEText
import data.sqlreader as sr
from datetime import datetime

# -------------------------- Utility Functions --------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

def save_users(users):
    with open("pickle_files/users.pkl", "wb") as f:
        pickle.dump(users, f)

def load_users():
    if os.path.exists("pickle_files/users.pkl"):
        with open("pickle_files/users.pkl", "rb") as f:
            users = pickle.load(f)
            if users:
                return users
    return {}

def save_dashboard_groups():
    os.makedirs("pickle_files", exist_ok=True)
    with open("pickle_files/dashboard_groups.pkl", "wb") as f:
        pickle.dump({
            "Dashboard_groups": st.session_state.Dashboard_groups
        }, f)

def load_dashboard_groups():
    if os.path.exists("pickle_files/dashboard_groups.pkl"):
        with open("pickle_files/dashboard_groups.pkl", "rb") as f:
            data = pickle.load(f)
            groups = data.get("Dashboard_groups", {})

            if isinstance(groups, set):
                groups = {g: {"Description": ""} for g in groups}
                with open("pickle_files/dashboard_groups.pkl", "wb") as fw:
                    pickle.dump({"Dashboard_groups": groups}, fw)
            return groups
    return {}

def save_dashboards():
    os.makedirs("pickle_files", exist_ok=True)
    with open("pickle_files/dashboards.pkl", "wb") as f:
        pickle.dump({
            "dashboards": st.session_state.dashboards
        }, f)

def load_dashboards():
    if os.path.exists("pickle_files/dashboards.pkl"):
        with open("pickle_files/dashboards.pkl", "rb") as f:
            data = pickle.load(f)
            return data.get("dashboards", {})
    return {}

def save_roles():
    with open("pickle_files/roles.pkl", "wb") as f:
        pickle.dump({
            "ROLES_MAP": st.session_state.ROLES_MAP
        }, f)

def load_roles():
    if os.path.exists("pickle_files/roles.pkl"):
        with open("pickle_files/roles.pkl", "rb") as f:
            data = pickle.load(f)
            return data.get("ROLES_MAP", {})
    return {}

def save_responsibilities():
    os.makedirs("pickle_files", exist_ok=True)
    with open("pickle_files/responsibilities.pkl", "wb") as f:
        pickle.dump(st.session_state.RESPONSIBILITIES, f)

def load_responsibilities():
    if os.path.exists("pickle_files/responsibilities.pkl"):
        with open("pickle_files/responsibilities.pkl", "rb") as f:
            data = pickle.load(f)
            if isinstance(data, dict):
                return data
            elif isinstance(data, (list, set)):
                return {r: [] for r in data}
    return {}

def generate_otp():
    return str(random.randint(10000,100000))

def send_email_otp(to_email, otp):
    sender_email = "omkaradireddy143@gmail.com"
    sender_password = "mmih jxwl suoj xvti"  # Use App Password for Gmail

    msg = MIMEText(f"Your OTP for password reset is: {otp}")
    msg['Subject'] = "Password Reset OTP"
    msg['From'] = sender_email
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        st.success("OTP sent to Successfully ")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def login():
    # --- Initialize Session State Variables ---
    # This is the crucial fix. It ensures these variables always exist.
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "show_otp_form" not in st.session_state:
        st.session_state.show_otp_form = False
    if "otp" not in st.session_state:
        st.session_state.otp = None
    if "reset_email" not in st.session_state:
        st.session_state.reset_email = None
    if 'USERS' not in st.session_state:
        st.session_state.USERS = load_users()

    # Dev bypass: if query param present, set logged_in and rerun
    try:
        _q = st.query_params
        if _q.get("sessionid") == ["1"]:
            st.session_state.logged_in = True
            st.session_state.username = "dev_bypass"
            st.session_state.role = "admin"
            
            # Cache Permissions
            try:
                perms_df = sr.fetch_sql_data(f"SELECT * FROM dashboard_access WHERE username = 'admin'")
                if not perms_df.empty:
                    st.session_state.user_perms = perms_df.iloc[0].to_dict()
            except:
                pass

            # Initial Menu selection
            if st.session_state.get('main_menu') is None and st.session_state.get('user_perms'):
                up = st.session_state.user_perms
                if up.get('HR') == 'T': st.session_state.main_menu = "👥 HR"
                elif up.get('SALES') == 'T': st.session_state.main_menu = "🧾 Sales"
                elif up.get('FINANCE') == 'T': st.session_state.main_menu = "💰 Finance"
                elif up.get('PURCHASE') == 'T': st.session_state.main_menu = "🛒 Purchase"
                elif up.get('SUPERUSER') == 'T' or up.get('DASHBOARDACCESS') == 'T': 
                    st.session_state.main_menu = "User Access"

            try:
                st.experimental_set_query_params()
            except Exception:
                pass
            st.rerun()
    except Exception:
        pass
    


    # Custom CSS
    st.markdown("""
        <style>
            .stApp { background: #ffffff; }
            .login-logo {
                width: 120px; height: 120px; border-radius: 50%;
                object-fit: contain; border: 3px solid #cccccc;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                margin-bottom: 25px; transition: transform 0.3s ease;
            }
            .login-logo:hover { transform: scale(1.5); }
            .login-title {
                color: #2a2a2a; font-size: 26px; font-weight: bold;
                margin-bottom: 25px;
            }
            label { color: #333333 !important; font-weight: bold; font-size: 14px; }
            div.stButton > button {
                width: 100%; background: #42a5f5; color: white;
                height: 45px; font-size: 16px; border-radius: 10px;
                border: none; box-shadow: 0 3px 6px rgba(0,0,0,0.2);
                transition: all 0.3s ease-in-out;
            }
            div.stButton > button:hover {
                background: #1e88e5; transform: translateY(-2px);
                box-shadow: 0 5px 10px rgba(0,0,0,0.3);
            }
        </style>
    """, unsafe_allow_html=True)

    # ✅ Logo
    image_path = "images/Aladrak.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/jpg;base64,{img_base64}' class='login-logo'></div>",
            unsafe_allow_html=True
        )
    else:
        st.info("Image not found. Please place 'Aladrak.png' in an 'images' folder.")
        
   

    # ---------------- LOGIN PAGE ----------------
    collog1,collog2,collog3=st.columns([5,4,5])
    collog2.markdown(
    """
    <div style="
        text-align: center;
        background-color: green;
        color: white;
        padding: 10px;
        border-radius: 10px;
        font-size: 12px;
    ">
        Al Adrak Trading and Contracting Co LLC
    </div>
    """,
    unsafe_allow_html=True
)

    if st.session_state.page == "login":
        st.session_state.USERS = load_users()


        with collog2.form("login_form"):
            username = st.text_input("Username", key="login_username_form")
            password = st.text_input("Password", type="password", key="login_password_form")
            
            # The form_submit_button handles the "Enter" key press.
            submitted = st.form_submit_button("Login")

            # Now, the login logic runs only when the form is submitted.
            if submitted:
                # We load the users here to make sure we have the latest data
                # before attempting to authenticate.
                st.session_state.USERS = load_users()
                
                if username in st.session_state.USERS:
                    user_data = st.session_state.USERS[username]
                    stored_password = user_data.get("password")
                    user_roles = user_data.get("roles", [])
                    email = user_data.get("email")
                    inactive = user_data.get("inactive", False)
                    is_admin = user_data.get("is_admin", False)

                    if inactive and not is_admin:
                        st.error("🚫 This user account is inactive. Please contact Admin.")
                    elif verify_password(stored_password, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = "admin" if is_admin else (user_roles[0] if user_roles else "user")

                        # Cache Permissions
                        try:
                            perms_df = sr.fetch_sql_data(f"SELECT * FROM dashboard_access WHERE username = '{username}'")
                            if not perms_df.empty:
                                st.session_state.user_perms = perms_df.iloc[0].to_dict()
                        except:
                            pass

                        # Initial Menu selection
                        if st.session_state.get('main_menu') is None and st.session_state.get('user_perms'):
                            up = st.session_state.user_perms
                            if up.get('HR') == 'T': st.session_state.main_menu = "👥 HR"
                            elif up.get('SALES') == 'T': st.session_state.main_menu = "🧾 Sales"
                            elif up.get('FINANCE') == 'T': st.session_state.main_menu = "💰 Finance"
                            elif up.get('PURCHASE') == 'T': st.session_state.main_menu = "🛒 Purchase"
                            elif up.get('SUPERUSER') == 'T' or up.get('DASHBOARDACCESS') == 'T':
                                st.session_state.main_menu = "User Access"

                        st.session_state.USERS[username]["last_activity"] = {
                            "status": True,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        save_users(st.session_state.USERS)
                        st.success("✅ Login Successful")
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password")
                else:
                    st.error("Invalid Username or Password")
