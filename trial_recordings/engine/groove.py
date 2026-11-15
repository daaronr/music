"""A livelier jazz rhythm section, shared by every recording in this repo.

Added 28 Sep 2026 after listening: the ride was too loud and the drums were one bar pattern
repeated. All five recordings (the three trial tunes through this engine, and the Tenebrae and
Noctilucent waltzes) now use these same helpers, so they stay comparable:

  drums()          ride figures that change from bar to bar (4/4 or 3/4), a closed-hat or
                   cross-stick texture for quieter sections, snare/kick comping from rhythmic
                   cells that answer phrase by phrase, small fills or set-ups at 4- and 8-bar
                   phrase ends, varied bigger fills at section changes (the ride stops for
                   them), kick "bombs" into new sections, and a softer ride
  bass_life()      ghost notes, triplet rakes, dead notes and shorter notes in walking lines
  pick_pattern()   comping-pattern choice that avoids playing one pattern three bars running

Times are in seconds from bar 0: t = (bar * beats + beat) * beat_sec.
"""
from __future__ import annotations

import dataclasses
import random

KICK, SNARE, SIDESTICK, HH_FOOT, HH_CLOSED, RIDE, CRASH, CRASH2 = 36, 38, 37, 33, 42, 51, 49, 57
TOM_HI, TOM_MID, TOM_LO = 48, 47, 43
T1, T2 = 1 / 3, 2 / 3


def _ride_figures(beats, s):
    """(name, [(position in beats, accent)]); accent 1 = the backbeat side of the figure."""
    if beats == 4:
        return {
            "spang": [(0, 0), (1, 1), (1 + s, .3), (2, 0), (3, 1), (3 + s, .3)],
            "spang_all": [(0, 0), (s, .3), (1, 1), (1 + s, .3), (2, 0), (2 + s, .3), (3, 1), (3 + s, .3)],
            "trip4": [(0, 0), (1, 1), (1 + s, .3), (2, 0), (3, 1), (3 + T1, .25), (3 + T2, .35)],
            "quarters": [(0, 0), (1, 1), (2, 0), (3, 1)],
            "late": [(0, 0), (1, 1), (2, 0), (2 + s, .3), (3, 1), (3 + s, .3)],
        }
    return {
        "waltz": [(0, 0), (1, 1), (1 + s, .3), (2, .5)],
        "waltz_skip3": [(0, 0), (1, 1), (1 + s, .3), (2, .5), (2 + s, .3)],
        "waltz_one": [(0, 0), (s, .3), (1, 1), (2, .5), (2 + s, .3)],
        "quarters": [(0, 0), (1, 1), (2, .5)],
        "waltz_trip": [(0, 0), (1, 1), (2, .5), (2 + T1, .25), (2 + T2, .35)],
    }


def _ride_weights(beats, texture, k):
    if beats == 4:
        if texture == "sparse":
            return {"quarters": 4, "spang": 2}
        if texture == "drive":
            return {"spang": 5, "spang_all": 2 + 2 * k, "trip4": 2, "late": 1}
        return {"spang": 7, "trip4": 1.5, "late": 1.2, "quarters": .6, "spang_all": .4 + k}
    if texture == "sparse":
        return {"quarters": 3, "waltz": 3}
    if texture == "drive":
        return {"waltz": 4, "waltz_skip3": 3, "waltz_one": 2, "waltz_trip": 1.5}
    return {"waltz": 6, "waltz_skip3": 2, "waltz_one": 1.5, "waltz_trip": 1, "quarters": .6}


# snare/kick comping cells: (position in beats, what) - 'a' snare accent, 'g' ghost,
# 'k' kick, 'b' kick and snare together
CELLS = {
    4: [[(1 + T2, "a")], [(3 + T2, "a")], [(1, "g"), (1 + T2, "a")], [(2 + T1, "g"), (2 + T2, "a")],
        [(1 + T2, "a"), (2 + T2, "a")], [(T2, "g"), (1 + T2, "g"), (2 + T2, "a")], [(3, "a"), (3 + T2, "k")],
        [(2, "a"), (3 + T2, "a")], [(1 + T2, "k"), (3, "a")], [(2 + T2, "b")], [(3 + T1, "g"), (3 + T2, "a")]],
    3: [[(1 + T2, "a")], [(2 + T2, "a")], [(1, "g"), (1 + T2, "a")], [(T2, "g"), (2, "a")], [(2, "b")],
        [(1 + T2, "a"), (2 + T2, "k")], [(T2, "g"), (1 + T2, "g"), (2 + T2, "a")], [(2 + T1, "g"), (2 + T2, "a")]],
}

