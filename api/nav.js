// api/nav.js

const sqlite3 = require("sqlite3").verbose();

module.exports = (req, res) => {
  // 1. Read query parameters
  const scheme_code = req.query.scheme_code;
  const date        = req.query.date;

  if (!scheme_code || !date) {
    return res
      .status(400)
      .json({ error: "Missing required query parameters: scheme_code and date" });
  }

  // 2. Open the same in-memory DB used by api/update.js
  const db = new sqlite3.Database(":memory:");

  // 3. Query for the NAV on that date
  db.get(
    "SELECT nav FROM navs WHERE scheme_code = ? AND date = ?",
    [scheme_code, date],
    (err, row) => {
      // Always close the DB
      db.close();

      // 4a. Database error?
      if (err) {
        console.error("DB error fetching NAV:", err);
        return res.status(500).json({ error: "Database error" });
      }

      // 4b. NAV not found for that date?
      if (!row) {
        return res
          .status(404)
          .json({ error: `NAV not found for scheme ${scheme_code} on ${date}` });
      }

      // 4c. Success: return an array with one entry (matches your client’s expectations)
      return res.status(200).json([{ date, nav: row.nav }]);
    }
  );
};
