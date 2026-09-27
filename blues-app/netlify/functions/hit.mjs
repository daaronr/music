// POST /api/hit: a minimal, cookie-free usage counter. One small record per
// event: what happened, a random per-tab session id, device class, and the
// referring site's host. No IPs, no user agents, nothing personal.
import { getStore } from '@netlify/blobs';
import { body, clean, json, preflight } from '../shared/http.mjs';

const EVENTS = ['view', 'play', 'tour', 'mix', 'vote', 'results', 'feedback', 'donation', 'donate-click', 'mp3', 'key', 'instrument', 'poster'];

export default async (req) => {
  if (req.method === 'OPTIONS') return preflight(req);
  if (req.method !== 'POST') return json(req, { error: 'POST only' }, 405);
  let b;
  try {
    b = await body(req);
  } catch {
    return json(req, { ok: false }, 400);
  }
  if (!EVENTS.includes(b.e)) return json(req, { ok: false }, 400);
  const now = new Date();
  const hit = {
    e: b.e,
    s: clean(b.s, 24),
    d: b.d === 'mobile' ? 'mobile' : 'desktop',
    o: clean(b.o, 60), // which copy of the app (host)
    r: clean(b.r, 80), // referrer host
    x: clean(b.x, 60), // event detail, e.g. form number or key
    t: now.toISOString(),
  };
  if (String(b.s || '').startsWith('test-')) return json(req, { ok: true });
  const key = `${now.toISOString().slice(0, 10)}/${now.getTime()}-${Math.random().toString(36).slice(2, 8)}`;
  await getStore('hits').setJSON(key, hit);
  return json(req, { ok: true });
};

export const config = { path: '/api/hit' };
