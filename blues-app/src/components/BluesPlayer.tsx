import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as Tone from 'tone';
import { Soundfont, DrumMachine } from 'smplr';
import { bluesVariations, parseChord, generateWalkingBass } from '../data/bluesProgressions';
import type { BluesVariation } from '../data/bluesProgressions';
import { ChordBox } from './ChordBox';
import { BluesFlowchart } from './BluesFlowchart';

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
  const [currentBeat, setCurrentBeat] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [tempo, setTempo] = useState(120);
  const [playedBars, setPlayedBars] = useState<Set<number>>(new Set());
  const [audioStarted, setAudioStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [selectedInstrument, setSelectedInstrument] = useState<InstrumentType>('electric_piano_1');
  const [showFlowchart, setShowFlowchart] = useState(true);

  // Volume controls
  const [pianoVolume, setPianoVolume] = useState(0.7);
  const [bassVolume, setBassVolume] = useState(0.8);
  const [drumVolume, setDrumVolume] = useState(0.5);

  const pianoRef = useRef<Soundfont | null>(null);
  const bassRef = useRef<Soundfont | null>(null);
  const drumsRef = useRef<DrumMachine | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sequenceRef = useRef<number | null>(null);
  const isPlayingRef = useRef(false);

  // Load instruments
  const loadInstruments = useCallback(async (instrumentName: InstrumentType) => {
    if (!audioContextRef.current) return;

    setIsLoading(true);
    setLoadingProgress(0);

    try {
      // Load piano/keys
      if (pianoRef.current) pianoRef.current.stop();
      pianoRef.current = new Soundfont(audioContextRef.current, {
        instrument: instrumentName,
        kit: 'FluidR3_GM',
      });

      // Load acoustic bass
      if (bassRef.current) bassRef.current.stop();
      bassRef.current = new Soundfont(audioContextRef.current, {
        instrument: 'acoustic_bass',
        kit: 'FluidR3_GM',
      });

      // Load drums
      if (drumsRef.current) drumsRef.current.stop();
      drumsRef.current = new DrumMachine(audioContextRef.current, {
        instrument: 'TR-808',
      });

      // Track loading
      let loaded = 0;
      const checkLoaded = () => {
        loaded++;
        setLoadingProgress((loaded / 3) * 100);
      };

      await Promise.all([
        pianoRef.current.load.then(checkLoaded),
        bassRef.current.load.then(checkLoaded),
        drumsRef.current.load.then(checkLoaded),
      ]);

      setIsLoading(false);
    } catch (error) {
      console.error('Failed to load instruments:', error);
      setIsLoading(false);
    }
  }, []);

  const startAudio = async () => {
    await Tone.start();
    audioContextRef.current = new AudioContext();
    setIsLoading(true);
    await loadInstruments(selectedInstrument);
    setAudioStarted(true);
  };

  // Handle instrument change
  useEffect(() => {
    if (audioStarted && audioContextRef.current) {
      loadInstruments(selectedInstrument);
    }
  }, [selectedInstrument, audioStarted, loadInstruments]);

  // Play a chord with jazz voicing
  const playChord = useCallback((chord: string, duration = 0.8) => {
    if (!pianoRef.current || isLoading) return;
    const notes = parseChord(chord);

    // Slight arpeggio for natural feel
    notes.forEach((note, i) => {
      setTimeout(() => {
        pianoRef.current?.start({
          note,
          velocity: (60 + Math.random() * 20) * pianoVolume,
          duration,
        });
      }, i * 15);
    });
  }, [isLoading, pianoVolume]);

  // Play bass note
  const playBass = useCallback((note: string, duration = 0.4) => {
    if (!bassRef.current || isLoading) return;
    bassRef.current.start({
      note,
      velocity: (80 + Math.random() * 15) * bassVolume,
      duration,
    });
  }, [isLoading, bassVolume]);

  // Play drum hit
  const playDrum = useCallback((drum: string) => {
    if (!drumsRef.current || isLoading) return;
    drumsRef.current.start({
      note: drum,
      velocity: (70 + Math.random() * 20) * drumVolume,
    });
  }, [isLoading, drumVolume]);

  // Main playback loop
  const startPlaying = useCallback(() => {
    if (!audioStarted || isLoading) return;
    if (isPlayingRef.current) return;

    isPlayingRef.current = true;
    setIsPlaying(true);
    setPlayedBars(new Set());
    setCurrentBar(0);
    setCurrentBeat(0);

    const chords = selectedVariation.chords;
    const beatDuration = 60000 / tempo; // ms per beat
    let barIndex = 0;
    let beatIndex = 0;

    const playBeat = () => {
      if (!isPlayingRef.current) return;

      const currentChord = chords[barIndex];
      const nextChord = chords[(barIndex + 1) % chords.length];

      // Generate walking bass for this bar
      const bassLine = generateWalkingBass(currentChord, nextChord);

      // Beat 1: Chord + kick + bass root
      if (beatIndex === 0) {
        playChord(currentChord, beatDuration * 3.5 / 1000);
        playDrum('kick');
        playBass(bassLine[0], beatDuration / 1000);
        setCurrentBar(barIndex);
        setPlayedBars(prev => new Set([...prev, barIndex]));
      }
      // Beat 2: Hi-hat + bass
      else if (beatIndex === 1) {
        playDrum('hihat');
        playBass(bassLine[1], beatDuration / 1000);
      }
      // Beat 3: Kick + hi-hat + bass
      else if (beatIndex === 2) {
        playDrum('kick');
        playDrum('hihat');
        playBass(bassLine[2], beatDuration / 1000);
      }
      // Beat 4: Hi-hat + bass approach note
      else if (beatIndex === 3) {
        playDrum('hihat');
        playBass(bassLine[3], beatDuration / 1000);
      }

      setCurrentBeat(beatIndex);

      // Advance
      beatIndex++;
      if (beatIndex >= 4) {
        beatIndex = 0;
        barIndex++;
        if (barIndex >= chords.length) {
          // Loop or stop
          barIndex = 0;
          // Uncomment to stop after one chorus:
          // isPlayingRef.current = false;
          // setIsPlaying(false);
          // setCurrentBar(-1);
          // setCurrentBeat(-1);
          // return;
        }
      }

      sequenceRef.current = window.setTimeout(playBeat, beatDuration);
    };

    playBeat();
  }, [audioStarted, isLoading, selectedVariation, tempo, playChord, playBass, playDrum]);

  const stopPlaying = useCallback(() => {
    isPlayingRef.current = false;
    if (sequenceRef.current) {
      clearTimeout(sequenceRef.current);
      sequenceRef.current = null;
    }
    pianoRef.current?.stop();
    bassRef.current?.stop();
    drumsRef.current?.stop();
    setIsPlaying(false);
    setCurrentBar(-1);
    setCurrentBeat(-1);
    setPlayedBars(new Set());
  }, []);

  const handleBarClick = (index: number) => {
    if (!audioStarted || isLoading) return;
    pianoRef.current?.stop();
    bassRef.current?.stop();

    const chord = selectedVariation.chords[index];
    const nextChord = selectedVariation.chords[(index + 1) % 12];
    const bassLine = generateWalkingBass(chord, nextChord);

    playChord(chord);
    playBass(bassLine[0]);
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
        className="text-center mb-6"
      >
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
          🎸 Blues Flow
        </h1>
        <p className="text-slate-400">Interactive 12-Bar Blues with Walking Bass & Drums</p>
      </motion.div>

      {/* Audio start overlay */}
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
              {isLoading ? '🎹 Loading...' : '🎵 Start Playing'}
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
                <p className="text-slate-400 text-sm mt-2">Loading piano, bass & drums...</p>
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
            <p className="text-white text-lg">Loading {instrumentNames[selectedInstrument]}...</p>
            <div className="w-48 h-2 bg-slate-700 rounded-full overflow-hidden mx-auto mt-3">
              <motion.div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                animate={{ width: `${loadingProgress}%` }}
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Variation & Instrument Selectors */}
      <div className="grid md:grid-cols-2 gap-4 mb-4">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          <label className="block text-sm text-slate-400 mb-2">Choose Your Blues:</label>
          <div className="flex gap-2">
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
              className="flex-1 bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
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
              🎲
            </motion.button>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}>
          <label className="block text-sm text-slate-400 mb-2">Keys Sound:</label>
          <div className="flex flex-wrap gap-2">
            {(Object.keys(instrumentNames) as InstrumentType[]).map((inst) => (
              <motion.button
                key={inst}
                onClick={() => setSelectedInstrument(inst)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedInstrument === inst
                    ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
                whileTap={{ scale: 0.98 }}
                disabled={isLoading}
              >
                {instrumentNames[inst]}
              </motion.button>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Variation Info */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedVariation.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          className="mb-4 p-3 bg-slate-800/50 rounded-xl border border-slate-700"
        >
          <h2 className="text-xl font-bold text-purple-300">{selectedVariation.name}</h2>
          <p className="text-slate-400 text-sm italic">{selectedVariation.description}</p>
        </motion.div>
      </AnimatePresence>

      {/* Beat indicator */}
      {isPlaying && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-center gap-2 mb-4"
        >
          {[0, 1, 2, 3].map((beat) => (
            <motion.div
              key={beat}
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                currentBeat === beat
                  ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white'
                  : 'bg-slate-700 text-slate-400'
              }`}
              animate={currentBeat === beat ? { scale: [1, 1.2, 1] } : {}}
              transition={{ duration: 0.15 }}
            >
              {beat + 1}
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* 12-Bar Grid */}
      <motion.div
        layout
        className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-12 gap-2 md:gap-3 mb-6"
      >
        <AnimatePresence mode="popLayout">
          {selectedVariation.chords.map((chord, index) => (
            <motion.div
              key={`${selectedVariation.id}-${index}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ delay: index * 0.03 }}
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

      {/* Flowchart toggle & display */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-6">
        <button
          onClick={() => setShowFlowchart(!showFlowchart)}
          className="text-sm text-slate-400 hover:text-white mb-2 flex items-center gap-1"
        >
          {showFlowchart ? '▼' : '▶'} Flowchart View
        </button>
        {showFlowchart && (
          <BluesFlowchart
            currentBar={currentBar}
            selectedVariation={selectedVariation.id}
          />
        )}
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex flex-wrap items-center justify-center gap-4 mb-6"
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
          {isPlaying ? '⏹ Stop' : '▶ Play'}
        </motion.button>

        {/* Tempo Control */}
        <div className="flex items-center gap-3 bg-slate-800 px-4 py-3 rounded-xl">
          <span className="text-slate-400">🥁</span>
          <input
            type="range"
            min="60"
            max="200"
            value={tempo}
            onChange={(e) => setTempo(Number(e.target.value))}
            className="w-20 accent-purple-500"
          />
          <span className="text-sm font-mono w-20">{tempo} BPM</span>
        </div>
      </motion.div>

      {/* Volume Controls */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="flex flex-wrap justify-center gap-4 mb-6 text-sm"
      >
        <div className="flex items-center gap-2 bg-slate-800/50 px-3 py-2 rounded-lg">
          <span>🎹</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={pianoVolume}
            onChange={(e) => setPianoVolume(Number(e.target.value))}
            className="w-16 accent-blue-500"
          />
        </div>
        <div className="flex items-center gap-2 bg-slate-800/50 px-3 py-2 rounded-lg">
          <span>🎸</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={bassVolume}
            onChange={(e) => setBassVolume(Number(e.target.value))}
            className="w-16 accent-amber-500"
          />
        </div>
        <div className="flex items-center gap-2 bg-slate-800/50 px-3 py-2 rounded-lg">
          <span>🥁</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={drumVolume}
            onChange={(e) => setDrumVolume(Number(e.target.value))}
            className="w-16 accent-red-500"
          />
        </div>
      </motion.div>

      {/* Legend */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="flex flex-wrap justify-center gap-3 text-xs"
      >
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-blue-500" />
          <span className="text-slate-400">Tonic</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-amber-500" />
          <span className="text-slate-400">Subdominant</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-red-500" />
          <span className="text-slate-400">Dominant</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-purple-500" />
          <span className="text-slate-400">Minor</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-pink-500" />
          <span className="text-slate-400">Chromatic</span>
        </div>
      </motion.div>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="text-center mt-8 text-slate-500 text-xs"
      >
        <p>🎹 Jazz voicings • 🎸 Walking bass • 🥁 4/4 swing feel</p>
      </motion.footer>
    </div>
  );
}
