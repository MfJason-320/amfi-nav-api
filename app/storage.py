# app/storage.py

import sqlite3

DB_PATH = "amfi.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS schemes (
        scheme_code TEXT PRIMARY KEY,
        scheme_name TEXT,
        launch_date TEXT
      )
    """)
    cur.execute("""
      CREATE TABLE IF NOT EXISTS navs (
        scheme_code TEXT,
        date TEXT,
        nav REAL,
        PRIMARY KEY (scheme_code, date),
        FOREIGN KEY (scheme_code) REFERENCES schemes(scheme_code)
      )
    """)
    conn.commit()
    conn.close()
