"""Write parsed measures to a MusicXML 3.1 partwise score."""

from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import escape

from notation import BAR, DIV, Measure

PAGE_W, PAGE_H, MARGIN = 1234, 1597, 75   # US Letter at 7 mm staff height (defaults)


def page_tenths(staff_mm: float):
    """US Letter page width, height and a 13 mm margin, in tenths for this staff size."""
    k = 40 / staff_mm
    return round(215.9 * k), round(279.4 * k), round(13.1 * k)


@dataclass
class PartSpec:
    pid: str
    name: str
    abbr: str
    measures: list
    clef: str = "treble"          # "treble" or "treble8vb" (guitar)
    transpose: tuple | None = None  # (diatonic, chromatic) written minus concert, e.g. (1, 2)
    program: int = 57             # General MIDI program, 1-based
    show_chords: bool = True
    simplify: bool = False        # respell awkward accidentals in the written part


@dataclass
class ScoreSpec:
    title: str
    parts: list
    subtitle: str = ""
    composer: str = ""
    left_label: str = ""          # e.g. "Trumpet in Bb" printed top-left
    tempo_text: str = ""
    bpm: int | None = None
    annotations: bool = False
    credits_extra: list = field(default_factory=list)  # (text, x-fraction, y, size, justify)
    staff_mm: float = 7.0
    system_distance: int = 110    # tenths between systems (MuseScore: min system distance)


def _credit(text, x, y, size, justify="center", valign="top", bold=False):
    weight = ' font-weight="bold"' if bold else ""
    return (f'<credit page="1"><credit-words default-x="{x}" default-y="{y}" '
            f'font-size="{size}"{weight} justify="{justify}" valign="{valign}">'
            f"{escape(text)}</credit-words></credit>")


def _pitch_xml(p) -> str:
    alter = f"<alter>{p.alter}</alter>" if p.alter else ""
    return f"<pitch><step>{p.step}</step>{alter}<octave>{p.octave}</octave></pitch>"