# fills: (length in beats, [(offset from fill start, drum, relative velocity)])
S, TH, TM, TL, K = SNARE, TOM_HI, TOM_MID, TOM_LO, KICK
FILLS = {
    "trip_down": (2, [(0, S, 0), (T1, S, -8), (T2, TH, 0), (1, S, 2), (1 + T1, TM, 0), (1 + T2, TL, 4)]),
    "snare_trip": (1, [(0, S, -6), (T1, S, -2), (T2, S, 4)]),
    "hits": (2, [(T2, "b", 6), (1 + T2, "b", 10)]),
    "eighths": (2, [(0, S, -4), (.62, TH, -2), (1, S, 0), (1.62, TM, 4)]),
    "toms_trip": (1, [(0, TH, 0), (T1, TM, 2), (T2, TL, 6)]),
    "long_trip": (3, [(i / 3, [S, S, TH, S, TH, TM, S, TM, TL][i], -8 + i * 2) for i in range(9)]),
}
SETUPS = [[(T2, "k")], [(T2, "b")], [(T1, "g"), (T2, "k")]]   # offsets inside the last beat


def drums(n_bars, beats, beat_sec, rng: random.Random, intensity, texture=lambda b: "time", *,
          section_starts=(), fills=(), crashes=(), phrase=8, ride_key=RIDE, swing=0.64,
          note_cls=None, start_bar=0):
    """intensity(bar) -> 0..1; texture(bar) -> 'time' | 'sparse' | 'drive' | 'hats' | 'sidestick'."""
    hits = []
    Note = note_cls

    def hit(bar, pos, key, vel, jit=0.004, lean=0.0):
        t = ((start_bar + bar) * beats + pos) * beat_sec + lean + rng.gauss(0, jit)
        hits.append(Note(t=t, dur=0.5, midi=key, vel=int(max(1, min(124, vel)))))

    figures = _ride_figures(beats, swing)
    starts = sorted(set(section_starts) | {0})
    recent_fig, recent_cell = [], []
    for b in range(n_bars):
        k = intensity(b)
        tex = texture(b)
        sec0 = max(s for s in starts if s <= b)
        in_phrase = (b - sec0) % phrase
        at_4 = (b - sec0) % 4 == 3
        at_8 = in_phrase == phrase - 1
        nxt_is_section = (b + 1) in starts

        # --- fill plan for this bar
        fill = None
        if b in fills:
            names = ["trip_down", "hits", "eighths"] + (["long_trip"] if beats >= 3 and k > .45 else [])
            fill = rng.choice(names)
        elif at_8 and rng.random() < .35 + .35 * k and tex != "sparse":
            fill = rng.choice(["snare_trip", "toms_trip", "hits"] if k > .4 else ["snare_trip", "hits"])
        fill_start = beats - FILLS[fill][0] if fill else beats

        # --- time keeping: ride (or closed hat) with a figure that changes
        w = _ride_weights(beats, tex, k)
        names = [n for n in w if not (len(recent_fig) >= 2 and recent_fig[-1] == recent_fig[-2] == n)]
        fig = rng.choices(names, weights=[w[n] for n in names])[0]
        recent_fig = (recent_fig + [fig])[-3:]
        cym = HH_CLOSED if tex == "hats" else ride_key
        base = (40 if tex == "hats" else 46) + 16 * k
        for pos, acc in figures[fig]:
            if pos >= fill_start - 1e-6:
                continue
            v = base + 7 * acc - (10 if acc < .5 and pos % 1 else 0) + rng.gauss(0, 3.5)
            hit(b, pos, cym, v, jit=.003, lean=-.003)
        # hat foot: 2 and 4, or 2 and 3 in a waltz (sometimes only 2)
        if tex != "hats":
            foot = [1, 3] if beats == 4 else ([1, 2] if rng.random() < .7 else [1])
            for pos in foot:
                hit(b, pos, HH_FOOT, 48 + 10 * k + rng.gauss(0, 3))
        # feathered kick, very light, and not in sparse sections
        if tex not in ("sparse", "hats"):
            for pos in (range(beats) if beats == 4 else [0]):
                if pos < fill_start:
                    hit(b, pos, KICK, 12 + 8 * k + rng.gauss(0, 2))
        if tex == "sidestick":
            hit(b, beats - 1, SIDESTICK, 52 + 12 * k + rng.gauss(0, 3), lean=.004)

        # --- comping: one cell per bar or two, never the same cell three times running
        busy = {"sparse": .12, "hats": .25, "sidestick": .2, "drive": .75}.get(tex, .3 + .45 * k)
        if rng.random() < busy:
            cells = [i for i in range(len(CELLS[beats])) if recent_cell[-2:].count(i) < 2]
            ci = rng.choice(cells)
            recent_cell = (recent_cell + [ci])[-4:]
            for pos, what in CELLS[beats][ci]:
                if pos >= fill_start:
                    continue
                if what in ("a", "b"):
                    hit(b, pos, SNARE, 46 + 34 * k + rng.gauss(0, 5), lean=.004)
                if what == "g":
                    hit(b, pos, SNARE, 16 + 14 * k + rng.gauss(0, 3), lean=.004)
                if what in ("k", "b"):
                    hit(b, pos, KICK, 48 + 30 * k + rng.gauss(0, 5))
        # scattered ghost notes on the triplet grid
        for beat in range(beats):
            for trip in (T1, T2):
                if beat + trip < fill_start and rng.random() < (.03 + .12 * k) * (tex != "sparse"):
                    hit(b, beat + trip, SNARE, 14 + 12 * k + rng.gauss(0, 3), lean=.005)

        # --- fills and set-ups
        if fill:
            length, seq = FILLS[fill]
            for off, key, rel in seq:
                v = 62 + 26 * k + rel + rng.gauss(0, 4)
                if key == "b":
                    hit(b, fill_start + off, SNARE, v)
                    hit(b, fill_start + off, KICK, v - 6)
                else:
                    hit(b, fill_start + off, key, v)
        elif at_4 and not at_8 and rng.random() < .18 + .25 * k and tex != "sparse":
            for off, what in rng.choice(SETUPS):
                p = beats - 1 + off
                if what in ("k", "b"):
                    hit(b, p, KICK, 50 + 28 * k)
                if what in ("b", "g"):
                    hit(b, p, SNARE, (48 if what == "b" else 20) + 26 * k)

        # --- crashes: given positions, plus some phrase starts after a fill
        if b in crashes or (b > 0 and in_phrase == 0 and b - 1 >= 0 and rng.random() < .25 * k):
            hit(b, 0, CRASH if rng.random() < .6 else CRASH2, 78 + 26 * k)
            hit(b, 0, KICK, 66 + 24 * k)
        if nxt_is_section and not fill and rng.random() < .6:
            hit(b, beats - 1 + T2, KICK, 58 + 26 * k)      # a bomb into the new section
    return hits


