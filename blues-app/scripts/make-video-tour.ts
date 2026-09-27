// YouTube video 2: a narrated walkthrough of the app.
// Drives the local dev copy (npm run dev -- --port 5178) in headless Chrome,
// records the screen, then adds Kokoro narration and, for the playback scene,
// the offline-rendered band from video 1 (same form and tempo).
//   node scripts/make-video-tour.ts    -> .cache/video2/blues-flow-tour.mp4
// Needs the dev server, Google Chrome, ffmpeg, rsvg-convert, the Kokoro venv,
// and .cache/video1/music.wav + timeline.json from the video-1 steps.

import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import puppeteer, { type Page } from 'puppeteer-core';

const APP = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DIR = join(APP, '.cache', 'video2');
mkdirSync(DIR, { recursive: true });
const URL = 'http://localhost:5178/music/';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const TEMPO = 126;
const PLAY_FORM = 10;

// ---------------------------------------------------------------- narration

const SCENES: Array<{ id: string; say: string }> = [
  { id: 'intro', say: 'Blues Flow is a free web app for learning the twelve-bar blues, eighteen different ways. It starts from a printed chart of eighteen progressions, from the plain three-chord blues up to Charlie Parker style changes.' },
  { id: 'forms', say: 'Pick a form from the list, or step through with the arrows. Pink dots mark the bars that changed from the form before, and the panel on the right explains what each form adds.' },
  { id: 'bar', say: 'Click any bar to hear it, and to see its chord tones, its guide tones, and a scale to try over it.' },
  { id: 'play', say: 'Press play for a backing band: piano, walking bass and ride cymbal. The bar you are in lights up.' },
  { id: 'keys', say: 'Change the key, show chord names for B-flat or E-flat instruments, or switch to roman numerals, so the same chart works in any key.' },
  { id: 'flow', say: 'The flowchart shows every chord the chart uses in each bar, with a line for each form. Open it full screen and zoom in to follow the paths. Click a chord to swap it into your progression, and hear how it sounds.' },
  { id: 'table', say: 'Or see all eighteen forms side by side, with the changes in bold.' },
  { id: 'vote', say: 'Vote for your favourite form, and then see how everyone else voted.' },
  { id: 'extras', say: 'There is also a narrated recording of all eighteen, and printable posters of the whole map, in several keys or in roman numerals.' },
  { id: 'support', say: 'It is free. If you find it useful, please consider a donation to The Unjournal or to GiveWell, and let David know, so he can thank you and put your suggestions first. Feedback is very welcome.' },
];
const OUTRO_SAY = 'Blues Flow. Find it at blues flow dot netlify dot app.';

function narration(): string[] {
  const texts = [...SCENES.map((s) => s.say), OUTRO_SAY];
  const dir = join(DIR, 'speech');
  mkdirSync(dir, { recursive: true });
  const manifest = join(dir, 'texts.json');
  const files = texts.map((_, i) => join(dir, `speech_${String(i).padStart(3, '0')}.wav`));
  if (existsSync(manifest) && readFileSync(manifest, 'utf8') === JSON.stringify(texts) && files.every(existsSync)) return files;
  writeFileSync(manifest, JSON.stringify(texts));
  const tools = join(homedir(), 'githubs/claude_code_misc_work/brass_playing_next_step');
  const r = spawnSync(join(tools, '.venv_kokoro/bin/python'), [join(tools, 'render_kokoro_segments.py'), manifest, dir], { stdio: 'ignore' });
  if (r.status !== 0) throw new Error('Kokoro failed');
  return files;
}

const duration = (f: string) =>
  Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString().trim());

// ---------------------------------------------------------------- browser helpers

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function cursorTo(page: Page, selector: string, click = true) {
  const el = await page.waitForSelector(selector, { visible: true });
  await el!.scrollIntoView();
  await sleep(250);
  const box = await el!.boundingBox();
  if (!box) return;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 28 });
  await sleep(180);
  if (click) {
    await page.mouse.down();
    await sleep(90);
    await page.mouse.up();
  }
}

