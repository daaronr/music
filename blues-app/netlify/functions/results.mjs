// GET /api/results?voter=id: vote tallies, only for a browser that has voted.
// Comments and instruments are for David and never returned here.
import { getStore } from '@netlify/blobs';
import { ID_RE, json, preflight } from '../shared/http.mjs';

export default async (req) => {
  if (req.method === 'OPTIONS') return preflight(req);
  const voter = new URL(req.url).searchParams.get('voter') || '';
  const store = getStore({ name: 'votes', consistency: 'strong' });
  if (!ID_RE.test(voter) || !(await store.get(voter))) return json(req, { error: 'vote first' }, 403);

  const keys = [];
  let cursor;
  do {
    const page = await store.list({ cursor });
    page.blobs.forEach((b) => keys.push(b.key));
    cursor = page.cursor;
  } while (cursor);
  const votes = (await Promise.all(keys.map((k) => store.get(k, { type: 'json' })))).filter((v) => v && !v.test);

  const fav = Array(18).fill(0);
  const also = Array(18).fill(0);
  const use = { learn: 0, practice: 0, teach: 0, listen: 0, other: 0 };
  for (const v of votes) {
    if (v.fav >= 1 && v.fav <= 18) fav[v.fav - 1] += 1;
    for (const a of v.also || []) if (a >= 1 && a <= 18) also[a - 1] += 1;
    if (v.use in use) use[v.use] += 1;
  }
  return json(req, { n: votes.length, fav, also, use, generated: new Date().toISOString() });
};

export const config = { path: '/api/results' };
