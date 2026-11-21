#!/usr/bin/env python3
"""Small engraving pipeline for 'Brightwork'.

Music is written once, as bars in a LilyPond-like subset (absolute octaves),
and rendered to both MusicXML (for MuseScore) and LilyPond (for PDF), so the
two outputs cannot drift apart.

Bar syntax (one string per 4/4 bar):
  notes   c' cis'' bes aes' ...   (c' = middle C; ' up, , down an octave)
  rests   r4 r8 ...
  length  1 2 4 8 16 with dots; sticky like LilyPond
  tie     ~ after the note
  triplet \\tuplet 3/2 { ... }
  chord   <a c' e'>4
  text    ^"label"   (attached to the previous note)
  artic   ->  -.  --  -^
"""
import re
from dataclasses import dataclass, field
from fractions import Fraction as F
from xml.sax.saxutils import escape

STEPS = "CDEFGAB"
STEP_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
BAR = F(1)  # 4/4
DIVISIONS = 24  # per quarter note


# ---------------------------------------------------------------- model
@dataclass
class Ev:
    pitches: list  # [(step, alter, octave)]; [] = rest
    base: int
    dots: int = 0
    tup: tuple = None  # (actual, normal)
    tup_start: bool = False
    tup_stop: bool = False
    tie: bool = False
    tied_in: bool = False
    texts: list = field(default_factory=list)
    artics: list = field(default_factory=list)

    @property
    def notated(self):
        d = add = F(1, self.base)
        for _ in range(self.dots):
            add /= 2
            d += add
        return d

    @property
    def dur(self):
        d = self.notated
        if self.tup:
            d = d * self.tup[1] / self.tup[0]
        return d

    @property
    def is_rest(self):
        return not self.pitches


def midi(p):
    step, alter, octv = p
    return 12 * (octv + 1) + STEP_PC[step] + alter


def transpose(p, dsteps, semis, simplify=True):
    """Diatonic transposition; optionally respell awkward results."""
    step, alter, octv = p
    i = STEPS.index(step) + dsteps
    nstep, noct = STEPS[i % 7], octv + i // 7
    nalter = midi(p) + semis - (12 * (noct + 1) + STEP_PC[nstep])
    q = (nstep, nalter, noct)
    return respell(q) if simplify else q


def respell(p):
    """B#->C, E#->F, Cb->B, Fb->E, and remove double accidentals."""
    step, alter, octv = p
    m = midi(p)
    if (step, alter) in (("B", 1), ("E", 1), ("C", -1), ("F", -1)) or abs(alter) > 1:
        prefer_sharp = alter > 0
        for cand_step in STEPS:
            for cand_alt in ((0, 1) if prefer_sharp else (0, -1)):
                pc = (STEP_PC[cand_step] + cand_alt) % 12
                if pc == m % 12 and (cand_step, cand_alt) not in (("B", 1), ("E", 1), ("C", -1), ("F", -1)):
                    octv2 = (m - STEP_PC[cand_step] - cand_alt) // 12 - 1
                    return (cand_step, cand_alt, octv2)
    return p


# --------------------------------------------------------------- parser
TOK = re.compile(
    r"""\s*(?:
    (?P<tup>\\tuplet\s+(?P<tn>\d+)/(?P<td>\d+)\s*\{)
  | (?P<close>\})
  | (?P<chord><(?P<cp>[^>]+)>)(?P<cdur>\d+\.*)?(?P<ctie>~)?
  | (?P<text>\^"(?P<tx>[^"]*)")
  | (?P<art>-[>.\-^])
  | (?P<rest>r)(?P<rdur>\d+\.*)?
  | (?P<note>[a-g](?:isis|eses|is|es)?[',]*)(?P<ndur>\d+\.*)?(?P<ntie>~)?
)""",
    re.X,
)
ACC = {"": 0, "is": 1, "es": -1, "isis": 2, "eses": -2}


