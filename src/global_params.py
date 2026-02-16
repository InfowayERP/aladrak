import streamlit as st
import plotly.express as px
import pandas as pd
import io
import os
import warnings
import calendar
import base64
import numpy as np
import json
import datetime as dt
from data.sqlite_reader import get_connection, create_table

def export_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Labour Strength")
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

def global_params(GP_COMP,GP_PROJ,GP_YEAR,GP_CATEGORY):
    report_title("Global Parameter")
   
    try:
        create_table()
    except:
        pass

         
    user='admin'
    
    #st.dataframe(GP_PROJ)
    with st.popover("🏢 Choose Company"):
                
                company = sorted(GP_COMP['COMPANYNAME'].unique())
                st.write("Select Company:")

                small_col1, small_col2 = st.columns([0.3, 0.7])
                                    
                with small_col1:
                    select_all = st.button("✔ Select All", use_container_width=True)

                with small_col2:
                    clear_all = st.button("✖ Clear All", use_container_width=True)

                selected_comp = []

                # --- Loop through companies ---
                for comp in company:
                    key = f"chk_{comp}"

                    # Clear all logic
                    if clear_all:
                        st.session_state[key] = False

                    # Select all logic
                    if select_all:
                        st.session_state[key] = True

                    checked = st.checkbox(comp, key=key)
                    if checked:
                        selected_comp.append(comp)





    

    with st.popover("📂 Choose Project"):

        project = sorted(GP_PROJ["PROJECTCODE"].unique())
        selected_projects = []

        st.write("Select Project:")

        # --- Buttons ---
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

        # --- Checkboxes ---
        for proj in project:
            key = f"chk_lpo_grn_proj_tab5_{proj}"

            if clear_project:
                st.session_state[key] = False

            if select_all_project:
                st.session_state[key] = True

            if st.checkbox(proj, key=key):
                selected_projects.append(proj)



    if st.button("Save Parameters"):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO global_params (user, company, project)
            VALUES (?, ?, ?)
        """, (
            user,
            json.dumps(selected_comp),
            json.dumps(selected_projects)
        ))

        conn.commit()
        conn.close()

        st.success("Saved Successfully!")
        