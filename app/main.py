# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from app.storage import init_db, get_conn
from app.nav_fetcher import (
    fetch_and_store_schemes,
    fetch_daily_nav,
    fetch_all_historical,
)

@asynccontextmanager
async def lifespan(lifespan_app: FastAPI):
    """
    Lifespan handler that:
    - Records a timezone-aware startup timestamp
    - Initializes the DB and loads all NAV data
    """
    # Record startup time with explicit UTC tzinfo
    lifespan_app.state.startup_time = datetime.now(timezone.utc)

    # Startup tasks
    init_db()
    fetch_and_store_schemes()
    fetch_all_historical()

    yield  # Application is now running

    # (Optional) Shutdown tasks could go here

app = FastAPI(lifespan=lifespan)

@app.get("/schemes")
def list_schemes():
    conn = get_conn()
    rows = conn.execute(
        "SELECT scheme_code, scheme_name, launch_date FROM schemes"
    ).fetchall()
    conn.close()
    return [
        {"scheme_code": c, "scheme_name": n, "launch_date": d}
        for c, n, d in rows
    ]

@app.get("/nav")
def get_nav(scheme_code: str = None, date: str = None):
    conn = get_conn()
    sql, params = "SELECT date, nav FROM navs WHERE 1=1", []
    if scheme_code:
        sql += " AND scheme_code=?"
        params.append(scheme_code)
    if date:
        sql += " AND date=?"
        params.append(date)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [{"date": dt, "nav": v} for dt, v in rows]

@app.get("/update")
def update_data():
    init_db()
    fetch_and_store_schemes()
    fetch_daily_nav()
    return {"status": "updated"}
