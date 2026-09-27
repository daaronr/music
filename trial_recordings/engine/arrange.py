"""The Halation recording's arrangement, stated as rules and applied to any tune.

This is claude_halation/src/audio/perform.py build(), with each Halation-
specific choice replaced by the rule it followed:

  intro     4 bars, rhythm section only, on the last four bars of the form
  head in   32 bars: trumpet melody, alto sax an octave below (level -1.5 dB)
  solos     the written two-chorus duo: trumpet + alto sax playing the guitar line
            (guitar chords -> top note; a bar that dips below the alto's low Db3
            or above its high Ab5 moves an octave, else single notes are folded in)
  head out  the head again, closing with the composer's written ending
  ending    final chord held: the trumpet's last note gets a fermata, the alto
            holds the chord tone nearest a fifth below it, the drummer swells on
            the ride, everyone cuts off on a crash, piano and bass let ring
  bass      two-feel in the head-in sections labelled A, walking elsewhere
  piano     same comping densities (strolls for the first 8 solo bars)
  drums     same intensity curve, fills and crashes at the same form positions
  tempo     the tempo marked by each tune's composer; same swing ratio for all
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

import perform as P
from chords import Chord, parse_chord, parse_ireal
from musiclib import BAR
from xmlread import read_part


@dataclass
class Tune:
    name: str
    tempo: int
    ireal_url: str
    head_xml: str
    head_part: int
    head_in: list[int]              # lead-sheet measure indices, 32 bars
    head_out: list[int]             # lead-sheet measure indices, head out incl. written ending
    head_out_form_bars: int         # how many of head_out follow the 32-bar form
    ending_chords: list[str]        # chords of the written-ending bars (after the form bars)
    solo_xml: str
    solo_parts: tuple[int, int]     # (trumpet, guitar) part indices
    sections: dict = field(default_factory=dict)   # form bar -> label


def fit_alto(bars, lo=49, hi=80):
    """Guitar line on alto: whole-bar octave moves, else fold single notes."""
    moved = []
    for bi, bar in enumerate(bars):
        notes = [p.midi for e in bar if e.kind == "note" for p in e.pitches]
        if not notes:
            continue
        shift = 0
        if min(notes) < lo and max(notes) + 12 <= hi:
            shift = 12
        elif max(notes) > hi and min(notes) - 12 >= lo:
            shift = -12
        if shift:
            moved.append((bi + 1, shift))
            for e in bar:
                if e.kind == "note":
                    e.pitches = [p.transpose(7 if shift > 0 else -7, shift) for p in e.pitches]
    return moved


def with_ticks(bars_of_chords):
    """Chord onsets: one chord = beat 1, two = beats 1 and 3, four = every beat."""
    out = []
    for bi, bar in enumerate(bars_of_chords):
        k = len(bar)
        offs = {1: [0], 2: [0, 48], 3: [0, 48, 72], 4: [0, 24, 48, 72]}[k]
        out.append([Chord(c.root_pc, c.quality, c.name, bi * BAR + o) for c, o in zip(bar, offs)])
    return out


def build(t: Tune, seed: int = 7):
    P.BEAT = 60.0 / t.tempo
    BEAT = P.BEAT
    Note = P.Note
    rng = random.Random(seed)
    changes = with_ticks(parse_ireal(t.ireal_url, 32))
    head = read_part(t.head_xml, t.head_part, t.head_in)
    head_out = read_part(t.head_xml, t.head_part, t.head_out)
    tpt_solo = read_part(t.solo_xml, t.solo_parts[0], list(range(64)))
    sax_solo = read_part(t.solo_xml, t.solo_parts[1], list(range(64)))
    assert len(head) == 32

    # the last note of the performance carries the fermata
    last = [e for bar in head_out for e in bar if e.kind == "note"][-1]
    if "F" not in last.flags:
        last.flags += "F"

    INTRO, HEAD_IN, SOLO, HEAD_OUT = 0, 4, 36, 100
    END_BAR = HEAD_OUT + len(t.head_out) - 1

    # ---- horns (same order of random draws as the Halation build)
    trumpet = P.notes_from_bars(head, HEAD_IN, rng, lag=0.010, base_dyn="mf")
    trumpet += P.notes_from_bars(tpt_solo, SOLO, rng, lag=0.010, base_dyn="mp")
    trumpet += P.notes_from_bars(head_out, HEAD_OUT, rng, lag=0.010, base_dyn="mf")

    moved = fit_alto(sax_solo)
    alto = P.notes_from_bars(head, HEAD_IN, rng, lag=0.016, base_dyn="mf", octave=-1, clamp=(49, 80))
    alto += P.notes_from_bars(sax_solo, SOLO, rng, lag=0.014, base_dyn="mp", clamp=(49, 80))
    alto += P.notes_from_bars(head_out, HEAD_OUT, rng, lag=0.016, base_dyn="mf", octave=-1, clamp=(49, 80))
    for n in alto:
        n.db -= 1.5 if n.t < SOLO * 4 * BEAT or n.t > HEAD_OUT * 4 * BEAT else 0

    # ---- chord timeline
    ending = [[parse_chord(c)] for c in t.ending_chords]
    ending = with_ticks(ending)
    tl = P.chord_timeline(changes, 4, INTRO, form_offset=28)
    tl += P.chord_timeline(changes, 32, HEAD_IN)
    tl += P.chord_timeline(changes, 64, SOLO)
    tl += P.chord_timeline(changes, t.head_out_form_bars, HEAD_OUT)
    for k, bar in enumerate(ending):
        for c in bar:
            tl.append((HEAD_OUT + t.head_out_form_bars + k + (c.tick % BAR) / 96, c))
    tl.sort(key=lambda x: x[0])
    final = P.chord_at(tl, END_BAR)

    # ending: the alto holds the final chord's tone nearest a fifth below the trumpet
    fermata_t = [n for n in trumpet if "F" in n.flags][-1]
    fermata_a = [n for n in alto if "F" in n.flags][-1]
    chord_pcs = {(final.root_pc + i) % 12 for i in final.tones | set(final.voicing)}
    target = fermata_t.midi - 7
    cands = [m for m in range(target - 4, target + 5) if m % 12 in chord_pcs and 49 <= m < fermata_t.midi]
    fermata_a.midi = min(cands, key=lambda m: (abs(m - target), m))
    cutoff = END_BAR * 4 * BEAT + 24 * 0.11 + 0.08
    for n in trumpet + alto:
        if "F" in n.flags:
            n.dur = cutoff - n.t
            n.flags = n.flags.replace("F", "")

    # ---- bass: two-feel in the head-in sections labelled A
    two_feel = set()
    labels = sorted(t.sections.items())
    for i, (start, label) in enumerate(labels):
        end = labels[i + 1][0] if i + 1 < len(labels) else 32
        if label.startswith("A"):
            two_feel |= set(range(HEAD_IN + start, HEAD_IN + end))
    bass = P.walking_bass(P.bass_segments(tl, END_BAR), rng, two_feel)
    low_root = next(m for m in range(28, 40) if m % 12 == final.root_pc)
    bass.append(Note(t=END_BAR * 4 * BEAT, dur=6.0, midi=low_root, vel=100))

    # ---- piano (Halation densities)
    def density(ab):
        if ab < HEAD_IN:
            return {"charleston": 3, "long": 2, "push4": 2}
        if ab < SOLO:
            return {"charleston": 3, "reverse": 2, "push4": 3, "twoand": 2, "long": 1}
        if ab < SOLO + 8:
            return {"rest": 1}
        if ab < SOLO + 32:
            return {"rest": 3, "one": 2, "long": 2, "push4": 1, "reverse": 1}
        if ab < SOLO + 56:
            return {"rest": 2, "charleston": 2, "push4": 2, "reverse": 1, "long": 1}
        if ab < HEAD_OUT:
            return {"charleston": 2, "twoand": 2, "push4": 2, "stabs": 1}
        return {"charleston": 3, "reverse": 2, "push4": 3, "twoand": 2}
    piano = P.piano_comp(tl, END_BAR, 0, density, rng)
    voicing = P.choose_voicing(final, None, rng)
    root2 = next(m for m in range(36, 48) if m % 12 == final.root_pc)
    ninth = next(m for m in range(74, 86) if m % 12 == (final.root_pc + 2) % 12)
    for k, m in enumerate([root2, root2 + 7] + voicing + [ninth]):
        piano.append(Note(t=END_BAR * 4 * BEAT + 0.02 * k, dur=6.0, midi=m, vel=70))

    # ---- drums (Halation curve and form positions)
    def intensity(ab):
        if ab < HEAD_IN:
            return 0.25
        if ab < SOLO:
            return 0.45
        if ab < SOLO + 32:
            return 0.30 + 0.25 * (ab - SOLO) / 32
        if ab < SOLO + 64:
            x = (ab - SOLO - 32) / 32
            return 0.55 + 0.4 * min(1, x * 1.6) if ab < SOLO + 59 else 0.6
        return 0.5
    fills = {HEAD_IN - 1, SOLO - 1, SOLO + 31, HEAD_OUT - 1, SOLO + 55}
    crashes = {HEAD_IN, SOLO, SOLO + 32, HEAD_OUT, SOLO + 56, HEAD_IN + 24, SOLO + 24}
    kit = P.drums(END_BAR, 0, intensity, rng, fills=fills, crashes=crashes)
    for i in range(24):
        kit.append(Note(t=END_BAR * 4 * BEAT + i * 0.11, dur=0.5, midi=P.RIDE, vel=int(30 + i * 3)))
    kit.append(Note(t=END_BAR * 4 * BEAT + 24 * 0.11, dur=2, midi=P.CRASH, vel=110))
    kit.append(Note(t=END_BAR * 4 * BEAT + 24 * 0.11, dur=2, midi=P.KICK, vel=100))
    kit.append(Note(t=END_BAR * 4 * BEAT, dur=2, midi=P.CRASH2, vel=70))

    length = END_BAR * 4 * BEAT + 8.0
    info = dict(end_bar=END_BAR, alto_bars_moved=moved, final_chord=final.name,
                ending_alto=fermata_a.midi, ending_trumpet=fermata_t.midi)
    return dict(trumpet=trumpet, alto=alto, piano=piano, bass=bass, drums=kit, length=length, info=info)
