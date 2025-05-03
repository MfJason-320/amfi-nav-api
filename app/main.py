# app/main.py
from fastapi import FastAPI
from app.storage import init_db, get_conn
from app.nav_fetcher import (
    fetch_and_store_schemes,
    fetch_daily_nav,
    fetch_all_historical,
)

app = FastAPI()

@app.on_event("startup")
def startup_tasks():
    init_db()
    fetch_and_store_schemes()
    fetch_all_historical()

@app.get("/schemes")
def list_schemes():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM schemes").fetchall()
    conn.close()
    return [
        {"scheme_code": r[0], "scheme_name": r[1], "launch_date": r[2]}
        for r in rows
    ]

@app.get("/nav")
def get_nav(scheme_code: str = None, date: str = None):
    conn = get_conn()
    sql = "SELECT date, nav FROM navs WHERE 1=1"
    params = []
    if scheme_code:
        sql += " AND scheme_code=?"
        params.append(scheme_code)
    if date:
        sql += " AND date=?"
        params.append(date)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [{"date": r[0], "nav": r[1]} for r in rows]

@app.get("/update")
def update_data():
    init_db()
    fetch_and_store_schemes()
    fetch_daily_nav()
    return {"status": "updated"}
