import { motion } from 'framer-motion';
import { bluesVariations } from '../data/bluesProgressions';

interface BluesFlowchartProps {
  currentBar: number;
  selectedVariation: number;
}

// Get muted color class for chord type
function getChordColorClass(chord: string): string {
  const c = chord.split(" ")[0].split("/")[0];

  if (c === "I7" || c === "Imaj" || c === "I") return 'bg-slate-600 text-slate-200';
  if (c.includes("IV") || c === "iv-" || c === "iv°7") return 'bg-amber-900/60 text-amber-200';
  if (c.includes("V") || c.includes("II") || c.includes("VII")) return 'bg-red-900/60 text-red-200';
  if (c.includes("vi") || c.includes("iii") || c.includes("ii") || c.includes("v-") || c.includes("i-")) return 'bg-indigo-900/60 text-indigo-200';
  if (c.includes("°") || c.includes("dim")) return 'bg-slate-600 text-slate-300';
  if (c.includes("♭") || c.includes("#")) return 'bg-pink-900/60 text-pink-200';

  return 'bg-slate-600 text-slate-200';
}

export function BluesFlowchart({ currentBar, selectedVariation }: BluesFlowchartProps) {
  const variation = bluesVariations.find(v => v.id === selectedVariation);
  if (!variation) return null;

  const chords = variation.chords;

  // Group into 4 rows of 3 bars (like sheet music)
  const rows = [
    chords.slice(0, 4),   // Bars 1-4
    chords.slice(4, 8),   // Bars 5-8
    chords.slice(8, 12),  // Bars 9-12
  ];

  return (
    <div className="bg-slate-800/30 rounded-md p-4 border border-slate-800">
      <div className="text-xs text-slate-500 mb-3 uppercase tracking-wide">Chord Path</div>

      {/* 3 rows of 4 bars */}
      <div className="space-y-2">
        {rows.map((row, rowIndex) => (
          <div key={rowIndex} className="flex gap-1.5">
            {row.map((chord, colIndex) => {
              const barIndex = rowIndex * 4 + colIndex;
              const isActive = currentBar === barIndex;
              const colorClass = getChordColorClass(chord);

              return (
                <motion.div
                  key={barIndex}
                  className={`flex-1 px-2 py-2.5 rounded text-center text-xs font-medium ${colorClass} ${
                    isActive ? 'ring-1 ring-slate-400' : 'opacity-70'
                  }`}
                  animate={isActive ? { opacity: 1 } : {}}
                >
                  <div className="text-[9px] text-slate-400 mb-0.5">{barIndex + 1}</div>
                  <div className="truncate">{chord}</div>
                </motion.div>
              );
            })}

            {/* Row connector */}
            {rowIndex < 2 && (
              <div className="flex items-center text-slate-600 text-xs px-1">↓</div>
            )}
          </div>
        ))}
      </div>

      {/* Simple legend */}
      <div className="flex flex-wrap gap-3 mt-4 pt-3 border-t border-slate-800 text-[10px] text-slate-500">
        <span><span className="inline-block w-2 h-2 rounded bg-slate-600 mr-1"></span>I (Tonic)</span>
        <span><span className="inline-block w-2 h-2 rounded bg-amber-900/60 mr-1"></span>IV</span>
        <span><span className="inline-block w-2 h-2 rounded bg-red-900/60 mr-1"></span>V/II</span>
        <span><span className="inline-block w-2 h-2 rounded bg-indigo-900/60 mr-1"></span>Minor</span>
        <span><span className="inline-block w-2 h-2 rounded bg-pink-900/60 mr-1"></span>Chromatic</span>
      </div>
    </div>
  );
}