def parse_pitch(name):
    letter = name[0].upper()
    body = name[1:].rstrip("',")
    octv = 3 + name.count("'") - name.count(",")
    return (letter, ACC[body], octv)


def parse_bar(src, state):
    """state = {'base': int, 'dots': int}; returns list[Ev]."""
    evs, pos, tup, tup_first = [], 0, None, False
    src = src.strip()
    while pos < len(src):
        m = TOK.match(src, pos)
        if not m or m.end() == pos:
            raise ValueError(f"cannot parse at: {src[pos:pos+20]!r} in bar {src!r}")
        pos = m.end()
        if m.group("tup"):
            tup, tup_first = (int(m.group("tn")), int(m.group("td"))), True
            continue
        if m.group("close"):
            evs[-1].tup_stop = True
            tup = None
            continue
        if m.group("text"):
            evs[-1].texts.append(m.group("tx"))
            continue
        if m.group("art"):
            evs[-1].artics.append(m.group("art"))
            continue
        if m.group("chord"):
            pitches = [parse_pitch(x) for x in m.group("cp").split()]
            d, tie = m.group("cdur"), bool(m.group("ctie"))
        elif m.group("rest"):
            pitches, d, tie = [], m.group("rdur"), False
        else:
            pitches = [parse_pitch(m.group("note"))]
            d, tie = m.group("ndur"), bool(m.group("ntie"))
        if d:
            state["base"] = int(d.rstrip("."))
            state["dots"] = d.count(".")
        ev = Ev(pitches, state["base"], state["dots"], tup=tup, tie=tie)
        if tup and tup_first:
            ev.tup_start, tup_first = True, False
        evs.append(ev)
    return evs


def parse_part(bars_src):
    """list[str] -> list[list[Ev]], validating bar lengths and ties."""
    state = {"base": 4, "dots": 0}
    bars = []
    for i, src in enumerate(bars_src):
        evs = parse_bar(src, state)
        total = sum((e.dur for e in evs), F(0))
        if total != BAR:
            raise ValueError(f"bar {i+1}: duration {total} != 1  ({src!r})")
        bars.append(evs)
    prev = None
    for i, evs in enumerate(bars):
        for e in evs:
            if prev is not None and prev.tie:
                if [midi(p) for p in prev.pitches] != [midi(p) for p in e.pitches]:
                    raise ValueError(f"bar {i+1}: tie to a different pitch")
                e.tied_in = True
            prev = e
    if prev is not None and prev.tie:
        raise ValueError("dangling tie at end of part")
    return bars


def transpose_part(bars, dsteps, semis):
    out = []
    for evs in bars:
        row = []
        for e in evs:
            ne = Ev([transpose(p, dsteps, semis) for p in e.pitches], e.base, e.dots, e.tup,
                    e.tup_start, e.tup_stop, e.tie, e.tied_in, list(e.texts), list(e.artics))
            row.append(ne)
        out.append(row)
    return out


# --------------------------------------------------------------- chords
# quality -> (musicxml kind, kind text, degrees, extra kind attrs, lily suffix, ireal, display)
QUAL = {
    "maj7":    ("major-seventh", "maj7", [], "", "maj7", "^7", "maj7"),
    "maj7#11": ("major-seventh", "maj7", [(11, 1, "add")], "", "maj7.11+", "^7#11", "maj7(#11)"),
    "m7":      ("minor-seventh", "m7", [], "", "m7", "-7", "m7"),
    "7":       ("dominant", "7", [], "", "7", "7", "7"),
    "7#11":    ("dominant", "7", [(11, 1, "add")], "", "7.11+", "7#11", "7(#11)"),
    "7b9":     ("dominant", "7", [(9, -1, "add")], "", "7.9-", "7b9", "7(b9)"),
    "7sus":    ("suspended-fourth", "7sus4", [(7, 0, "add")], ' parentheses-degrees="yes"', "sus4.7", "7sus", "7sus"),
    "7alt":    ("dominant", "7alt", [(5, -1, "alter"), (9, 1, "add")],
                ' parentheses-degrees="yes" stack-degrees="yes"', "7.5-.9+", "7alt", "7alt"),
}
ROOT_RE = re.compile(r"^([A-G])([b#]?)(.*)$")