async function smoothScrollTo(page: Page, selector: string, offset = 90) {
  await page.evaluate(
    (sel, off) => {
      const el = document.querySelector(sel)!;
      window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - off, behavior: 'smooth' });
    },
    selector,
    offset,
  );
  await sleep(1100);
}

async function selectValue(page: Page, selector: string, value: string) {
  await cursorTo(page, selector, false);
  await page.select(selector, value);
}

// A visible cursor and click ripple (headless recordings have none).
const CURSOR = `
  const c = document.createElement('div');
  c.style.cssText = 'position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:rgba(255,122,89,.35);border:2px solid #ff7a59;z-index:99999;pointer-events:none;transition:transform .12s';
  document.body.appendChild(c);
  addEventListener('mousemove', (e) => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
  addEventListener('mousedown', () => { c.style.transform = 'scale(.7)'; }, true);
  addEventListener('mouseup', () => { c.style.transform = 'scale(1)'; }, true);
`;

// ---------------------------------------------------------------- record

const speech = narration();
const lengths = speech.map(duration);
console.log('Narration:', lengths.map((d) => d.toFixed(1)).join(' '));

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: true,
  args: ['--autoplay-policy=no-user-gesture-required', '--disable-extensions', '--hide-scrollbars'],
  defaultViewport: { width: 1280, height: 720, deviceScaleFactor: 1.5 },
});
const page = await browser.newPage();
await page.goto(URL, { waitUntil: 'networkidle0' });
await page.evaluate((tempo) => {
  localStorage.clear();
  localStorage.setItem(
    'blues-flow-prefs-v2',
    JSON.stringify({ view: {}, sound: { tempo, countIn: true, comp: 'swing', bass: 'walk', sound: 'piano', swing: 0.64 } }),
  );
}, TEMPO);
await page.goto(`${URL}#v=1&k=F`, { waitUntil: 'networkidle0' });
await page.reload({ waitUntil: 'networkidle0' }); // a hash-only change doesn't reload, and the saved tempo must load
const shownTempo = await page.$eval('.tempo-val', (e) => e.textContent);
if (shownTempo !== `${TEMPO} bpm`) throw new Error(`Tempo is ${shownTempo}, expected ${TEMPO}`);
await page.evaluate(CURSOR);
await page.mouse.move(640, 360);
await sleep(500);

const raw = join(DIR, 'raw.webm');
const recorder = await page.screencast({ path: raw as `${string}.webm` });
const t0 = Date.now();
const marks: Record<string, number> = {};
const scene = async (i: number, act: () => Promise<void>, extraMs = 0) => {
  marks[SCENES[i].id] = (Date.now() - t0) / 1000;
  const until = Date.now() + lengths[i] * 1000 + 600 + extraMs;
  await act();
  while (Date.now() < until) await sleep(50);
};

