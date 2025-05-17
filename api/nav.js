// api/nav.js
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

export default async function handler(req, res) {
  const { scheme_code, date } = req.query;
  if (!scheme_code || !date) {
    return res.status(400).json({ error: 'Missing scheme_code or date' });
  }

  const { data, error } = await supabase
    .from('navs')
    .select('nav')
    .eq('scheme_code', scheme_code)
    .eq('date', date)
    .single();

  if (error && error.code === 'PGRST116') {
    // no rows found
    return res.status(404).json({ error: `NAV not found for ${scheme_code} on ${date}` });
  } else if (error) {
    console.error(error);
    return res.status(500).json({ error: error.message });
  }

  return res.status(200).json([{ date, nav: data.nav }]);
}