def parse_chord(sym):
    """'Fmaj7#11' -> (('F', 0), 'maj7#11')"""
    m = ROOT_RE.match(sym)
    root = (m.group(1), {"": 0, "b": -1, "#": 1}[m.group(2)])
    qual = m.group(3)
    if qual not in QUAL:
        raise ValueError(f"unknown chord quality {qual!r} in {sym!r}")
    return root, qual


def transpose_root(root, dsteps, semis):
    s, a, _ = transpose((root[0], root[1], 4), dsteps, semis)
    return (s, a)


def root_name(root):
    return root[0] + {0: "", 1: "#", -1: "b"}[root[1]]


def parse_changes(changes, dsteps=0, semis=0):
    """list of bars, each 'Fmaj7#11' or 'Bm7 E7' (two beats each) ->
    list of bars, each [(offset as Fraction of whole, root, qual)]"""
    out = []
    for bar in changes:
        syms = bar.split()
        n = len(syms)
        row = []
        for k, s in enumerate(syms):
            root, qual = parse_chord(s)
            if dsteps or semis:
                root = transpose_root(root, dsteps, semis)
            row.append((F(k, n), root, qual))
        out.append(row)
    return out


# ------------------------------------------------------------- MusicXML
TYPE = {1: "whole", 2: "half", 4: "quarter", 8: "eighth", 16: "16th", 32: "32nd"}
ACCNAME = {-2: "flat-flat", -1: "flat", 0: "natural", 1: "sharp", 2: "double-sharp"}
SHARP_ORDER, FLAT_ORDER = "FCGDAEB", "BEADGCF"
ARTIC = {"->": "accent", "-.": "staccato", "--": "tenuto", "-^": "strong-accent"}
# rest lengths (fraction of a whole note) that are one symbol: (base, dots)
SIMPLE = {F(1): (1, 0), F(3, 4): (2, 1), F(1, 2): (2, 0), F(3, 8): (4, 1), F(1, 4): (4, 0),
          F(3, 16): (8, 1), F(1, 8): (8, 0), F(1, 16): (16, 0)}


def key_alters(fifths):
    d = {s: 0 for s in STEPS}
    for s in SHARP_ORDER[:max(fifths, 0)]:
        d[s] = 1
    for s in FLAT_ORDER[:max(-fifths, 0)]:
        d[s] = -1
    return d


def _harmony_xml(root, qual):
    kind, text, degrees, attrs, *_ = QUAL[qual]
    x = ['      <harmony print-frame="no">', "        <root>", f"          <root-step>{root[0]}</root-step>"]
    if root[1]:
        x.append(f"          <root-alter>{root[1]}</root-alter>")
    x.append("        </root>")
    x.append(f'        <kind text="{text}"{attrs}>{kind}</kind>')
    for val, alt, typ in degrees:
        x += ["        <degree>", f"          <degree-value>{val}</degree-value>",
              f"          <degree-alter>{alt}</degree-alter>", f"          <degree-type>{typ}</degree-type>",
              "        </degree>"]
    x.append("      </harmony>")
    return x


