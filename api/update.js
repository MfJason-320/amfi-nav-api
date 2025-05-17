// api/update.js
const sqlite3 = require("sqlite3").verbose();
const axios   = require("axios");

const DB_PATH        = "/tmp/amfi.db";  // Persisted across invocations on Vercel
const SCHEME_CSV_URL = "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0";
const DAILY_NAV_URL  = "https://www.amfiindia.com/spages/NAVAll.txt";

module.exports = async (req, res) => {
  try {
    const db = new sqlite3.Database(DB_PATH);

    // Initialize tables
    await new Promise((r, e) =>
      db.exec(`
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
      `, err => err ? e(err) : r())
    );

    // Fetch & store schemes
    const schemeText = (await axios.get(SCHEME_CSV_URL)).data;
    schemeText.split("\n").slice(1).forEach(line => {
      const parts = line.split(";");
      if (parts.length < 3) return;
      const [code, name, launch] = parts;
      db.run(
        "INSERT OR IGNORE INTO schemes VALUES (?, ?, ?)",
        [code.trim(), name.trim(), launch.trim()]
      );
    });

    // Fetch & store daily NAVs
    const navText = (await axios.get(DAILY_NAV_URL)).data;
    navText.split("\n").slice(1).forEach(line => {
      const parts = line.split(";");
      if (parts.length < 8) return;
      const [code,,, navStr,,,, dateStr] = parts;
      db.run(
        "INSERT OR REPLACE INTO navs VALUES (?, ?, ?)",
        [code.trim(), dateStr.trim(), parseFloat(navStr)]
      );
    });

    db.close();
    return res.json({ status: "success", message: "NAV data updated." });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
};
