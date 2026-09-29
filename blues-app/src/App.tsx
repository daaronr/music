import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { LINKS, track } from './api.ts';
import { Engine, type Position } from './audio/engine.ts';
import { ChartTable } from './components/ChartTable.tsx';
import { FlowChart } from './components/FlowChart.tsx';
import { LeadSheet } from './components/LeadSheet.tsx';
import { Notes } from './components/Notes.tsx';
import { Suggest } from './components/Suggest.tsx';
import { Support } from './components/Support.tsx';
import { Transport, type SoundPrefs } from './components/Transport.tsx';
import { Videos } from './components/Videos.tsx';
import { Vote } from './components/Vote.tsx';
import { View, decodeMix, encodeMix } from './music/display.ts';
import { INTRO, VARIATIONS } from './music/progressions.ts';
import { KEYS, TRANSPOSITIONS, type Notation, type Transposition } from './music/theory.ts';

type Tag = { variationId: number; mixed: boolean };

interface ViewPrefs {
  key: string;
  transposition: Transposition;
  notation: Notation;
  romanOnly: boolean;
  lowerRoman: boolean; // flowchart and table only
  showRoman: boolean;
  showGuide: boolean;
  compare: 'prev' | 'basic' | 'off';
  tab: 'flow' | 'table';
}

const PREFS_KEY = 'blues-flow-prefs-v2';
const DEFAULT_VIEW: ViewPrefs = { key: 'F', transposition: 'C', notation: 'chart', romanOnly: false, lowerRoman: false, showRoman: true, showGuide: false, compare: 'prev', tab: 'flow' };
const DEFAULT_SOUND: SoundPrefs = {
  tempo: 120,
  swing: 0.64,
  comp: 'swing',
  bass: 'walk',
  sound: 'piano',
  countIn: true,
  mode: 'loop',
  levels: { keys: 1, bass: 1, drums: 1 },
};

function loadPrefs(): { view: ViewPrefs; sound: SoundPrefs } {
  try {
    const saved = JSON.parse(localStorage.getItem(PREFS_KEY) ?? '{}');
    return { view: { ...DEFAULT_VIEW, ...saved.view }, sound: { ...DEFAULT_SOUND, ...saved.sound, mode: 'loop' } };
  } catch {
    return { view: DEFAULT_VIEW, sound: DEFAULT_SOUND };
  }
}

function readHash() {
  const p = new URLSearchParams(location.hash.slice(1));
  const v = Number(p.get('v'));
  const k = p.get('k');
  const t = p.get('t') as Transposition | null;
  return {
    v: v >= 1 && v <= 18 ? v : null,
    mix: p.get('m') ? decodeMix(p.get('m')!) : null,
    key: k && KEYS.includes(k) ? k : null,
    transposition: t && t in TRANSPOSITIONS ? t : null,
  };
}

const keyLabel = (k: string) => k.replace('b', '♭');

// In-page links that scroll without touching the hash, which holds the app state.
const jumpTo = (id: string) => (e: React.MouseEvent) => {
  e.preventDefault();
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
};
const POSTERS: Array<[string, string]> = [
  ['blues-map_roman-numerals_A4.pdf', 'Roman numerals, any key (A4)'],
  ['blues-map_roman-numerals_A3.pdf', 'Roman numerals, any key (A3)'],
  ['blues-map_F_concert_A4.pdf', 'F, concert (A4)'],
  ['blues-map_F_concert_A3.pdf', 'F, concert (A3)'],
  ['blues-map_Bb_concert_A4.pdf', 'B♭, concert (A4)'],
  ['blues-map_F_for-Bb-instruments_A4.pdf', 'Concert F for B♭ trumpet, clarinet, tenor (A4)'],
  ['blues-map_Bb_for-Bb-instruments_A4.pdf', 'Concert B♭ for B♭ trumpet, clarinet, tenor (A4)'],
];
const AUDIO_URL = `${import.meta.env.BASE_URL}audio/blues-18-forms.mp3`;

