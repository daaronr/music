// Blues progression data - 18 variations
export interface BluesVariation {
  id: number;
  name: string;
  chords: string[];
  description?: string;
}

export const bluesVariations: BluesVariation[] = [
  {
    id: 1,
    name: "Basic Blues",
    chords: ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "V7", "I7", "I7"],
    description: "The foundation - where it all begins"
  },
  {
    id: 2,
    name: "Classic V-IV Turnaround",
    chords: ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
    description: "That sweet turnaround that pulls you back"
  },
  {
    id: 3,
    name: "Dominant II-V",
    chords: ["I7", "IV7", "I7", "I7", "IV7", "IV7", "I7", "I7", "II7", "V7", "I7", "V7"],
    description: "Jazz influence creeping in"
  },
  {
    id: 4,
    name: "Dominant 6-2-5-1",
    chords: ["I7", "IV7", "I7", "I7", "IV7", "IV7", "I7", "VI7", "II7", "V7", "I7", "V7"],
    description: "The classic cycle of fifths"
  },
  {
    id: 5,
    name: "Diatonic 6-2-5-1",
    chords: ["I7", "IV7", "I7", "I7", "IV7", "IV7", "I7", "VI7", "ii-7", "V7", "I7", "ii- V7"],
    description: "Smooth minor chord substitution"
  },
  {
    id: 6,
    name: "IV of IV + ♭VI Turnaround",
    chords: ["I7", "IV7", "I7", "I7", "IV7", "VII7", "I7", "VI7", "♭VI7", "V7", "I7", "♭VI7 V7"],
    description: "Chromatic magic with the flat six"
  },
  {
    id: 7,
    name: "2-5 Delays + Minor Subdom",
    chords: ["I7", "IV7", "I7", "v- I7", "IV7", "VII7", "I7", "iii- VI7", "ii-7", "V7", "iii- VI7", "ii- V7"],
    description: "Bebop sophistication"
  },
  {
    id: 8,
    name: "Minor Subdom Extended",
    chords: ["I7", "IV7", "I7", "v- I7", "IV7", "VII7", "iii-", "VI7", "ii-7", "V7", "iii- VI7", "ii- V7"],
    description: "Deep minor territory"
  },
  {
    id: 9,
    name: "Bebop Plagal Cadence",
    chords: ["I7", "IV7", "I7", "v- I7", "IV7", "IV7", "I7", "vi7", "ii7", "V7", "vi7", "I7"],
    description: "That churchy plagal feel"
  },
  {
    id: 10,
    name: "Diminished Passing Chords",
    chords: ["Imaj", "vii- III7", "vi- II7", "v- I7", "IV7", "#iv°7", "I7", "IV7", "iv°7", "I7", "IV7", "iv°7"],
    description: "Spooky diminished movement"
  },
  {
    id: 11,
    name: "Diminished Pedal Point",
    chords: ["Imaj", "vii- ♭vii-", "vi- ♭vi-", "v- ♭V7", "IVmaj", "iv-", "iv°7", "I7", "Imaj", "iv°7", "I7", "Imaj"],
    description: "Hypnotic pedal tones"
  },
  {
    id: 12,
    name: "Major Seventh Cycle",
    chords: ["Imaj", "IVmaj", "iii- ii-", "#i- ♭V7", "IVmaj", "Imaj", "iv°7", "I7", "Imaj", "iv°7", "I7", "Imaj"],
    description: "Lush major seventh harmony"
  },
  {
    id: 13,
    name: "Major Diminished Variation",
    chords: ["Imaj", "IVmaj", "iii- ii-", "#i- ♭V7", "IVmaj", "Imaj", "iv°7", "I7", "Imaj", "iv°7", "I7", "Imaj"],
    description: "Major meets diminished"
  },
  {
    id: 14,
    name: "Major IV Diminished Mix",
    chords: ["Imaj", "vii- III7", "vi- II7", "v- I7", "IVmaj", "iv°7", "I7", "Imaj", "iv°7", "I7", "Imaj", "iv°7"],
    description: "Mixing major and diminished colors"
  },
  {
    id: 15,
    name: "Major Diminished Interchange",
    chords: ["Imaj", "vii- III7", "vi- II7", "#i- ♭V7", "IVmaj", "iv°7", "I7", "Imaj", "iv°7", "I7", "Imaj", "iv°7"],
    description: "Chromatic interchange mastery"
  },
  {
    id: 16,
    name: "Major IV Contrast",
    chords: ["#i- #IV7", "vii- III7", "vi- II7", "v- I7", "IVmaj", "Imaj", "iv°7", "I7", "Imaj", "iv°7", "I7", "Imaj"],
    description: "Bold harmonic contrast"
  },
  {
    id: 17,
    name: "Major Diminished Mix-up",
    chords: ["Imaj", "#i- ♭V7", "VIImaj ♭VIImaj", "♭VImaj ♭Vmaj", "IVmaj", "Imaj", "iv°7", "I7", "Imaj", "iv°7", "I7", "Imaj"],
    description: "Wild chromatic adventure"
  },
  {
    id: 18,
    name: "Slash Bass Blues",
    chords: ["v-/I", "i-/IV", "v-/I", "v-/I", "i-/IV", "I7/V", "I7/V", "IV7/♭VII", "IV7/♭VII", "I7/V", "I7/V", "I7/V"],
    description: "Groovy slash bass movement"
  }
];

