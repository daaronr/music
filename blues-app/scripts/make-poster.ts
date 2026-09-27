// Printable map of the 18 blues forms, from the same data as the app.
//   node scripts/make-poster.ts                 # the standard set into public/posters/
//   node scripts/make-poster.ts --key Bb --for Bb --paper A3
// Page 1: every chord option for every bar, laid out 4 bars to a line.
// Page 2: the same options as a flowchart, one line per form.
// Page 3: the 18 forms as a table.
//   --roman yes   prints roman numerals only, so one sheet works in any key.
// Needs Google Chrome (prints the PDF headless).

import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { FLOW, View } from '../src/music/display.ts';
import { VARIATIONS } from '../src/music/progressions.ts';
import { TRANSPOSITIONS, type Transposition } from '../src/music/theory.ts';

const APP = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const OUT = join(APP, 'public', 'posters');
const TMP = join(APP, '.cache', 'posters');
mkdirSync(OUT, { recursive: true });
mkdirSync(TMP, { recursive: true });

type Paper = 'A4' | 'A3';
interface Variant {
  key: string;
  for: Transposition;
  paper: Paper;
  roman: boolean;
}

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const flat = (s: string) => s.replace('b', '♭');

function formList(ids: number[]) {
  if (ids.length === 18) return 'all';
  const parts: string[] = [];
  for (let i = 0; i < ids.length; i++) {
    let j = i;
    while (j + 1 < ids.length && ids[j + 1] === ids[j] + 1) j++;
    parts.push(j > i + 1 ? `${ids[i]}–${ids[j]}` : j === i + 1 ? `${ids[i]} ${ids[j]}` : `${ids[i]}`);
    i = j;
  }
  return parts.join(' ');
}

const PHRASES = [
  ['Bars 1–4', 'I, or something standing in for it'],
  ['Bars 5–8', 'IV, then back toward I'],
  ['Bars 9–12', 'V (or a ii–V), home to I'],
];

