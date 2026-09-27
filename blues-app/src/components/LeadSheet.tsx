import type { View } from '../music/display.ts';

interface Props {
  bars: string[];
  view: View;
  changed: boolean[];
  showRoman: boolean;
  showGuide: boolean;
  activeBar: number | null;
  activeBeat: number | null;
  selectedBar: number | null;
  onBar: (index: number) => void;
}

export function LeadSheet({ bars, view, changed, showRoman, showGuide, activeBar, activeBeat, selectedBar, onBar }: Props) {
  return (
    <div className="sheet" role="list" aria-label="Twelve bars">
      {bars.map((bar, i) => {
        const chords = view.bar(bar);
        const active = activeBar === i;
        const half = active && activeBeat !== null && chords.length === 2 ? (activeBeat < 2 ? 0 : 1) : null;
        return (
          <button
            key={i}
            role="listitem"
            className={['bar', active && 'is-active', changed[i] && 'is-changed', selectedBar === i && 'is-selected']
              .filter(Boolean)
              .join(' ')}
            onClick={() => onBar(i)}
            aria-label={`Bar ${i + 1}: ${chords.map((c) => c.symbol).join(', ')}${changed[i] ? ' (changed)' : ''}`}
          >
            <span className="bar-num">{i + 1}</span>
            {changed[i] && <span className="bar-changed" title="Different from the form it is compared with" />}
            <span className={`bar-chords n${chords.length}`}>
              {chords.map((c, j) => (
                <span key={j} className={`chord q-${c.quality}${half === j ? ' is-sounding' : ''}`}>
                  <span className="sym">{c.symbol}</span>
                  {showRoman && <span className="roman">{c.roman}</span>}
                  {showGuide && <span className="guide">{c.guide.map((g) => g.name).join(' ')}</span>}
                </span>
              ))}
            </span>
            <span className="beats" aria-hidden="true">
              {[0, 1, 2, 3].map((b) => (
                <span key={b} className={active && activeBeat !== null && b <= activeBeat ? 'on' : ''} />
              ))}
            </span>
          </button>
        );
      })}
    </div>
  );
}
