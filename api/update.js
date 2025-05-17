// api/update.js
const axios = require("axios");

const SCHEME_CSV_URL = "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0";
const DAILY_NAV_URL  = "https://www.amfiindia.com/spages/NAVAll.txt";

module.exports = async (req, res) => {
  try {
    // Fetch & parse scheme data
    const schemeText = (await axios.get(SCHEME_CSV_URL)).data;
    const schemes = schemeText.split("\n").slice(1).map(line => {
      const parts = line.split(";");
      if (parts.length < 3) return null;
      return {
        scheme_code: parts[0].trim(),
        scheme_name: parts[1].trim(),
        launch_date: parts[2].trim()
      };
    }).filter(Boolean);

    // Fetch & parse NAV data
    const navText = (await axios.get(DAILY_NAV_URL)).data;
    const navs = navText.split("\n").slice(1).map(line => {
      const parts = line.split(";");
      if (parts.length < 8) return null;
      return {
        scheme_code: parts[0].trim(),
        nav: parseFloat(parts[3]),
        date: parts[7].trim()
      };
    }).filter(Boolean);

    return res.json({
      status: "success",
      message: "NAV data fetched (not saved).",
      schemes_count: schemes.length,
      navs_count: navs.length
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
};
