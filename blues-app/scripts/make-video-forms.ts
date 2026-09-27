// YouTube video: all 18 forms in sequence, one chorus each, with a title card
// and an on-screen lead sheet whose current bar and beat light up.
//   node scripts/render-tour.ts --out .cache/video1/music.wav --timeline .cache/video1/timeline.json   (narrated; or --voice none --gap 3.5 for music only)
//   node scripts/make-video-forms.ts            # -> .cache/video1/blues-18-forms.mp4 + description
// Needs rsvg-convert and ffmpeg.

import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { cpus } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { View, splitRefs } from '../src/music/display.ts';
import { VARIATIONS } from '../src/music/progressions.ts';

const APP = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DIR = join(APP, '.cache', 'video1');
const FRAMES = join(DIR, 'frames');
mkdirSync(FRAMES, { recursive: true });

interface Timeline {
  tempo: number;
  key: string;
  spb: number;
  total: number;
  forms: Array<{ id: number; title: number; countIn: number; end: number }>;
  chapters: Array<{ title: string; start: number }>;
}
const tl: Timeline = JSON.parse(readFileSync(join(DIR, 'timeline.json'), 'utf8'));
const view = new View({ key: tl.key, transposition: 'C', notation: 'chart' });

const W = 1920;
const H = 1080;
const C = {
  bg: '#121419', surface: '#1b1e26', line: '#2f3441', text: '#eceef3', muted: '#a3aabb', faint: '#737b8d',
  accent: '#ff7a59', accentSoft: 'rgba(255,122,89,0.16)', changed: '#f06ba8',
  dom7: '#f2b35b', min7: '#92b2ff', maj7: '#6fd6a2', dim7: '#d39dff', maj: '#eceef3', sus: '#5bd3d3',
} as const;
const FONT = `font-family="Helvetica Neue, Helvetica, Arial, sans-serif"`;
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const keyName = tl.key.replace('b', '♭');

// ---------------------------------------------------------------- text with {{chord}} refs, wrapped

type Run = { text: string; color?: string; bold?: boolean };

function runs(text: string): Run[] {
  const out: Run[] = [];
  for (const part of splitRefs(text)) {
    if (!part.chords) {
      out.push({ text: part.text });
      continue;
    }
    view.bar(part.chords).forEach((c, i) => out.push({ text: (i ? ' ' : '') + c.symbol, color: C[c.quality], bold: true }));
  }
  return out;
}

/** Word-wrap runs to lines of roughly maxChars, returning SVG tspans per line. */
function wrap(rs: Run[], maxChars: number): string[] {
  const words: Run[] = [];
  for (const r of rs) {
    if (r.color) words.push(r);
    else for (const w of r.text.split(/(\s+)/)) if (w) words.push({ text: w });
  }
  const lines: Run[][] = [[]];
  let len = 0;
  for (const w of words) {
    if (len + w.text.length > maxChars && w.text.trim() && len > 0) {
      lines.push([]);
      len = 0;
      if (!w.text.trim()) continue;
    }
    if (len === 0 && !w.text.trim()) continue;
    lines[lines.length - 1].push(w);
    len += w.text.length;
  }
  return lines.map((line) =>
    line.map((w) => `<tspan${w.color ? ` fill="${w.color}"` : ''}${w.bold ? ' font-weight="700"' : ''}>${esc(w.text)}</tspan>`).join(''),
  );
}

function textBlock(lines: string[], x: number, y: number, size: number, lh: number, fill: string, anchor = 'start') {
  return lines
    .map((l, i) => `<text xml:space="preserve" x="${x}" y="${y + i * lh}" font-size="${size}" fill="${fill}" text-anchor="${anchor}" ${FONT}>${l}</text>`)
    .join('');
}

// ---------------------------------------------------------------- frames

const footer = `
  <text x="96" y="1040" font-size="26" fill="${C.faint}" ${FONT}>Key of ${keyName} · ${tl.tempo} bpm · Blues Flow by David Reinstein</text>
  <text x="${W - 96}" y="1040" font-size="26" fill="${C.muted}" text-anchor="end" font-weight="700" ${FONT}>blues-flow.netlify.app</text>`;

