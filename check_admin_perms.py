import oracledb
import pandas as pd
import data.sqlreader as sr

def check_user(username):
    print(f"Checking permissions for user: {username}")
    try:
        df = sr.fetch_sql_data(f"SELECT * FROM dashboard_access WHERE username = '{username}'")
        if not df.empty:
            print(df.iloc[0].to_dict())
        else:
            print("User not found in dashboard_access.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user('admin')
