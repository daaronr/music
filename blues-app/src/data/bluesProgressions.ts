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

// Map chord symbols to actual notes in C
export const chordToNotes: Record<string, string[]> = {
  "I7": ["C3", "E3", "G3", "Bb3"],
  "IV7": ["F3", "A3", "C4", "Eb4"],
  "V7": ["G3", "B3", "D4", "F4"],
  "II7": ["D3", "F#3", "A3", "C4"],
  "VI7": ["A3", "C#4", "E4", "G4"],
  "VII7": ["B3", "D#4", "F#4", "A4"],
  "ii-7": ["D3", "F3", "A3", "C4"],
  "ii-": ["D3", "F3", "A3"],
  "iii-": ["E3", "G3", "B3"],
  "vi7": ["A3", "C4", "E4", "G4"],
  "v-": ["G3", "Bb3", "D4"],
  "Imaj": ["C3", "E3", "G3", "B3"],
  "IVmaj": ["F3", "A3", "C4", "E4"],
  "iv-": ["F3", "Ab3", "C4"],
  "iv°7": ["F3", "Ab3", "B3", "D4"],
  "#iv°7": ["F#3", "A3", "C4", "Eb4"],
  "♭VI7": ["Ab3", "C4", "Eb4", "Gb4"],
  "♭V7": ["Gb3", "Bb3", "Db4", "E4"],
  "vii-": ["B3", "D4", "F#4"],
  "III7": ["E3", "G#3", "B3", "D4"],
  "vi-": ["A3", "C4", "E4"],
  "VIImaj": ["B3", "D#4", "F#4", "A#4"],
  "♭VIImaj": ["Bb3", "D4", "F4", "A4"],
  "♭VImaj": ["Ab3", "C4", "Eb4", "G4"],
  "♭Vmaj": ["Gb3", "Bb3", "Db4", "F4"],
  "#i-": ["C#3", "E3", "G#3"],
  "#IV7": ["F#3", "A#3", "C#4", "E4"],
};

// For compound chords, split them
export function parseChord(chord: string): string[] {
  // Handle slash chords
  if (chord.includes("/")) {
    const [chordPart] = chord.split("/");
    return chordToNotes[chordPart] || chordToNotes["I7"];
  }
  // Handle compound chords like "ii- V7"
  if (chord.includes(" ")) {
    const parts = chord.split(" ");
    return chordToNotes[parts[0]] || chordToNotes["I7"];
  }
  return chordToNotes[chord] || chordToNotes["I7"];
}

// Get chord color based on function
export function getChordColor(chord: string): string {
  if (chord.includes("I") && !chord.includes("V") && !chord.includes("i-")) return "#3B82F6"; // Blue - tonic
  if (chord.includes("IV") || chord.includes("iv")) return "#F59E0B"; // Amber - subdominant
  if (chord.includes("V") || chord.includes("II") || chord.includes("VII")) return "#EF4444"; // Red - dominant
  if (chord.includes("vi") || chord.includes("iii") || chord.includes("ii")) return "#8B5CF6"; // Purple - relative minor
  if (chord.includes("°") || chord.includes("dim")) return "#6B7280"; // Gray - diminished
  if (chord.includes("♭") || chord.includes("#")) return "#EC4899"; // Pink - chromatic
  return "#10B981"; // Green - other
}
