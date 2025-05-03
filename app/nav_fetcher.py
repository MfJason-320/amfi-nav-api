# app/nav_fetcher.py

import requests
from datetime import datetime, timedelta
from app.storage import get_conn

SCHEME_CSV_URL = "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0"
DAILY_NAV_URL  = "https://www.amfiindia.com/spages/NAVAll.txt"
HIST_NAV_URL   = "http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

def sniff_delimiter(header_line: str) -> str:
    """Return ';' if the header line contains semicolons, else ','."""
    return ';' if ';' in header_line else ','

def fetch_and_store_schemes():
    """
    Download the AMFI schemes file, detect its delimiter,
    and parse only the first three columns (code, name, launch date).
    """
    r = requests.get(SCHEME_CSV_URL)
    r.raise_for_status()
    lines = [line for line in r.text.splitlines() if line.strip()]
    if not lines:
        return

    delimiter = sniff_delimiter(lines[0])
    conn = get_conn()
    cur  = conn.cursor()

    # Skip header, parse rows
    for row in lines[1:]:
        parts = row.split(delimiter)
        if len(parts) < 3:
            continue  # malformed row

        code        = parts[0].strip()
        name        = parts[1].strip()
        # Some CSVs put date in third field; others may have extra fields
        raw_date    = parts[2].strip()
        try:
            launch_date = datetime.strptime(raw_date, "%d-%b-%Y").date().isoformat()
        except ValueError:
            # If parsing fails, skip this row
            continue

        cur.execute(
            "INSERT OR IGNORE INTO schemes (scheme_code, scheme_name, launch_date) VALUES (?, ?, ?)",
            (code, name, launch_date)
        )

    conn.commit()
    conn.close()


def fetch_daily_nav():
    r = requests.get(DAILY_NAV_URL)
    r.raise_for_status()
    lines = [line for line in r.text.splitlines() if line.strip()]
    conn = get_conn()
    cur  = conn.cursor()

    # Semicolon‑delimited: code;name;...;nav;...;date;...
    for line in lines[1:]:
        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 8:
            continue

        code     = parts[0]
        nav_str  = parts[3]
        date_str = parts[7]
        try:
            date = datetime.strptime(date_str, "%d-%b-%Y").date().isoformat()
            nav  = float(nav_str)
        except ValueError:
            continue

        cur.execute(
            "INSERT OR REPLACE INTO navs (scheme_code, date, nav) VALUES (?, ?, ?)",
            (code, date, nav)
        )

    conn.commit()
    conn.close()


def fetch_historical_nav_for_scheme(code, launch_date):
    from_date = datetime.fromisoformat(launch_date)
    today     = datetime.today()
    conn      = get_conn()
    cur       = conn.cursor()

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

        rows = [ln for ln in r.text.splitlines() if ln.strip()][1:]
        for row in rows:
            cols = [c.strip() for c in row.split(",")]
            if len(cols) < 2:
                continue
            try:
                date = datetime.strptime(cols[0], "%d-%b-%Y").date().isoformat()
                nav  = float(cols[1])
            except ValueError:
                continue

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