def bass_life(notes, beat_sec, rng: random.Random, where=lambda t: True,
              p_ghost=.09, p_rake=.05, p_short=.10, p_dead=.03):
    """Post-process a bass line: ghosts, rakes into the next note, shorter and dead notes.
    Only touches walking quarters (0.55-1.1 beats long) inside `where(t)`."""
    ns = sorted(notes, key=lambda n: n.t)
    out = []
    for i, n in enumerate(ns):
        nxt = ns[i + 1] if i + 1 < len(ns) else None
        walking = .55 * beat_sec < n.dur < 1.1 * beat_sec and where(n.t)
        if walking:
            r = rng.random()
            if r < p_dead:
                n = dataclasses.replace(n, dur=.22 * beat_sec, vel=max(28, n.vel - 34))
            elif r < p_dead + p_short:
                n = dataclasses.replace(n, dur=n.dur * .55)
        out.append(n)
        if not (walking and nxt) or nxt.t - n.t < .8 * beat_sec:
            continue
        r = rng.random()
        if r < p_ghost:                       # muted ghost on the last triplet
            out.append(dataclasses.replace(n, t=nxt.t - beat_sec / 3, dur=.12 * beat_sec,
                                           vel=max(24, n.vel - 40)))
        elif r < p_ghost + p_rake:            # triplet rake from a whole step away
            out[-1] = dataclasses.replace(out[-1], dur=min(out[-1].dur, .3 * beat_sec))
            d = 1 if rng.random() < .5 else -1
            out.append(dataclasses.replace(n, t=nxt.t - 2 * beat_sec / 3, dur=.3 * beat_sec,
                                           midi=nxt.midi + 2 * d, vel=max(30, n.vel - 22)))
            out.append(dataclasses.replace(n, t=nxt.t - beat_sec / 3, dur=.3 * beat_sec,
                                           midi=nxt.midi + d, vel=max(30, n.vel - 18)))
    return out


def pick_pattern(names, weights, recent, rng):
    """Weighted choice that avoids a third bar in a row of the same comping pattern."""
    ok = [(n, w) for n, w in zip(names, weights) if not (len(recent) >= 2 and recent[-1] == recent[-2] == n)]
    if not ok:
        ok = list(zip(names, weights))
    choice = rng.choices([n for n, _ in ok], weights=[w for _, w in ok])[0]
    recent.append(choice)
    del recent[:-3]
    return choice
