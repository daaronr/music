// Talks to the Netlify functions (netlify/functions/). The app is served from
// Netlify and from GitHub Pages; both use the Netlify endpoints.
// In development every id starts with "test-", which the functions keep out
// of results and usage counts.

const NETLIFY = 'https://blues-flow.netlify.app';
const API = location.hostname.endsWith('blues-flow.netlify.app') ? '' : NETLIFY;
const PREFIX = import.meta.env.DEV ? 'test-' : '';

function randomId(n = 16) {
  const a = new Uint8Array(n);
  crypto.getRandomValues(a);
  return Array.from(a, (b) => (b % 36).toString(36)).join('');
}

function stored(storage: Storage | undefined, key: string, make: () => string): string {
  try {
    const have = storage?.getItem(key);
    if (have) return have;
    const v = make();
    storage?.setItem(key, v);
    return v;
  } catch {
    return make();
  }
}

const safe = <T,>(f: () => T): T | undefined => {
  try {
    return f();
  } catch {
    return undefined;
  }
};

/** Kept in this browser so a later vote replaces an earlier one. */
export const voterId = stored(safe(() => localStorage), 'bf-voter', () => PREFIX + randomId());
/** Per-tab, for counting sessions. Not stored across visits. */
const sessionId = stored(safe(() => sessionStorage), 'bf-session', () => PREFIX + randomId(10));

const device = matchMedia('(pointer: coarse)').matches || innerWidth < 700 ? 'mobile' : 'desktop';
const referrer = safe(() => (document.referrer ? new URL(document.referrer).host : '')) ?? '';
const optedOut = navigator.doNotTrack === '1' || (navigator as Navigator & { globalPrivacyControl?: boolean }).globalPrivacyControl;

export type TrackEvent =
  | 'view' | 'play' | 'tour' | 'mix' | 'vote' | 'results' | 'feedback' | 'donation' | 'donate-click' | 'mp3' | 'key' | 'instrument' | 'poster' | 'suggestion' | 'suggest-try';

/** Count a use of the app. Fire and forget; never blocks or throws. */
export function track(e: TrackEvent, detail = '') {
  if (optedOut) return;
  const payload = JSON.stringify({ e, s: sessionId, d: device, o: location.host, r: referrer === location.host ? '' : referrer, x: detail });
  try {
    if (navigator.sendBeacon?.(`${API}/api/hit`, payload)) return;
    void fetch(`${API}/api/hit`, { method: 'POST', body: payload, keepalive: true, mode: 'no-cors' });
  } catch {
    /* counting is optional */
  }
}

async function post(path: string, data: object) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(data),
  });
  const out = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(out.error || `Error ${res.status}`);
  return out;
}

export interface VoteInput {
  fav: number;
  also: number[];
  use: string;
  instrument: string;
  comment: string;
}

export interface Results {
  n: number;
  fav: number[];
  also: number[];
  use: Record<string, number>;
}

export const sendVote = (v: VoteInput) => post('/api/vote', { voter: voterId, ...v });

export async function getResults(): Promise<Results> {
  const res = await fetch(`${API}/api/results?voter=${encodeURIComponent(voterId)}`);
  if (!res.ok) throw new Error('No results yet');
  return res.json();
}

export interface NoteInput {
  kind: 'feedback' | 'donation' | 'suggestion';
  message: string;
  name: string;
  email: string;
  where?: string;
  amount?: string;
  creditOk?: boolean;
  context?: string;
  website?: string; // honeypot
  // suggestions only
  formName?: string;
  bars?: string[];
  chartBars?: string[];
  typedIn?: string;
  source?: string;
}

export const sendNote = (n: NoteInput) => post('/api/note', { voter: voterId, ...n });

export const LINKS = {
  youtube: 'https://www.youtube.com/@daaronr',
  playlist: 'https://www.youtube.com/playlist?list=PLwCHmz77VrK1TvvBeyKYlk52rQ6PeHJzk',
  kHouse: 'https://kay-house.netlify.app/',
  unjournalDonate: 'https://info.unjournal.org/donate.html',
  unjournal: 'https://unjournal.org',
  givewellDonate: 'https://www.givewell.org/donate',
  email: 'daaronr@gmail.com',
};
