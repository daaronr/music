"""Turn the written parts into a performance: swing, humanised timing and
dynamics for the horns, plus a generated rhythm section (walking bass,
piano comping with voice-led rootless voicings, jazz ride-cymbal drums).

Form of the recording (bars of 4/4 at 184 bpm):
  intro   4  rhythm section on the last four bars of the form (turnaround)
  head   32  trumpet melody, alto sax an octave below
  solo   64  the written duo solo: trumpet + alto sax (the guitar line)
  head   30  head out, then the 2nd-ending bar with a fermata
"""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from musiclib import BAR  # noqa: E402
from chords import parse_chord  # noqa: E402

TEMPO = 184
BEAT = 60.0 / TEMPO
SWING = 0.61            # off-beat 8th lands at 61% of the beat (horn lines)
RIDE_SWING = 0.64       # drummer's skip note a touch later

DYN_DB = {"pp": -16, "p": -12, "mp": -8, "mf": -4, "f": 0, "ff": 3}


@dataclass
class Note:
    t: float                 # seconds
    dur: float               # seconds (sounding)
    midi: int
    db: float = 0.0          # level relative to the track's reference
    vel: int = 80            # for sampled instruments with velocity layers
    flags: str = ""
    legato_in: bool = False  # slurred/soft-tongued into this note
    graces: list = field(default_factory=list)


# ------------------------------------------------------------------ time map

def warp(tick_in_bar: int, swing: float = SWING) -> float:
    """Position within the bar (ticks, 24/quarter) -> beats, with swing."""
    beat, p = divmod(tick_in_bar, 24)
    if p <= 12:
        frac = p / 12 * swing
    else:
        frac = swing + (p - 12) / 12 * (1 - swing)
    return beat + frac


class Clock:
    def __init__(self, bar_offset: int = 0):
        self.bar_offset = bar_offset

    def time(self, abs_bar: float, beats: float) -> float:
        return (abs_bar * 4 + beats) * BEAT


# ------------------------------------------------------------------ written parts

def notes_from_bars(bars, start_bar: int, rng: random.Random, lag=0.0, jitter=0.006,
                    base_dyn="mf", octave=0, clamp=None, chord_pick="top"):
    """Merge ties, apply swing (not to triplets), dynamics, articulation."""
    out: list[Note] = []
    dyn = base_dyn
    hair = None          # (kind, start_db)
    flat = [e for bar in bars for e in bar]
    i = 0
    pending_graces = []
    while i < len(flat):
        e = flat[i]
        if e.dynamic:
            dyn = e.dynamic
        if e.hairpin in ("crescendo", "diminuendo"):
            hair = (e.hairpin, e.tick)
        if e.hairpin == "stop":
            hair = None
        if e.kind == "rest":
            i += 1
            continue
        # merge tie chain
        j = i
        while flat[j].tie_start and j + 1 < len(flat):
            j += 1
        first, last = flat[i], flat[j]
        end_tick = last.tick + last.dur
        bar0 = first.tick // BAR
        pos0 = first.tick % BAR
        straight = first.tuplet is not None
        b0 = (pos0 / 24) if straight else warp(pos0)
        bar1, pos1 = divmod(end_tick, BAR)
        b1 = (pos1 / 24) if (last.tuplet is not None) else warp(pos1)
        t0 = (start_bar + bar0) * 4 * BEAT + b0 * BEAT
        t1 = (start_bar + bar1) * 4 * BEAT + b1 * BEAT
        pitches = [p.midi for p in first.pitches]
        if len(pitches) > 1:
            pitches = [max(pitches)] if chord_pick == "top" else [min(pitches)]
        midi = pitches[0] + 12 * octave
        if clamp:
            while midi < clamp[0]:
                midi += 12
            while midi > clamp[1]:
                midi -= 12
        db = DYN_DB.get(dyn, -4)
        if hair:
            prog = min(1.0, (first.tick - hair[1]) / (4 * BAR))
            db += (3 if hair[0] == "crescendo" else -3) * prog
        flags = "".join(sorted(set(first.flags + last.flags)))
        if ">" in flags or "^" in flags:
            db += 3
        jit = rng.gauss(0, jitter)
        out.append(Note(t=t0 + lag + jit, dur=max(0.05, t1 - t0), midi=midi, db=db, flags=flags,
                        graces=[g.midi + 12 * octave for g in first.graces]))
        i = j + 1
    # phrasing: legato between touching notes, bebop upbeat lift, contour accents
    for k, n in enumerate(out):
        prev = out[k - 1] if k else None
        if prev and abs(prev.t + prev.dur - n.t) < 0.03 and ">" not in n.flags and "^" not in n.flags:
            n.legato_in = True
        beat_pos = (n.t / BEAT) % 1.0
        if 0.45 < beat_pos < 0.8 and n.dur < BEAT:
            n.db += 1.2          # lift the upbeats
        elif n.dur < BEAT:
            n.db -= 0.6
        if prev and n.midi > prev.midi + 4 and n.dur >= BEAT * 0.9:
            n.db += 1.0
        # articulation lengths
        if "." in n.flags:
            n.dur = min(n.dur, BEAT * 0.42)
        elif n.dur < BEAT * 1.1 and not ("-" in n.flags):
            n.dur *= 0.94
        n.db += rng.gauss(0, 0.8)
    return out


