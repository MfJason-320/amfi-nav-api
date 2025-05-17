// api/update.js
const Database = require("better-sqlite3");
const axios = require("axios");

const DB_PATH = "/tmp/amfi.db"; // Vercel temp dir
const SCHEME_CSV_URL = "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0";
const DAILY_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt";

module.exports = async (req, res) => {
  try {
    const db = new Database(DB_PATH);

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
    `);

    // Fetch and insert schemes
    const schemeText = (await axios.get(SCHEME_CSV_URL)).data;
    const insertScheme = db.prepare("INSERT OR IGNORE INTO schemes VALUES (?, ?, ?)");

    schemeText.split("\n").slice(1).forEach(line => {
      const parts = line.split(";");
      if (parts.length < 3) return;
      insertScheme.run(parts[0].trim(), parts[1].trim(), parts[2].trim());
    });

    // Fetch and insert NAVs
    const navText = (await axios.get(DAILY_NAV_URL)).data;
    const insertNAV = db.prepare("INSERT OR REPLACE INTO navs VALUES (?, ?, ?)");

    navText.split("\n").slice(1).forEach(line => {
      const parts = line.split(";");
      if (parts.length < 8) return;
      insertNAV.run(parts[0].trim(), parts[7].trim(), parseFloat(parts[3]));
    });

    db.close();
    return res.status(200).json({ status: "success", message: "NAV data updated." });

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
};
