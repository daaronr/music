import { VARIATIONS, type Variation } from '../music/progressions.ts';
import { sourcesOf, type View } from '../music/display.ts';
import { SCALE_HINT, TRANSPOSITIONS, chordTones } from '../music/theory.ts';
import { ChordText } from './ChordText.tsx';

interface Props {
  variation: Variation;
  mix: string[] | null;
  bars: string[];
  view: View;
  showRoman: boolean;
  selectedBar: number | null;
  onSelectBar: (i: number) => void;
  onHear: (i: number) => void;
  onGoTo: (id: number) => void;
}

function formList(ids: number[]) {
  if (ids.length === 18) return 'all 18 forms';
  const parts: string[] = [];
  for (let i = 0; i < ids.length; i++) {
    let j = i;
    while (j + 1 < ids.length && ids[j + 1] === ids[j] + 1) j++;
    parts.push(j > i + 1 ? `${ids[i]}–${ids[j]}` : j === i + 1 ? `${ids[i]}, ${ids[j]}` : `${ids[i]}`);
    i = j;
  }
  return `form${ids.length > 1 ? 's' : ''} ${parts.join(', ')}`;
}

export function Notes({ variation, mix, bars, view, showRoman, selectedBar, onSelectBar, onHear, onGoTo }: Props) {
  const noteEntries = mix ? [] : Object.entries(variation.notes).map(([bar, text]) => [Number(bar), text] as const);
  const sel = selectedBar !== null ? view.bar(bars[selectedBar]) : null;
  const selSources = selectedBar !== null ? sourcesOf(selectedBar, bars[selectedBar]) : [];

  return (
    <section className="notes" aria-label="About this progression">
      {mix ? (
        <>
          <h2>Your mix</h2>
          <p>
            Built on form {variation.id} ({variation.name}). Bars that differ from it are marked. The chart itself notes that
            its rows can be combined; some joins work better than others, so trust your ears. Think it deserves a place on the
            list? <a
              href="#suggest"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById('suggest')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Suggest it as a new form
            </a>.
          </p>
          <ul className="bar-notes">
            {mix.map((bar, i) =>
              bar !== variation.bars[i] ? (
                <li key={i}>
                  <button className="link" onClick={() => onSelectBar(i)}>
                    Bar {i + 1}
                  </button>{' '}
                  <ChordText text={`{{${bar}}}`} view={view} showRoman={showRoman} />{' '}
                  {sourcesOf(i, bar).length ? `from ${formList(sourcesOf(i, bar))}` : '(not on the chart)'}
                </li>
              ) : null,
            )}
          </ul>
        </>
      ) : (
        <>
          <h2>
            <span className="num">{variation.id}</span> {variation.name}
          </h2>
          <p>
            <ChordText text={variation.summary} view={view} showRoman={showRoman} />
          </p>
          {noteEntries.length > 0 && (
            <ul className="bar-notes">
              {noteEntries.map(([bar, text]) => (
                <li key={bar}>
                  <button className="link" onClick={() => onSelectBar(bar - 1)}>
                    Bar {bar}
                  </button>{' '}
                  <ChordText text={text} view={view} showRoman={showRoman} />
                </li>
              ))}
            </ul>
          )}
        </>
      )}

      {sel && selectedBar !== null && (
        <div className="detail">
          <div className="detail-head">
            <h3>Bar {selectedBar + 1}</h3>
            <button className="small" onClick={() => onHear(selectedBar)}>
              Hear it
            </button>
          </div>
          {sel.map((c, i) => (
            <div key={i} className="detail-chord">
              <div>
                <span className={`detail-sym q-${c.quality}`}>{c.symbol}</span> <span className="roman">{c.roman}</span>
              </div>
              <dl>
                <dt>Chord tones</dt>
                <dd>
                  {chordTones(c.shown, view.dk.preferFlats).map((t, k) => (
                    <span key={k} className="tone">
                      {t.name}
                      <sub>{t.degree}</sub>
                    </span>
                  ))}
                </dd>
                <dt>Guide tones</dt>
                <dd>{c.guide.map((g) => `${g.name} (${g.degree})`).join(', ')}</dd>
                <dt>Scale</dt>
                <dd>{SCALE_HINT[c.quality]}</dd>
              </dl>
            </div>
          ))}
          <p className="detail-sources">
            {selSources.length ? `Used in ${formList(selSources)}.` : 'Not on the chart.'}{' '}
            {selSources
              .filter((id) => id !== variation.id)
              .slice(0, 6)
              .map((id) => (
                <button key={id} className="chip" onClick={() => onGoTo(id)} title={VARIATIONS[id - 1].name}>
                  {id}
                </button>
              ))}
          </p>
          {view.opts.transposition !== 'C' && (
            <p className="hint">
              Written for {TRANSPOSITIONS[view.opts.transposition].label} (key of {view.dk.name.replace('b', '♭')}); the audio stays at
              concert pitch.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