def beam_groups(evs):
    """Standard 4/4 beaming: flagged notes are beamed within each half bar.
    -> {event index: 'begin' | 'continue' | 'end'}"""
    res, cur, pos, half, tup = {}, [], F(0), None, None

    def flush():
        if len(cur) >= 2:
            res[cur[0]] = "begin"
            for i in cur[1:-1]:
                res[i] = "continue"
            res[cur[-1]] = "end"
        cur.clear()

    for i, e in enumerate(evs):
        h = int(pos // F(1, 2))
        beamable = not e.is_rest and e.base >= 8
        if not beamable or h != half or e.tup != tup:
            flush()
        if beamable:
            cur.append(i)
            half, tup = h, e.tup
        pos += e.dur
    flush()
    return res


def _note_xml(e, pitch_idx, state, keyalt, beam=None):
    p = e.pitches[pitch_idx] if e.pitches else None
    x = ["      <note>"]
    if pitch_idx > 0:
        x.append("        <chord/>")
    if p is None:
        x.append("        <rest/>")
    else:
        x.append("        <pitch>")
        x.append(f"          <step>{p[0]}</step>")
        if p[1]:
            x.append(f"          <alter>{p[1]}</alter>")
        x.append(f"          <octave>{p[2]}</octave>")
        x.append("        </pitch>")
    x.append(f"        <duration>{int(e.dur * 4 * DIVISIONS)}</duration>")
    if p is not None:
        if e.tied_in:
            x.append('        <tie type="stop"/>')
        if e.tie:
            x.append('        <tie type="start"/>')
    x.append("        <voice>1</voice>")
    x.append(f"        <type>{TYPE[e.base]}</type>")
    x += ["        <dot/>"] * e.dots
    if p is not None and not e.tied_in:
        key = (p[0], p[2])
        current = state.get(key, keyalt[p[0]])
        if p[1] != current:
            x.append(f"        <accidental>{ACCNAME[p[1]]}</accidental>")
        state[key] = p[1]
    if e.tup:
        x += ["        <time-modification>", f"          <actual-notes>{e.tup[0]}</actual-notes>",
              f"          <normal-notes>{e.tup[1]}</normal-notes>", "        </time-modification>"]
    if beam and pitch_idx == 0:
        x.append(f'        <beam number="1">{beam}</beam>')
    nots = []
    if p is not None and e.tied_in:
        nots.append('          <tied type="stop"/>')
    if p is not None and e.tie:
        nots.append('          <tied type="start"/>')
    if pitch_idx == 0 and e.tup_start:
        nots.append('          <tuplet type="start" bracket="yes"/>')
    if pitch_idx == 0 and e.tup_stop:
        nots.append('          <tuplet type="stop"/>')
    if pitch_idx == 0 and e.artics and p is not None:
        nots.append("          <articulations>")
        nots += [f"            <{ARTIC[a]}/>" for a in e.artics]
        nots.append("          </articulations>")
    if nots:
        x += ["        <notations>"] + nots + ["        </notations>"]
    x.append("      </note>")
    return x


def musicxml(title, composer, parts, sections=None, tempo=160, tempo_text="Medium-up swing",
             subtitle="", bars_per_system=4, rights=""):
    """parts: list of dicts with keys
         id, name, abbr, bars (parsed), fifths, clef ('G' | 'G8vb'),
         transpose (diatonic, chromatic) | None, chords (parsed changes) | None,
         midi_program (1-based)
    """
    sections = sections or {}
    nbars = len(parts[0]["bars"])
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" '
         '"http://www.musicxml.org/dtds/partwise.dtd">',
         '<score-partwise version="3.1">',
         "  <work>"]
    if subtitle:
        # MuseScore shows work-number as the subtitle when there is no movement-title
        x.append(f"    <work-number>{escape(subtitle)}</work-number>")
    x += [f"    <work-title>{escape(title)}</work-title>", "  </work>"]
    x += ["  <identification>", f'    <creator type="composer">{escape(composer)}</creator>']
    if rights:
        x.append(f"    <rights>{escape(rights)}</rights>")
    x += ["    <encoding>", "      <software>brightwork engine.py</software>",
          '      <supports element="accidental" type="yes"/>',
          '      <supports element="beam" type="yes"/>',
          '      <supports element="print" attribute="new-system" type="yes" value="yes"/>',
          "    </encoding>", "  </identification>", "  <part-list>"]
    for p in parts:
        x += [f'    <score-part id="{p["id"]}">', f"      <part-name>{escape(p['name'])}</part-name>",
              f"      <part-abbreviation>{escape(p['abbr'])}</part-abbreviation>",
              f'      <score-instrument id="{p["id"]}-I1">',
              f"        <instrument-name>{escape(p['name'])}</instrument-name>", "      </score-instrument>",
              f'      <midi-instrument id="{p["id"]}-I1">', "        <midi-channel>1</midi-channel>",
              f"        <midi-program>{p['midi_program']}</midi-program>", "      </midi-instrument>",
              "    </score-part>"]
    x.append("  </part-list>")
    for pi, p in enumerate(parts):
        keyalt = key_alters(p["fifths"])
        x.append(f'  <part id="{p["id"]}">')
        for bi in range(nbars):
            evs = p["bars"][bi]
            x.append(f'    <measure number="{bi + 1}">')
            if pi == 0 and bi > 0 and bi % bars_per_system == 0:
                x.append('      <print new-system="yes"/>')
            if bi == 0:
                x += ["      <attributes>", f"        <divisions>{DIVISIONS}</divisions>",
                      "        <key>", f"          <fifths>{p['fifths']}</fifths>", "        </key>",
                      "        <time>", "          <beats>4</beats>", "          <beat-type>4</beat-type>",
                      "        </time>", "        <clef>", "          <sign>G</sign>", "          <line>2</line>"]
                if p["clef"] == "G8vb":
                    x.append("          <clef-octave-change>-1</clef-octave-change>")
                x.append("        </clef>")
                if p.get("transpose"):
                    d, c = p["transpose"]
                    x += ["        <transpose>", f"          <diatonic>{d}</diatonic>",
                          f"          <chromatic>{c}</chromatic>", "        </transpose>"]
                x.append("      </attributes>")
                if pi == 0:
                    x += ['      <direction placement="above">', "        <direction-type>",
                          f'          <words font-weight="bold">{escape(tempo_text)}</words>',
                          "        </direction-type>", "        <direction-type>",
                          "          <metronome>", "            <beat-unit>quarter</beat-unit>",
                          f"            <per-minute>{tempo}</per-minute>", "          </metronome>",
                          "        </direction-type>", f'        <sound tempo="{tempo}"/>', "      </direction>"]
            if bi in sections and pi == 0:
                x += ['      <direction placement="above">', "        <direction-type>",
                      f"          <rehearsal>{escape(sections[bi])}</rehearsal>", "        </direction-type>",
                      "      </direction>"]
            chords = p.get("chords")
            pending = list(chords[bi]) if chords else []
            pos, acc_state = F(0), {}
            beams = beam_groups(evs)
            for ei, e in enumerate(evs):
                while pending and pending[0][0] == pos:
                    _, root, qual = pending.pop(0)
                    x += _harmony_xml(root, qual)
                for t in e.texts:
                    x += ['      <direction placement="above">', "        <direction-type>",
                          f'          <words font-style="italic" font-size="8">{escape(t)}</words>',
                          "        </direction-type>", "      </direction>"]
                inside = [c for c in pending if pos < c[0] < pos + e.dur]
                cuts = [pos] + [c[0] for c in inside] + [pos + e.dur]
                segs = [cuts[k + 1] - cuts[k] for k in range(len(cuts) - 1)]
                if e.is_rest and inside and not e.tup and all(s in SIMPLE for s in segs):
                    # a rest that spans a chord change: split it so the symbol sits on a real event
                    for k, seg in enumerate(segs):
                        if k > 0:
                            _, root, qual = inside[k - 1]
                            pending.remove(inside[k - 1])
                            x += _harmony_xml(root, qual)
                        x += _note_xml(Ev([], *SIMPLE[seg]), 0, acc_state, keyalt)
                else:
                    for k in range(max(1, len(e.pitches))):
                        x += _note_xml(e, k, acc_state, keyalt, beams.get(ei))
                pos += e.dur
                # chord changes that fall inside this event (no note starts there)
                while pending and pending[0][0] < pos:
                    off, root, qual = pending.pop(0)
                    back = int((pos - off) * 4 * DIVISIONS)
                    x += ["      <backup>", f"        <duration>{back}</duration>", "      </backup>"]
                    x += _harmony_xml(root, qual)
                    x += ["      <forward>", f"        <duration>{back}</duration>", "      </forward>"]
            last = bi == nbars - 1
            if last or (bi + 1) in sections:
                style = "light-heavy" if last else "light-light"
                x += ['      <barline location="right">', f"        <bar-style>{style}</bar-style>",
                      "      </barline>"]
            x.append("    </measure>")
        x.append("  </part>")
    x.append("</score-partwise>")
    return "\n".join(x) + "\n"


