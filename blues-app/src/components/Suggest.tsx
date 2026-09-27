import { useMemo, useState } from 'react';
import { sendNote, track } from '../api.ts';
import type { View } from '../music/display.ts';
import { parseTypedBar } from '../music/parse.ts';
import { TRANSPOSITIONS, chartString } from '../music/theory.ts';

interface Props {
  bars: string[]; // what's on screen (chart spelling)
  view: View;
  context: string;
  onTry: (chartBars: string[]) => void;
}

const shown = (view: View, bars: string[]) => bars.map((b) => view.bar(b).map((c) => c.symbol).join(' '));

export function Suggest({ bars, view, context, onTry }: Props) {
  const [typed, setTyped] = useState<string[]>(() => shown(view, bars));
  const [formName, setFormName] = useState('');
  const [why, setWhy] = useState('');
  const [source, setSource] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [creditOk, setCreditOk] = useState(false);
  const [website, setWebsite] = useState('');
  const [state, setState] = useState<'idle' | 'busy' | 'done'>('idle');
  const [error, setError] = useState<string | null>(null);

  const parsed = useMemo(() => typed.map((t) => parseTypedBar(t, view.dk.iv)), [typed, view]);
  const problems = parsed.map((p, i) => (typeof p === 'string' ? `Bar ${i + 1}: ${p}` : null)).filter(Boolean) as string[];
  const chartBars = problems.length ? null : parsed.map((p) => (p as Exclude<typeof p, string>).map(chartString).join(' '));
  const typedIn = view.opts.romanOnly
    ? 'roman numerals (or letters)'
    : view.opts.transposition === 'C'
      ? `the key of ${view.dk.name.replace('b', '♭')}`
      : `${TRANSPOSITIONS[view.opts.transposition].label}, written key of ${view.dk.name.replace('b', '♭')}`;

  const setBar = (i: number, v: string) => setTyped((xs) => xs.map((x, k) => (k === i ? v : x)));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chartBars) return;
    setState('busy');
    setError(null);
    try {
      await sendNote({ kind: 'suggestion', formName, bars: typed, chartBars, typedIn, source, message: why, name, email, creditOk, context, website });
      track('suggestion');
      setState('done');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'That did not go through.');
      setState('idle');
    }
  };

  return (
    <section className="panel suggest" id="suggest" aria-labelledby="suggest-h">
      <h2 id="suggest-h">Suggest a new form</h2>
      {state === 'done' ? (
        <p className="thanks">
          Thanks! I'll have a listen, and if it earns a place I'll add it (with credit, if you ticked the box).{' '}
          <button className="link" onClick={() => setState('idle')}>
            Suggest another
          </button>
        </p>
      ) : (
        <>
          <p>
            Know a blues form that isn't here (from a tune, a book, a teacher, or your own head)? Outline it below. It starts as
            the progression on screen; change any bars. Type chords in {typedIn}, e.g. <code>C7</code> <code>Fm7</code>{' '}
            <code>B♭maj7</code> <code>E°</code> <code>Gm7♭5</code>, or roman numerals like <code>ii−7 V7</code>. Two chords in a bar
            get two beats each.
          </p>
          <div className="suggest-grid">
            {typed.map((t, i) => (
              <label key={i} className={typeof parsed[i] === 'string' ? 'bad' : undefined}>
                <span>{i + 1}</span>
                <input type="text" value={t} spellCheck={false} autoCapitalize="off" onChange={(e) => setBar(i, e.target.value)} aria-label={`Bar ${i + 1}`} />
              </label>
            ))}
          </div>
          {problems.length > 0 && <p className="error">{problems.join(' · ')}</p>}
          <div className="suggest-actions">
            <button
              className="small"
              disabled={!chartBars}
              onClick={() => {
                if (!chartBars) return;
                onTry(chartBars);
                track('suggest-try');
              }}
            >
              Try it on the lead sheet
            </button>
            <button className="small" onClick={() => setTyped(shown(view, bars))}>
              Start again from what's on screen
            </button>
          </div>
          <form className="note-form" onSubmit={submit}>
            <label>
              <span>A name for it</span>
              <input type="text" required maxLength={80} value={formName} onChange={(e) => setFormName(e.target.value)} />
            </label>
            <label>
              <span>What makes it different, or why it works (optional)</span>
              <textarea rows={3} maxLength={3000} value={why} onChange={(e) => setWhy(e.target.value)} />
            </label>
            <label>
              <span>Where it comes from: a tune, recording, book or teacher (optional)</span>
              <input type="text" maxLength={300} value={source} onChange={(e) => setSource(e.target.value)} />
            </label>
            <div className="row">
              <label>
                <span>Your name (optional)</span>
                <input type="text" maxLength={100} autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} />
              </label>
              <label>
                <span>Email (optional, if you want a reply)</span>
                <input type="email" maxLength={160} autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </label>
            </div>
            <label className="check">
              <input type="checkbox" checked={creditOk} onChange={(e) => setCreditOk(e.target.checked)} /> If it's added, credit me by name
            </label>
            <label className="hp" aria-hidden="true">
              Leave this empty <input type="text" tabIndex={-1} autoComplete="off" value={website} onChange={(e) => setWebsite(e.target.value)} />
            </label>
            {error && <p className="error">{error}</p>}
            <button className="primary" type="submit" disabled={!chartBars || state === 'busy'}>
              {state === 'busy' ? 'Sending…' : 'Send the suggestion'}
            </button>
            <p className="hint">Only David sees these.</p>
          </form>
        </>
      )}
    </section>
  );
}