def _beams(events) -> dict:
    """Return {event index: [(number, value), ...]} for eighth/16th groups."""
    beams = {}
    groups, cur = [], []

    def flush():
        if len(cur) >= 2:
            groups.append(list(cur))
        cur.clear()

    for i, ev in enumerate(events):
        beamable = ev.pitches and ev.ntype in ("eighth", "16th")
        if not beamable:
            flush()
            continue
        if cur:
            prev = events[cur[-1]]
            same_half = (prev.start // (BAR // 2)) == (ev.start // (BAR // 2))
            same_tuplet = bool(prev.tuplet) == bool(ev.tuplet) and \
                (not ev.tuplet or prev.tuplet in ("start", "mid"))
            contiguous = prev.start + prev.dur == ev.start
            if not (same_half and same_tuplet and contiguous):
                flush()
        cur.append(i)
        if ev.tuplet == "stop":
            flush()
    flush()
    for g in groups:
        for k, i in enumerate(g):
            v = "begin" if k == 0 else "end" if k == len(g) - 1 else "continue"
            beams[i] = [(1, v)]
        # second-level beams for sixteenths
        sixteen = [events[i].ntype == "16th" for i in g]
        for k, i in enumerate(g):
            if not sixteen[k]:
                continue
            left = k > 0 and sixteen[k - 1]
            right = k < len(g) - 1 and sixteen[k + 1]
            if left and right:
                v = "continue"
            elif right:
                v = "begin"
            elif left:
                v = "end"
            else:
                v = "backward hook" if k > 0 else "forward hook"
            beams[i].append((2, v))
    return beams


def _direction(kind, value, annotations) -> str:
    if kind == "dyn":
        return (f'<direction placement="below"><direction-type><dynamics><{value}/>'
                f"</dynamics></direction-type></direction>")
    if kind == "wedge":
        t = {"cresc": "crescendo", "dim": "diminuendo", "endw": "stop"}[value]
        return (f'<direction placement="below"><direction-type><wedge type="{t}"/>'
                f"</direction-type></direction>")
    if kind == "txt":
        return (f'<direction placement="above"><direction-type><words font-style="italic">'
                f"{escape(value)}</words></direction-type></direction>")
    if kind == "ann":
        if not annotations:
            return ""
        return (f'<direction placement="below"><direction-type><words font-size="7.5" '
                f'color="#5A4A8A">{escape(value)}</words></direction-type></direction>')
    raise ValueError(kind)


ART_XML = {"acc": "<accent/>", "stac": "<staccato/>", "ten": "<tenuto/>",
           "marc": "<strong-accent/>", "fall": "<falloff/>", "doit": "<doit/>",
           "scoop": "<scoop/>"}


def _note_xml(ev, pitch, is_chord_tone, beam, dia_chrom, simplify) -> str:
    x = ["<note>"]
    if is_chord_tone:
        x.append("<chord/>")
    if pitch is None:
        x.append("<rest/>")
    else:
        p = pitch.transpose(*dia_chrom, simplify=simplify) if dia_chrom else pitch
        x.append(_pitch_xml(p))
    x.append(f"<duration>{ev.dur}</duration>")
    if pitch is not None:
        if ev.tie_stop:
            x.append('<tie type="stop"/>')
        if ev.tie_start:
            x.append('<tie type="start"/>')
    x.append("<voice>1</voice>")
    x.append(f"<type>{ev.ntype}</type>")
    x.extend("<dot/>" for _ in range(ev.dots))
    if ev.tuplet:
        x.append("<time-modification><actual-notes>3</actual-notes>"
                 "<normal-notes>2</normal-notes></time-modification>")
    if beam and not is_chord_tone:
        x.extend(f'<beam number="{n}">{v}</beam>' for n, v in beam)
    nots = []
    if pitch is not None:
        if ev.tie_stop:
            nots.append('<tied type="stop"/>')
        if ev.tie_start:
            nots.append('<tied type="start"/>')
    if not is_chord_tone:
        if ev.slur_start:
            nots.append('<slur type="start" number="1"/>')
        if ev.slur_stop:
            nots.append('<slur type="stop" number="1"/>')
        if ev.tuplet == "start":
            nots.append('<tuplet type="start" bracket="yes"/>')
        if ev.tuplet == "stop":
            nots.append('<tuplet type="stop"/>')
        arts = [ART_XML[a] for a in ev.arts if a in ART_XML]
        if arts:
            nots.append("<articulations>" + "".join(arts) + "</articulations>")
        if "ferm" in ev.arts:
            nots.append('<fermata type="upright"/>')
    if nots:
        x.append("<notations>" + "".join(nots) + "</notations>")
    x.append("</note>")
    return "".join(x)


def _measure_xml(part: PartSpec, idx: int, m: Measure, score: ScoreSpec, first_part: bool):
    x = [f'<measure number="X{idx + 1}" implicit="yes">' if m.implicit
         else f'<measure number="{idx + 1}">']
    if idx > 0 and m.new_page:
        x.append('<print new-page="yes"/>')
    elif idx > 0 and m.new_system:
        x.append('<print new-system="yes"/>')
    if idx == 0:
        x.append(f"<attributes><divisions>{DIV}</divisions><key><fifths>0</fifths></key>"
                 "<time><beats>4</beats><beat-type>4</beat-type></time>")
        if part.clef == "treble8vb":
            x.append("<clef><sign>G</sign><line>2</line>"
                     "<clef-octave-change>-1</clef-octave-change></clef>")
        else:
            x.append("<clef><sign>G</sign><line>2</line></clef>")
        if part.transpose:
            dia, chrom = part.transpose
            x.append(f"<transpose><diatonic>{-dia}</diatonic>"
                     f"<chromatic>{-chrom}</chromatic></transpose>")
        x.append("</attributes>")
        if first_part and (score.tempo_text or score.bpm):
            label = score.tempo_text
            if score.bpm:
                label = f"{label}   ♩ = {score.bpm}".strip()
            x.append(f'<direction placement="above"><direction-type><words font-weight="bold">'
                     f"{escape(label)}</words></direction-type>"
                     + (f'<sound tempo="{score.bpm}"/>' if score.bpm else "")
                     + "</direction>")
    if m.rehearsal and first_part:
        x.append(f'<direction placement="above"><direction-type><rehearsal>'
                 f"{escape(m.rehearsal)}</rehearsal></direction-type></direction>")
    chords = []
    if part.show_chords:
        for tick, ch in m.chords:
            chords.append((tick, ch.transpose(*part.transpose) if part.transpose else ch))
    texts = list(m.texts)
    beams = _beams(m.events)
    for i, ev in enumerate(m.events):
        for tick, text, placement in [t for t in texts if t[0] <= ev.start]:
            if first_part or placement == "all":
                x.append(f'<direction placement="above"><direction-type><words '
                         f'font-weight="bold">{escape(text)}</words></direction-type></direction>')
            texts.remove((tick, text, placement))
        for tick, ch in [c for c in chords if c[0] < ev.start + ev.dur]:
            x.append(ch.xml(offset=max(0, tick - ev.start)))
            chords.remove((tick, ch))
        for kind, value in ev.dirs:
            x.append(_direction(kind, value, score.annotations))
        pitches = ev.pitches or [None]
        for k, p in enumerate(pitches):
            x.append(_note_xml(ev, p, k > 0, beams.get(i), part.transpose, part.simplify))
    if m.barline:
        x.append(f'<barline location="right"><bar-style>{m.barline}</bar-style></barline>')
    x.append("</measure>")
    return "".join(x)


def write_score(score: ScoreSpec, path: str) -> None:
    PAGE_W, PAGE_H, MARGIN = page_tenths(score.staff_mm)
    x = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
         '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" '
         '"http://www.musicxml.org/dtds/partwise.dtd">',
         '<score-partwise version="3.1">',
         f"<work><work-title>{escape(score.title)}</work-title></work>",
         f"<movement-title>{escape(score.title)}</movement-title>",
         "<identification>"
         + (f'<creator type="composer">{escape(score.composer)}</creator>' if score.composer else "")
         + "<encoding><software>claude_parallax/src/musicxml.py</software></encoding>"
         "</identification>",
         f"<defaults><scaling><millimeters>{score.staff_mm}</millimeters><tenths>40</tenths>"
         "</scaling>"
         f"<page-layout><page-height>{PAGE_H}</page-height><page-width>{PAGE_W}</page-width>"
         f'<page-margins type="both"><left-margin>{MARGIN}</left-margin>'
         f"<right-margin>{MARGIN}</right-margin><top-margin>{MARGIN}</top-margin>"
         f"<bottom-margin>{MARGIN}</bottom-margin></page-margins></page-layout>"
         "<system-layout><system-margins><left-margin>0</left-margin><right-margin>0"
         f"</right-margin></system-margins><system-distance>{score.system_distance}"
         "</system-distance>"
         "<top-system-distance>190</top-system-distance></system-layout>"
         "<staff-layout><staff-distance>95</staff-distance></staff-layout>"
         "</defaults>"]
    top = PAGE_H - MARGIN
    x.append(_credit(score.title, PAGE_W / 2, top, 24, bold=True))
    if score.subtitle:
        x.append(_credit(score.subtitle, PAGE_W / 2, top - 45, 11))
    label_y = top - 45     # same line as the subtitle, flush left / right
    if score.composer:
        x.append(_credit(score.composer, PAGE_W - MARGIN, label_y, 10, justify="right"))
    if score.left_label:
        x.append(_credit(score.left_label, MARGIN, label_y, 11, justify="left", bold=True))
    for text, fx, cy, size, justify in score.credits_extra:
        # cy > 0: absolute; cy < 0: offset below the top margin; 0: bottom margin
        y = cy if cy > 0 else (top + cy if cy < 0 else MARGIN)
        x.append(_credit(text, fx * PAGE_W, y, size, justify=justify))
    x.append("<part-list>")
    for part in score.parts:
        x.append(f'<score-part id="{part.pid}"><part-name>{escape(part.name)}</part-name>'
                 f"<part-abbreviation>{escape(part.abbr)}</part-abbreviation>"
                 f'<score-instrument id="{part.pid}-I1"><instrument-name>{escape(part.name)}'
                 f"</instrument-name></score-instrument>"
                 f'<midi-instrument id="{part.pid}-I1"><midi-channel>{score.parts.index(part) + 1}'
                 f"</midi-channel><midi-program>{part.program}</midi-program></midi-instrument>"
                 "</score-part>")
    x.append("</part-list>")
    for pi, part in enumerate(score.parts):
        x.append(f'<part id="{part.pid}">')
        for idx, m in enumerate(part.measures):
            x.append(_measure_xml(part, idx, m, score, pi == 0))
        x.append("</part>")
    x.append("</score-partwise>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(x))
