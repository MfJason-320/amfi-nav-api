# app/nav_fetcher.py

import requests
from datetime import datetime, timedelta
from app.storage import get_conn

SCHEME_CSV_URL = "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0"
DAILY_NAV_URL  = "https://www.amfiindia.com/spages/NAVAll.txt"
HIST_NAV_URL   = "http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

def fetch_and_store_schemes():
    """
    Download the raw CSV, split by lines, then by commas.
    Use fixed column positions to avoid header mismatches:
      0: Scheme Code, 1: Scheme Name, 2: Launch Date
    """
    r = requests.get(SCHEME_CSV_URL)
    r.raise_for_status()
    lines = r.text.splitlines()

    conn = get_conn()
    cur  = conn.cursor()

    # Skip the first line (header) and split each row by comma
    for line in lines[1:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue  # malformed row—skip

        code        = parts[0]
        name        = parts[1]
        launch_date = datetime.strptime(parts[2], "%d-%b-%Y").date().isoformat()

        cur.execute(
            "INSERT OR IGNORE INTO schemes (scheme_code, scheme_name, launch_date) VALUES (?, ?, ?)",
            (code, name, launch_date)
        )

    conn.commit()
    conn.close()

def fetch_daily_nav():
    r = requests.get(DAILY_NAV_URL)
    r.raise_for_status()
    lines = r.text.splitlines()

    conn = get_conn()
    cur  = conn.cursor()

    for line in lines[1:]:
        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 8:
            continue

        code     = parts[0]
        nav_str  = parts[3]
        date_str = parts[7]

        date = datetime.strptime(date_str, "%d-%b-%Y").date().isoformat()
        nav  = float(nav_str)

        cur.execute(
            "INSERT OR REPLACE INTO navs (scheme_code, date, nav) VALUES (?, ?, ?)",
            (code, date, nav)
        )

    conn.commit()
    conn.close()

def fetch_historical_nav_for_scheme(code, launch_date):
    from_date = datetime.fromisoformat(launch_date)
    today     = datetime.today()

    conn = get_conn()
    cur  = conn.cursor()

    while from_date < today:
        to_date = min(from_date + timedelta(days=5*365), today)
        params  = {
            "tp": 1,
            "frmdt": from_date.strftime("%d-%b-%Y"),
            "todt": to_date.strftime("%d-%b-%Y"),
            "SchemeCode": code
        }
        r = requests.get(HIST_NAV_URL, params=params)
        r.raise_for_status()
        rows = r.text.splitlines()[1:]  # skip header

        for row in rows:
            cols = [c.strip() for c in row.split(",")]
            if len(cols) < 2:
                continue

            date = datetime.strptime(cols[0], "%d-%b-%Y").date().isoformat()
            nav  = float(cols[1])

            cur.execute(
                "INSERT OR REPLACE INTO navs (scheme_code, date, nav) VALUES (?, ?, ?)",
                (code, date, nav)
            )

        conn.commit()
        from_date = to_date

    conn.close()

def fetch_all_historical():
    conn = get_conn()
    cur  = conn.cursor()

    for code, launch in cur.execute("SELECT scheme_code, launch_date FROM schemes"):
        fetch_historical_nav_for_scheme(code, launch)

    conn.close()
