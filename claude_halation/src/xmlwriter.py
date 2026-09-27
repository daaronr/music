"""MusicXML (3.1 partwise) writer for the Halation materials."""
from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import escape

from musiclib import BAR, DIV, XML_KIND, Chord, Event, Pitch

ART = {">": "<accent/>", "^": '<strong-accent type="up"/>', ".": "<staccato/>",
       "-": "<tenuto/>", "f": "<falloff/>", "d": "<doit/>", "s": "<scoop/>",
       "b": "<breath-mark/>"}


@dataclass
class PartSpec:
    pid: str
    name: str
    abbrev: str
    sound: str                      # MusicXML instrument-sound id
    program: int                    # General MIDI program (1-based)
    bars: list[list[Event]]         # concert pitch events
    clef: str = "G"                 # "G" or "G8vb"
    transpose: tuple[int, int] | None = None   # (steps, semis) concert->written
    chords: list[list[Chord]] | None = None    # per bar, concert
    show_chords: bool = True
    volume: int = 80
    pan: int = 0


@dataclass
class Layout:
    bars_per_system: int = 4
    page_breaks: list[int] = field(default_factory=list)     # bar indexes (0-based)
    system_breaks: list[int] | None = None                   # explicit list overrides
    rehearsal: dict[int, str] = field(default_factory=dict)  # bar index -> mark
    double_bars: list[int] = field(default_factory=list)     # bar index with light-light at end
    final_bar: bool = True
    tempo_text: str | None = None
    tempo_bpm: int | None = None
    top_texts: dict[int, list[str]] = field(default_factory=dict)  # bar -> texts (first part)
    repeat_start: int | None = None
    repeat_end: int | None = None
    endings: list[tuple[int, int, str, str]] = field(default_factory=list)  # (first,last,num,label)
    pickup: bool = False


def _pitch_xml(p: Pitch) -> str:
    alter = f"<alter>{p.alter}</alter>" if p.alter else ""
    return f"<pitch><step>{p.step}</step>{alter}<octave>{p.octave}</octave></pitch>"


def _harmony_xml(ch: Chord, offset: int = 0) -> str:
    kind, text, degrees = XML_KIND[ch.suffix]
    alter = f"<root-alter>{ch.root_alter}</root-alter>" if ch.root_alter else ""
    deg = "".join(
        f"<degree><degree-value>{v}</degree-value><degree-alter>{a}</degree-alter>"
        f"<degree-type>{t}</degree-type></degree>" for v, a, t in degrees)
    off = f"<offset>{offset}</offset>" if offset else ""
    return (f'<harmony print-frame="no"><root><root-step>{ch.root_step}</root-step>{alter}</root>'
            f'<kind text="{escape(text)}">{kind}</kind>{deg}{off}</harmony>')


def _direction(inner: str, placement: str = "above", sound: str = "") -> str:
    return f'<direction placement="{placement}">{inner}{sound}</direction>'


def _words(text: str, italic=True, bold=False, size=None) -> str:
    attrs = []
    if italic:
        attrs.append('font-style="italic"')
    if bold:
        attrs.append('font-weight="bold"')
    if size:
        attrs.append(f'font-size="{size}"')
    return f"<direction-type><words {' '.join(attrs)}>{escape(text)}</words></direction-type>"


def _note_xml(ev: Event, p: Pitch, chord_member: bool, voice: int = 1) -> str:
    parts = ["<note>"]
    if chord_member:
        parts.append("<chord/>")
    parts.append(_pitch_xml(p))
    parts.append(f"<duration>{ev.dur}</duration>")
    if ev.tie_stop:
        parts.append('<tie type="stop"/>')
    if ev.tie_start:
        parts.append('<tie type="start"/>')
    parts.append(f"<voice>{voice}</voice><type>{ev.typ}</type>")
    parts.extend("<dot/>" for _ in range(ev.dots))
    if ev.tuplet:
        parts.append("<time-modification><actual-notes>3</actual-notes>"
                     "<normal-notes>2</normal-notes></time-modification>")
    if "g" in ev.flags:
        parts.append('<notehead parentheses="yes">normal</notehead>')
    elif "x" in ev.flags:
        parts.append("<notehead>x</notehead>")
    nots = []
    if ev.tie_stop:
        nots.append('<tied type="stop"/>')
    if ev.tie_start:
        nots.append('<tied type="start"/>')
    if not chord_member:
        if ev.slur_start:
            nots.append('<slur type="start" number="1"/>')
        if ev.slur_stop:
            nots.append('<slur type="stop" number="1"/>')
        if ev.tuplet == "start":
            nots.append('<tuplet type="start" bracket="yes"/>')
        elif ev.tuplet == "stop":
            nots.append('<tuplet type="stop"/>')
        arts = "".join(ART[c] for c in ev.flags if c in ART)
        if arts:
            nots.append(f"<articulations>{arts}</articulations>")
        if "F" in ev.flags:
            nots.append('<fermata type="upright"/>')
    if nots:
        parts.append("<notations>" + "".join(nots) + "</notations>")
    parts.append("</note>")
    return "".join(parts)


