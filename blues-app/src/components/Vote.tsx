import { useEffect, useState } from 'react';
import { VARIATIONS } from '../music/progressions.ts';
import { getResults, sendVote, track, type Results, type VoteInput } from '../api.ts';

const USES: Array<[string, string]> = [
  ['learn', 'Learning the changes'],
  ['practice', 'Practising / playing along'],
  ['teach', 'Teaching'],
  ['listen', 'Just listening'],
  ['other', 'Something else'],
];

const SAVED = 'bf-my-vote';

function loadSaved(): VoteInput | null {
  try {
    return JSON.parse(localStorage.getItem(SAVED) ?? 'null');
  } catch {
    return null;
  }
}

export function Vote({ currentId }: { currentId: number }) {
  const [mine, setMine] = useState<VoteInput | null>(loadSaved);
  const [editing, setEditing] = useState(!mine);
  const [fav, setFav] = useState(mine?.fav ?? currentId);
  const [also, setAlso] = useState<number[]>(mine?.also ?? []);
  const [use, setUse] = useState(mine?.use ?? '');
  const [instrument, setInstrument] = useState(mine?.instrument ?? '');
  const [comment, setComment] = useState(mine?.comment ?? '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Results | null>(null);

  useEffect(() => {
    if (mine && !editing) getResults().then(setResults, () => setResults(null));
  }, [mine, editing]);

  const toggleAlso = (id: number) =>
    setAlso((xs) => (xs.includes(id) ? xs.filter((x) => x !== id) : xs.length >= 3 ? xs : [...xs, id]));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const vote = { fav, also: also.filter((a) => a !== fav), use, instrument, comment };
    try {
      await sendVote(vote);
      try {
        localStorage.setItem(SAVED, JSON.stringify(vote));
      } catch {
        /* fine: results still show this visit */
      }
      track('vote', String(fav));
      setMine(vote);
      setEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'That did not go through. Try again?');
    } finally {
      setBusy(false);
    }
  };

  if (!editing && mine) {
    const max = results ? Math.max(1, ...results.fav) : 1;
    return (
      <section className="panel vote" aria-labelledby="vote-h">
        <h2 id="vote-h">Favourite forms</h2>
        <p>
          Thanks. You picked <strong>{mine.fav}. {VARIATIONS[mine.fav - 1].name}</strong>.{' '}
          <button className="link" onClick={() => setEditing(true)}>
            Change my vote
          </button>
        </p>
        {!results ? (
          <p className="hint">Loading results…</p>
        ) : (
          <>
            <p className="hint">
              {results.n} {results.n === 1 ? 'person has' : 'people have'} voted. Bars count favourites; the number in brackets counts
              "also like".
            </p>
            <ol className="bars" aria-label="Favourite votes per form">
              {VARIATIONS.map((v, i) => (
                <li key={v.id} className={v.id === mine.fav ? 'is-mine' : undefined} title={`${results.fav[i]} favourite, ${results.also[i]} also like`}>
                  <span className="bar-label">
                    <span className="num">{v.id}</span> {v.name}
                  </span>
                  <span className="bar-track">
                    <span className="bar-fill" style={{ width: `${(results.fav[i] / max) * 100}%` }} />
                  </span>
                  <span className="bar-value">
                    {results.fav[i]}
                    {results.also[i] > 0 && <span className="also"> ({results.also[i]})</span>}
                  </span>
                </li>
              ))}
            </ol>
          </>
        )}
      </section>
    );
  }

  return (
    <section className="panel vote" aria-labelledby="vote-h">
      <h2 id="vote-h">Which form do you like best?</h2>
      <p className="hint">Vote to see how everyone else voted. One vote per browser; you can change it later.</p>
      <form onSubmit={submit} className="vote-form">
        <label>
          <span>Favourite</span>
          <select value={fav} onChange={(e) => setFav(Number(e.target.value))}>
            {VARIATIONS.map((v) => (
              <option key={v.id} value={v.id}>
                {v.id}. {v.name}
              </option>
            ))}
          </select>
        </label>
        <fieldset>
          <legend>Also like (up to 3, optional)</legend>
          <div className="chips">
            {VARIATIONS.filter((v) => v.id !== fav).map((v) => (
              <button
                type="button"
                key={v.id}
                className={`chip${also.includes(v.id) ? ' on' : ''}`}
                aria-pressed={also.includes(v.id)}
                onClick={() => toggleAlso(v.id)}
                title={v.name}
              >
                {v.id}
              </button>
            ))}
          </div>
        </fieldset>
        <fieldset>
          <legend>What are you using this for? (optional)</legend>
          <div className="chips">
            {USES.map(([k, label]) => (
              <button type="button" key={k} className={`chip${use === k ? ' on' : ''}`} aria-pressed={use === k} onClick={() => setUse(use === k ? '' : k)}>
                {label}
              </button>
            ))}
          </div>
        </fieldset>
        <label>
          <span>Your instrument (optional)</span>
          <input type="text" value={instrument} maxLength={60} onChange={(e) => setInstrument(e.target.value)} />
        </label>
        <label>
          <span>Anything to add? (optional; only David sees this)</span>
          <textarea rows={2} value={comment} maxLength={1500} onChange={(e) => setComment(e.target.value)} />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="primary" type="submit" disabled={busy}>
          {busy ? 'Sending…' : 'Vote and see results'}
        </button>
      </form>
    </section>
  );
}