# ------------------------------------------------------------- LilyPond
LY_ACC = {0: "", 1: "is", -1: "es", 2: "isis", -2: "eses"}


def ly_pitch(p):
    step, alter, octv = p
    n = octv - 3
    return step.lower() + LY_ACC[alter] + ("'" * n if n > 0 else "," * -n)


def ly_bar(evs, annotate=True):
    out = []
    for e in evs:
        s = ""
        if e.tup_start:
            s += f"\\tuplet {e.tup[0]}/{e.tup[1]} {{ "
        if e.is_rest:
            s += "r"
        elif len(e.pitches) == 1:
            s += ly_pitch(e.pitches[0])
        else:
            s += "<" + " ".join(ly_pitch(p) for p in e.pitches) + ">"
        s += str(e.base) + "." * e.dots
        if e.tie:
            s += "~"
        for a in e.artics:
            s += a
        if annotate:
            for t in e.texts:
                s += f' ^\\markup {{ \\italic \\fontsize #-3 "{t}" }}'
        if e.tup_stop:
            s += " }"
        out.append(s)
    return " ".join(out)


def ly_chords(changes):
    out = []
    for row in changes:
        n = len(row)
        dur = {1: "1", 2: "2", 4: "4"}[n]
        out.append(" ".join(
            f"{root[0].lower()}{LY_ACC[root[1]]}{dur}:{QUAL[qual][4]}" for _, root, qual in row))
    return out


