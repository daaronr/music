import { useState } from 'react';
import { motion } from 'framer-motion';
import { bluesVariations } from '../data/bluesProgressions';

interface BluesFlowchartProps {
  currentBar: number;
  selectedVariation: number;
}

// Get muted color class for chord type
function getChordColorClass(chord: string, isActive: boolean = false): string {
  const c = chord.split(" ")[0].split("/")[0];
  const opacity = isActive ? '' : '/40';

  if (c === "I7" || c === "Imaj" || c === "I") return `bg-slate-600${opacity} text-slate-200`;
  if (c.includes("IV") || c === "iv-" || c === "iv°7") return `bg-amber-800${opacity} text-amber-100`;
  if (c.includes("V") || c.includes("II") || c.includes("VII")) return `bg-red-800${opacity} text-red-100`;
  if (c.includes("vi") || c.includes("iii") || c.includes("ii") || c.includes("v-") || c.includes("i-")) return `bg-indigo-800${opacity} text-indigo-100`;
  if (c.includes("°") || c.includes("dim")) return `bg-slate-500${opacity} text-slate-200`;
  if (c.includes("♭") || c.includes("#")) return `bg-pink-800${opacity} text-pink-100`;

  return `bg-slate-600${opacity} text-slate-200`;
}

// Build the flowchart data: for each bar, get all unique chords and which variations use them
function buildFlowchartData() {
  const data: Array<{ bar: number; options: Array<{ chord: string; variations: number[] }> }> = [];

  for (let bar = 0; bar < 12; bar++) {
    const chordMap = new Map<string, number[]>();

    bluesVariations.forEach(v => {
      const chord = v.chords[bar];
      if (!chordMap.has(chord)) {
        chordMap.set(chord, []);
      }
      chordMap.get(chord)!.push(v.id);
    });

    // Sort by most common first
    const options = Array.from(chordMap.entries())
      .sort((a, b) => b[1].length - a[1].length)
      .map(([chord, variations]) => ({ chord, variations }));

    data.push({ bar: bar + 1, options });
  }

  return data;
}

const flowchartData = buildFlowchartData();

export function BluesFlowchart({ currentBar, selectedVariation }: BluesFlowchartProps) {
  const [viewMode, setViewMode] = useState<'path' | 'flowchart'>('flowchart');

  const variation = bluesVariations.find(v => v.id === selectedVariation);
  if (!variation) return null;

  const currentPath = variation.chords;

  return (
    <div className="bg-slate-800/30 rounded-md p-4 border border-slate-800">
      {/* View toggle */}
      <div className="flex items-center justify-between mb-3">
        <div className="text-xs text-slate-500 uppercase tracking-wide">
          {viewMode === 'path' ? 'Current Path' : 'All Variations Flowchart'}
        </div>
        <div className="flex gap-1">
          <button
            onClick={() => setViewMode('path')}
            className={`px-2 py-1 text-[10px] rounded ${
              viewMode === 'path' ? 'bg-slate-600 text-slate-200' : 'bg-slate-800 text-slate-500 hover:text-slate-400'
            }`}
          >
            Path
          </button>
          <button
            onClick={() => setViewMode('flowchart')}
            className={`px-2 py-1 text-[10px] rounded ${
              viewMode === 'flowchart' ? 'bg-slate-600 text-slate-200' : 'bg-slate-800 text-slate-500 hover:text-slate-400'
            }`}
          >
            Flowchart
          </button>
        </div>
      </div>

      {viewMode === 'path' ? (
        <PathView currentBar={currentBar} currentPath={currentPath} />
      ) : (
        <FlowchartView currentBar={currentBar} selectedVariation={selectedVariation} currentPath={currentPath} />
      )}

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mt-4 pt-3 border-t border-slate-800 text-[10px] text-slate-500">
        <span><span className="inline-block w-2 h-2 rounded bg-slate-600 mr-1"></span>I</span>
        <span><span className="inline-block w-2 h-2 rounded bg-amber-800 mr-1"></span>IV</span>
        <span><span className="inline-block w-2 h-2 rounded bg-red-800 mr-1"></span>V/II/VII</span>
        <span><span className="inline-block w-2 h-2 rounded bg-indigo-800 mr-1"></span>Minor</span>
        <span><span className="inline-block w-2 h-2 rounded bg-pink-800 mr-1"></span>Chromatic</span>
      </div>
    </div>
  );
}

