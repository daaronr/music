import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as Tone from 'tone';
import { Soundfont } from 'smplr';
import { bluesVariations, parseChord } from '../data/bluesProgressions';
import type { BluesVariation } from '../data/bluesProgressions';
import { ChordBox } from './ChordBox';

type InstrumentType = 'acoustic_grand_piano' | 'electric_piano_1' | 'electric_guitar_jazz' | 'drawbar_organ';

const instrumentNames: Record<InstrumentType, string> = {
  'acoustic_grand_piano': '🎹 Grand Piano',
  'electric_piano_1': '🎸 Electric Piano',
  'electric_guitar_jazz': '🎸 Jazz Guitar',
  'drawbar_organ': '🎛️ Hammond Organ',
};

export function BluesPlayer() {
  const [selectedVariation, setSelectedVariation] = useState<BluesVariation>(bluesVariations[0]);
  const [currentBar, setCurrentBar] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [tempo, setTempo] = useState(100);
  const [playedBars, setPlayedBars] = useState<Set<number>>(new Set());
  const [audioStarted, setAudioStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [selectedInstrument, setSelectedInstrument] = useState<InstrumentType>('acoustic_grand_piano');

  const instrumentRef = useRef<Soundfont | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sequenceRef = useRef<Tone.Sequence | null>(null);

  // Load instrument when selection changes
  const loadInstrument = useCallback(async (instrumentName: InstrumentType) => {
    if (!audioContextRef.current) return;

    setIsLoading(true);
    setLoadingProgress(0);

    // Dispose old instrument
    if (instrumentRef.current) {
      instrumentRef.current.stop();
    }

    try {
      instrumentRef.current = new Soundfont(audioContextRef.current, {
        instrument: instrumentName,
        kit: 'FluidR3_GM',
      });

      // Track loading progress
      instrumentRef.current.load.then(() => {
        setLoadingProgress(100);
        setIsLoading(false);
      });

      // Simulate progress while loading
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress < 90) {
          setLoadingProgress(Math.min(progress, 90));
        } else {
          clearInterval(interval);
        }
      }, 100);

      await instrumentRef.current.load;
      clearInterval(interval);
    } catch (error) {
      console.error('Failed to load instrument:', error);
      setIsLoading(false);
    }
  }, []);

  const startAudio = async () => {
    await Tone.start();

    // Create audio context
    audioContextRef.current = new AudioContext();

    setIsLoading(true);
    await loadInstrument(selectedInstrument);
    setAudioStarted(true);
  };

  // Handle instrument change
  useEffect(() => {
    if (audioStarted && audioContextRef.current) {
      loadInstrument(selectedInstrument);
    }
  }, [selectedInstrument, audioStarted, loadInstrument]);

  const playChord = useCallback((chord: string, duration = 1.5) => {
    if (!instrumentRef.current || isLoading) return;

    const notes = parseChord(chord);

    // Play each note with slight timing variation for more natural feel
    notes.forEach((note, i) => {
      const delay = i * 0.015; // Slight arpeggio effect
      setTimeout(() => {
        instrumentRef.current?.start({
          note,
          velocity: 70 + Math.random() * 20, // Slight velocity variation
          duration,
        });
      }, delay * 1000);
    });
  }, [isLoading]);

  const startPlaying = useCallback(() => {
    if (!audioStarted || isLoading) return;

    Tone.getTransport().bpm.value = tempo;

    // Stop any existing sequence
    if (sequenceRef.current) {
      sequenceRef.current.dispose();
    }

    setPlayedBars(new Set());
    setCurrentBar(0);

    const chords = selectedVariation.chords;
    const beatDuration = 60 / tempo; // Duration of one beat in seconds

    sequenceRef.current = new Tone.Sequence(
      (time, index) => {
        if (index < chords.length) {
          // Schedule the chord to play
          Tone.getDraw().schedule(() => {
            playChord(chords[index], beatDuration * 1.8);
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
  }, [audioStarted, isLoading, selectedVariation, tempo, playChord]);

  const stopPlaying = useCallback(() => {
    Tone.getTransport().stop();
    Tone.getTransport().cancel();
    if (sequenceRef.current) {
      sequenceRef.current.dispose();
      sequenceRef.current = null;
    }
    instrumentRef.current?.stop();
    setIsPlaying(false);
    setCurrentBar(-1);
    setPlayedBars(new Set());
  }, []);

  const handleBarClick = (index: number) => {
    if (!audioStarted || isLoading) return;
    instrumentRef.current?.stop(); // Stop any currently playing notes
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
          <div className="text-center">
            <motion.button
              onClick={startAudio}
              disabled={isLoading}
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl text-2xl font-bold shadow-2xl disabled:opacity-50"
              whileHover={{ scale: isLoading ? 1 : 1.1 }}
              whileTap={{ scale: 0.95 }}
              animate={{
                boxShadow: isLoading ? 'none' : ['0 0 20px #3B82F6', '0 0 40px #8B5CF6', '0 0 20px #3B82F6'],
              }}
              transition={{ repeat: Infinity, duration: 2 }}
            >
              {isLoading ? '🎹 Loading Piano...' : '🎵 Start Playing'}
            </motion.button>
            {isLoading && (
              <div className="mt-4">
                <div className="w-64 h-2 bg-slate-700 rounded-full overflow-hidden mx-auto">
                  <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${loadingProgress}%` }}
                  />
                </div>
                <p className="text-slate-400 text-sm mt-2">Loading high-quality samples...</p>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Loading overlay when changing instruments */}
      {audioStarted && isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-40"
        >
          <div className="text-center">
            <div className="text-4xl mb-4">🎹</div>
            <p className="text-white text-lg">Loading {instrumentNames[selectedInstrument]}...</p>
            <div className="w-48 h-2 bg-slate-700 rounded-full overflow-hidden mx-auto mt-3">
              <motion.div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                initial={{ width: 0 }}
                animate={{ width: `${loadingProgress}%` }}
              />
            </div>
          </div>
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

      {/* Instrument Selector */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25 }}
        className="mb-6"
      >
        <label className="block text-sm text-slate-400 mb-2">Choose Your Sound:</label>
        <div className="flex flex-wrap gap-2">
          {(Object.keys(instrumentNames) as InstrumentType[]).map((inst) => (
            <motion.button
              key={inst}
              onClick={() => setSelectedInstrument(inst)}
              className={`px-4 py-2 rounded-xl font-medium transition-all ${
                selectedInstrument === inst
                  ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              disabled={isLoading}
            >
              {instrumentNames[inst]}
            </motion.button>
          ))}
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
          disabled={!audioStarted || isLoading}
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
        <p className="mt-1">🎹 Real instrument samples powered by FluidR3 SoundFont 🎺</p>
      </motion.footer>
    </div>
  );
}
