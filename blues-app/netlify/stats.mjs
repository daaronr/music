// Read Blues Flow's votes, notes and usage counts from Netlify Blobs.
//   node blues-app/netlify/stats.mjs            # summary: visits, events, votes
//   node blues-app/netlify/stats.mjs notes      # feedback and donation notes (private)
//   node blues-app/netlify/stats.mjs votes      # every vote, with comments
//   node blues-app/netlify/stats.mjs --days 7   # limit usage counts to the last 7 days
// Uses the Netlify CLI's login token and the site id saved by `netlify deploy`.
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { getStore } from '@netlify/blobs';

const here = dirname(fileURLToPath(import.meta.url));
const siteID = JSON.parse(readFileSync(join(here, '.netlify/state.json'), 'utf8')).siteId;
const cli = JSON.parse(readFileSync(join(homedir(), 'Library/Preferences/netlify/config.json'), 'utf8'));
const token = cli.users[cli.userId].auth.token;
const store = (name) => getStore({ name, siteID, token });

const args = process.argv.slice(2);
const mode = args.find((a) => !a.startsWith('--') && !/^\d+$/.test(a)) ?? 'summary';
const days = Number(args[args.indexOf('--days') + 1]) || 36500;

async function all(name, prefix) {
  const s = store(name);
  const out = [];
  let cursor;
  do {
    const page = await s.list({ cursor, prefix });
    for (const b of page.blobs) out.push({ key: b.key, ...(await s.get(b.key, { type: 'json' })) });
    cursor = page.cursor;
  } while (cursor);
  return out;
}

const count = (xs) => Object.entries(xs.reduce((m, x) => ((m[x] = (m[x] ?? 0) + 1), m), {})).sort((a, b) => b[1] - a[1]);

if (mode === 'notes') {
  for (const n of (await all('notes')).filter((n) => !n.test)) {
    console.log(`\n${n.ts}  ${n.kind.toUpperCase()}${n.where ? ` (${n.where}${n.amount ? `, ${n.amount}` : ''})` : ''}`);
    console.log(`  from: ${n.name || '(no name)'} <${n.email || 'no email'}>${n.creditOk ? '  [ok to thank publicly]' : ''}`);
    if (n.message) console.log(`  ${n.message.replace(/\n/g, '\n  ')}`);
    if (n.context) console.log(`  (was looking at: ${n.context})`);
    if (n.kind === 'suggestion') {
      console.log(`  form: "${n.formName}"  (typed in ${n.typedIn})${n.source ? `  source: ${n.source}` : ''}`);
      console.log(`  bars: | ${n.bars.join(' | ')} |`);
      console.log(`  in F: | ${n.chartBars.join(' | ')} |`);
    }
  }
} else if (mode === 'votes') {
  for (const v of (await all('votes')).filter((v) => !v.test))
    console.log(`${v.ts}  fav ${v.fav}  also [${v.also.join(', ')}]  ${v.use}  ${v.instrument}  ${v.comment ? `— ${v.comment}` : ''}`);
} else {
  const since = new Date(Date.now() - days * 864e5).toISOString().slice(0, 10);
  const hits = (await all('hits')).filter((h) => h.key.slice(0, 10) >= since);
  const views = hits.filter((h) => h.e === 'view');
  const sessions = new Set(hits.map((h) => h.s));
  console.log(`Usage ${days < 36500 ? `since ${since}` : 'all time'}: ${views.length} page views, ${sessions.size} sessions`);
  console.log('\nViews by day:');
  for (const [d, n] of count(views.map((h) => h.key.slice(0, 10))).sort()) console.log(`  ${d}  ${n}`);
  console.log('\nEvents:', count(hits.map((h) => h.e)).map(([e, n]) => `${e} ${n}`).join(', '));
  console.log('Devices:', count(views.map((h) => h.d)).map(([e, n]) => `${e} ${n}`).join(', '));
  console.log('Copies:', count(views.map((h) => h.o)).map(([e, n]) => `${e} ${n}`).join(', '));
  console.log('Referrers:', count(views.map((h) => h.r || '(direct)')).slice(0, 10).map(([e, n]) => `${e} ${n}`).join(', '));
  console.log('Forms played:', count(hits.filter((h) => h.e === 'play').map((h) => h.x)).slice(0, 10).map(([e, n]) => `${e} ${n}`).join(', '));
  const votes = (await all('votes')).filter((v) => !v.test);
  console.log(`\nVotes: ${votes.length}. Favourites:`, count(votes.map((v) => v.fav)).map(([f, n]) => `#${f} ${n}`).join(', '));
  const notes = (await all('notes')).filter((n) => !n.test);
  console.log(`Notes: ${notes.filter((n) => n.kind === 'feedback').length} feedback, ${notes.filter((n) => n.kind === 'donation').length} donations, ${notes.filter((n) => n.kind === 'suggestion').length} suggested forms (see: stats.mjs notes)`);
}
