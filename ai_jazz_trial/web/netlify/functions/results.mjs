// Aggregate results, shown only to a browser whose id has a stored vote.
// Comments are kept for David and never returned here.
import { getStore } from "@netlify/blobs";

const TUNES = ["halation", "parallax", "glass_meridian"];
const ID_RE = /^[A-Za-z0-9-]{8,64}$/;

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

export default async (req) => {
  const voter = new URL(req.url).searchParams.get("voter") || "";
  const store = getStore({ name: "votes", consistency: "strong" });
  if (!ID_RE.test(voter) || !(await store.get(voter))) {
    return json({ error: "vote first" }, 403);
  }
  const keys = [];
  let cursor;
  do {
    const page = await store.list({ cursor });
    page.blobs.forEach((b) => keys.push(b.key));
    cursor = page.cursor;
  } while (cursor);
  const votes = (await Promise.all(keys.map((k) => store.get(k, { type: "json" }))))
    .filter((v) => v && !v.test);

  const prefs = { halation: 0, parallax: 0, glass_meridian: 0, none: 0 };
  const ratings = {};
  TUNES.forEach((t) => (ratings[t] = { n: 0, sum: 0, dist: [0, 0, 0, 0, 0] }));
  const did = { listened: 0, read: 0, played: 0 };
  const instruments = {};
  for (const v of votes) {
    if (v.pref in prefs) prefs[v.pref] += 1;
    for (const t of TUNES) {
      const r = v.ratings ? v.ratings[t] : undefined;
      if (Number.isInteger(r) && r >= 1 && r <= 5) {
        ratings[t].n += 1;
        ratings[t].sum += r;
        ratings[t].dist[r - 1] += 1;
      }
    }
    (v.did || []).forEach((d) => { if (d in did) did[d] += 1; });
    const inst = (v.instrument || "").toLowerCase().trim();
    if (inst) instruments[inst] = (instruments[inst] || 0) + 1;
  }
  const out = {};
  TUNES.forEach((t) => {
    const r = ratings[t];
    out[t] = { n: r.n, mean: r.n ? Math.round((r.sum / r.n) * 100) / 100 : null, dist: r.dist };
  });
  const topInstruments = Object.entries(instruments).sort((a, b) => b[1] - a[1]).slice(0, 8);
  return json({ n: votes.length, prefs, ratings: out, did, instruments: topInstruments,
                generated: new Date().toISOString() });
};

export const config = { path: "/api/results" };