def _grace_xml(p: Pitch) -> str:
    return (f'<note><grace slash="yes"/>{_pitch_xml(p)}<voice>1</voice>'
            f"<type>eighth</type></note>")


def _rest_xml(ev: Event, whole_bar: bool) -> str:
    if whole_bar:
        return (f'<note><rest measure="yes"/><duration>{ev.dur}</duration>'
                f"<voice>1</voice></note>")
    dots = "<dot/>" * ev.dots
    tm = ("<time-modification><actual-notes>3</actual-notes><normal-notes>2</normal-notes>"
          "</time-modification>") if ev.tuplet else ""
    nots = ""
    if ev.tuplet == "start":
        nots = '<notations><tuplet type="start" bracket="yes"/></notations>'
    elif ev.tuplet == "stop":
        nots = '<notations><tuplet type="stop"/></notations>'
    fer = '<notations><fermata type="upright"/></notations>' if "F" in ev.flags else ""
    return (f"<note><rest/><duration>{ev.dur}</duration><voice>1</voice>"
            f"<type>{ev.typ}</type>{dots}{tm}{nots}{fer}</note>")


PLAIN = {96: ("whole", 0), 84: ("half", 2), 72: ("half", 1), 48: ("half", 0),
         42: ("quarter", 2), 36: ("quarter", 1), 24: ("quarter", 0), 21: ("eighth", 2),
         18: ("eighth", 1), 12: ("eighth", 0), 9: ("16th", 1), 6: ("16th", 0), 3: ("32nd", 0)}


def _pieces(start: int, dur: int) -> list[int]:
    """Split a span into notatable durations, never crossing a beat when it
    starts off the beat."""
    out = []
    while dur:
        limit = dur
        if start % DIV:
            limit = min(dur, DIV - start % DIV)
        piece = max(d for d in PLAIN if d <= limit)
        out.append(piece)
        start += piece
        dur -= piece
    return out


def split_at(bars: list[list[Event]], ticks: set[int]) -> list[list[Event]]:
    """Give every chord change an onset: split notes/rests that sustain across
    a chord tick into tied pieces (standard practice at beat 3 of 4/4)."""
    out = []
    for bar in bars:
        new_bar = []
        for ev in bar:
            cuts = sorted(t for t in ticks if ev.tick < t < ev.tick + ev.dur)
            if not cuts or ev.tuplet:
                new_bar.append(ev)
                continue
            bounds = [ev.tick] + cuts + [ev.tick + ev.dur]
            spans = []
            for a, b in zip(bounds, bounds[1:]):
                pos = a
                for d in _pieces(a % BAR, b - a):
                    spans.append((pos, d))
                    pos += d
            for i, (pos, d) in enumerate(spans):
                typ, dots = PLAIN[d]
                piece = Event(**{**ev.__dict__})
                piece.tick, piece.dur, piece.typ, piece.dots = pos, d, typ, dots
                first, last = i == 0, i == len(spans) - 1
                if ev.kind == "note":
                    piece.tie_start = ev.tie_start if last else True
                    piece.tie_stop = ev.tie_stop if first else True
                ending = "".join(c for c in ev.flags if c in "Ffd")   # belong on the last piece
                opening = "".join(c for c in ev.flags if c not in "Ffd")
                piece.flags = (opening if first else "") + (ending if last else "")
                if not first:
                    piece.graces, piece.slur_start, piece.dynamic = [], False, None
                    piece.hairpin, piece.texts = None, []
                if not last:
                    piece.slur_stop = False
                new_bar.append(piece)
        out.append(new_bar)
    return out