await scene(0, async () => {
  await sleep(1500);
  await smoothScrollTo(page, '.notes', 400);
  await sleep(2500);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
});
await scene(1, async () => {
  await cursorTo(page, 'button[aria-label="Next form"]');
  await sleep(1400);
  await cursorTo(page, 'button[aria-label="Next form"]');
  await sleep(1400);
  await selectValue(page, '.picker select', String(PLAY_FORM));
  await sleep(1200);
  await cursorTo(page, '.notes h2', false);
});
await scene(2, async () => {
  await cursorTo(page, '.sheet .bar:nth-child(6)');
  await sleep(1200);
  await cursorTo(page, '.detail', false);
});
let countIn = 0;
await scene(
  3,
  async () => {
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
    await sleep(700);
    await cursorTo(page, 'button.play');
    const start = Date.now();
    while (Date.now() - start < 20000) {
      const s = await page.$eval('.status', (e) => e.textContent ?? '');
      if (s.startsWith('Count-in')) break;
      await sleep(20);
    }
    countIn = (Date.now() - t0) / 1000;
    await page.mouse.move(1150, 620, { steps: 20 });
  },
  9000, // let the band play past the narration
);
await cursorTo(page, 'button.play');
await sleep(500);
await scene(4, async () => {
  await selectValue(page, '.view-controls label:nth-child(1) select', 'Bb');
  await sleep(1500);
  await selectValue(page, '.view-controls label:nth-child(2) select', 'Bb');
  await sleep(1800);
  await selectValue(page, '.view-controls label:nth-child(3) select', 'roman-chart');
  await sleep(1800);
  await selectValue(page, '.view-controls label:nth-child(3) select', 'chart');
  await selectValue(page, '.view-controls label:nth-child(2) select', 'C');
  await selectValue(page, '.view-controls label:nth-child(1) select', 'F');
});
await scene(5, async () => {
  await smoothScrollTo(page, '.lower', 60);
  await cursorTo(page, '.flow-tools button:nth-child(5)'); // full screen
  await sleep(700);
  await cursorTo(page, '.flow-tools button[aria-label="Zoom in"]');
  await sleep(500);
  await cursorTo(page, '.flow-tools button[aria-label="Zoom in"]');
  await sleep(700);
  await cursorTo(page, '.flow .node[aria-label^="Bar 3: D− G7"]', false);
  await sleep(1600);
  await cursorTo(page, '.flow .node[aria-label^="Bar 7: F7 E7"]', false);
  await sleep(1400);
  await cursorTo(page, '.flow .node[aria-label^="Bar 7: F7 E7"]');
  await sleep(900);
  await cursorTo(page, '.flow-tools button:nth-child(5)'); // close full screen
  await cursorTo(page, '.flow-tools button:nth-child(4)'); // fit width again
  await sleep(500);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(1300);
  await cursorTo(page, '.mix-badge', false);
});
await scene(6, async () => {
  await smoothScrollTo(page, '.lower', 60);
  await cursorTo(page, '.tabs button:nth-child(2)');
  await sleep(1000);
  await page.mouse.move(800, 450, { steps: 20 });
});
await scene(7, async () => {
  await smoothScrollTo(page, '#vote', 40);
  await cursorTo(page, '.vote-form select', false);
  await sleep(700);
  await cursorTo(page, '.vote-form .chips .chip:nth-child(14)', false);
});
await scene(8, async () => {
  await smoothScrollTo(page, '.about', 40);
  await cursorTo(page, '.listen audio', false);
  await sleep(1500);
  await cursorTo(page, '.poster-list li:first-child a', false);
});
await scene(9, async () => {
  await smoothScrollTo(page, '.support', 40);
  await cursorTo(page, '.support .panel:nth-child(3) a', false);
  await sleep(2500);
  await cursorTo(page, '.support .panel:nth-child(2) textarea', false);
});
const recordedEnd = (Date.now() - t0) / 1000;
await recorder.stop();
await browser.close();
console.log('Scene starts:', marks, 'count-in at', countIn.toFixed(2), 'end', recordedEnd.toFixed(1));

// ---------------------------------------------------------------- outro card

const outroSvg = join(DIR, 'outro.svg');
writeFileSync(
  outroSvg,
  `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><rect width="1920" height="1080" fill="#121419"/>
  <g font-family="Helvetica Neue, Helvetica, Arial, sans-serif" text-anchor="middle">
  <text x="960" y="420" font-size="96" font-weight="700" fill="#eceef3">Blues Flow</text>
  <text x="960" y="540" font-size="84" font-weight="700" fill="#ff7a59">blues-flow.netlify.app</text>
  <text x="960" y="650" font-size="40" fill="#a3aabb">18 ways through a 12-bar blues · free · any key</text>
  <text x="960" y="760" font-size="34" fill="#737b8d">Made by David Reinstein · youtube.com/@daaronr</text></g></svg>`,
);
execFileSync('rsvg-convert', ['-o', join(DIR, 'outro.png'), outroSvg]);
const outroLen = lengths[lengths.length - 1] + 2.5;

