import oracledb
import pandas as pd


db_username='adk2026'
db_password='log'
db_host='172.16.1.85'
db_port=1521
db_service='orcl'

def check_table(table_name):
    try:
        with oracledb.connect(user=db_username, password=db_password, host=db_host, port=db_port, service_name=db_service) as connection:
            with connection.cursor() as cursor:
                query = f"SELECT column_name FROM all_tab_columns WHERE table_name = '{table_name.upper()}'"
                cursor.execute(query)
                columns = cursor.fetchall()
                if columns:
                    print(f"Columns for {table_name}:")
                    for col in columns:
                        print(f"  - {col[0]}")
                else:
                    print(f"Table {table_name} not found or no access.")
    except Exception as e:
        print(f"Error checking table {table_name}: {e}")

if __name__ == "__main__":
    check_table("AXUSERS")
    check_table("DASHBOARD_ACCESS")