LY_HEAD = r'''\version "2.24.0"
#(set-default-paper-size "a4")
#(set-global-staff-size %(staffsize)s)
\paper {
  top-margin = 12\mm
  bottom-margin = 12\mm
  left-margin = 14\mm
  right-margin = 14\mm
  indent = %(indent)s\mm
  short-indent = %(shortindent)s\mm
  ragged-last-bottom = ##f
  ragged-bottom = ##f
  print-page-number = ##t
  markup-system-spacing.basic-distance = #18
  system-system-spacing.basic-distance = #%(sysdist)s
  system-system-spacing.minimum-distance = #%(sysmin)s
}
\header {
  title = "%(title)s"
  subtitle = "%(subtitle)s"
  composer = "%(composer)s"
  poet = "%(poet)s"
  tagline = "%(tagline)s"
}
chExc = {
  <c e g b fis'>1-\markup { "maj7(" \hspace #-0.5 \raise #0.9 \fontsize #-3 \sharp \hspace #-0.3 "11)" }
  <c e g bes fis'>1-\markup { "7(" \hspace #-0.5 \raise #0.9 \fontsize #-3 \sharp \hspace #-0.3 "11)" }
  <c e g bes des'>1-\markup { "7(" \hspace #-0.5 \raise #0.5 \fontsize #-3 \flat \hspace #-0.3 "9)" }
  <c f g bes>1-\markup { "7sus" }
  <c e ges bes dis'>1-\markup { "7alt" }
  <c e g bes>1-\markup { "7" }
  <c e g b>1-\markup { "maj7" }
  <c es g bes>1-\markup { "m7" }
}
chExceptions = #(append (sequential-music-to-chord-exceptions chExc #t) ignatzekExceptions)
'''


