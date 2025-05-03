# app/nav_fetcher.py

import requests
import csv
from datetime import datetime, timedelta
from app.storage import get_conn

SCHEME_CSV_URL = "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0"
DAILY_NAV_URL   = "https://www.amfiindia.com/spages/NAVAll.txt"
HIST_NAV_URL    = "http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

def fetch_and_store_schemes():
    r = requests.get(SCHEME_CSV_URL)
    r.raise_for_status()
    lines = r.text.splitlines()
    reader = csv.DictReader(lines)

    # Normalize headers: strip whitespace & BOM
    reader.fieldnames = [h.strip().lstrip("\ufeff") for h in reader.fieldnames]

    conn = get_conn()
    cur  = conn.cursor()
    for raw_row in reader:
        # Normalize each key in the row
        row = {k.strip(): v for k, v in raw_row.items()}

        # Now safe to access by normalized key
        code   = row["Scheme Code"]
        name   = row["Scheme Name"]
        launch = datetime.strptime(
                    row["Launch Date"], "%d-%b-%Y"
                 ).date().isoformat()

        cur.execute("""
          INSERT OR IGNORE INTO schemes
            (scheme_code, scheme_name, launch_date)
          VALUES (?, ?, ?)
        """, (code, name, launch))

    conn.commit()
    conn.close()


def fetch_daily_nav():
    r = requests.get(DAILY_NAV_URL)
    r.raise_for_status()
    lines = r.text.splitlines()

    conn = get_conn()
    cur  = conn.cursor()
    for line in lines[1:]:
        parts    = line.split(";")
        code     = parts[0].strip()
        nav_str  = parts[3].strip()
        date_str = parts[7].strip()

        date = datetime.strptime(date_str, "%d-%b-%Y").date().isoformat()
        nav  = float(nav_str)

        cur.execute("""
          INSERT OR REPLACE INTO navs
            (scheme_code, date, nav)
          VALUES (?, ?, ?)
        """, (code, date, nav))

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

        # CSV: Date,NAV
        for line in r.text.splitlines()[1:]:
            parts = line.split(",")
            date  = datetime.strptime(parts[0].strip(), "%d-%b-%Y")\
                            .date().isoformat()
            nav   = float(parts[1].strip())
            cur.execute("""
              INSERT OR REPLACE INTO navs
                (scheme_code, date, nav)
              VALUES (?, ?, ?)
            """, (code, date, nav))

        conn.commit()
        from_date = to_date

    conn.close()


def fetch_all_historical():
    conn = get_conn()
    cur  = conn.cursor()
    for code, launch in cur.execute(
         "SELECT scheme_code, launch_date FROM schemes"
       ):
        fetch_historical_nav_for_scheme(code, launch)
    conn.close()
