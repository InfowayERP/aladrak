import sqlite3

def get_connection():
    return sqlite3.connect("global_params.db")

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS global_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            company TEXT,
            year TEXT,
            month TEXT,
            project TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_params():
    conn = get_connection()
    c = conn.cursor()
    c.execute(" SELECT COMPANY,PROJECT FROM global_params ORDER BY id DESC LIMIT 1")
    rows = c.fetchall()
    conn.close()
    return rows