// POST /api/vote: one vote per browser (a random id kept in the visitor's
// localStorage); a later vote from the same id replaces the earlier one.
// Stores no names or IPs. Ids starting "test-" are kept out of the results.
import { getStore } from '@netlify/blobs';
import { ID_RE, body, clean, json, preflight } from '../shared/http.mjs';

const USES = ['learn', 'practice', 'teach', 'listen', 'other'];

export default async (req) => {
  if (req.method === 'OPTIONS') return preflight(req);
  if (req.method !== 'POST') return json(req, { error: 'Send the vote as a POST.' }, 405);
  let b;
  try {
    b = await body(req);
  } catch {
    return json(req, { error: "The vote didn't arrive as JSON." }, 400);
  }
  const voter = String(b.voter || '');
  if (!ID_RE.test(voter)) return json(req, { error: 'Missing or malformed voter id.' }, 400);
  const fav = Number(b.fav);
  if (!Number.isInteger(fav) || fav < 1 || fav > 18) return json(req, { error: 'Pick a favourite form, 1 to 18.' }, 400);
  const also = [...new Set((Array.isArray(b.also) ? b.also : []).map(Number))]
    .filter((n) => Number.isInteger(n) && n >= 1 && n <= 18 && n !== fav)
    .slice(0, 3);
  const use = USES.includes(b.use) ? b.use : '';

  await getStore({ name: 'votes', consistency: 'strong' }).setJSON(voter, {
    fav,
    also,
    use,
    instrument: clean(b.instrument, 60),
    comment: clean(b.comment, 1500),
    test: voter.startsWith('test-'),
    ts: new Date().toISOString(),
  });
  return json(req, { ok: true });
};

export const config = { path: '/api/vote' };