// Simple path view for current variation
function PathView({ currentBar, currentPath }: { currentBar: number; currentPath: string[] }) {
  const rows = [
    currentPath.slice(0, 4),
    currentPath.slice(4, 8),
    currentPath.slice(8, 12),
  ];

  return (
    <div className="space-y-2">
      {rows.map((row, rowIndex) => (
        <div key={rowIndex} className="flex gap-1.5">
          {row.map((chord, colIndex) => {
            const barIndex = rowIndex * 4 + colIndex;
            const isActive = currentBar === barIndex;

            return (
              <motion.div
                key={barIndex}
                className={`flex-1 px-2 py-2.5 rounded text-center text-xs font-medium ${getChordColorClass(chord, true)} ${
                  isActive ? 'ring-1 ring-slate-300' : 'opacity-70'
                }`}
              >
                <div className="text-[9px] opacity-60 mb-0.5">{barIndex + 1}</div>
                <div className="truncate">{chord}</div>
              </motion.div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

// Flowchart view showing all branching paths
function FlowchartView({
  currentBar,
  selectedVariation,
  currentPath
}: {
  currentBar: number;
  selectedVariation: number;
  currentPath: string[];
}) {
  // Group into rows of 4 bars
  const rows = [
    flowchartData.slice(0, 4),
    flowchartData.slice(4, 8),
    flowchartData.slice(8, 12),
  ];

  return (
    <div className="space-y-3">
      {rows.map((row, rowIndex) => (
        <div key={rowIndex} className="flex gap-2">
          {row.map((barData, colIndex) => {
            const barIndex = rowIndex * 4 + colIndex;
            const isCurrentBar = currentBar === barIndex;
            const activeChord = currentPath[barIndex];

            return (
              <div
                key={barIndex}
                className={`flex-1 rounded border ${
                  isCurrentBar ? 'border-slate-500 bg-slate-800/50' : 'border-slate-800'
                }`}
              >
                {/* Bar header */}
                <div className={`text-[9px] text-center py-1 border-b ${
                  isCurrentBar ? 'border-slate-600 text-slate-300' : 'border-slate-800 text-slate-600'
                }`}>
                  Bar {barData.bar}
                </div>

                {/* Chord options */}
                <div className="p-1.5 space-y-1">
                  {barData.options.map((option, optIndex) => {
                    const isActive = option.chord === activeChord;
                    const isOnPath = option.variations.includes(selectedVariation);

                    return (
                      <motion.div
                        key={optIndex}
                        className={`px-1.5 py-1 rounded text-[10px] font-medium text-center ${
                          getChordColorClass(option.chord, isOnPath)
                        } ${isActive && isCurrentBar ? 'ring-1 ring-slate-300' : ''} ${
                          !isOnPath ? 'opacity-30' : ''
                        }`}
                        animate={isActive && isCurrentBar ? { scale: [1, 1.02, 1] } : {}}
                        transition={{ repeat: Infinity, duration: 0.8 }}
                        title={`Variations: ${option.variations.join(', ')}`}
                      >
                        <div className="truncate">{option.chord}</div>
                        <div className="text-[8px] opacity-50 mt-0.5">
                          {option.variations.length === 18 ? 'all' : option.variations.length}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      ))}

      {/* Info text */}
      <div className="text-[10px] text-slate-600 text-center pt-2">
        Bright = variation {selectedVariation}'s path · Faded = other options · Number = how many variations use it
      </div>
    </div>
  );
}