const svg = (body: string) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="${C.bg}"/>${body}</svg>`;

function card(lines: Array<{ text: string; size: number; fill: string; bold?: boolean; gap?: number }>) {
  let y = 0;
  const placed = lines.map((l) => {
    y += (l.gap ?? 0) + l.size * 1.25;
    return { ...l, y };
  });
  const top = (H - y) / 2;
  return svg(
    placed
      .map((l) => `<text x="${W / 2}" y="${top + l.y}" font-size="${l.size}" fill="${l.fill}" text-anchor="middle" ${l.bold ? 'font-weight="700"' : ''} ${FONT}>${l.text}</text>`)
      .join('') + footer,
  );
}

function titleCard(id: number) {
  const v = VARIATIONS[id - 1];
  const summary = wrap(runs(v.summary), 62);
  const top = 300;
  return svg(`
    <text x="${W / 2}" y="${top}" font-size="40" fill="${C.muted}" text-anchor="middle" ${FONT}>Form ${id} of 18</text>
    <text x="${W / 2}" y="${top + 120}" font-size="104" fill="${C.text}" font-weight="700" text-anchor="middle" ${FONT}>${esc(v.name)}</text>
    ${textBlock(summary, W / 2, top + 230, 40, 56, C.muted, 'middle')}
    ${footer}`);
}

const CELL_W = 420;
const CELL_H = 196;
const GAP = 16;
const X0 = (W - (4 * CELL_W + 3 * GAP)) / 2;
const Y0 = 300;

function sheet(id: number, bar: number | null, beat: number | null, countBeat: number | null) {
  const v = VARIATIONS[id - 1];
  const prev = id > 1 ? VARIATIONS[id - 2].bars : null;
  const summary = wrap(runs(v.summary), 96).slice(0, 3);
  const head = `
    <text x="${X0}" y="96" font-size="30" fill="${C.muted}" ${FONT}>Form ${id} of 18</text>
    <text x="${X0}" y="166" font-size="64" fill="${C.text}" font-weight="700" ${FONT}>${esc(v.name)}</text>
    ${textBlock(summary, X0, 218, 27, 36, C.muted)}`;
  const count =
    countBeat === null
      ? ''
      : [0, 1, 2, 3]
          .map(
            (k) =>
              `<text x="${W - X0 - (3 - k) * 70}" y="166" font-size="64" font-weight="700" text-anchor="end" fill="${k <= countBeat ? C.accent : C.line}" ${FONT}>${k + 1}</text>`,
          )
          .join('') + `<text x="${W - X0}" y="96" font-size="30" fill="${C.muted}" text-anchor="end" ${FONT}>count-in</text>`;
  const cells = v.bars
    .map((b, i) => {
      const x = X0 + (i % 4) * (CELL_W + GAP);
      const y = Y0 + Math.floor(i / 4) * (CELL_H + GAP);
      const active = bar === i;
      const chords = view.bar(b);
      const changed = prev && prev[i] !== b;
      const two = chords.length === 2;
      const half = active && two && beat !== null ? (beat < 2 ? 0 : 1) : null;
      const sym = chords
        .map((c, j) => {
          const cx = two ? x + CELL_W * (j === 0 ? 0.27 : 0.73) : x + CELL_W / 2;
          return `
          ${half === j ? `<rect x="${x + (j === 0 ? 10 : CELL_W / 2 + 4)}" y="${y + 34}" width="${CELL_W / 2 - 14}" height="${CELL_H - 70}" rx="8" fill="${C.accentSoft}"/>` : ''}
          <text x="${cx}" y="${y + (two ? 118 : 122)}" font-size="${two ? 54 : 72}" font-weight="700" fill="${C[c.quality]}" text-anchor="middle" ${FONT}>${esc(c.symbol)}</text>
          <text x="${cx}" y="${y + 160}" font-size="26" fill="${C.muted}" text-anchor="middle" ${FONT}>${esc(c.roman)}</text>`;
        })
        .join(two ? `<line x1="${x + CELL_W / 2}" x2="${x + CELL_W / 2}" y1="${y + 40}" y2="${y + CELL_H - 30}" stroke="${C.line}" stroke-width="2"/>` : '');
      const beats = active
        ? [0, 1, 2, 3]
            .map((k) => `<rect x="${x + 16 + k * ((CELL_W - 32) / 4)}" y="${y + CELL_H - 16}" width="${(CELL_W - 32) / 4 - 8}" height="6" rx="3" fill="${beat !== null && k <= beat ? C.accent : C.line}"/>`)
            .join('')
        : '';
      return `
        <rect x="${x}" y="${y}" width="${CELL_W}" height="${CELL_H}" rx="12" fill="${active ? C.accentSoft : C.surface}" stroke="${active ? C.accent : C.line}" stroke-width="${active ? 5 : 2}"/>
        ${i % 4 === 0 ? `<rect x="${x}" y="${y + 10}" width="5" height="${CELL_H - 20}" fill="${C.muted}"/>` : ''}
        <text x="${x + 18}" y="${y + 34}" font-size="24" fill="${C.faint}" ${FONT}>${i + 1}</text>
        ${changed ? `<circle cx="${x + CELL_W - 22}" cy="${y + 24}" r="8" fill="${C.changed}"/>` : ''}
        ${sym}${beats}`;
    })
    .join('');
  const legend = `<text xml:space="preserve" x="${X0}" y="${Y0 + 3 * (CELL_H + GAP) + 20}" font-size="24" ${FONT}><tspan fill="${C.dom7}">7 dominant</tspan><tspan fill="${C.faint}">   ·   </tspan><tspan fill="${C.min7}">− minor 7</tspan><tspan fill="${C.faint}">   ·   </tspan><tspan fill="${C.maj7}">Δ major 7</tspan><tspan fill="${C.faint}">   ·   </tspan><tspan fill="${C.dim7}">° diminished</tspan><tspan fill="${C.faint}">   ·   </tspan><tspan fill="${C.sus}">sus</tspan>${prev ? `<tspan fill="${C.faint}">   ·   </tspan><tspan fill="${C.changed}">●</tspan><tspan fill="${C.faint}"> changed from form ${id - 1}</tspan>` : ''}</text>`;
  return svg(head + count + cells + legend + footer);
}

// ---------------------------------------------------------------- timeline of frames

const frames: Array<{ file: string; at: number }> = [];
const seen = new Map<string, string>();
function frame(at: number, content: string) {
  let file = seen.get(content);
  if (!file) {
    file = join(FRAMES, `f${String(seen.size).padStart(4, '0')}.svg`);
    writeFileSync(file, content);
    seen.set(content, file);
  }
  frames.push({ file, at });
}

frame(0, card([
  { text: '18 ways through a 12-bar blues', size: 92, fill: C.text, bold: true },
  { text: 'From three chords to Charlie Parker: one chorus of each, in F', size: 44, fill: C.muted, gap: 20 },
  { text: 'Watch the chart; the lit bar is where the band is', size: 36, fill: C.faint, gap: 60 },
]));
for (const f of tl.forms) {
  frame(f.title, titleCard(f.id));
  for (let k = 0; k < 4; k++) frame(f.countIn + k * tl.spb, sheet(f.id, null, null, k));
  for (let b = 0; b < 12; b++)
    for (let k = 0; k < 4; k++) frame(f.countIn + (4 + b * 4 + k) * tl.spb, sheet(f.id, b, k, null));
  frame(f.countIn + 52 * tl.spb, sheet(f.id, null, null, null));
}
frame(tl.forms[tl.forms.length - 1].end, card([
  { text: 'Play along, change key, mix your own', size: 64, fill: C.text, bold: true },
  { text: 'blues-flow.netlify.app', size: 84, fill: C.accent, bold: true, gap: 30 },
  { text: 'Printable posters · vote for your favourite form · send feedback', size: 38, fill: C.muted, gap: 40 },
  { text: 'Made by David Reinstein · youtube.com/@daaronr', size: 34, fill: C.faint, gap: 30 },
]));

console.log(`${frames.length} frame changes, ${seen.size} distinct images`);

// Rasterise distinct frames in parallel batches.
const svgs = [...seen.values()];
const jobs = Math.max(2, cpus().length - 1);
for (let i = 0; i < svgs.length; i += jobs) {
  const batch = svgs.slice(i, i + jobs).filter((f) => !existsSync(f.replace(/\.svg$/, '.png')) || process.argv.includes('--force'));
  if (!batch.length) continue;
  execFileSync('bash', ['-c', batch.map((f) => `rsvg-convert -w ${W} -h ${H} -o "${f.replace(/\.svg$/, '.png')}" "${f}" &`).join(' ') + ' wait']);
  process.stdout.write(`\rRasterised ${Math.min(i + jobs, svgs.length)}/${svgs.length}`);
}
console.log();

// ffmpeg concat list: each image held until the next change.
const list = frames
  .map((f, i) => `file '${f.file.replace(/\.svg$/, '.png')}'\nduration ${((frames[i + 1]?.at ?? tl.total) - f.at).toFixed(4)}`)
  .join('\n');
writeFileSync(join(DIR, 'frames.txt'), `${list}\nfile '${frames[frames.length - 1].file.replace(/\.svg$/, '.png')}'\n`);
const out = join(DIR, 'blues-18-forms.mp4');
execFileSync('ffmpeg', [
  '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', join(DIR, 'frames.txt'), '-i', join(DIR, 'music.wav'),
  '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-tune', 'stillimage',
  '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out,
]);

const stamp = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
writeFileSync(
  join(DIR, 'youtube-description.txt'),
  `18 ways through a 12-bar blues, from three chords to Charlie Parker. One chorus of each form in ${keyName} at ${tl.tempo} bpm, each with a short spoken introduction, the chart on screen and the current bar lit.

Play along, change key, see chord tones and guide tones, or mix your own at https://blues-flow.netlify.app (printable posters there too).

The progressions come from a printed chart of 18 blues progressions in F. The backing band (piano, upright bass, ride cymbal) is generated by the app from sampled instruments.

Made by David Reinstein. More: https://www.youtube.com/@daaronr

${tl.chapters.filter((c) => c.title !== 'End').map((c) => `${stamp(c.start)} ${c.title}`).join('\n')}
`,
);
console.log(`Wrote ${out}`);
