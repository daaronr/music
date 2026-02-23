import { motion } from 'framer-motion';
import { getChordColor } from '../data/bluesProgressions';

interface ChordBoxProps {
  chord: string;
  barNumber: number;
  isActive: boolean;
  isPlayed: boolean;
  onClick: () => void;
}

export function ChordBox({ chord, barNumber, isActive, isPlayed, onClick }: ChordBoxProps) {
  const bgColor = getChordColor(chord);

  return (
    <motion.button
      onClick={onClick}
      className="relative rounded-xl p-3 cursor-pointer overflow-hidden"
      style={{
        backgroundColor: isActive ? bgColor : isPlayed ? `${bgColor}99` : `${bgColor}40`,
        border: `3px solid ${bgColor}`,
        boxShadow: isActive ? `0 0 30px ${bgColor}80, 0 0 60px ${bgColor}40` : 'none',
      }}
      whileHover={{ scale: 1.05, y: -2 }}
      whileTap={{ scale: 0.95 }}
      animate={{
        scale: isActive ? [1, 1.02, 1] : 1,
      }}
      transition={{
        scale: { repeat: isActive ? Infinity : 0, duration: 0.5 }
      }}
    >
      {/* Bar number badge */}
      <div
        className="absolute top-1 left-1 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold"
        style={{ backgroundColor: bgColor, color: 'white' }}
      >
        {barNumber}
      </div>

      {/* Chord symbol */}
      <div className="pt-4 text-center">
        <span
          className="text-xl font-bold tracking-tight"
          style={{ color: isActive || isPlayed ? 'white' : bgColor }}
        >
          {chord}
        </span>
      </div>

      {/* Active indicator */}
      {isActive && (
        <motion.div
          className="absolute inset-0 rounded-xl"
          style={{ border: `3px solid white` }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 0.8 }}
        />
      )}

      {/* Musical note decoration */}
      {isActive && (
        <motion.div
          className="absolute -top-2 -right-2 text-2xl"
          animate={{
            rotate: [0, 10, -10, 0],
            y: [0, -5, 0]
          }}
          transition={{ repeat: Infinity, duration: 0.5 }}
        >
          ♪
        </motion.div>
      )}
    </motion.button>
  );
}
