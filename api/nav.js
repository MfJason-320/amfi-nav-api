// api/nav.js

const sqlite3 = require("sqlite3").verbose();

module.exports = (req, res) => {
  // 1) Read the query parameters
  const scheme_code = req.query.scheme_code;
  const date        = req.query.date;

  // 2) Open the same in-memory DB your update function used
  const db = new sqlite3.Database(":memory:");

  // 3) Query for that scheme + date
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
        return res.status(404).json({ error: "NAV not found" });
      }
      // 4) Return the NAV in an array (to match your Streamlit code)
      return res.json([{ date, nav: row.nav }]);
    }
  );
};
