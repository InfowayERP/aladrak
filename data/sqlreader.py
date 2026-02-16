import oracledb
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


db_username='adk2026'
db_password='log'
db_host='172.16.1.85'
db_port=1521
db_service='orcl'

def fetch_sql_data(query_string):
    with oracledb.connect(user=db_username, password=db_password, host=db_host, port=db_port, service_name=db_service) as connection:
        with connection.cursor() as cursor:
           return pd.read_sql(query_string,connection)


def run_sql_query(query_string):
    with oracledb.connect(user=db_username, password=db_password, host=db_host, port=db_port, service_name=db_service) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query_string)
            connection.commit()
