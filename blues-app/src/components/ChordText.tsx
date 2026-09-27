import { splitRefs, type View } from '../music/display.ts';

/** Prose with {{chord}} references shown in the reader's key and notation. */
export function ChordText({ text, view, showRoman }: { text: string; view: View; showRoman: boolean }) {
  return (
    <>
      {splitRefs(text).map((part, i) => {
        if (!part.chords) return <span key={i}>{part.text}</span>;
        const chords = view.bar(part.chords);
        return (
          <span key={i} className="chord-ref" title={chords.map((c) => c.roman).join(' ')}>
            {chords.map((c, j) => (
              <span key={j} className={`q-${c.quality}`}>
                {j > 0 ? ' ' : ''}
                {c.symbol}
              </span>
            ))}
            {showRoman && <span className="chord-ref-roman"> ({chords.map((c) => c.roman).join(' ')})</span>}
          </span>
        );
      })}
    </>
  );
}
