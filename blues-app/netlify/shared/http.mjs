// Shared helpers for the Blues Flow functions: JSON responses with CORS for the
// two places the app is served from (Netlify and GitHub Pages) plus local dev.

const ALLOWED = [/^https:\/\/blues-flow\.netlify\.app$/, /^https:\/\/daaronr\.github\.io$/, /^http:\/\/localhost:\d+$/, /^https:\/\/[a-z0-9-]+--blues-flow\.netlify\.app$/];

export function cors(req) {
  const origin = req.headers.get('origin') || '';
  const ok = ALLOWED.some((re) => re.test(origin));
  return ok
    ? {
        'access-control-allow-origin': origin,
        'access-control-allow-methods': 'GET, POST, OPTIONS',
        'access-control-allow-headers': 'content-type',
        vary: 'origin',
      }
    : {};
}

export function json(req, obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store', ...cors(req) },
  });
}

export function preflight(req) {
  return new Response(null, { status: 204, headers: cors(req) });
}

/** Body as JSON, whether sent as application/json or text/plain (sendBeacon). */
export async function body(req) {
  const text = await req.text();
  if (text.length > 8000) throw new Error('too long');
  return JSON.parse(text);
}

export const ID_RE = /^[A-Za-z0-9-]{8,64}$/;

export const clean = (v, max) => String(v ?? '').trim().slice(0, max);

export function randomKey() {
  return `${new Date().toISOString()}-${Math.random().toString(36).slice(2, 10)}`;
}
