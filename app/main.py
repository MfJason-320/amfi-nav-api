# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from storage import init_db, get_conn
from nav_fetcher import (
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

class NAVQuery(BaseModel):
    scheme_code: str = None
    date: str = None

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
def get_nav(q: NAVQuery):
    conn = get_conn()
    sql = "SELECT date, nav FROM navs WHERE 1=1"
    params = []
    if q.scheme_code:
        sql += " AND scheme_code=?"
        params.append(q.scheme_code)
    if q.date:
        sql += " AND date=?"
        params.append(q.date)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [{"date": r[0], "nav": r[1]} for r in rows]

@app.get("/update")
def update_data():
    fetch_and_store_schemes()
    fetch_daily_nav()
    return {"status": "updated"}