# ------------------------------------------------------------------ harmony helpers

def chord_timeline(changes, n_bars, start_bar, form_offset=0):
    """List of (abs_bar_float_start, chord) for the given span."""
    tl = []
    for b in range(n_bars):
        form_bar = (b + form_offset) % 32
        for c in changes[form_bar]:
            pos = (c.tick % BAR) / 24.0
            tl.append((start_bar + b + pos / 4.0, c))
    return tl


def chord_at(tl, abs_bar):
    cur = tl[0][1]
    for s, c in tl:
        if s <= abs_bar + 1e-9:
            cur = c
        else:
            break
    return cur


def pcs(chord, which="scale"):
    base = {"tones": chord.tones, "scale": chord.scale}[which]
    return sorted({(chord.root_pc + i) % 12 for i in base})


# ------------------------------------------------------------------ walking bass

def bass_segments(tl, end_bar):
    """One segment per chord: (absolute beat, beats, chord, next chord, kind)."""
    segs, prev_text = [], None
    for bar in range(end_bar):
        chords = [(s, c) for s, c in tl if bar - 1e-9 <= s < bar + 1 - 1e-9]
        if not chords:
            chords = [(bar, chord_at(tl, bar))]
        for idx, (s, c) in enumerate(chords):
            beats = 4 if len(chords) == 1 else 2
            nxt = chords[idx + 1][1] if idx + 1 < len(chords) else chord_at(tl, bar + 1)
            kind = "second-bar" if (beats == 4 and prev_text == c.text()) else "first"
            segs.append((int(round(s * 4)), beats, c, nxt, kind))
            prev_text = c.text()
    return segs


