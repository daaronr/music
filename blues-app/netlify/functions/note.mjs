// POST /api/note: feedback, or a note that someone donated (so David can thank
// them and put their suggestions first). Private: nothing here is ever served back.
import { getStore } from '@netlify/blobs';
import { body, clean, json, preflight, randomKey } from '../shared/http.mjs';

const KINDS = ['feedback', 'donation', 'suggestion'];
const WHERE = ['unjournal', 'givewell', 'other', ''];

export default async (req) => {
  if (req.method === 'OPTIONS') return preflight(req);
  if (req.method !== 'POST') return json(req, { error: 'Send it as a POST.' }, 405);
  let b;
  try {
    b = await body(req);
  } catch {
    return json(req, { error: "That didn't arrive as JSON." }, 400);
  }
  if (b.website) return json(req, { ok: true }); // honeypot: bots fill every field
  const kind = KINDS.includes(b.kind) ? b.kind : null;
  if (!kind) return json(req, { error: 'Unknown note type.' }, 400);
  const message = clean(b.message, 3000);
  if (kind === 'feedback' && !message) return json(req, { error: 'The message is empty.' }, 400);
  const suggestion =
    kind === 'suggestion'
      ? {
          formName: clean(b.formName, 80),
          bars: (Array.isArray(b.bars) ? b.bars : []).slice(0, 12).map((x) => clean(x, 40)),
          chartBars: (Array.isArray(b.chartBars) ? b.chartBars : []).slice(0, 12).map((x) => clean(x, 40)),
          typedIn: clean(b.typedIn, 80),
          source: clean(b.source, 300),
        }
      : null;
  if (suggestion && (suggestion.bars.length !== 12 || suggestion.bars.some((x) => !x)))
    return json(req, { error: 'A suggested form needs all 12 bars.' }, 400);

  const note = {
    kind,
    message,
    name: clean(b.name, 100),
    email: clean(b.email, 160),
    where: WHERE.includes(b.where) ? b.where : '',
    amount: clean(b.amount, 40),
    creditOk: Boolean(b.creditOk),
    context: clean(b.context, 200),
    ...(suggestion ?? {}),
    test: String(b.voter || '').startsWith('test-'),
    ts: new Date().toISOString(),
  };
  await getStore({ name: 'notes', consistency: 'strong' }).setJSON(randomKey(), note);
  return json(req, { ok: true });
};

export const config = { path: '/api/note' };
