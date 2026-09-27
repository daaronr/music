import { useState } from 'react';
import { LINKS, sendNote, track, type NoteInput } from '../api.ts';

function NoteForm({ kind, context }: { kind: 'feedback' | 'donation'; context: string }) {
  const [f, setF] = useState<NoteInput>({ kind, message: '', name: '', email: '', where: '', amount: '', creditOk: false, website: '' });
  const [state, setState] = useState<'idle' | 'busy' | 'done'>('idle');
  const [error, setError] = useState<string | null>(null);
  const set = (patch: Partial<NoteInput>) => setF((x) => ({ ...x, ...patch }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setState('busy');
    setError(null);
    try {
      await sendNote({ ...f, context });
      track(kind);
      setState('done');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'That did not go through.');
      setState('idle');
    }
  };

  if (state === 'done')
    return (
      <p className="thanks">
        {kind === 'donation'
          ? "Thank you, that's really kind. I'll be in touch if you left an email, and your suggestions go to the front of the queue."
          : 'Thanks, got it.'}{' '}
        <button className="link" onClick={() => { setState('idle'); set({ message: '' }); }}>
          Send another
        </button>
      </p>
    );

  return (
    <form className="note-form" onSubmit={submit}>
      {kind === 'donation' && (
        <div className="row">
          <label>
            <span>Donated to</span>
            <select value={f.where} onChange={(e) => set({ where: e.target.value })} required>
              <option value="">Choose…</option>
              <option value="unjournal">The Unjournal</option>
              <option value="givewell">GiveWell / a GiveWell charity</option>
              <option value="other">Another effective charity</option>
            </select>
          </label>
          <label>
            <span>Amount (optional)</span>
            <input type="text" value={f.amount} maxLength={40} onChange={(e) => set({ amount: e.target.value })} />
          </label>
        </div>
      )}
      <label>
        <span>{kind === 'donation' ? 'Anything you want added or fixed? (optional)' : 'What works, what doesn’t, what’s missing?'}</span>
        <textarea rows={3} value={f.message} maxLength={3000} required={kind === 'feedback'} onChange={(e) => set({ message: e.target.value })} />
      </label>
      <div className="row">
        <label>
          <span>Name (optional)</span>
          <input type="text" value={f.name} maxLength={100} autoComplete="name" onChange={(e) => set({ name: e.target.value })} />
        </label>
        <label>
          <span>Email (optional, if you want a reply)</span>
          <input type="email" value={f.email} maxLength={160} autoComplete="email" onChange={(e) => set({ email: e.target.value })} />
        </label>
      </div>
      {kind === 'donation' && (
        <label className="check">
          <input type="checkbox" checked={f.creditOk} onChange={(e) => set({ creditOk: e.target.checked })} /> OK to thank me by name on this page
        </label>
      )}
      <label className="hp" aria-hidden="true">
        Leave this empty <input type="text" tabIndex={-1} autoComplete="off" value={f.website} onChange={(e) => set({ website: e.target.value })} />
      </label>
      {error && <p className="error">{error}</p>}
      <button className="primary" type="submit" disabled={state === 'busy'}>
        {state === 'busy' ? 'Sending…' : kind === 'donation' ? 'Let David know' : 'Send feedback'}
      </button>
      <p className="hint">Only David sees these. Nothing is shared or used for anything else.</p>
    </form>
  );
}

export function Support({ context }: { context: string }) {
  return (
    <section className="support" id="about" aria-label="About, feedback and support">
      <div className="panel">
        <h2>Who made this</h2>
        <p>
          I'm David Reinstein. I play tuba, trombone and flugelhorn, including with <a href={LINKS.kHouse}>K-House</a>, a jazz group in
          Exeter. This started from a printed chart of 18 blues progressions I wanted to get into my ears. You can hear me on{' '}
          <a href={LINKS.youtube}>YouTube</a>, including a <a href={LINKS.playlist}>tuba and flugelhorn playlist</a>.
        </p>
        <p className="hint">Claude (Anthropic's AI) did most of the coding, from my design and an earlier version.</p>
      </div>

      <div className="panel">
        <h2>Feedback</h2>
        <p>Found a wrong chord, a bug, or something you wish it did? Tell me. Or email {LINKS.email}.</p>
        <NoteForm kind="feedback" context={context} />
      </div>

      <div className="panel">
        <h2>If you find it useful</h2>
        <p>
          It's free. Rather than buying me a coffee, please consider a donation to{' '}
          <a href={LINKS.unjournalDonate} onClick={() => track('donate-click', 'unjournal')}>
            The Unjournal
          </a>{' '}
          (where I'm co-director; we commission open, public evaluations of research that matters for the world) or to{' '}
          <a href={LINKS.givewellDonate} onClick={() => track('donate-click', 'givewell')}>
            GiveWell's top charities
          </a>
          . This app isn't an Unjournal project; I'd just rather the goodwill went somewhere useful.
        </p>
        <p>If you do give, let me know below. I'll thank you, and your requests and suggestions for the app get priority.</p>
        <NoteForm kind="donation" context={context} />
      </div>
    </section>
  );
}