export default function App() {
  const initial = useMemo(() => {
    const prefs = loadPrefs();
    const hash = readHash();
    return {
      view: { ...prefs.view, key: hash.key ?? prefs.view.key, transposition: hash.transposition ?? prefs.view.transposition },
      sound: prefs.sound,
      v: hash.v ?? 1,
      mix: hash.mix,
    };
  }, []);

  const [variationId, setVariationId] = useState(initial.v);
  const [mix, setMix] = useState<string[] | null>(initial.mix);
  const [vp, setVp] = useState<ViewPrefs>(initial.view);
  const [sp, setSp] = useState<SoundPrefs>(initial.sound);
  const [pos, setPos] = useState<Position<Tag> | null>(null);
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState<number | null>(null);
  const [selectedBar, setSelectedBar] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const variation = VARIATIONS[variationId - 1];
  const bars = mix ?? variation.bars;
  const view = useMemo(
    () => new View({ key: vp.key, transposition: vp.transposition, notation: vp.notation, romanOnly: vp.romanOnly }),
    [vp.key, vp.transposition, vp.notation, vp.romanOnly],
  );
  const lowerView = useMemo(
    () => (vp.lowerRoman && !vp.romanOnly ? new View({ ...view.opts, romanOnly: true }) : view),
    [view, vp.lowerRoman, vp.romanOnly],
  );
  // With roman numerals as the main label, a second roman line (or letter-name guide tones) would just repeat or confuse.
  const showRoman = vp.showRoman && !vp.romanOnly;
  const showGuide = vp.showGuide && !vp.romanOnly;
  const setView = (patch: Partial<ViewPrefs>) => setVp((p) => ({ ...p, ...patch }));
  const setSound = useCallback((patch: Partial<SoundPrefs>) => setSp((p) => ({ ...p, ...patch })), []);

  useEffect(() => track('view', `form ${initial.v}`), [initial.v]);
  useEffect(() => {
    if (vp.key !== 'F') track('key', vp.key);
  }, [vp.key]);

  // ------------------------------------------------------------ persistence
  useEffect(() => {
    try {
      localStorage.setItem(PREFS_KEY, JSON.stringify({ view: vp, sound: sp }));
    } catch {
      /* private mode: settings just won't persist */
    }
  }, [vp, sp]);

  useEffect(() => {
    const onHash = () => {
      if (!location.hash.includes('=')) return;
      const h = readHash();
      if (h.v) setVariationId(h.v);
      setMix(h.mix);
      // Transposition is the reader's own instrument, so a link without one keeps theirs.
      setVp((p) => ({ ...p, key: h.key ?? p.key, transposition: h.transposition ?? p.transposition }));
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  useEffect(() => {
    const p = new URLSearchParams();
    p.set('v', String(variationId));
    if (mix) p.set('m', encodeMix(mix));
    p.set('k', vp.key);
    if (vp.transposition !== 'C') p.set('t', vp.transposition);
    history.replaceState(null, '', `#${p.toString()}`);
  }, [variationId, mix, vp.key, vp.transposition]);

  // ------------------------------------------------------------ engine
  const [engine] = useState(() => new Engine<Tag>());

  // Latest state for the engine's callbacks, which run outside React.
  const live = useRef({ bars, variationId, mix, view, mode: sp.mode });
  useLayoutEffect(() => {
    live.current = { bars, variationId, mix, view, mode: sp.mode };
  });
  const tour = useRef({ id: variationId, chorus: 0 });

  useEffect(() => {
    if (import.meta.env.DEV) Object.assign(window, { __engine: engine }); // for poking at from the console
    const planBar: Engine<Tag>['planBar'] = (chorus, bar) => {
      const L = live.current;
      if (L.mode === 'tour') {
        if (bar === 0 && chorus !== tour.current.chorus) {
          tour.current = { id: (tour.current.id % 18) + 1, chorus };
        }
        const v = VARIATIONS[tour.current.id - 1];
        const following = bar === 11 ? VARIATIONS[tour.current.id % 18].bars[0] : v.bars[bar + 1];
        return { chords: L.view.concert(v.bars[bar]), next: L.view.concert(following)[0], tag: { variationId: v.id, mixed: false } };
      }
      return {
        chords: L.view.concert(L.bars[bar]),
        next: L.view.concert(L.bars[(bar + 1) % 12])[0],
        tag: { variationId: L.variationId, mixed: !!L.mix },
      };
    };
    const onPosition: Engine<Tag>['onPosition'] = (p) => {
      setPos(p);
      if (p?.tag && live.current.mode === 'tour' && p.tag.variationId !== live.current.variationId) {
        setVariationId(p.tag.variationId);
        setMix(null);
      }
    };
    engine.connect({ planBar, onPosition, onLoading: setLoading });
    return () => engine.stop();
  }, [engine]);

  useEffect(() => {
    engine.configure({ tempo: sp.tempo, settings: { swing: sp.swing, comp: sp.comp, bass: sp.bass }, countIn: sp.countIn });
    engine.setLevel('keys', sp.levels.keys);
    engine.setLevel('bass', sp.levels.bass);
    engine.setLevel('drums', sp.levels.drums);
    if (engine.ctx) engine.setKeysSound(sp.sound).catch(() => setError('Could not load that sound.'));
    if (sp.sound !== 'piano') track('instrument', sp.sound);
  }, [engine, sp]);

  const toggle = useCallback(async () => {
    setError(null);
    if (engine.playing) {
      engine.stop();
      setPlaying(false);
      return;
    }
    try {
      tour.current = { id: live.current.variationId, chorus: 0 };
      await engine.ensureReady();
      await engine.setKeysSound(sp.sound);
      await engine.start();
      setPlaying(true);
      track(live.current.mode === 'tour' ? 'tour' : 'play', live.current.mix ? 'mix' : String(live.current.variationId));
    } catch {
      setLoading(null);
      setError('Could not load the sounds. Check your connection and try again.');
    }
  }, [engine, sp.sound]);

  // ------------------------------------------------------------ navigation
  const goTo = useCallback((id: number) => {
    const next = ((id - 1 + 18) % 18) + 1;
    setVariationId(next);
    setMix(null);
    tour.current = { ...tour.current, id: next };
  }, []);

  const hearBar = (i: number) => {
    if (engine.playing) return;
    engine.audition(view.concert(bars[i])).catch(() => setError('Could not load the sounds.'));
  };

  const selectBar = (i: number) => {
    setSelectedBar(i);
    hearBar(i);
  };

  const pick = (i: number, bar: string) => {
    const nextBars = [...bars];
    nextBars[i] = bar;
    const exact = VARIATIONS.find((v) => v.bars.every((b, k) => b === nextBars[k]));
    if (exact) {
      setVariationId(exact.id);
      setMix(null);
    } else {
      setMix(nextBars);
      track('mix', `bar ${i + 1}`);
    }
    if (sp.mode === 'tour') setSound({ mode: 'loop' });
    setSelectedBar(i);
    if (!engine.playing) engine.audition(view.concert(bar)).catch(() => {});
  };

  const tryBars = (next: string[]) => {
    const exact = VARIATIONS.find((v) => v.bars.every((b, k) => b === next[k]));
    if (exact) {
      setVariationId(exact.id);
      setMix(null);
    } else setMix(next);
    if (sp.mode === 'tour') setSound({ mode: 'loop' });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const randomMix = () => {
    const r = () => VARIATIONS[Math.floor(Math.random() * 18)].bars;
    const [a, b, c] = [r(), r(), r()];
    setMix([...a.slice(0, 4), ...b.slice(4, 8), ...c.slice(8, 12)]);
    track('mix', 'random');
    if (sp.mode === 'tour') setSound({ mode: 'loop' });
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement;
      if (el.closest('input, select, textarea') || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === ' ' && !el.closest('button')) {
        e.preventDefault();
        void toggle();
      } else if (e.key === 'ArrowRight') goTo(live.current.variationId + 1);
      else if (e.key === 'ArrowLeft') goTo(live.current.variationId - 1);
      else if (e.key === '+' || e.key === '=') setSp((p) => ({ ...p, tempo: Math.min(300, p.tempo + 4) }));
      else if (e.key === '-') setSp((p) => ({ ...p, tempo: Math.max(40, p.tempo - 4) }));
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [toggle, goTo]);

  // ------------------------------------------------------------ derived
  const compareBars = mix
    ? variation.bars
    : vp.compare === 'prev'
      ? variationId > 1
        ? VARIATIONS[variationId - 2].bars
        : null
      : vp.compare === 'basic' && variationId > 1
        ? VARIATIONS[0].bars
        : null;
  const changed = bars.map((b, i) => (compareBars ? b !== compareBars[i] : false));
  const activeBar = pos && !pos.countIn ? pos.bar : null;
  const activeBeat = pos ? pos.beat : null;
  const status = !pos
    ? ''
    : pos.countIn
      ? `Count-in ${pos.beat + 1}`
      : sp.mode === 'tour'
        ? `Form ${pos.tag?.variationId} · bar ${pos.bar + 1}`
        : `Chorus ${pos.chorus + 1} · bar ${pos.bar + 1}`;

  return (
    <div className="app">
      <header className="top">
        <div className="title">
          <h1>Blues Flow</h1>
          <p>
            18 ways through a 12-bar blues · by{' '}
            <a href="#about" onClick={jumpTo('about')}>
              David Reinstein
            </a>{' '}
            ·{' '}
            <a href="#videos" onClick={jumpTo('videos')}>
              videos
            </a>
          </p>
        </div>
        <div className="view-controls">
          <label>
            <span>Key</span>
            <select value={vp.key} onChange={(e) => setView({ key: e.target.value })}>
              {KEYS.map((k) => (
                <option key={k} value={k}>
                  {keyLabel(k)}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Chord names for</span>
            <select value={vp.transposition} onChange={(e) => setView({ transposition: e.target.value as Transposition })}>
              {Object.entries(TRANSPOSITIONS).map(([k, t]) => (
                <option key={k} value={k}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Symbols</span>
            <select
              value={vp.romanOnly ? `roman-${vp.notation}` : vp.notation}
              onChange={(e) => {
                const v = e.target.value;
                setView(v.startsWith('roman-') ? { romanOnly: true, notation: v.slice(6) as Notation } : { romanOnly: false, notation: v as Notation });
              }}
            >
              <option value="chart">C− FΔ B° (as on the chart)</option>
              <option value="standard">Cm7 Fmaj7 B°7</option>
              <option value="roman-chart">Roman numerals: ii−7 IΔ7</option>
              <option value="roman-standard">Roman numerals: iim7 Imaj7</option>
            </select>
          </label>
          <label>
            <span>Mark changes</span>
            <select value={vp.compare} onChange={(e) => setView({ compare: e.target.value as ViewPrefs['compare'] })}>
              <option value="prev">vs the form before</option>
              <option value="basic">vs the basic blues</option>
              <option value="off">off</option>
            </select>
          </label>
          <label className="check">
            <input type="checkbox" checked={vp.showRoman} disabled={vp.romanOnly} onChange={(e) => setView({ showRoman: e.target.checked })} /> Roman numerals
          </label>
          <label className="check">
            <input type="checkbox" checked={vp.showGuide} disabled={vp.romanOnly} onChange={(e) => setView({ showGuide: e.target.checked })} /> Guide tones
          </label>
        </div>
      </header>

      <nav className="picker" aria-label="Choose a form">
        <div className="picker-core">
          <button className="small" onClick={() => goTo(variationId - 1)} aria-label="Previous form" aria-keyshortcuts="ArrowLeft">
            ‹
          </button>
          <select value={variationId} onChange={(e) => goTo(Number(e.target.value))} aria-label="Form">
            {VARIATIONS.map((v) => (
              <option key={v.id} value={v.id}>
                {v.id}. {v.name}
              </option>
            ))}
          </select>
          <button className="small" onClick={() => goTo(variationId + 1)} aria-label="Next form" aria-keyshortcuts="ArrowRight">
            ›
          </button>
        </div>
        {mix && (
          <>
            <span className="mix-badge">Mixed</span>
            <button className="small" onClick={() => setMix(null)}>
              Back to form {variationId}
            </button>
          </>
        )}
        <button className="small" onClick={randomMix} title="Bars 1–4, 5–8 and 9–12 from three random forms">
          Random mix
        </button>
        <a className="small-link" href="#vote" onClick={jumpTo('vote')}>
          Vote for your favourite
        </a>
        <a className="small-link" href="#suggest" onClick={jumpTo('suggest')}>
          Suggest a form
        </a>
      </nav>

      <main className="main">
        <div className="sheet-wrap">
          <LeadSheet
            bars={bars}
            view={view}
            changed={changed}
            showRoman={showRoman}
            showGuide={showGuide}
            activeBar={activeBar}
            activeBeat={activeBeat}
            selectedBar={selectedBar}
            onBar={selectBar}
          />
          <p className="legend">
            <span className="q-dom7">7 dominant</span>
            <span className="q-min7">− minor 7</span>
            <span className="q-maj7">Δ major 7</span>
            <span className="q-dim7">° diminished</span>
            <span className="q-sus">sus</span>
            {compareBars && <span className="legend-changed">changed bar</span>}
            <span className="legend-tip">Click a bar to hear it and see its notes.</span>
          </p>
        </div>
        <Notes
          variation={variation}
          mix={mix}
          bars={bars}
          view={view}
          showRoman={showRoman}
          selectedBar={selectedBar}
          onSelectBar={selectBar}
          onHear={hearBar}
          onGoTo={goTo}
        />
      </main>

      <section className="lower">
        <div className="tabs" role="tablist">
          <button role="tab" aria-selected={vp.tab === 'flow'} className={vp.tab === 'flow' ? 'on' : ''} onClick={() => setView({ tab: 'flow' })}>
            Flowchart
          </button>
          <button role="tab" aria-selected={vp.tab === 'table'} className={vp.tab === 'table' ? 'on' : ''} onClick={() => setView({ tab: 'table' })}>
            All 18
          </button>
          <label className="check tabs-opt">
            <input
              type="checkbox"
              checked={vp.romanOnly || vp.lowerRoman}
              disabled={vp.romanOnly}
              onChange={(e) => setView({ lowerRoman: e.target.checked })}
            />{' '}
            Roman numerals only
          </label>
        </div>
        {vp.tab === 'flow' ? (
          <FlowChart bars={bars} view={lowerView} activeBar={activeBar} selectedBar={selectedBar} onPick={pick} />
        ) : (
          <ChartTable view={lowerView} currentId={mix ? null : variationId} activeBar={activeBar} onSelect={goTo} />
        )}
      </section>

      <Videos
        currentId={variationId}
        onPause={() => {
          if (!engine.playing) return;
          engine.stop();
          setPlaying(false);
        }}
      />

      <section className="about">
        <details>
          <summary>How the chart works</summary>
          <p>{INTRO}</p>
          <p>
            Keys: <kbd>Space</kbd> play or stop, <kbd>←</kbd> <kbd>→</kbd> previous or next form, <kbd>+</kbd> <kbd>−</kbd> tempo.
          </p>
        </details>
        <div className="listen">
          <h2>Listen to all 18</h2>
          <p>One chorus of each form in F at 126 bpm, with a short spoken introduction to each (11½ minutes).</p>
          <audio controls preload="none" src={AUDIO_URL} onPlay={() => track('mp3')} />
          <p>
            <a href={AUDIO_URL} download>
              Download the MP3
            </a>{' '}
            · <a href={AUDIO_URL.replace(/\.mp3$/, '.txt')}>Track list</a>
          </p>
        </div>
        <div className="listen">
          <h2>Posters to print</h2>
          <p>Three landscape pages: every chord option bar by bar, the flowchart, and all 18 forms as a table.</p>
          <ul className="poster-list">
            {POSTERS.map(([file, label]) => (
              <li key={file}>
                <a href={`${import.meta.env.BASE_URL}posters/${file}`} onClick={() => track('poster', file)}>
                  {label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <div id="vote">
        <Vote currentId={variationId} />
      </div>

      <Suggest
        key={`${vp.key}-${vp.transposition}-${vp.romanOnly}`}
        bars={bars}
        view={view}
        context={mix ? `mix of form ${variationId}` : `form ${variationId}`}
        onTry={tryBars}
      />

      <Support context={mix ? `mix of form ${variationId}` : `form ${variationId}`} />

      <footer className="foot">
        <p>
          Made by David Reinstein. Progressions transcribed from a printed chart of 18 blues progressions in F. Samples: Splendid
          Grand Piano; 1958 Otto Rubner double bass, pizzicato (D. Smolken); cymbals from the Versilian Community Sample Library; via
          smplr.{' '}
          <a href="https://projects.davidreinstein.org/">More projects by David Reinstein</a>
        </p>
        <p>
          Comments or suggestions? Annotate with <a href="https://web.hypothes.is/">Hypothes.is</a> (panel at the right edge), use the
          feedback form above, or email {LINKS.email}.
        </p>
        <p>
          Privacy: the page counts visits and which features get used (no cookies, no IP addresses, nothing personal), and skips even
          that if your browser sends Do Not Track. The videos load from YouTube (its no-cookie player) only when you press play.
        </p>
      </footer>

      <div className="dock">
        {error && <p className="error">{error}</p>}
        <Transport prefs={sp} set={setSound} playing={playing} loading={loading} status={status} onToggle={toggle} />
      </div>
    </div>
  );
}
