import { VARIATIONS } from '../music/progressions.ts';
import type { View } from '../music/display.ts';

interface Props {
  view: View;
  currentId: number | null;
  activeBar: number | null;
  onSelect: (id: number) => void;
}

export function ChartTable({ view, currentId, activeBar, onSelect }: Props) {
  return (
    <div className="table-scroll">
      <table className="chart-table">
        <thead>
          <tr>
            <th scope="col" className="name-col">
              Form
            </th>
            {Array.from({ length: 12 }, (_, i) => (
              <th key={i} scope="col" className={activeBar === i ? 'is-now' : undefined}>
                {i + 1}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {VARIATIONS.map((v, row) => (
            <tr key={v.id} className={v.id === currentId ? 'is-current' : undefined} onClick={() => onSelect(v.id)}>
              <th scope="row" className="name-col">
                <button onClick={() => onSelect(v.id)}>
                  <span className="num">{v.id}</span> {v.name}
                </button>
              </th>
              {v.bars.map((bar, i) => {
                const changed = row > 0 && VARIATIONS[row - 1].bars[i] !== bar;
                return (
                  <td key={i} className={[changed && 'is-changed', activeBar === i && 'is-now'].filter(Boolean).join(' ') || undefined}>
                    {view.bar(bar).map((c, j) => (
                      <span key={j} className={`q-${c.quality}`}>
                        {j > 0 ? ' ' : ''}
                        {c.symbol}
                      </span>
                    ))}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="hint">The chart as printed, in your chosen key. Bold cells differ from the row above.</p>
    </div>
  );
}
