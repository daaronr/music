// Records one vote per browser (a random id kept in the visitor's localStorage).
// A later vote from the same id replaces the earlier one. No IPs or names are stored.
import { getStore } from "@netlify/blobs";

const TUNES = ["halation", "parallax", "glass_meridian"];
const PREFS = [...TUNES, "none"];
const DID = ["listened", "read", "played"];
const ID_RE = /^[A-Za-z0-9-]{8,64}$/;

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Send the vote as a POST." }, 405);
  let body;
  try {
    body = await req.json();
  } catch {
    return json({ error: "The vote didn't arrive as JSON." }, 400);
  }
  const voter = String(body.voter || "");
  if (!ID_RE.test(voter)) return json({ error: "Missing or malformed voter id." }, 400);
  const pref = String(body.pref || "");
  if (!PREFS.includes(pref)) return json({ error: "Pick a favourite (or 'no preference')." }, 400);

  const ratings = {};
  for (const t of TUNES) {
    const r = body.ratings ? body.ratings[t] : undefined;
    if (r === undefined || r === null || r === "") continue;
    const n = Number(r);
    if (!Number.isInteger(n) || n < 1 || n > 5) return json({ error: "Ratings run from 1 to 5." }, 400);
    ratings[t] = n;
  }
  const did = Array.isArray(body.did) ? body.did.filter((d) => DID.includes(d)) : [];
  const instrument = String(body.instrument || "").trim().slice(0, 60);
  const comment = String(body.comment || "").trim().slice(0, 1500);

  const store = getStore({ name: "votes", consistency: "strong" });
  await store.setJSON(voter, {
    pref, ratings, did, instrument, comment,
    test: voter.startsWith("test-"),
    ts: new Date().toISOString(),
  });
  return json({ ok: true });
};

export const config = { path: "/api/vote" };
