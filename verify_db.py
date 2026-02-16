import oracledb
import pandas as pd
import data.sqlqueries as sq
import data.sqlreader as sr

def test_sync():
    print("Testing Synchronization...")
    try:
        sr.run_sql_query(sq.QR_SYNC_USERS)
        print("Sync query executed successfully.")
    except Exception as e:
        print(f"Sync query failed: {e}")

def test_fetch():
    print("\nFetching Dashboard Access Data...")
    try:
        df = sr.fetch_sql_data(sq.QR_DASHBOARD_ACCESS)
        print(f"Found {len(df)} users.")
        if not df.empty:
            print(df.head())
    except Exception as e:
        print(f"Fetch failed: {e}")

if __name__ == "__main__":
    test_sync()
    test_fetch()
