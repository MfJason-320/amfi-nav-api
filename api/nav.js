// api/nav.js
const sqlite3 = require("sqlite3").verbose();
const DB_PATH = "/tmp/amfi.db";

module.exports = (req, res) => {
  const scheme_code = req.query.scheme_code;
  const date        = req.query.date;
  if (!scheme_code || !date) {
    return res.status(400).json({ error: "Missing scheme_code or date" });
  }

  const db = new sqlite3.Database(DB_PATH);
  db.get(
    "SELECT nav FROM navs WHERE scheme_code = ? AND date = ?",
    [scheme_code, date],
    (err, row) => {
      db.close();
      if (err) {
        console.error(err);
        return res.status(500).json({ error: "Database error" });
      }
      if (!row) {
        return res.status(404).json({ error: `NAV not found for ${scheme_code} on ${date}` });
      }
      return res.json([{ date, nav: row.nav }]);
    }
  );
};