function html(v: Variant): string {
  const view = new View({ key: v.key, transposition: v.for, notation: 'chart', romanOnly: v.roman });
  const written = flat(view.dk.name);
  const forLine = v.roman
    ? 'Any key: I is the key chord'
    : v.for === 'C'
      ? `Key of ${flat(v.key)}, concert pitch`
      : `Concert ${flat(v.key)}, written for ${TRANSPOSITIONS[v.for].label} (key of ${written})`;
  const chords = (bar: string) =>
    view
      .bar(bar)
      .map((c) => `<span class="q-${c.quality}">${esc(c.symbol)}</span>`)
      .join('<span class="sep"> </span>');
  const romans = (bar: string) => view.bar(bar).map((c) => esc(c.roman)).join('  ');

  const cell = (i: number) => `
    <div class="cell">
      <div class="barnum">${i + 1}</div>
      ${FLOW[i]
        .map(
          (o, j) => `
        <div class="opt${j === 0 ? ' first' : ''}">
          <div class="sym">${chords(o.bar)}</div>
          <div class="meta">${v.roman ? '' : `<span class="rn">${romans(o.bar)}</span>`}<span class="forms">${formList(o.variations)}</span></div>
        </div>`,
        )
        .join('')}
    </div>`;

  const map = PHRASES.map(
    ([label, gist], row) => `
    <div class="phrase">
      <div class="plabel"><b>${label}</b><span>${gist}</span></div>
      ${[0, 1, 2, 3].map((k) => cell(row * 4 + k)).join('')}
    </div>`,
  ).join('');

  const flow = flowSvg(chords);

  const table = VARIATIONS.map(
    (f, r) => `
    <tr>
      <th><span class="n">${f.id}</span> ${esc(f.name)}</th>
      ${f.bars
        .map((b, i) => `<td class="${r > 0 && VARIATIONS[r - 1].bars[i] !== b ? 'chg' : ''}">${chords(b)}</td>`)
        .join('')}
    </tr>`,
  ).join('');

  const scale = v.paper === 'A3' ? 1 : 0.72;
  return `<!doctype html><html><head><meta charset="utf-8"><title>Blues map</title><style>
@page { size: ${v.paper} landscape; margin: 0; }
:root { font-size: ${scale * 16}px; --dom7:#8a4d00; --min7:#1f4fb8; --maj7:#0f6b3f; --dim7:#6d2fae; --sus:#07686b; --maj:#111; --line:#cfc9bb; --faint:#6b6f78; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #111; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: ${v.paper === 'A3' ? 420 : 297}mm; height: ${v.paper === 'A3' ? 297 : 210}mm; padding: ${scale * 10}mm ${scale * 11}mm; display: flex; flex-direction: column; page-break-after: always; overflow: hidden; }
header { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 0.14rem solid #111; padding-bottom: 0.35rem; margin-bottom: 0.6rem; }
h1 { font-size: 1.7rem; letter-spacing: -0.01em; }
h1 small { font-weight: 400; font-size: 1rem; color: var(--faint); margin-left: 0.6rem; }
.key { font-size: 1.15rem; font-weight: 700; }
.q-dom7 { color: var(--dom7); } .q-min7 { color: var(--min7); } .q-maj7 { color: var(--maj7); } .q-dim7 { color: var(--dim7); } .q-sus { color: var(--sus); } .q-maj { color: var(--maj); }
.map { flex: 1; display: grid; grid-template-rows: 7fr 8fr 8fr; gap: 0.4rem; min-height: 0; }
.phrase { display: grid; grid-template-columns: 5.2rem repeat(4, 1fr); gap: 0.35rem; }
.plabel { display: flex; flex-direction: column; gap: 0.2rem; font-size: 0.72rem; color: var(--faint); padding-top: 0.2rem; }
.plabel b { color: #111; font-size: 0.85rem; }
.cell { border: 0.06rem solid var(--line); border-radius: 0.3rem; padding: 0.25rem 0.45rem 0.2rem; position: relative; display: flex; flex-direction: column; }
.phrase .cell:nth-child(2) { border-left: 0.2rem solid #111; }
.barnum { position: absolute; top: 0.15rem; right: 0.4rem; font-size: 0.7rem; color: var(--faint); font-weight: 700; }
.opt { display: flex; align-items: baseline; justify-content: space-between; gap: 0.4rem; padding: 0.13rem 0; border-top: 0.05rem dotted var(--line); }
.opt.first { border-top: 0; }
.opt .sym { font-weight: 700; font-size: 1.16rem; white-space: nowrap; }
.opt.first .sym { font-size: 1.5rem; }
.sep { display: inline-block; width: 0.45rem; }
.meta { display: flex; flex-direction: column; align-items: flex-end; line-height: 1.1; }
.rn { font-size: 0.68rem; color: #333; white-space: nowrap; }
.forms { font-size: 0.6rem; color: var(--faint); white-space: nowrap; }
footer { display: flex; justify-content: space-between; gap: 1rem; margin-top: 0.5rem; font-size: 0.66rem; color: var(--faint); }
.legend span { margin-right: 0.8rem; font-weight: 700; }
table { border-collapse: collapse; width: 100%; font-size: 1.12rem; flex: 1; }
th, td { border-bottom: 0.05rem solid var(--line); padding: 0.18rem 0.35rem; text-align: left; white-space: nowrap; font-weight: 400; }
thead th { font-size: 0.66rem; color: var(--faint); }
tbody th { font-size: 0.8rem; font-weight: 700; }
tbody th .n { color: var(--faint); display: inline-block; width: 1.1rem; }
td.chg { font-weight: 800; background: #f3efe4; }
.flow { flex: 1; display: flex; align-items: center; }
.flow svg { width: 100%; height: auto; max-height: 100%; }
.flow text { font-family: inherit; }
td:nth-child(6), td:nth-child(10) { border-left: 0.12rem solid #111; }
thead th:nth-child(6), thead th:nth-child(10) { border-left: 0.12rem solid #111; }
</style></head><body>
<section class="page">
  <header><h1>The 12-bar blues map<small>every chord option in 18 forms, simplest first</small></h1><div class="key">${esc(forLine)}</div></header>
  <div class="map">${map}</div>
  <footer>
    <div class="legend"><span class="q-dom7">7 dominant</span><span class="q-min7">− minor 7</span><span class="q-maj7">Δ major 7</span><span class="q-dim7">° diminished</span><span class="q-sus">−/ sus (minor 7 over the 4th)</span> Grey numbers: which of the 18 forms use that chord. Two chords in a bar get two beats each.</div>
    <div>David Reinstein · blues-flow.netlify.app</div>
  </footer>
</section>
<section class="page">
  <header><h1>The blues flowchart<small>each line is one of the 18 forms; thicker lines are shared by more forms</small></h1><div class="key">${esc(forLine)}</div></header>
  <div class="flow">${flow}</div>
  <footer>
    <div class="legend"><span class="q-dom7">7 dominant</span><span class="q-min7">− minor 7</span><span class="q-maj7">Δ major 7</span><span class="q-dim7">° diminished</span><span class="q-sus">sus</span> Simplest option at the top of each bar. The basic blues runs along the top row. Grey numbers: forms that use the chord.</div>
    <div>David Reinstein · blues-flow.netlify.app</div>
  </footer>
</section>
<section class="page">
  <header><h1>The 18 forms<small>bold: changed from the row above</small></h1><div class="key">${esc(forLine)}</div></header>
  <table><thead><tr><th>Form</th>${Array.from({ length: 12 }, (_, i) => `<th>${i + 1}</th>`).join('')}</tr></thead><tbody>${table}</tbody></table>
  <footer><div>From a printed chart of 18 blues progressions in F. Play them, hear them and mix bars at blues-flow.netlify.app</div><div>David Reinstein</div></footer>
</section>
</body></html>`;
}

// ---------------------------------------------------------------- flowchart page