def _written(ev: Event, tr) -> Event:
    if not tr:
        return ev
    steps, semis = tr
    new = Event(**{**ev.__dict__})
    new.pitches = [p.transpose(steps, semis) for p in ev.pitches]
    new.graces = [p.transpose(steps, semis) for p in ev.graces]
    return new


def build_musicxml(title: str, subtitle: str, composer: str, parts: list[PartSpec],
                   layout: Layout, credit_lines: list[str] | None = None,
                   page_size=(1224, 1584), staff_mm=6.5) -> str:
    """page_size in tenths (Letter at 40 tenths = staff height)."""
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" '
           '"http://www.musicxml.org/dtds/partwise.dtd">',
           '<score-partwise version="3.1">',
           f"<work><work-title>{escape(title)}</work-title></work>",
           f'<identification><creator type="composer">{escape(composer)}</creator>'
           "<encoding><software>claude_halation/src/build.py</software></encoding></identification>"]
    # scaling: staff_mm millimetres per 40 tenths
    tenths_per_mm = 40 / staff_mm
    width_t = round(215.9 * tenths_per_mm)
    height_t = round(279.4 * tenths_per_mm)
    margin = round(12 * tenths_per_mm)
    out.append(f"<defaults><scaling><millimeters>{staff_mm}</millimeters><tenths>40</tenths></scaling>"
               f"<page-layout><page-height>{height_t}</page-height><page-width>{width_t}</page-width>"
               f'<page-margins type="both"><left-margin>{margin}</left-margin>'
               f"<right-margin>{margin}</right-margin><top-margin>{margin}</top-margin>"
               f"<bottom-margin>{margin}</bottom-margin></page-margins></page-layout></defaults>")
    out.append(f'<credit page="1"><credit-type>title</credit-type><credit-words justify="center" '
               f'valign="top" font-size="24" default-x="{width_t // 2}" default-y="{height_t - margin}">'
               f"{escape(title)}</credit-words></credit>")
    if subtitle:
        out.append(f'<credit page="1"><credit-type>subtitle</credit-type><credit-words justify="center" '
                   f'valign="top" font-size="12" default-x="{width_t // 2}" '
                   f'default-y="{height_t - margin - 60}">{escape(subtitle)}</credit-words></credit>')
    out.append(f'<credit page="1"><credit-type>composer</credit-type><credit-words justify="right" '
               f'valign="top" font-size="10" default-x="{width_t - margin}" '
               f'default-y="{height_t - margin - 90}">{escape(composer)}</credit-words></credit>')
    out.append("<part-list>")
    for i, ps in enumerate(parts):
        out.append(f'<score-part id="{ps.pid}"><part-name>{escape(ps.name)}</part-name>'
                   f"<part-abbreviation>{escape(ps.abbrev)}</part-abbreviation>"
                   f'<score-instrument id="{ps.pid}-I1"><instrument-name>{escape(ps.name)}'
                   f"</instrument-name><instrument-sound>{ps.sound}</instrument-sound></score-instrument>"
                   f'<midi-instrument id="{ps.pid}-I1"><midi-channel>{i + 1}</midi-channel>'
                   f"<midi-program>{ps.program}</midi-program><volume>{ps.volume}</volume>"
                   f"<pan>{ps.pan}</pan></midi-instrument></score-part>")
    out.append("</part-list>")

    nbars = len(parts[0].bars)
    sys_starts = set(layout.system_breaks if layout.system_breaks is not None
                     else range(0, nbars, layout.bars_per_system))
    for pi, ps in enumerate(parts):
        out.append(f'<part id="{ps.pid}">')
        part_bars = ps.bars
        if ps.chords and ps.show_chords:
            part_bars = split_at(ps.bars, {c.tick for bar in ps.chords for c in bar})
        for bi, bar in enumerate(part_bars):
            number = bi if layout.pickup else bi + 1
            attrs = ' implicit="yes"' if (layout.pickup and bi == 0) else ""
            out.append(f'<measure number="{number}"{attrs}>')
            if bi in layout.page_breaks and bi > 0:
                out.append('<print new-page="yes"/>')
            elif bi in sys_starts and bi > 0:
                out.append('<print new-system="yes"/>')
            # left barline (repeat start / endings)
            left = []
            if layout.repeat_start == bi:
                left.append('<bar-style>heavy-light</bar-style><repeat direction="forward"/>')
            for first, last, num, label in layout.endings:
                if bi == first:
                    left.append(f'<ending number="{num}" type="start">{escape(label)}</ending>')
            if left:
                out.append('<barline location="left">' + "".join(left) + "</barline>")
            if bi == 0:
                clef = ("<clef><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change></clef>"
                        if ps.clef == "G8vb" else "<clef><sign>G</sign><line>2</line></clef>")
                trans = ""
                if ps.transpose:
                    st, se = ps.transpose
                    trans = f"<transpose><diatonic>{-st}</diatonic><chromatic>{-se}</chromatic></transpose>"
                out.append(f"<attributes><divisions>{DIV}</divisions><key><fifths>0</fifths>"
                           f"<mode>none</mode></key><time><beats>4</beats><beat-type>4</beat-type></time>"
                           f"{clef}{trans}</attributes>")
            if pi == 0:
                if bi == 0 and layout.tempo_text:
                    inner = _words(layout.tempo_text + "  ", italic=False, bold=True)
                    sound = ""
                    if layout.tempo_bpm:
                        inner += ("<direction-type><metronome parentheses=\"no\"><beat-unit>quarter"
                                  f"</beat-unit><per-minute>{layout.tempo_bpm}</per-minute>"
                                  "</metronome></direction-type>")
                        sound = f'<sound tempo="{layout.tempo_bpm}"/>'
                    out.append(_direction(inner, "above", sound))
                if bi in layout.rehearsal:
                    out.append(_direction(
                        f'<direction-type><rehearsal enclosure="square">{escape(layout.rehearsal[bi])}'
                        "</rehearsal></direction-type>"))
                for t in layout.top_texts.get(bi, []):
                    out.append(_direction(_words(t, italic=False, bold=True, size=10)))
            # events
            bar_chords = list(ps.chords[bi]) if (ps.chords and ps.show_chords) else []
            if ps.transpose and bar_chords:
                bar_chords = [c.transposed(*ps.transpose) for c in bar_chords]
            whole_rest = len(bar) == 1 and bar[0].kind == "rest" and bar[0].dur == BAR
            for ev in bar:
                # chord symbols that begin during this event (offset if mid-event)
                for ch in [c for c in bar_chords if ev.tick <= c.tick < ev.tick + ev.dur]:
                    out.append(_harmony_xml(ch, ch.tick - ev.tick))
                    bar_chords.remove(ch)
                wev = _written(ev, ps.transpose)
                if ev.hairpin == "stop":
                    out.append(_direction('<direction-type><wedge type="stop"/></direction-type>', "below"))
                if ev.dynamic:
                    out.append(_direction(f"<direction-type><dynamics><{ev.dynamic}/></dynamics>"
                                          "</direction-type>", "below"))
                if ev.hairpin in ("crescendo", "diminuendo"):
                    out.append(_direction(f'<direction-type><wedge type="{ev.hairpin}"/>'
                                          "</direction-type>", "below"))
                for place, text in ev.texts:
                    out.append(_direction(_words(text), place))
                if ev.kind == "rest":
                    out.append(_rest_xml(ev, whole_rest))
                else:
                    for g in wev.graces:
                        out.append(_grace_xml(g))
                    for k, p in enumerate(wev.pitches):
                        out.append(_note_xml(wev, p, k > 0))
            if bar_chords:
                raise ValueError(f"{ps.pid} bar {bi + 1}: unplaced chords {bar_chords}")
            # right barline
            right = []
            for first, last, num, label in layout.endings:
                if bi == last:
                    kind = "stop" if layout.repeat_end == bi or num == "1" else "discontinue"
                    right.append(f'<ending number="{num}" type="{kind}"/>')
            if layout.repeat_end == bi:
                out.append('<barline location="right"><bar-style>light-heavy</bar-style>'
                           + "".join(right) + '<repeat direction="backward"/></barline>')
            elif bi == nbars - 1 and layout.final_bar:
                out.append('<barline location="right"><bar-style>light-heavy</bar-style>'
                           + "".join(right) + "</barline>")
            elif bi in layout.double_bars or right:
                style = "<bar-style>light-light</bar-style>" if bi in layout.double_bars else ""
                out.append('<barline location="right">' + style + "".join(right) + "</barline>")
            out.append("</measure>")
        out.append("</part>")
    out.append("</score-partwise>")
    return "\n".join(out)