// Jazz voicings - rootless voicings in comfortable piano range
// These are "A" voicings (3-5-7-9) and "B" voicings (7-9-3-5) commonly used
export interface ChordVoicing {
  notes: string[];      // Piano voicing (rootless or shell)
  root: string;         // Bass root note
  chordTones: string[]; // All chord tones for walking bass
  type: 'dom7' | 'maj7' | 'min7' | 'dim7' | 'min';
}

export const jazzVoicings: Record<string, ChordVoicing> = {
  // Dominant 7ths - rootless voicings (3-7-9 or 7-3-13)
  "I7": {
    notes: ["E3", "Bb3", "D4"],      // 3-7-9 voicing
    root: "C2",
    chordTones: ["C", "E", "G", "Bb"],
    type: 'dom7'
  },
  "IV7": {
    notes: ["A3", "Eb4", "G4"],      // 3-7-9
    root: "F2",
    chordTones: ["F", "A", "C", "Eb"],
    type: 'dom7'
  },
  "V7": {
    notes: ["B3", "F4", "A4"],       // 3-7-9
    root: "G2",
    chordTones: ["G", "B", "D", "F"],
    type: 'dom7'
  },
  "II7": {
    notes: ["F#3", "C4", "E4"],      // 3-7-9
    root: "D2",
    chordTones: ["D", "F#", "A", "C"],
    type: 'dom7'
  },
  "VI7": {
    notes: ["C#4", "G4", "B4"],      // 3-7-9
    root: "A2",
    chordTones: ["A", "C#", "E", "G"],
    type: 'dom7'
  },
  "VII7": {
    notes: ["D#4", "A4", "C#5"],     // 3-7-9
    root: "B2",
    chordTones: ["B", "D#", "F#", "A"],
    type: 'dom7'
  },
  "♭VI7": {
    notes: ["C4", "Gb4", "Bb4"],     // 3-7-9
    root: "Ab2",
    chordTones: ["Ab", "C", "Eb", "Gb"],
    type: 'dom7'
  },
  "♭V7": {
    notes: ["Bb3", "E4", "Ab4"],     // 3-7-9
    root: "Gb2",
    chordTones: ["Gb", "Bb", "Db", "E"],
    type: 'dom7'
  },
  "#IV7": {
    notes: ["A#3", "E4", "G#4"],
    root: "F#2",
    chordTones: ["F#", "A#", "C#", "E"],
    type: 'dom7'
  },
  "III7": {
    notes: ["G#3", "D4", "F#4"],
    root: "E2",
    chordTones: ["E", "G#", "B", "D"],
    type: 'dom7'
  },

  // Minor 7ths - rootless voicings
  "ii-7": {
    notes: ["F3", "A3", "C4"],       // b3-5-b7
    root: "D2",
    chordTones: ["D", "F", "A", "C"],
    type: 'min7'
  },
  "ii-": {
    notes: ["F3", "A3", "C4"],
    root: "D2",
    chordTones: ["D", "F", "A", "C"],
    type: 'min7'
  },
  "iii-": {
    notes: ["G3", "B3", "D4"],
    root: "E2",
    chordTones: ["E", "G", "B", "D"],
    type: 'min7'
  },
  "vi7": {
    notes: ["C4", "E4", "G4"],
    root: "A2",
    chordTones: ["A", "C", "E", "G"],
    type: 'min7'
  },
  "vi-": {
    notes: ["C4", "E4", "G4"],
    root: "A2",
    chordTones: ["A", "C", "E", "G"],
    type: 'min7'
  },
  "v-": {
    notes: ["Bb3", "D4", "F4"],
    root: "G2",
    chordTones: ["G", "Bb", "D", "F"],
    type: 'min7'
  },
  "vii-": {
    notes: ["D4", "F#4", "A4"],
    root: "B2",
    chordTones: ["B", "D", "F#", "A"],
    type: 'min7'
  },
  "iv-": {
    notes: ["Ab3", "C4", "Eb4"],
    root: "F2",
    chordTones: ["F", "Ab", "C", "Eb"],
    type: 'min7'
  },
  "i-": {
    notes: ["Eb3", "G3", "Bb3"],
    root: "C2",
    chordTones: ["C", "Eb", "G", "Bb"],
    type: 'min7'
  },
  "#i-": {
    notes: ["E3", "G#3", "B3"],
    root: "C#2",
    chordTones: ["C#", "E", "G#", "B"],
    type: 'min7'
  },
  "♭vi-": {
    notes: ["B3", "Eb4", "Gb4"],
    root: "Ab2",
    chordTones: ["Ab", "B", "Eb", "Gb"],
    type: 'min7'
  },
  "♭vii-": {
    notes: ["Db4", "F4", "Ab4"],
    root: "Bb2",
    chordTones: ["Bb", "Db", "F", "Ab"],
    type: 'min7'
  },
  "ii7": {
    notes: ["F3", "A3", "C4"],
    root: "D2",
    chordTones: ["D", "F", "A", "C"],
    type: 'min7'
  },

  // Major 7ths
  "Imaj": {
    notes: ["E3", "G3", "B3"],       // 3-5-7
    root: "C2",
    chordTones: ["C", "E", "G", "B"],
    type: 'maj7'
  },
  "IVmaj": {
    notes: ["A3", "C4", "E4"],
    root: "F2",
    chordTones: ["F", "A", "C", "E"],
    type: 'maj7'
  },
  "VIImaj": {
    notes: ["D#4", "F#4", "A#4"],
    root: "B2",
    chordTones: ["B", "D#", "F#", "A#"],
    type: 'maj7'
  },
  "♭VIImaj": {
    notes: ["D4", "F4", "A4"],
    root: "Bb2",
    chordTones: ["Bb", "D", "F", "A"],
    type: 'maj7'
  },
  "♭VImaj": {
    notes: ["C4", "Eb4", "G4"],
    root: "Ab2",
    chordTones: ["Ab", "C", "Eb", "G"],
    type: 'maj7'
  },
  "♭Vmaj": {
    notes: ["Bb3", "Db4", "F4"],
    root: "Gb2",
    chordTones: ["Gb", "Bb", "Db", "F"],
    type: 'maj7'
  },

  // Diminished 7ths
  "iv°7": {
    notes: ["Ab3", "B3", "D4"],      // Fully diminished
    root: "F2",
    chordTones: ["F", "Ab", "B", "D"],
    type: 'dim7'
  },
  "#iv°7": {
    notes: ["A3", "C4", "Eb4"],
    root: "F#2",
    chordTones: ["F#", "A", "C", "Eb"],
    type: 'dim7'
  },
};

