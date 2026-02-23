import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as Tone from 'tone';
import { bluesVariations, parseChord } from '../data/bluesProgressions';
import type { BluesVariation } from '../data/bluesProgressions';
import { ChordBox } from './ChordBox';

export function BluesPlayer() {
  const [selectedVariation, setSelectedVariation] = useState<BluesVariation>(bluesVariations[0]);
  const [currentBar, setCurrentBar] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [tempo, setTempo] = useState(100);
  const [playedBars, setPlayedBars] = useState<Set<number>>(new Set());
  const [audioStarted, setAudioStarted] = useState(false);

  const synthRef = useRef<Tone.PolySynth | null>(null);
  const sequenceRef = useRef<Tone.Sequence | null>(null);

  // Initialize synth
  useEffect(() => {
    synthRef.current = new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: 'triangle' },
      envelope: {
        attack: 0.02,
        decay: 0.3,
        sustain: 0.4,
        release: 0.8,
      },
    }).toDestination();

    // Add some reverb for richness
    const reverb = new Tone.Reverb({ decay: 2, wet: 0.3 }).toDestination();
    synthRef.current.connect(reverb);

    return () => {
      synthRef.current?.dispose();
    };
  }, []);

  const startAudio = async () => {
    await Tone.start();
    setAudioStarted(true);
  };

  const playChord = useCallback((chord: string) => {
    if (!synthRef.current) return;
    const notes = parseChord(chord);
    synthRef.current.triggerAttackRelease(notes, '2n');
  }, []);

  const startPlaying = useCallback(() => {
    if (!audioStarted) return;

    Tone.getTransport().bpm.value = tempo;

    // Stop any existing sequence
    if (sequenceRef.current) {
      sequenceRef.current.dispose();
    }

    setPlayedBars(new Set());
    setCurrentBar(0);

    const chords = selectedVariation.chords;

    sequenceRef.current = new Tone.Sequence(
      (time, index) => {
        if (index < chords.length) {
          const notes = parseChord(chords[index]);
          synthRef.current?.triggerAttackRelease(notes, '2n', time);

          // Update state on the main thread
          Tone.getDraw().schedule(() => {
            setCurrentBar(index);
            setPlayedBars(prev => new Set([...prev, index]));
          }, time);
        }
      },
      Array.from({ length: chords.length }, (_, i) => i),
      '2n'
    ).start(0);

    // Stop after all bars
    Tone.getTransport().scheduleOnce(() => {
      setIsPlaying(false);
      setCurrentBar(-1);
    }, Tone.Time('2n').toSeconds() * chords.length);

    Tone.getTransport().start();
    setIsPlaying(true);
  }, [audioStarted, selectedVariation, tempo]);

  const stopPlaying = useCallback(() => {
    Tone.getTransport().stop();
    Tone.getTransport().cancel();
    if (sequenceRef.current) {
      sequenceRef.current.dispose();
      sequenceRef.current = null;
    }
    setIsPlaying(false);
    setCurrentBar(-1);
    setPlayedBars(new Set());
  }, []);

  const handleBarClick = (index: number) => {
    if (!audioStarted) return;
    playChord(selectedVariation.chords[index]);
    setCurrentBar(index);
    setPlayedBars(prev => new Set([...prev, index]));
  };

  const shuffleVariation = () => {
    const randomIndex = Math.floor(Math.random() * bluesVariations.length);
    stopPlaying();
    setSelectedVariation(bluesVariations[randomIndex]);
    setPlayedBars(new Set());
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-4 md:p-8">
      {/* Header */}
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
          🎸 Blues Flow
        </h1>
        <p className="text-slate-400 text-lg">Interactive 12-Bar Blues Explorer</p>
      </motion.div>

      {/* Audio start button (required for web audio) */}
      {!audioStarted && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
        >
          <motion.button
            onClick={startAudio}
            className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl text-2xl font-bold shadow-2xl"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            animate={{
              boxShadow: ['0 0 20px #3B82F6', '0 0 40px #8B5CF6', '0 0 20px #3B82F6'],
            }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            🎵 Start Playing
          </motion.button>
        </motion.div>
      )}

      {/* Variation Selector */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="mb-6"
      >
        <label className="block text-sm text-slate-400 mb-2">Choose Your Blues:</label>
        <div className="flex flex-wrap gap-2">
          <select
            value={selectedVariation.id}
            onChange={(e) => {
              const variation = bluesVariations.find(v => v.id === Number(e.target.value));
              if (variation) {
                stopPlaying();
                setSelectedVariation(variation);
                setPlayedBars(new Set());
              }
            }}
            className="flex-1 min-w-[200px] bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
          >
            {bluesVariations.map(v => (
              <option key={v.id} value={v.id}>
                #{v.id} - {v.name}
              </option>
            ))}
          </select>
          <motion.button
            onClick={shuffleVariation}
            className="px-4 py-3 bg-gradient-to-r from-pink-500 to-orange-500 rounded-xl font-semibold"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🎲 Shuffle
          </motion.button>
        </div>
      </motion.div>

      {/* Variation Info */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedVariation.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          className="mb-6 p-4 bg-slate-800/50 rounded-xl border border-slate-700"
        >
          <h2 className="text-2xl font-bold text-purple-300">{selectedVariation.name}</h2>
          <p className="text-slate-400 italic">{selectedVariation.description}</p>
        </motion.div>
      </AnimatePresence>

      {/* 12-Bar Grid */}
      <motion.div
        layout
        className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-12 gap-2 md:gap-3 mb-8"
      >
        <AnimatePresence mode="popLayout">
          {selectedVariation.chords.map((chord, index) => (
            <motion.div
              key={`${selectedVariation.id}-${index}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ delay: index * 0.05 }}
            >
              <ChordBox
                chord={chord}
                barNumber={index + 1}
                isActive={currentBar === index}
                isPlayed={playedBars.has(index)}
                onClick={() => handleBarClick(index)}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex flex-wrap items-center justify-center gap-4 mb-8"
      >
        {/* Play/Stop Button */}
        <motion.button
          onClick={isPlaying ? stopPlaying : startPlaying}
          className={`px-8 py-4 rounded-2xl text-xl font-bold shadow-lg ${
            isPlaying
              ? 'bg-gradient-to-r from-red-500 to-orange-500'
              : 'bg-gradient-to-r from-green-500 to-emerald-500'
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={!audioStarted}
        >
          {isPlaying ? '⏹ Stop' : '▶ Play All'}
        </motion.button>

        {/* Tempo Control */}
        <div className="flex items-center gap-3 bg-slate-800 px-4 py-3 rounded-xl">
          <span className="text-slate-400">🥁</span>
          <input
            type="range"
            min="60"
            max="180"
            value={tempo}
            onChange={(e) => {
              const newTempo = Number(e.target.value);
              setTempo(newTempo);
              Tone.getTransport().bpm.value = newTempo;
            }}
            className="w-24 accent-purple-500"
          />
          <span className="text-sm font-mono w-16">{tempo} BPM</span>
        </div>
      </motion.div>

      {/* Legend */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="flex flex-wrap justify-center gap-4 text-sm"
      >
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-blue-500" />
          <span className="text-slate-400">Tonic (I)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-amber-500" />
          <span className="text-slate-400">Subdominant (IV)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-500" />
          <span className="text-slate-400">Dominant (V, II, VII)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-purple-500" />
          <span className="text-slate-400">Minor (ii, iii, vi)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-pink-500" />
          <span className="text-slate-400">Chromatic</span>
        </div>
      </motion.div>

      {/* Fun footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="text-center mt-12 text-slate-500 text-sm"
      >
        <p>Click any chord to hear it • Explore all 18 variations!</p>
        <p className="mt-1">🎹 Built with love for the blues 🎺</p>
      </motion.footer>
    </div>
  );
}