def lilypond(title, composer, parts, sections=None, tempo=160, tempo_text="Medium-up swing",
             subtitle="", poet="", bars_per_system=4, staffsize=20, tagline="", annotate=True,
             systems_per_page=None, sysdist=14, pagebreaks=()):
    sections = sections or {}
    multi = len(parts) > 1
    head = LY_HEAD % dict(staffsize=staffsize, indent=16 if multi else 0, shortindent=10 if multi else 0,
                          title=title, subtitle=subtitle, composer=composer, poet=poet, tagline=tagline,
                          sysdist=sysdist, sysmin=sysdist - 4)
    nbars = len(parts[0]["bars"])
    body = [head]
    # global structure (marks, breaks, barlines)
    g = ["global = {", f'  \\time 4/4 \\tempo "{tempo_text}" 4 = {tempo}']
    for bi in range(nbars):
        line = "  "
        if bi in sections:
            if bi > 0:
                line += '\\bar "||" '
            line += f'\\mark \\markup {{ \\box \\bold "{sections[bi]}" }} '
        line += "s1"
        if bi == nbars - 1:
            line += ' \\bar "|."'
        elif (bi + 1) in pagebreaks:
            line += " \\pageBreak"
        elif (bi + 1) % bars_per_system == 0:
            line += " \\break"
        g.append(line)
    g.append("}")
    body.append("\n".join(g))
    staves = []
    for pi, p in enumerate(parts):
        var = "part" + "ABCDEFG"[pi]
        key = {0: "c", 2: "d", -1: "f", 1: "g"}[p["fifths"]]
        clef = '"treble_8"' if p["clef"] == "G8vb" else "treble"
        lines = [f"{var} = {{", f"  \\clef {clef} \\key {key} \\major"]
        for bi, evs in enumerate(p["bars"]):
            lines.append(f"  {ly_bar(evs, annotate)} | % {bi + 1}")
        lines.append("}")
        body.append("\n".join(lines))
        blk = ""
        if p.get("chords"):
            cvar = "chords" + "ABCDEFG"[pi]
            body.append(f"{cvar} = \\chordmode {{\n  " + " |\n  ".join(ly_chords(p["chords"])) + " |\n}")
            blk += (f"    \\new ChordNames \\with {{ chordNameExceptions = #chExceptions chordChanges = ##t "
                    f"\\override ChordName.font-size = #1.5 "
                    f"\\override ChordName.extra-spacing-width = #'(-0.3 . 1.6) }} \\{cvar}\n")
        inst = ""
        if multi:
            inst = (f' \\with {{ instrumentName = "{p["name"]}" shortInstrumentName = "{p["abbr"]}" }}')
        g_ref = "\\global" if pi == 0 else "\\globalSkips"
        blk += f"    \\new Staff{inst} << {g_ref} \\{var} >>\n"
        staves.append(blk)
    if multi:
        # second staff needs the breaks/barlines but not a second set of marks
        body.append("globalSkips = { " + " ".join("s1" for _ in range(nbars)) + " }")
    layout = ("  \\layout {\n    \\context { \\Score \\override BarNumber.break-visibility = ##(#f #f #t)\n"
              "      \\override RehearsalMark.self-alignment-X = #LEFT\n"
              "      \\override MetronomeMark.padding = #2.5 }\n"
              "    \\context { \\Staff \\override TextScript.staff-padding = #2.2 }\n  }\n")
    grp = "\\new StaffGroup <<\n" if multi else "<<\n"
    body.append("\\score {\n  " + grp + "".join(staves) + "  >>\n" + layout + "}\n")
    return "\n\n".join(body)