// Get the first chord from compound chord symbols
function getFirstChord(chord: string): string {
  if (chord.includes("/")) {
    return chord.split("/")[0];
  }
  if (chord.includes(" ")) {
    return chord.split(" ")[0];
  }
  return chord;
}

// Get voicing for a chord symbol
export function getVoicing(chord: string): ChordVoicing {
  const firstChord = getFirstChord(chord);
  return jazzVoicings[firstChord] || jazzVoicings["I7"];
}

// Parse chord to get piano notes (for backwards compatibility)
export function parseChord(chord: string): string[] {
  return getVoicing(chord).notes;
}

// Get bass root for a chord
export function getBassRoot(chord: string): string {
  // Handle slash chords - the bass note is after the slash
  if (chord.includes("/")) {
    const bassSymbol = chord.split("/")[1];
    const bassNotes: Record<string, string> = {
      "I": "C2", "II": "D2", "III": "E2", "IV": "F2", "V": "G2", "VI": "A2", "VII": "B2",
      "♭VII": "Bb2", "♭VI": "Ab2", "♭V": "Gb2", "♭III": "Eb2", "♭II": "Db2"
    };
    return bassNotes[bassSymbol] || getVoicing(chord).root;
  }
  return getVoicing(chord).root;
}

// Generate walking bass line for a chord (4 notes for 4 beats)
export function generateWalkingBass(
  currentChord: string,
  nextChord: string
): string[] {
  const current = getVoicing(currentChord);

  const currentRoot = getBassRoot(currentChord);
  const nextRoot = getBassRoot(nextChord);

  // Get numeric value for note
  const noteToNum: Record<string, number> = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
  };

  // Parse note to get pitch class and octave
  const parseNote = (note: string): { pitch: string; octave: number } => {
    const match = note.match(/([A-G][#b]?)(\d)/);
    if (!match) return { pitch: 'C', octave: 2 };
    return { pitch: match[1], octave: parseInt(match[2]) };
  };

  const currentRootParsed = parseNote(currentRoot);
  const nextRootParsed = parseNote(nextRoot);

  // Get chord tones in bass register
  const bassOctave = 2;
  const chordTones = current.chordTones.map(t => {
    const num = noteToNum[t];
    return { note: t, num };
  });

  // Beat 1: Root
  const beat1 = currentRoot;

  // Beat 2: 3rd or 5th of chord
  const third = chordTones.find(t =>
    (current.type === 'min7' || current.type === 'min' || current.type === 'dim7')
      ? (t.num === (noteToNum[currentRootParsed.pitch] + 3) % 12)
      : (t.num === (noteToNum[currentRootParsed.pitch] + 4) % 12)
  );
  const fifth = chordTones.find(t =>
    t.num === (noteToNum[currentRootParsed.pitch] + 7) % 12
  );
  const beat2Note = third ? third.note : (fifth ? fifth.note : currentRootParsed.pitch);
  const beat2 = beat2Note + bassOctave;

  // Beat 3: 5th or another chord tone
  const beat3Note = fifth ? fifth.note : currentRootParsed.pitch;
  const beat3 = beat3Note + bassOctave;

  // Beat 4: Approach note to next root (chromatic or scale)
  const nextRootNum = noteToNum[nextRootParsed.pitch];
  const currentRootNum = noteToNum[currentRootParsed.pitch];

  // Choose approach note - half step below or above
  let approachNum: number;
  const diff = (nextRootNum - currentRootNum + 12) % 12;
  if (diff <= 6) {
    // Moving up - approach from below
    approachNum = (nextRootNum - 1 + 12) % 12;
  } else {
    // Moving down - approach from above
    approachNum = (nextRootNum + 1) % 12;
  }

  const numToNote: Record<number, string> = {
    0: 'C', 1: 'Db', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F',
    6: 'Gb', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'
  };

  const beat4 = numToNote[approachNum] + bassOctave;

  return [beat1, beat2, beat3, beat4];
}

// Get chord color based on function
export function getChordColor(chord: string): string {
  const c = chord.split(" ")[0].split("/")[0];
  if (c === "I7" || c === "Imaj" || c === "I") return "#3B82F6"; // Blue - tonic
  if (c.includes("IV") || c.includes("iv")) return "#F59E0B"; // Amber - subdominant
  if (c.includes("V") || c.includes("II") || c.includes("VII")) return "#EF4444"; // Red - dominant
  if (c.includes("vi") || c.includes("iii") || c.includes("ii")) return "#8B5CF6"; // Purple - relative minor
  if (c.includes("°") || c.includes("dim")) return "#6B7280"; // Gray - diminished
  if (c.includes("♭") || c.includes("#")) return "#EC4899"; // Pink - chromatic
  return "#10B981"; // Green - other
}

// Flowchart structure - simplified paths through the 12 bars
export interface FlowNode {
  bar: number;
  choices: {
    chord: string;
    variations: number[];
    nextBar: number;
  }[];
}

export const bluesFlowchart: FlowNode[] = [
  { bar: 1, choices: [{ chord: "I7", variations: [1,2,3,4,5,6,7,8,9], nextBar: 2 }, { chord: "Imaj", variations: [10,11,12,13,14,15,17], nextBar: 2 }, { chord: "#i-", variations: [16], nextBar: 2 }] },
  { bar: 2, choices: [{ chord: "I7", variations: [1,2], nextBar: 3 }, { chord: "IV7", variations: [3,4,5,6,7,8,9], nextBar: 3 }, { chord: "IVmaj", variations: [12,13], nextBar: 3 }, { chord: "vii-", variations: [10,14,15,16], nextBar: 3 }] },
  { bar: 3, choices: [{ chord: "I7", variations: [1,2,3,4,5,6,7,8,9], nextBar: 4 }, { chord: "vi-", variations: [10,14,15], nextBar: 4 }, { chord: "iii-", variations: [12,13], nextBar: 4 }] },
  { bar: 4, choices: [{ chord: "I7", variations: [1,2,3,4,5,6], nextBar: 5 }, { chord: "v- I7", variations: [7,8,9,10,14,16], nextBar: 5 }, { chord: "#i-", variations: [12,13,15], nextBar: 5 }] },
  { bar: 5, choices: [{ chord: "IV7", variations: [1,2,3,4,5,7,8,9,10], nextBar: 6 }, { chord: "IVmaj", variations: [11,12,13,14,15,16,17], nextBar: 6 }] },
  { bar: 6, choices: [{ chord: "IV7", variations: [1,2,3,4,5,9], nextBar: 7 }, { chord: "VII7", variations: [6,7,8], nextBar: 7 }, { chord: "#iv°7", variations: [10], nextBar: 7 }, { chord: "iv-", variations: [11], nextBar: 7 }, { chord: "Imaj", variations: [12,13,16,17], nextBar: 7 }] },
  { bar: 7, choices: [{ chord: "I7", variations: [1,2,3,4,5,6,7,9,10], nextBar: 8 }, { chord: "iii-", variations: [8], nextBar: 8 }, { chord: "iv°7", variations: [11,12,13,14,15,16,17], nextBar: 8 }] },
  { bar: 8, choices: [{ chord: "I7", variations: [1,2,3], nextBar: 9 }, { chord: "VI7", variations: [4,5,6,8], nextBar: 9 }, { chord: "iii-", variations: [7], nextBar: 9 }, { chord: "vi7", variations: [9], nextBar: 9 }, { chord: "IV7", variations: [10], nextBar: 9 }, { chord: "I7/Imaj", variations: [11,12,13,14,15,16,17], nextBar: 9 }] },
  { bar: 9, choices: [{ chord: "V7", variations: [1,2], nextBar: 10 }, { chord: "II7", variations: [3,4], nextBar: 10 }, { chord: "ii-7", variations: [5,7,8,9], nextBar: 10 }, { chord: "♭VI7", variations: [6], nextBar: 10 }, { chord: "iv°7", variations: [10,11,12,13,14,15,16,17], nextBar: 10 }] },
  { bar: 10, choices: [{ chord: "V7", variations: [1,3,4,5,6,7,8,9], nextBar: 11 }, { chord: "IV7", variations: [2,10], nextBar: 11 }, { chord: "I7", variations: [11,12,13,14,15,16,17], nextBar: 11 }] },
  { bar: 11, choices: [{ chord: "I7", variations: [1,3,4], nextBar: 12 }, { chord: "iii-", variations: [7,8], nextBar: 12 }, { chord: "vi7", variations: [9], nextBar: 12 }, { chord: "IV7", variations: [10], nextBar: 12 }, { chord: "Imaj", variations: [11,12,13,14,15,16,17], nextBar: 12 }] },
  { bar: 12, choices: [{ chord: "I7", variations: [1,9], nextBar: 1 }, { chord: "V7", variations: [2,3,4], nextBar: 1 }, { chord: "ii- V7", variations: [5,7,8], nextBar: 1 }, { chord: "♭VI7 V7", variations: [6], nextBar: 1 }, { chord: "iv°7", variations: [10,11,12,13,14,15,16,17], nextBar: 1 }] },
];
