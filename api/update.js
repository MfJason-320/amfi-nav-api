import sqlite3 from "sqlite3";
import axios from "axios";
import { promisify } from "util";

const DB_PATH = "/tmp/amfi.db";  // This works on Vercel runtime
const SCHEME_CSV_URL = "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0";
const DAILY_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method Not Allowed" });
  }

  try {
    const db = new sqlite3.Database(DB_PATH);
    const dbExec = promisify(db.exec).bind(db);
    const dbRun = promisify(db.run).bind(db);
    const dbClose = promisify(db.close).bind(db);

    // Create tables
    await dbExec(`
      CREATE TABLE IF NOT EXISTS schemes (
        scheme_code TEXT PRIMARY KEY,
        scheme_name TEXT,
        launch_date TEXT
      );
      CREATE TABLE IF NOT EXISTS navs (
        scheme_code TEXT,
        date TEXT,
        nav REAL,
        PRIMARY KEY (scheme_code, date)
      );
    `);

    // Fetch & insert scheme data
    const schemeText = (await axios.get(SCHEME_CSV_URL)).data;
    const schemeLines = schemeText.split("\n").slice(1);

    for (const line of schemeLines) {
      const parts = line.split(";");
      if (parts.length < 3) continue;
      const [code, name, launch] = parts;
      await dbRun(
        "INSERT OR IGNORE INTO schemes VALUES (?, ?, ?)",
        [code.trim(), name.trim(), launch.trim()]
      );
    }

    // Fetch & insert NAV data
    const navText = (await axios.get(DAILY_NAV_URL)).data;
    const navLines = navText.split("\n").slice(1);

    for (const line of navLines) {
      const parts = line.split(";");
      if (parts.length < 8) continue;
      const [code,,, navStr,,,, dateStr] = parts;
      await dbRun(
        "INSERT OR REPLACE INTO navs VALUES (?, ?, ?)",
        [code.trim(), dateStr.trim(), parseFloat(navStr)]
      );
    }

    await dbClose();
    return res.status(200).json({ status: "success", message: "NAV data updated." });

  } catch (err) {
    console.error("Update error:", err);
    return res.status(500).json({ error: err.message });
  }
}
