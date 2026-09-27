import { useMemo, useState } from 'react';
import { VARIATIONS } from '../music/progressions.ts';
import { FLOW, type View } from '../music/display.ts';

interface Props {
  bars: string[]; // the progression being played
  view: View;
  activeBar: number | null;
  selectedBar: number | null;
  onPick: (barIndex: number, bar: string) => void;
}

const COL_W = 108;
const NODE_W = 94;
const NODE_H = 30;
const GAP = 9;
const TOP = 24;
const PAD = 6;

const rows = Math.max(...FLOW.map((col) => col.length));
const WIDTH = PAD * 2 + 11 * COL_W + NODE_W;
const HEIGHT = TOP + rows * (NODE_H + GAP) + PAD;

const nodeX = (bar: number) => PAD + bar * COL_W;
const nodeY = (row: number) => TOP + row * (NODE_H + GAP);
const rowOf = (bar: number, text: string) => FLOW[bar].findIndex((o) => o.bar === text);

interface Edge {
  from: number;
  a: number;
  b: number;
  variations: number[];
}

const EDGES: Edge[] = (() => {
  const map = new Map<string, Edge>();
  for (const v of VARIATIONS)
    for (let i = 0; i < 11; i++) {
      const a = rowOf(i, v.bars[i]);
      const b = rowOf(i + 1, v.bars[i + 1]);
      const key = `${i}:${a}:${b}`;
      const e = map.get(key) ?? { from: i, a, b, variations: [] };
      e.variations.push(v.id);
      map.set(key, e);
    }
  return [...map.values()];
})();

function edgePath(from: number, a: number, b: number) {
  const x1 = nodeX(from) + NODE_W;
  const x2 = nodeX(from + 1);
  const y1 = nodeY(a) + NODE_H / 2;
  const y2 = nodeY(b) + NODE_H / 2;
  const c = (x2 - x1) * 0.55;
  return `M${x1},${y1} C${x1 + c},${y1} ${x2 - c},${y2} ${x2},${y2}`;
}

export function FlowChart({ bars, view, activeBar, selectedBar, onPick }: Props) {
  const [hover, setHover] = useState<{ bar: number; row: number } | null>(null);
  const pathRows = bars.map((b, i) => rowOf(i, b));
  const hoverSet = useMemo(() => (hover ? new Set(FLOW[hover.bar][hover.row].variations) : null), [hover]);

  return (
    <div className="flow">
      <div className="flow-scroll">
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} width={WIDTH} height={HEIGHT} role="img" aria-label="Every chord option for each bar, with lines for each of the 18 forms">
          {activeBar !== null && <rect className="flow-now" x={nodeX(activeBar) - 4} y={2} width={NODE_W + 8} height={HEIGHT - 4} rx={6} />}
          {selectedBar !== null && selectedBar !== activeBar && (
            <rect className="flow-sel" x={nodeX(selectedBar) - 4} y={2} width={NODE_W + 8} height={HEIGHT - 4} rx={6} />
          )}
          {FLOW.map((_, i) => (
            <text key={i} className="flow-head" x={nodeX(i) + NODE_W / 2} y={15} textAnchor="middle">
              {i + 1}
            </text>
          ))}
          <g className="flow-edges">
            {EDGES.map((e) => {
              const lit = hoverSet ? e.variations.some((v) => hoverSet.has(v)) : false;
              return (
                <path
                  key={`${e.from}:${e.a}:${e.b}`}
                  d={edgePath(e.from, e.a, e.b)}
                  className={lit ? 'edge is-lit' : hoverSet ? 'edge is-dim' : 'edge'}
                  strokeWidth={1 + e.variations.length * 0.45}
                />
              );
            })}
          </g>
          <g className="flow-path">
            {pathRows.slice(0, 11).map((a, i) => {
              const b = pathRows[i + 1];
              if (a < 0 || b < 0) return null;
              const exists = EDGES.some((e) => e.from === i && e.a === a && e.b === b);
              return <path key={i} d={edgePath(i, a, b)} className={exists ? 'path' : 'path is-new'} />;
            })}
          </g>
          {FLOW.map((col, i) =>
            col.map((opt, j) => {
              const chords = view.bar(opt.bar);
              const onPath = pathRows[i] === j;
              const lit = hoverSet ? opt.variations.some((v) => hoverSet.has(v)) : false;
              const q = chords.length === 1 ? chords[0].quality : 'mixed';
              return (
                <g
                  key={`${i}:${j}`}
                  className={['node', `q-${q}`, onPath && 'on-path', lit && 'is-lit', hoverSet && !lit && 'is-dim'].filter(Boolean).join(' ')}
                  transform={`translate(${nodeX(i)},${nodeY(j)})`}
                  onMouseEnter={() => setHover({ bar: i, row: j })}
                  onMouseLeave={() => setHover(null)}
                  onClick={() => onPick(i, opt.bar)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(ev) => {
                    if (ev.key === 'Enter' || ev.key === ' ') {
                      ev.preventDefault();
                      onPick(i, opt.bar);
                    }
                  }}
                  aria-label={`Bar ${i + 1}: ${chords.map((c) => c.symbol).join(' ')}. Used in form${opt.variations.length > 1 ? 's' : ''} ${opt.variations.join(', ')}.`}
                >
                  <title>{`Bar ${i + 1}: used in form${opt.variations.length > 1 ? 's' : ''} ${opt.variations.join(', ')}. Click to use it.`}</title>
                  <rect width={NODE_W} height={NODE_H} rx={5} />
                  <text x={NODE_W / 2} y={NODE_H / 2 + 4.5} textAnchor="middle">
                    {chords.map((c) => c.symbol).join(' ')}
                  </text>
                  <text className="node-count" x={NODE_W - 4} y={9} textAnchor="end">
                    {opt.variations.length}
                  </text>
                </g>
              );
            }),
          )}
        </svg>
      </div>
      <p className="hint">
        Each column lists every chord the chart uses in that bar, simplest at the top; the small number is how many of the 18
        forms use it. Lines join consecutive bars of a form, thicker where forms share them. Hover a chord to trace the forms
        that use it, and click it to swap it into the progression you are playing. A dashed line is a join no form on the chart
        uses.
      </p>
    </div>
  );
}
