import { motion } from 'framer-motion';

interface ChordBoxProps {
  chord: string;
  barNumber: number;
  isActive: boolean;
  isPlayed: boolean;
  onClick: () => void;
}

// Muted color palette based on chord function
function getChordStyle(chord: string): { bg: string; border: string; text: string } {
  const c = chord.split(" ")[0].split("/")[0];

  // Tonic (I)
  if (c === "I7" || c === "Imaj" || c === "I") {
    return { bg: 'bg-slate-700', border: 'border-slate-600', text: 'text-slate-200' };
  }
  // Subdominant (IV, iv)
  if (c.includes("IV") || c === "iv-" || c === "iv°7") {
    return { bg: 'bg-slate-700', border: 'border-amber-700/50', text: 'text-amber-200/90' };
  }
  // Dominant (V, II, VII)
  if (c.includes("V") || c.includes("II") || c.includes("VII")) {
    return { bg: 'bg-slate-700', border: 'border-red-800/50', text: 'text-red-200/90' };
  }
  // Minor (ii, iii, vi, v, i)
  if (c.includes("vi") || c.includes("iii") || c.includes("ii") || c.includes("v-") || c.includes("i-")) {
    return { bg: 'bg-slate-700', border: 'border-indigo-700/50', text: 'text-indigo-200/90' };
  }
  // Diminished
  if (c.includes("°") || c.includes("dim")) {
    return { bg: 'bg-slate-700', border: 'border-slate-500', text: 'text-slate-300' };
  }
  // Chromatic (flats, sharps)
  if (c.includes("♭") || c.includes("#")) {
    return { bg: 'bg-slate-700', border: 'border-pink-800/50', text: 'text-pink-200/90' };
  }

  return { bg: 'bg-slate-700', border: 'border-slate-600', text: 'text-slate-200' };
}

export function ChordBox({ chord, barNumber, isActive, isPlayed, onClick }: ChordBoxProps) {
  const style = getChordStyle(chord);

  return (
    <motion.button
      onClick={onClick}
      className={`relative rounded-md p-2.5 cursor-pointer min-h-[60px] ${style.bg} border ${
        isActive ? 'border-slate-400 ring-1 ring-slate-400' : style.border
      } ${isActive ? 'opacity-100' : isPlayed ? 'opacity-80' : 'opacity-60'}`}
      whileHover={{ opacity: 1 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Bar number */}
      <div className="absolute top-1 left-1.5 text-[10px] text-slate-500 font-medium">
        {barNumber}
      </div>

      {/* Chord symbol */}
      <div className="pt-3 text-center">
        <span className={`text-sm font-semibold ${style.text}`}>
          {chord}
        </span>
      </div>

      {/* Active dot indicator */}
      {isActive && (
        <motion.div
          className="absolute bottom-1.5 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-slate-400"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 0.6 }}
        />
      )}
    </motion.button>
  );
}
