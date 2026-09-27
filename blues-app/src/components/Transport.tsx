import { useRef, useState } from 'react';
import { KEYS_SOUNDS, type KeysSound } from '../audio/engine.ts';
import type { Part } from '../music/arranger.ts';

export interface SoundPrefs {
  tempo: number;
  swing: number;
  comp: 'swing' | 'sustain';
  bass: 'walk' | 'two';
  sound: KeysSound;
  countIn: boolean;
  mode: 'loop' | 'tour';
  levels: Record<Part, number>;
}

interface Props {
  prefs: SoundPrefs;
  set: (patch: Partial<SoundPrefs>) => void;
  playing: boolean;
  loading: number | null;
  status: string;
  onToggle: () => void;
}

const clampTempo = (t: number) => Math.max(40, Math.min(300, Math.round(t)));

export function Transport({ prefs, set, playing, loading, status, onToggle }: Props) {
  const [open, setOpen] = useState(false);
  const taps = useRef<number[]>([]);

  const tap = () => {
    const now = performance.now();
    taps.current = [...taps.current.filter((t) => now - t < 2500), now].slice(-6);
    if (taps.current.length >= 3) {
      const gaps = taps.current.slice(1).map((t, i) => t - taps.current[i]);
      set({ tempo: clampTempo(60000 / (gaps.reduce((s, g) => s + g, 0) / gaps.length)) });
    }
  };

  const swingLabel = prefs.swing < 0.54 ? 'straight' : prefs.swing < 0.62 ? 'light' : prefs.swing < 0.69 ? 'medium' : 'heavy';

  return (
    <div className="transport">
      <div className="transport-row">
        <button className={`play${playing ? ' is-playing' : ''}`} onClick={onToggle} disabled={loading !== null && !playing} aria-keyshortcuts="Space">
          {loading !== null && !playing ? (
            `Loading ${Math.round(loading * 100)}%`
          ) : playing ? (
            <>
              <svg viewBox="0 0 16 16" aria-hidden="true">
                <rect x="3" y="3" width="10" height="10" rx="1" />
              </svg>
              Stop
            </>
          ) : (
            <>
              <svg viewBox="0 0 16 16" aria-hidden="true">
                <path d="M4 2.5v11l9.5-5.5z" />
              </svg>
              Play
            </>
          )}
        </button>

        <div className="tempo">
          <button className="small" onClick={() => set({ tempo: clampTempo(prefs.tempo - 4) })} aria-label="Slower">
            −
          </button>
          <input
            type="range"
            min={40}
            max={300}
            value={prefs.tempo}
            onChange={(e) => set({ tempo: Number(e.target.value) })}
            aria-label="Tempo"
          />
          <button className="small" onClick={() => set({ tempo: clampTempo(prefs.tempo + 4) })} aria-label="Faster">
            +
          </button>
          <span className="tempo-val">{prefs.tempo} bpm</span>
          <button className="small tap" onClick={tap} title="Tap four times to set the tempo">
            Tap
          </button>
        </div>

        <div className="seg" role="radiogroup" aria-label="What to play">
          <button role="radio" aria-checked={prefs.mode === 'loop'} className={prefs.mode === 'loop' ? 'on' : ''} onClick={() => set({ mode: 'loop' })}>
            <span className="long">Loop this form</span>
            <span className="short">Loop</span>
          </button>
          <button role="radio" aria-checked={prefs.mode === 'tour'} className={prefs.mode === 'tour' ? 'on' : ''} onClick={() => set({ mode: 'tour' })}>
            <span className="long">Step through all 18</span>
            <span className="short">All 18</span>
          </button>
        </div>

        <label className="check">
          <input type="checkbox" checked={prefs.countIn} onChange={(e) => set({ countIn: e.target.checked })} /> Count-in
        </label>

        <span className="status" aria-live="polite">
          {status}
        </span>

        <button className="small more" aria-expanded={open} onClick={() => setOpen(!open)}>
          Sound {open ? '▴' : '▾'}
        </button>
      </div>

      {open && (
        <div className="sound-panel">
          <label>
            <span>Chords on</span>
            <select value={prefs.sound} onChange={(e) => set({ sound: e.target.value as KeysSound })}>
              {Object.entries(KEYS_SOUNDS).map(([k, label]) => (
                <option key={k} value={k}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Comping</span>
            <select value={prefs.comp} onChange={(e) => set({ comp: e.target.value as SoundPrefs['comp'] })}>
              <option value="swing">Swing rhythms</option>
              <option value="sustain">Held chords (clearest)</option>
            </select>
          </label>
          <label>
            <span>Bass</span>
            <select value={prefs.bass} onChange={(e) => set({ bass: e.target.value as SoundPrefs['bass'] })}>
              <option value="walk">Walking</option>
              <option value="two">Two-feel</option>
            </select>
          </label>
          <label>
            <span>Swing: {swingLabel}</span>
            <input type="range" min={0.5} max={0.72} step={0.01} value={prefs.swing} onChange={(e) => set({ swing: Number(e.target.value) })} />
          </label>
          {(['keys', 'bass', 'drums'] as Part[]).map((part) => (
            <label key={part}>
              <span>{part === 'keys' ? 'Chords' : part === 'bass' ? 'Bass' : 'Drums'} level</span>
              <input
                type="range"
                min={0}
                max={1.6}
                step={0.05}
                value={prefs.levels[part]}
                onChange={(e) => set({ levels: { ...prefs.levels, [part]: Number(e.target.value) } })}
              />
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