def walking_bass(segments, rng, two_feel_bars=set()):
    """segments: (absolute beat, beats, chord, next chord, kind)."""
    notes: list[Note] = []
    prev = 41                       # A1-ish start (sounding MIDI)
    lo, hi = 28, 50                 # E1 .. D3

    def nearest(pc, ref):
        cands = [m for m in range(lo, hi + 1) if m % 12 == pc]
        return min(cands, key=lambda m: abs(m - ref))

    # plan every segment's first note first, so approaches aim at the real target
    firsts = []
    for (beat0, beats, ch, nxt, kind) in segments:
        tones = pcs(ch, "tones")
        first_pc = ch.root_pc
        if kind == "second-bar":     # same chord continues: start on the 3rd or 5th
            third = next(((ch.root_pc + i) % 12 for i in (4, 3) if (ch.root_pc + i) % 12 in tones),
                         ch.root_pc)
            fifth = next(((ch.root_pc + i) % 12 for i in (7, 8, 6) if (ch.root_pc + i) % 12 in tones),
                         ch.root_pc)
            first_pc = rng.choice([third, fifth, ch.root_pc])
        firsts.append(first_pc)
    firsts.append(firsts[-1])

    for si, (beat0, beats, ch, nxt, kind) in enumerate(segments):
        bar = beat0 // 4
        scale = pcs(ch, "scale")
        target_next = firsts[si + 1]
        line = [nearest(firsts[si], prev)]
        if len(line) and notes and abs(line[0] - prev) > 9:
            line[0] = nearest(firsts[si], prev + (7 if line[0] < prev else -7))
        # destination for the downbeat after this segment
        dest = nearest(target_next, line[0] + rng.choice([-5, 5, 7, -7, 3, -3]))
        for k in range(1, beats):
            remaining = beats - k
            cur = line[-1]
            if remaining == 1:       # approach note: chromatic, or a 5th if it fits the chord
                opts = [dest - 1, dest + 1, dest + 1, dest - 1]
                fifth = nearest((target_next + 7) % 12, cur)
                if fifth % 12 in scale:
                    opts.append(fifth)
                opts = [o for o in opts if lo <= o <= hi and o != cur] or [dest - 1]
                line.append(rng.choice(opts))
            else:
                step_dir = 1 if dest > cur else -1
                cands = [m for m in range(cur - 5, cur + 6)
                         if m != cur and lo <= m <= hi and m % 12 in scale]
                cands.sort(key=lambda m: (abs((m - cur) - 2 * step_dir), rng.random()))
                line.append(cands[0])
        if bar in two_feel_bars:
            # half notes on 1 and 3 (with a pickup now and then)
            half = [line[0], line[min(2, len(line) - 1)]] if beats == 4 else [line[0]]
            for h_i, m in enumerate(half):
                t = (beat0 + h_i * 2) * BEAT
                notes.append(Note(t=t - 0.004 + rng.gauss(0, 0.004), dur=BEAT * 1.85, midi=m,
                                  vel=int(rng.gauss(86, 5)), db=0))
            if rng.random() < 0.3 and beats == 4:
                t = (beat0 + 3 + warp(12) % 1) * BEAT
                notes.append(Note(t=t, dur=BEAT * 0.3, midi=line[-1], vel=64, db=-5))
        else:
            for b_i, m in enumerate(line):
                t = (beat0 + b_i) * BEAT
                acc = 3 if (beat0 + b_i) % 2 == 1 else 0
                notes.append(Note(t=t - 0.006 + rng.gauss(0, 0.004), dur=BEAT * 0.9, midi=m,
                                  vel=max(40, min(120, int(rng.gauss(84 + acc, 5)))), db=0))
            # occasional triplet "skip" into the next beat
            if rng.random() < 0.12 and beats >= 2:
                t = (beat0 + beats - 1 + 2 / 3) * BEAT
                notes.append(Note(t=t, dur=BEAT * 0.2, midi=line[-1], vel=50, db=-6))
        prev = line[-1]
    return notes


# ------------------------------------------------------------------ piano comping

VOICING_PCS = {  # 4 colour tones per chord quality (semitones above the root)
    "maj7#11": [4, 11, 2, 6], "maj7#5": [4, 8, 11, 2], "7sus(b9)": [5, 10, 1, 7],
    "7alt": [4, 10, 3, 8], "m9": [3, 7, 10, 2], "13sus": [5, 10, 2, 9], "m7": [3, 7, 10, 2],
    "7": [4, 9, 10, 2], "7(b9)": [4, 9, 10, 1], "m7b5": [3, 6, 10, 5], "m(maj7)": [3, 7, 11, 2],
    "9(#11)": [4, 10, 2, 6], "7(#11)": [4, 10, 6, 9],
}


def voicing_options(chord, lo=50, hi=77):
    pcs_ = sorted({(chord.root_pc + i) % 12 for i in chord.voicing})
    opts = []
    for bottom in pcs_:                       # each inversion of the close voicing
        for base in range(lo, lo + 12):
            if base % 12 != bottom:
                continue
            v = sorted(base + ((pc - bottom) % 12) for pc in pcs_)
            if v[-1] <= hi:
                opts.append(v)
                d2 = sorted([v[0], v[1], v[3], v[2] - 12])   # drop-2: more open
                if d2[0] >= lo - 5:
                    opts.append(d2)
    return opts


def choose_voicing(chord, prev, rng):
    opts = voicing_options(chord)
    if prev is None:
        prev = [57, 62, 65, 69]
    center = sum(prev) / len(prev)

    def cost(v):
        move = sum(min(abs(a - b) for b in prev) for a in v)
        drift = abs(sum(v) / len(v) - 63) * 0.6
        return move + drift + rng.random() * 1.5
    return min(opts, key=cost)


