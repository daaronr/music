import { motion } from 'framer-motion';
import { bluesFlowchart, getChordColor } from '../data/bluesProgressions';

interface BluesFlowchartProps {
  currentBar: number;
  selectedVariation: number;
}

export function BluesFlowchart({ currentBar, selectedVariation }: BluesFlowchartProps) {
  return (
    <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 overflow-x-auto">
      <h3 className="text-lg font-semibold text-slate-300 mb-3">🎼 Blues Flowchart</h3>
      <div className="flex gap-1 min-w-max">
        {bluesFlowchart.map((node, barIndex) => {
          const isCurrentBar = currentBar === barIndex;
          // Find which choice applies to current variation
          const activeChoice = node.choices.find(c => c.variations.includes(selectedVariation));

          return (
            <div key={node.bar} className="flex flex-col items-center">
              {/* Bar number */}
              <div className={`text-xs mb-1 font-mono ${isCurrentBar ? 'text-white font-bold' : 'text-slate-500'}`}>
                {node.bar}
              </div>

              {/* Chord choices */}
              <div className="flex flex-col gap-1">
                {node.choices.map((choice, choiceIndex) => {
                  const isActive = activeChoice === choice;
                  const color = getChordColor(choice.chord);

                  return (
                    <motion.div
                      key={choiceIndex}
                      className={`px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${
                        isActive ? 'ring-2 ring-white' : 'opacity-40'
                      }`}
                      style={{
                        backgroundColor: isActive ? color : `${color}40`,
                        color: isActive ? 'white' : color,
                      }}
                      animate={isCurrentBar && isActive ? {
                        scale: [1, 1.05, 1],
                        boxShadow: [`0 0 0px ${color}`, `0 0 10px ${color}`, `0 0 0px ${color}`]
                      } : {}}
                      transition={{ repeat: Infinity, duration: 0.5 }}
                    >
                      {choice.chord}
                    </motion.div>
                  );
                })}
              </div>

              {/* Arrow to next bar */}
              {barIndex < 11 && (
                <div className="text-slate-600 text-xs mt-1">→</div>
              )}
              {barIndex === 11 && (
                <div className="text-slate-600 text-xs mt-1">↺</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
        <span>Highlighted = current variation path</span>
        <span>•</span>
        <span>Faded = alternative choices</span>
      </div>
    </div>
  );
}