// ---------------------------------------------------------------- audio

// Band audio for the playback scene: form 10 from video 1, same tempo, from its count-in.
const v1 = JSON.parse(readFileSync(join(APP, '.cache', 'video1', 'timeline.json'), 'utf8'));
const f10 = v1.forms.find((f: { id: number }) => f.id === PLAY_FORM);
const musicLen = marks.keys - countIn - 0.3;
const inputs: string[] = [];
const filters: string[] = [];
SCENES.forEach((_, i) => {
  inputs.push('-i', speech[i]);
  filters.push(`[${i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay=${Math.round(marks[SCENES[i].id] * 1000)}:all=1,volume=1.0[s${i}]`);
});
const n = SCENES.length;
inputs.push('-ss', String(f10.countIn), '-t', String(musicLen), '-i', join(APP, '.cache', 'video1', 'music.wav'));
filters.push(`[${n}:a]aresample=48000,volume=0.55,afade=t=out:st=${Math.max(0, musicLen - 1.2)}:d=1.2,adelay=${Math.round(countIn * 1000 + 60)}:all=1[m]`);
inputs.push('-i', speech[n]);
filters.push(`[${n + 1}:a]aresample=48000,aformat=channel_layouts=stereo,adelay=${Math.round((recordedEnd + 1) * 1000)}:all=1[o]`);
filters.push(`${SCENES.map((_, i) => `[s${i}]`).join('')}[m][o]amix=inputs=${n + 2}:normalize=0:duration=longest,loudnorm=I=-16:TP=-1.5[a]`);
const audio = join(DIR, 'audio.wav');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', filters.join(';'), '-map', '[a]', '-ar', '48000', audio]);

// ---------------------------------------------------------------- video

const screen = join(DIR, 'screen.mp4');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', raw, '-vf', 'scale=1920:1080:flags=lanczos,fps=30,format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', screen]);
const outro = join(DIR, 'outro.mp4');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-loop', '1', '-t', String(outroLen), '-i', join(DIR, 'outro.png'), '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-tune', 'stillimage', outro]);
writeFileSync(join(DIR, 'parts.txt'), `file '${screen}'\nfile '${outro}'\n`);
const silentVideo = join(DIR, 'video.mp4');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', join(DIR, 'parts.txt'), '-c', 'copy', silentVideo]);
const out = join(DIR, 'blues-flow-tour.mp4');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', silentVideo, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out]);

const stamp = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
// YouTube only shows chapters that are all at least 10 seconds long, so short scenes fold into their neighbours.
const chapterNames: Record<string, string> = {
  intro: 'What it is', forms: 'The 18 forms and chord tones', play: 'Play along', keys: 'Keys, B♭/E♭ parts, roman numerals',
  flow: 'Flowchart, mixing, all 18 side by side', vote: 'Vote, MP3 and posters', support: 'Support and feedback',
};
writeFileSync(
  join(DIR, 'youtube-description.txt'),
  `A quick tour of Blues Flow, a free web app for learning 18 versions of the 12-bar blues: https://blues-flow.netlify.app

It shows each form as a lead sheet in any key (or for B♭/E♭ instruments, or in roman numerals), plays it with a piano/bass/drums backing band, explains what each form adds, and lets you mix bars from different forms. There are printable posters and a narrated recording of all 18 too.

It's free. If you find it useful, please consider a donation to The Unjournal (https://info.unjournal.org/donate.html) or GiveWell (https://www.givewell.org/donate), and let me know through the site.

Made by David Reinstein. All 18 forms played through: see my channel, https://www.youtube.com/@daaronr

${Object.entries(marks).filter(([k]) => k in chapterNames).map(([k, t]) => `${stamp(k === 'intro' ? 0 : t)} ${chapterNames[k]}`).join('\n')}
`,
);
console.log(`Wrote ${out} (${stamp(recordedEnd + outroLen)})`);