COMP_PATTERNS = {   # (position in 8ths, length in beats, accent)
    "charleston": [(0, 0.6, 0), (3, 0.5, 2)],
    "reverse": [(1, 0.5, 1), (4, 0.9, 0)],
    "push4": [(7, 1.2, 2)],               # anticipates the next bar
    "twoand": [(3, 0.4, 1), (7, 0.9, 2)],
    "long": [(0, 3.4, -2)],
    "stabs": [(1, 0.3, 1), (5, 0.3, 1)],
    "one": [(0, 1.0, 0)],
    "three": [(4, 1.5, 0)],
    "rest": [],
}


def piano_comp(tl, bars, start_bar, density, rng):
    """density: function(abs_bar) -> dict of pattern weights."""
    notes: list[Note] = []
    prev = None
    for b in range(bars):
        abs_bar = start_bar + b
        weights = density(abs_bar)
        names = list(weights)
        pat = rng.choices(names, weights=[weights[n] for n in names])[0]
        for pos8, length, acc in COMP_PATTERNS[pat]:
            beat_pos = warp(pos8 * 12, 0.62)
            when_bar = abs_bar + beat_pos / 4
            # an off-beat hit just before a chord change anticipates it
            ch = chord_at(tl, when_bar + (0.14 if pos8 % 2 else 0.01))
            v = choose_voicing(ch, prev, rng)
            prev = v
            t = (abs_bar * 4 + beat_pos) * BEAT + rng.gauss(0, 0.006)
            base = rng.gauss(62 + 4 * acc, 5)
            for k, m in enumerate(v):
                roll = k * rng.uniform(0.0, 0.006)
                notes.append(Note(t=t + roll, dur=length * BEAT, midi=m,
                                  vel=int(max(35, min(110, base + (6 if k == 3 else 0)))), db=0))
    return notes


# ------------------------------------------------------------------ drums (SoCal kit keys)

KICK, SNARE, SIDESTICK, HH_FOOT, HH_CLOSED, RIDE, RIDE_BELL, CRASH, CRASH2 = 36, 38, 37, 33, 42, 51, 53, 49, 57
TOM_HI, TOM_MID, TOM_LO = 48, 47, 43


def drums(bars, start_bar, intensity, rng, fills=set(), crashes=set(), ride_key=RIDE):
    """intensity: function(abs_bar) -> 0..1."""
    hits: list[Note] = []

    def hit(abs_bar, beats, key, vel, jitter=0.004):
        t = (abs_bar * 4 + beats) * BEAT + rng.gauss(0, jitter)
        hits.append(Note(t=t, dur=0.5, midi=key, vel=int(max(1, min(127, vel)))))

    skip = warp(12, RIDE_SWING) % 1       # position of the ride "skip" note
    for b in range(bars):
        ab = start_bar + b
        k = intensity(ab)
        for beat in range(4):
            v = 70 + 18 * k + (8 if beat % 2 else 0) + rng.gauss(0, 4)
            hit(ab, beat, ride_key, v)
            if beat % 2 == 1:
                hit(ab, beat + skip, ride_key, v - 20 + rng.gauss(0, 4))
                hit(ab, beat, HH_FOOT, 62 + 16 * k + rng.gauss(0, 4))
            hit(ab, beat, KICK, 18 + 10 * k + rng.gauss(0, 3))           # feathered
        # snare comping: triplet-grid ghost notes and the odd accent
        for beat in range(4):
            for trip in (1 / 3, 2 / 3):
                if rng.random() < 0.10 + 0.25 * k:
                    hit(ab, beat + trip, SNARE, 18 + 22 * k + rng.gauss(0, 5))
        if rng.random() < 0.25 + 0.4 * k:
            beat = rng.choice([1, 2, 3]) + rng.choice([0.0, 2 / 3])
            hit(ab, beat, SNARE, 55 + 30 * k + rng.gauss(0, 6))
            if rng.random() < 0.4:
                hit(ab, beat, KICK, 45 + 30 * k)
        if ab in crashes:
            hit(ab, 0, CRASH if rng.random() < 0.6 else CRASH2, 92 + 20 * k)
            hit(ab, 0, KICK, 80 + 20 * k)
        if ab in fills:
            # triplet fill on beats 3-4 down the kit
            seq = [SNARE, SNARE, TOM_HI, SNARE, TOM_MID, TOM_LO]
            for i, key in enumerate(seq):
                hit(ab, 2 + i / 3, key, 70 + 25 * k + rng.gauss(0, 5))
    return hits


