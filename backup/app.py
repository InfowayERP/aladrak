import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import calendar
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Purchase Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    grn_data = pd.read_csv(os.path.join("data", "grn_data.csv"))
    lpo_data = pd.read_csv(os.path.join("data", "lpo_data.csv"))
    lpo_grn_gross_amount = pd.read_csv(os.path.join("data", "lpo_grn_gross_amount.csv"))
    lpo_grn_net_values = pd.read_csv(os.path.join("data", "lpo_grn_net_values.csv"))
    return grn_data, lpo_data, lpo_grn_gross_amount, lpo_grn_net_values


grn_data, lpo_data, lpo_grn_gross_amount, lpo_grn_net_values = load_data()

grn_data['Year']=grn_data['Year'].astype('str')
lpo_data['Year']=lpo_data['Year'].astype('str')
total_lpo = lpo_data["Amount"].sum()
total_grn = grn_data["Amount"].sum()
difference = total_lpo - total_grn



st.header('LPO Dashboard', divider="red")


col1,col2=st.columns([0.5,2])
selected_year_lpo=col1.multiselect('Choose the Year',sorted(lpo_data['Year'].unique()))
if not selected_year_lpo:
        lpo_data=lpo_data.copy()
else:
        lpo_data=lpo_data[lpo_data['Year'].isin(selected_year_lpo)]

selected_mon_lpo=col1.multiselect('Choose the Month',sorted(lpo_data['Month'].unique()))
if not selected_mon_lpo:
        lpo_data=lpo_data.copy()
else:
        lpo_data=lpo_data[lpo_data['Month'].isin(selected_mon_lpo)]

total_lpo = lpo_data["Amount"].sum()
col1.metric("lpo Amount", f"{total_lpo:,.0f}")

lpo_pur_year = lpo_data.groupby('Year')['Amount'].sum().reset_index()
lpo_pur_year['Year']=lpo_pur_year['Year'].astype(int).astype(str)
lpo_pur_year['Amount'] = (lpo_pur_year['Amount'] / 1_000_000).round(1)


fig_bar = px.bar(lpo_pur_year, 
                x='Year', 
                y='Amount',
                text_auto=True)
# Show all year labels
fig_bar.update_xaxes(
    tickmode='array', 
    tickvals=lpo_pur_year['Year'], 
    ticktext=lpo_pur_year['Year']
)
fig_bar.update_yaxes(tickformat=",")

col2.subheader("LPO Yearly Summary", divider="blue")
col2.plotly_chart(fig_bar, use_container_width=True)


lpo_pur_year_month = lpo_data.groupby(['Year', 'Month'])['Amount'].sum().reset_index()

# Convert numeric months to names
if lpo_pur_year_month['Month'].dtype != object:
    lpo_pur_year_month['Month'] = lpo_pur_year_month['Month'].apply(lambda x: calendar.month_abbr[int(x)])

# Combine for display
lpo_pur_year_month['YearMonth'] = lpo_pur_year_month['Year'].astype(str) + "-" + lpo_pur_year_month['Month']

lpo_pur_year_month['Amount'] = (lpo_pur_year_month['Amount'] / 1_000_000).round(1)
# Sort
#lpo_pur_year_month = lpo_pur_year_month.sort_values(by='Amount', ascending=False)

# Create bar chart
fig_bar2 = px.bar(
    lpo_pur_year_month, 
    x='YearMonth', 
    y='Amount',
    text_auto=True
)
fig_bar2.update_yaxes(tickformat=",") 

col2.subheader("LPO Monthly Summary", divider="blue")
col2.plotly_chart(fig_bar2, use_container_width=True)

st.header('GRN Dashboard', divider="red")
# KPIs

col3,col4=st.columns([0.5,2])
selected_year_grn=col3.multiselect('Choose the Year',sorted(grn_data['Year'].unique()),key="grn_year_selector")
if not selected_year_grn:
        grn_data=grn_data.copy()
else:
        grn_data=grn_data[grn_data['Year'].isin(selected_year_grn)]

selected_mon_grn=col3.multiselect('Choose the Month',sorted(grn_data['Month'].unique()),key="grn_month_selector")
if not selected_mon_grn:
        grn_data=grn_data.copy()
else:
        grn_data=grn_data[grn_data['Month'].isin(selected_mon_grn)]

total_grn = grn_data["Amount"].sum()

col3.metric("GRN Amount", f"{total_grn:,.0f}")

grn_pur_year = grn_data.groupby('Year')['Amount'].sum().reset_index()
if grn_pur_year['Year'].dtype != object:
    grn_pur_year['Year'] = grn_pur_year['Year'].apply(lambda x: str(int(x)))

# Sort the DataFrame in descending order based on TOTALAMOUNT
grn_pur_year = grn_pur_year.sort_values(by='Amount', ascending=False)
grn_pur_year['Year'] = grn_pur_year['Year'].astype(int).astype(str)
grn_pur_year['Amount'] = (grn_pur_year['Amount'] / 1_000_000).round(1)

# Create the bar chart using Plotly
fig_bar = px.bar(grn_pur_year, 
                x='Year', 
                y='Amount',
                text_auto=True)
# Show all year labels
fig_bar.update_xaxes(
    tickmode='array', 
    tickvals=grn_pur_year['Year'], 
    ticktext=grn_pur_year['Year']
)
fig_bar.update_yaxes(tickformat=",")


col4.subheader("GRN Yearly Summary", divider="blue")
col4.plotly_chart(fig_bar, use_container_width=True)


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
    text_auto=True
)
fig_bar2.update_yaxes(tickformat=",") 

col4.subheader("GRN Monthly Summary", divider="blue")
col4.plotly_chart(fig_bar2, use_container_width=True)