function flowSvg(chords: (bar: string) => string): string {
  const COL = 158, W = 118, H = 58, GAP = 58, TOP = 34, PAD = 4;
  const rows = Math.max(...FLOW.map((c) => c.length));
  const width = PAD * 2 + 11 * COL + W;
  const height = TOP + rows * (H + GAP);
  const x = (bar: number) => PAD + bar * COL;
  const y = (row: number) => TOP + row * (H + GAP);
  const rowOf = (bar: number, text: string) => FLOW[bar].findIndex((o) => o.bar === text);
  const edges = new Map<string, { i: number; a: number; b: number; n: number; basic: boolean }>();
  for (const f of VARIATIONS)
    for (let i = 0; i < 11; i++) {
      const a = rowOf(i, f.bars[i]);
      const b = rowOf(i + 1, f.bars[i + 1]);
      const k = `${i}:${a}:${b}`;
      const e = edges.get(k) ?? { i, a, b, n: 0, basic: false };
      e.n += 1;
      if (f.id === 1) e.basic = true;
      edges.set(k, e);
    }
  const paths = [...edges.values()]
    .map(({ i, a, b, n, basic }) => {
      const x1 = x(i) + W, x2 = x(i + 1), y1 = y(a) + H / 2, y2 = y(b) + H / 2, c = (x2 - x1) * 0.55;
      return `<path d="M${x1},${y1} C${x1 + c},${y1} ${x2 - c},${y2} ${x2},${y2}" fill="none" stroke="${basic ? '#555' : '#b9b2a2'}" stroke-width="${1 + n * 0.7}" stroke-linecap="round"/>`;
    })
    .join('');
  // Chord text arrives as HTML spans; convert them to SVG tspans.
  const label = (bar: string) =>
    chords(bar)
      .replace(/<span class="sep"> <\/span>/g, '<tspan> </tspan>')
      .replace(/<span class="q-(\w+)">/g, (_, q) => `<tspan class="q-${q}" fill="var(--${q})">`)
      .replace(/<\/span>/g, '</tspan>');
  const heads = FLOW.map((_, i) => `<text x="${x(i) + W / 2}" y="20" text-anchor="middle" font-size="18" font-weight="700" fill="#6b6f78">${i + 1}</text>`).join('');
  const phraseBreaks = [4, 8].map((i) => `<line x1="${x(i) - (COL - W) / 2}" x2="${x(i) - (COL - W) / 2}" y1="4" y2="${height}" stroke="#111" stroke-width="1.6"/>`).join('');
  const nodes = FLOW.map((col, i) =>
    col
      .map(
        (o, j) => `<g transform="translate(${x(i)},${y(j)})">
      <rect width="${W}" height="${H}" rx="6" fill="#fff" stroke="${j === 0 ? '#555' : '#cfc9bb'}" stroke-width="${j === 0 ? 1.4 : 1}"/>
      <text x="${W / 2}" y="27" text-anchor="middle" font-size="${o.bar.includes(' ') ? 18 : 23}" font-weight="700">${label(o.bar)}</text>
      <text x="${W / 2}" y="${H - 9}" text-anchor="middle" font-size="12" fill="#6b6f78">${formList(o.variations)}</text>
    </g>`,
      )
      .join(''),
  ).join('');
  return `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">${heads}${phraseBreaks}${paths}${nodes}</svg>`;
}

function render(v: Variant) {
  const name = v.roman ? `blues-map_roman-numerals_${v.paper}` : `blues-map_${v.key}${v.for === 'C' ? '_concert' : `_for-${v.for}-instruments`}_${v.paper}`;
  const htmlFile = join(TMP, `${name}.html`);
  writeFileSync(htmlFile, html(v));
  const pdf = join(OUT, `${name}.pdf`);
  rmSync(pdf, { force: true });
  // A throwaway profile with no extensions; headless Chrome sometimes lingers after writing, hence the timeout.
  try {
    execFileSync(
      CHROME,
      ['--headless=new', '--disable-gpu', '--disable-extensions', '--no-first-run', `--user-data-dir=${join(TMP, 'chrome-profile')}`,
        '--no-pdf-header-footer', `--print-to-pdf=${pdf}`, `file://${htmlFile}`],
      { stdio: 'ignore', timeout: 45000, killSignal: 'SIGKILL' },
    );
  } catch (err) {
    if (!existsSync(pdf)) throw err;
  }
  console.log(pdf);
}

const args = new Map<string, string>();
for (let i = 2; i < process.argv.length; i += 2) args.set(process.argv[i].replace(/^--/, ''), process.argv[i + 1]);
if (args.size) {
  render({
    key: args.get('key') ?? 'F',
    for: (args.get('for') ?? 'C') as Transposition,
    paper: (args.get('paper') ?? 'A4') as Paper,
    roman: args.get('roman') === 'yes',
  });
} else {
  for (const paper of ['A4', 'A3'] as Paper[]) render({ key: 'F', for: 'C', paper, roman: true });
  for (const key of ['F', 'Bb']) for (const t of ['C', 'Bb'] as Transposition[]) render({ key, for: t, paper: 'A4', roman: false });
  render({ key: 'F', for: 'C', paper: 'A3', roman: false });
}
