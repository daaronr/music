import { motion } from 'framer-motion';
import { getChordColor } from '../data/bluesProgressions';

interface BluesFlowchartProps {
  currentBar: number;
  selectedVariation: number;
}

// Flowchart data based on the original PDF - covers variations 1-9
// This shows all possible paths through the 12-bar blues
const flowchartData = [
  { bar: 1, chords: ["I7"] },
  { bar: 2, chords: ["I7", "IV7"] },
  { bar: 3, chords: ["I7"] },
  { bar: 4, chords: ["I7", "v- I7"] },
  { bar: 5, chords: ["IV7"] },
  { bar: 6, chords: ["IV7", "♭VII7", "#iv°7"] },
  { bar: 7, chords: ["I7", "iii-"] },
  { bar: 8, chords: ["I7", "VI7", "vi7"] },
  { bar: 9, chords: ["V7", "II7", "ii-7", "♭VI7"] },
  { bar: 10, chords: ["V7", "IV7"] },
  { bar: 11, chords: ["I7", "iii- VI7", "vi7"] },
  { bar: 12, chords: ["I7", "V7", "ii- V7", "♭VI7 V7"] },
];

// Which chord each variation uses at each bar (1-indexed for readability)
const variationPaths: Record<number, string[]> = {
  1: ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "V7", "I7", "I7"],
  2: ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
  3: ["I7", "IV7", "I7", "I7", "IV7", "IV7", "I7", "I7", "II7", "V7", "I7", "V7"],
  4: ["I7", "IV7", "I7", "I7", "IV7", "IV7", "I7", "VI7", "II7", "V7", "I7", "V7"],
  5: ["I7", "IV7", "I7", "I7", "IV7", "IV7", "I7", "VI7", "ii-7", "V7", "I7", "ii- V7"],
  6: ["I7", "IV7", "I7", "I7", "IV7", "♭VII7", "I7", "VI7", "♭VI7", "V7", "I7", "♭VI7 V7"],
  7: ["I7", "IV7", "I7", "v- I7", "IV7", "♭VII7", "I7", "iii- VI7", "ii-7", "V7", "iii- VI7", "ii- V7"],
  8: ["I7", "IV7", "I7", "v- I7", "IV7", "♭VII7", "iii-", "VI7", "ii-7", "V7", "iii- VI7", "ii- V7"],
  9: ["I7", "IV7", "I7", "v- I7", "IV7", "IV7", "I7", "vi7", "ii7", "V7", "vi7", "I7"],
};

export function BluesFlowchart({ currentBar, selectedVariation }: BluesFlowchartProps) {
  // Only show flowchart for variations 1-9
  const showFlowchart = selectedVariation >= 1 && selectedVariation <= 9;
  const currentPath = variationPaths[selectedVariation] || variationPaths[1];

  if (!showFlowchart) {
    return (
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-slate-300 mb-2">🎼 Blues Flowchart</h3>
        <p className="text-slate-500 text-sm">
          Flowchart available for variations 1-9 (dominant blues).
          Variations 10-18 use major 7ths and diminished chords with different structures.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <h3 className="text-xl font-bold text-slate-200 mb-4">🎼 12-Bar Blues Flowchart</h3>

      {/* Main flowchart grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {flowchartData.map((node, barIndex) => {
          const isCurrentBar = currentBar === barIndex;
          const activeChord = currentPath[barIndex];

          return (
            <div
              key={node.bar}
              className={`relative p-4 rounded-xl border-2 transition-all ${
                isCurrentBar
                  ? 'border-yellow-400 bg-yellow-400/10 shadow-lg shadow-yellow-400/20'
                  : 'border-slate-600 bg-slate-900/50'
              }`}
            >
              {/* Bar number header */}
              <div className={`text-center mb-3 pb-2 border-b ${
                isCurrentBar ? 'border-yellow-400/50' : 'border-slate-700'
              }`}>
                <span className={`text-lg font-bold ${
                  isCurrentBar ? 'text-yellow-400' : 'text-slate-400'
                }`}>
                  Bar {node.bar}
                </span>
              </div>

              {/* Chord choices */}
              <div className="flex flex-col gap-2">
                {node.chords.map((chord, chordIndex) => {
                  const isActive = chord === activeChord ||
                    (chord.includes(activeChord) || activeChord.includes(chord.split(' ')[0]));
                  const color = getChordColor(chord);

                  return (
                    <motion.div
                      key={chordIndex}
                      className={`px-4 py-3 rounded-lg text-center font-bold text-lg transition-all ${
                        isActive
                          ? 'ring-2 ring-white shadow-lg'
                          : 'opacity-30'
                      }`}
                      style={{
                        backgroundColor: isActive ? color : `${color}30`,
                        color: isActive ? 'white' : color,
                      }}
                      animate={isCurrentBar && isActive ? {
                        scale: [1, 1.05, 1],
                      } : {}}
                      transition={{ repeat: Infinity, duration: 0.6 }}
                    >
                      {chord}
                    </motion.div>
                  );
                })}
              </div>

              {/* Arrow indicator */}
              {barIndex < 11 && (
                <div className="absolute -right-3 top-1/2 transform -translate-y-1/2 text-slate-500 text-2xl hidden xl:block">
                  →
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Flow lines visualization for larger screens */}
      <div className="mt-6 p-4 bg-slate-900/50 rounded-lg hidden lg:block">
        <div className="text-sm text-slate-400 mb-3 font-semibold">Current Path (Variation {selectedVariation}):</div>
        <div className="flex flex-wrap items-center gap-2">
          {currentPath.map((chord, index) => {
            const isCurrentBar = currentBar === index;
            const color = getChordColor(chord);

            return (
              <div key={index} className="flex items-center">
                <motion.div
                  className={`px-3 py-2 rounded-lg font-bold ${
                    isCurrentBar ? 'ring-2 ring-yellow-400' : ''
                  }`}
                  style={{
                    backgroundColor: isCurrentBar ? color : `${color}60`,
                    color: 'white',
                  }}
                  animate={isCurrentBar ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ repeat: Infinity, duration: 0.5 }}
                >
                  <div className="text-xs opacity-70 mb-0.5">{index + 1}</div>
                  <div className="text-sm">{chord}</div>
                </motion.div>
                {index < 11 && (
                  <span className="text-slate-500 mx-1">→</span>
                )}
              </div>
            );
          })}
          <span className="text-slate-500 mx-1">↺</span>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-blue-500"></div>
          <span>Tonic (I)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-amber-500"></div>
          <span>Subdominant (IV)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-500"></div>
          <span>Dominant (V, II, VII)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-purple-500"></div>
          <span>Minor (ii, iii, vi)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-pink-500"></div>
          <span>Chromatic (♭VI)</span>
        </div>
      </div>

      <div className="mt-3 text-xs text-slate-500">
        Bright = active path for variation {selectedVariation} • Faded = other options
      </div>
    </div>
  );
}
