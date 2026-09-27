#!/usr/bin/env python3
"""Simple audio-to-MusicXML melody transcription.

This is intentionally dependency-light: it uses ffmpeg for decoding and
numpy/scipy for a rough monophonic pitch track, then writes MusicXML directly.
If you have a lead-sheet MusicXML chart, its chord symbols are repeated under
the detected melody.
"""

from __future__ import annotations

import argparse
import copy
import math
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import median_filter
from scipy.signal import butter, sosfiltfilt, stft


INSTRUMENT_PROFILES = {
    "flugelhorn": (53, 82, "treble"),
    "melody": (48, 76, "treble"),
    "tuba": (34, 65, "bass"),
    "bass": (34, 64, "bass"),
    "voice": (45, 76, "treble"),
}

NOTE_TYPES = {
    16: ("whole", 0),
    12: ("half", 1),
    8: ("half", 0),
    6: ("quarter", 1),
    4: ("quarter", 0),
    3: ("eighth", 1),
    2: ("eighth", 0),
    1: ("16th", 0),
}
SPLIT_DURATIONS = (16, 12, 8, 6, 4, 3, 2, 1)

FLAT_NAMES = {
    0: ("C", 0),
    1: ("D", -1),
    2: ("D", 0),
    3: ("E", -1),
    4: ("E", 0),
    5: ("F", 0),
    6: ("G", -1),
    7: ("G", 0),
    8: ("A", -1),
    9: ("A", 0),
    10: ("B", -1),
    11: ("B", 0),
}
SHARP_NAMES = {
    0: ("C", 0),
    1: ("C", 1),
    2: ("D", 0),
    3: ("D", 1),
    4: ("E", 0),
    5: ("F", 0),
    6: ("F", 1),
    7: ("G", 0),
    8: ("G", 1),
    9: ("A", 0),
    10: ("A", 1),
    11: ("B", 0),
}


@dataclass
class Chart:
    title: str
    composer: str
    measures: list[list[tuple[int, ET.Element]]]
    fifths: int
    mode: str
    beats: int
    beat_type: int


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"Required command not found: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Command failed with exit code {exc.returncode}: {' '.join(cmd)}") from exc


def decode_audio(audio: Path, sample_rate: int) -> tuple[int, np.ndarray]:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required for audio decoding.")

    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "audio.wav"
        run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(audio),
                "-ac",
                "1",
                "-ar",
                str(sample_rate),
                str(wav),
            ]
        )
        sr, data = wavfile.read(wav)

    if data.ndim > 1:
        data = data.mean(axis=1)
    if np.issubdtype(data.dtype, np.integer):
        data = data.astype(np.float32) / np.iinfo(data.dtype).max
    else:
        data = data.astype(np.float32)
    data = data - float(np.mean(data))
    peak = float(np.max(np.abs(data)))
    if peak > 0:
        data = data / peak
    return sr, data


def midi_to_freq(midi: np.ndarray | float) -> np.ndarray | float:
    return 440.0 * (2.0 ** ((np.asarray(midi) - 69.0) / 12.0))


def spectral_pitch_track(
    audio: np.ndarray,
    sr: int,
    min_midi: int,
    max_midi: int,
    min_confidence: float,
    high_bias: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    low = max(25.0, float(midi_to_freq(min_midi)) * 0.75)
    high = min(sr / 2 - 100.0, float(midi_to_freq(max_midi)) * 4.5)
    sos = butter(4, [low, high], btype="bandpass", fs=sr, output="sos")
    filtered = sosfiltfilt(sos, audio).astype(np.float32)

    frame = 4096
    hop = 512
    freqs, times, zxx = stft(
        filtered,
        fs=sr,
        window="hann",
        nperseg=frame,
        noverlap=frame - hop,
        boundary=None,
        padded=False,
    )
    mag = np.abs(zxx).astype(np.float32)

    candidates = np.arange(min_midi, max_midi + 1)
    candidate_freqs = midi_to_freq(candidates)
    scores = np.zeros((len(candidates), mag.shape[1]), dtype=np.float32)
    for harmonic, weight in ((1, 1.0), (2, 0.55), (3, 0.35), (4, 0.2)):
        hfreqs = candidate_freqs * harmonic
        valid = hfreqs < freqs[-1]
        bins = np.searchsorted(freqs, hfreqs[valid])
        bins = np.clip(bins, 0, len(freqs) - 1)
        scores[valid] += weight * mag[bins]

    if high_bias:
        pos = np.linspace(0.0, 1.0, len(candidates), dtype=np.float32)[:, None]
        scores *= 1.0 + high_bias * pos

    scores = median_filter(scores, size=(1, 3))
    best_idx = np.argmax(scores, axis=0)
    best_scores = scores[best_idx, np.arange(scores.shape[1])]
    background = np.percentile(scores, 65, axis=0) + 1e-7
    confidence = best_scores / background

    energy = np.sqrt(np.mean(mag * mag, axis=0))
    energy_floor = np.quantile(energy, 0.35) * 1.25
    voiced = (confidence >= min_confidence) & (energy > energy_floor)

    midi = candidates[best_idx].astype(np.int16)
    midi[~voiced] = -1
    return times, midi, confidence


def smooth_unit_pitches(
    times: np.ndarray,
    frame_midi: np.ndarray,
    duration: float,
    tempo: float,
    quant: int,
    total_units: int,
    min_note_units: int,
    max_gap_units: int,
) -> np.ndarray:
    unit_seconds = 60.0 / tempo * (4.0 / quant)
    unit_pitches = np.full(total_units, -1, dtype=np.int16)
    if len(times) == 0:
        return unit_pitches

    for unit in range(total_units):
        center = (unit + 0.5) * unit_seconds
        if center > duration:
            break
        idx = int(np.searchsorted(times, center))
        lo = max(0, idx - 2)
        hi = min(len(times), idx + 3)
        values = frame_midi[lo:hi]
        values = values[values >= 0]
        if len(values):
            counts = np.bincount(values)
            unit_pitches[unit] = int(np.argmax(counts))

    if len(unit_pitches) >= 5:
        shifted = unit_pitches.copy()
        shifted[shifted < 0] = 0
        voiced = unit_pitches >= 0
        smoothed = median_filter(shifted, size=3)
        unit_pitches[voiced] = smoothed[voiced]

    unit_pitches = merge_short_gaps(unit_pitches, max_gap_units)
    unit_pitches = remove_short_notes(unit_pitches, min_note_units)
    return unit_pitches


def merge_short_gaps(pitches: np.ndarray, max_gap: int) -> np.ndarray:
    if max_gap <= 0:
        return pitches
    out = pitches.copy()
    i = 0
    while i < len(out):
        if out[i] != -1:
            i += 1
            continue
        j = i
        while j < len(out) and out[j] == -1:
            j += 1
        if j - i <= max_gap and i > 0 and j < len(out) and out[i - 1] == out[j]:
            out[i:j] = out[i - 1]
        i = j
    return out


def remove_short_notes(pitches: np.ndarray, min_units: int) -> np.ndarray:
    if min_units <= 1:
        return pitches
    out = pitches.copy()
    i = 0
    while i < len(out):
        j = i + 1
        while j < len(out) and out[j] == out[i]:
            j += 1
        if out[i] >= 0 and j - i < min_units:
            left = out[i - 1] if i > 0 else -1
            right = out[j] if j < len(out) else -1
            out[i:j] = left if left == right else -1
        i = j
    return out


def parse_chart(path: Path, quant: int) -> Chart:
    tree = ET.parse(path)
    root = tree.getroot()
    title = root.findtext("./work/work-title") or path.stem
    composer = ""
    for creator in root.findall("./identification/creator"):
        if creator.attrib.get("type") == "composer":
            composer = creator.text or ""
            break

    first = root.find("./part/measure")
    if first is None:
        raise SystemExit(f"No measures found in chart: {path}")

    divisions = int(first.findtext("./attributes/divisions") or "1")
    fifths = int(first.findtext("./attributes/key/fifths") or "0")
    mode = first.findtext("./attributes/key/mode") or "major"
    beats = int(first.findtext("./attributes/time/beats") or "4")
    beat_type = int(first.findtext("./attributes/time/beat-type") or "4")
    units_per_quarter = quant // 4

    measures: list[list[tuple[int, ET.Element]]] = []
    for measure in root.findall("./part/measure"):
        offset_quarter_divisions = 0
        entries: list[tuple[int, ET.Element]] = []
        for child in list(measure):
            if child.tag in {"harmony", "direction"}:
                offset_units = round(offset_quarter_divisions / divisions * units_per_quarter)
                entries.append((offset_units, copy.deepcopy(child)))
            elif child.tag == "note":
                duration = child.findtext("duration")
                if duration:
                    offset_quarter_divisions += int(duration)
        measures.append(entries)

    return Chart(title, composer, measures, fifths, mode, beats, beat_type)


def infer_tempo_and_repeats(duration: float, chart: Chart) -> tuple[float, int]:
    beats_per_form = len(chart.measures) * chart.beats * (4.0 / chart.beat_type)
    candidates: list[tuple[float, float, int]] = []
    for repeats in range(1, 9):
        tempo = beats_per_form * repeats * 60.0 / duration
        if 60.0 <= tempo <= 180.0:
            # Medium swing practice recordings are more likely near 100 than 150.
            score = abs(math.log(tempo / 100.0)) + 0.05 * max(0, repeats - 1)
            candidates.append((score, tempo, repeats))
    if not candidates:
        return 120.0, max(1, round(duration / (beats_per_form * 60.0 / 120.0)))
    _, tempo, repeats = min(candidates)
    return tempo, repeats


def split_duration(units: int) -> list[int]:
    pieces: list[int] = []
    remaining = units
    while remaining > 0:
        for duration in SPLIT_DURATIONS:
            if duration <= remaining:
                pieces.append(duration)
                remaining -= duration
                break
    return pieces


def pitch_name(midi: int, prefer_flats: bool) -> tuple[str, int, int]:
    pc = midi % 12
    octave = midi // 12 - 1
    step, alter = (FLAT_NAMES if prefer_flats else SHARP_NAMES)[pc]
    return step, alter, octave


def add_text(parent: ET.Element, tag: str, text: str | int | float) -> ET.Element:
    child = ET.SubElement(parent, tag)
    child.text = str(text)
    return child


def add_note(
    measure: ET.Element,
    midi: int,
    duration_units: int,
    prefer_flats: bool,
    tie_stop: bool = False,
    tie_start: bool = False,
) -> None:
    pieces = split_duration(duration_units)
    for idx, piece in enumerate(pieces):
        note = ET.SubElement(measure, "note")
        if midi < 0:
            ET.SubElement(note, "rest")
        else:
            pitch = ET.SubElement(note, "pitch")
            step, alter, octave = pitch_name(midi, prefer_flats)
            add_text(pitch, "step", step)
            if alter:
                add_text(pitch, "alter", alter)
            add_text(pitch, "octave", octave)
            if tie_stop or idx > 0:
                ET.SubElement(note, "tie", {"type": "stop"})
            if tie_start or idx < len(pieces) - 1:
                ET.SubElement(note, "tie", {"type": "start"})
        add_text(note, "duration", piece)
        note_type, dots = NOTE_TYPES[piece]
        add_text(note, "type", note_type)
        for _ in range(dots):
            ET.SubElement(note, "dot")
        if midi >= 0 and (tie_stop or tie_start or len(pieces) > 1):
            notations = ET.SubElement(note, "notations")
            if tie_stop or idx > 0:
                ET.SubElement(notations, "tied", {"type": "stop"})
            if tie_start or idx < len(pieces) - 1:
                ET.SubElement(notations, "tied", {"type": "start"})


def build_musicxml(
    out: Path,
    title: str,
    composer: str,
    unit_pitches: np.ndarray,
    chart: Chart | None,
    tempo: float,
    quant: int,
    clef: str,
    repeats: int,
) -> None:
    beats = chart.beats if chart else 4
    beat_type = chart.beat_type if chart else 4
    fifths = chart.fifths if chart else 0
    mode = chart.mode if chart else "major"
    measures_per_form = len(chart.measures) if chart else 0
    units_per_measure = int(beats * quant / beat_type)
    total_measures = math.ceil(len(unit_pitches) / units_per_measure)
    if chart:
        total_measures = max(total_measures, len(chart.measures) * repeats)
    total_units = total_measures * units_per_measure
    if len(unit_pitches) < total_units:
        unit_pitches = np.pad(unit_pitches, (0, total_units - len(unit_pitches)), constant_values=-1)
    else:
        unit_pitches = unit_pitches[:total_units]

    root = ET.Element("score-partwise", {"version": "3.1"})
    work = ET.SubElement(root, "work")
    add_text(work, "work-title", title)
    identification = ET.SubElement(root, "identification")
    if composer:
        add_text(identification, "creator", composer).set("type", "composer")
    encoding = ET.SubElement(identification, "encoding")
    add_text(encoding, "software", "transcribe.py")

    part_list = ET.SubElement(root, "part-list")
    score_part = ET.SubElement(part_list, "score-part", {"id": "P1"})
    add_text(score_part, "part-name", "Melody")

    part = ET.SubElement(root, "part", {"id": "P1"})
    prefer_flats = fifths < 0
    for measure_idx in range(total_measures):
        measure = ET.SubElement(part, "measure", {"number": str(measure_idx + 1)})
        if measure_idx and measure_idx % 4 == 0:
            ET.SubElement(measure, "print", {"new-system": "yes"})
        if measure_idx == 0:
            attrs = ET.SubElement(measure, "attributes")
            add_text(attrs, "divisions", quant // 4)
            key = ET.SubElement(attrs, "key")
            add_text(key, "fifths", fifths)
            add_text(key, "mode", mode)
            time = ET.SubElement(attrs, "time")
            add_text(time, "beats", beats)
            add_text(time, "beat-type", beat_type)
            clef_el = ET.SubElement(attrs, "clef")
            if clef == "bass":
                add_text(clef_el, "sign", "F")
                add_text(clef_el, "line", 4)
            else:
                add_text(clef_el, "sign", "G")
                add_text(clef_el, "line", 2)
            direction = ET.SubElement(measure, "direction", {"placement": "above"})
            direction_type = ET.SubElement(direction, "direction-type")
            metronome = ET.SubElement(direction_type, "metronome")
            add_text(metronome, "beat-unit", "quarter")
            add_text(metronome, "per-minute", round(tempo, 2))
            sound = ET.SubElement(measure, "sound")
            sound.set("tempo", f"{tempo:.3f}")

        start_unit = measure_idx * units_per_measure
        end_unit = start_unit + units_per_measure
        measure_pitches = unit_pitches[start_unit:end_unit]

        entries: list[tuple[int, ET.Element]] = []
        if chart and measures_per_form:
            entries = chart.measures[measure_idx % measures_per_form]
        by_offset: dict[int, list[ET.Element]] = {}
        for offset, elem in entries:
            by_offset.setdefault(max(0, min(units_per_measure - 1, offset)), []).append(elem)

        cursor = 0
        while cursor < units_per_measure:
            for elem in by_offset.get(cursor, []):
                measure.append(copy.deepcopy(elem))

            pitch = int(measure_pitches[cursor])
            next_change = cursor + 1
            while next_change < units_per_measure and int(measure_pitches[next_change]) == pitch:
                if next_change in by_offset:
                    break
                next_change += 1

            absolute = start_unit + cursor
            absolute_end = start_unit + next_change
            tie_stop = pitch >= 0 and absolute > 0 and int(unit_pitches[absolute - 1]) == pitch
            tie_start = (
                pitch >= 0
                and absolute_end < len(unit_pitches)
                and int(unit_pitches[absolute_end]) == pitch
            )
            add_note(measure, pitch, next_change - cursor, prefer_flats, tie_stop, tie_start)
            cursor = next_change

        for offset in sorted(k for k in by_offset if k >= units_per_measure):
            for elem in by_offset[offset]:
                measure.append(copy.deepcopy(elem))

    ET.indent(root, space="  ")
    out.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)


def find_default_chart(audio: Path) -> Path | None:
    charts = sorted(audio.parent.glob("*.musicxml"))
    return charts[0] if charts else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe a simple melody from audio to MusicXML, optionally using a chord chart."
    )
    parser.add_argument("audio", type=Path, help="Input audio file: wav, mp3, m4a, etc.")
    parser.add_argument("--chart", type=Path, help="Lead-sheet MusicXML file to use for chords.")
    parser.add_argument("--out", type=Path, help="Output MusicXML path.")
    parser.add_argument("--tempo", type=float, help="Quarter-note BPM. Inferred from chart if omitted.")
    parser.add_argument("--chart-repeats", type=int, help="Number of times to repeat the chart chords.")
    parser.add_argument("--instrument", choices=sorted(INSTRUMENT_PROFILES), default="melody")
    parser.add_argument("--min-midi", type=int, help="Lowest MIDI note to consider.")
    parser.add_argument("--max-midi", type=int, help="Highest MIDI note to consider.")
    parser.add_argument("--clef", choices=("treble", "bass"), help="Output clef.")
    parser.add_argument("--quant", type=int, default=16, choices=(8, 16), help="Rhythmic grid denominator.")
    parser.add_argument("--min-confidence", type=float, default=1.18)
    parser.add_argument("--min-note-units", type=int, default=2, help="Drop notes shorter than this grid length.")
    parser.add_argument("--max-gap-units", type=int, default=1, help="Bridge short gaps between same-pitch notes.")
    parser.add_argument("--high-bias", type=float, default=0.15, help="Favor higher notes in the selected range.")
    parser.add_argument("--sample-rate", type=int, default=22050)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audio = args.audio
    if not audio.exists():
        raise SystemExit(f"Audio file not found: {audio}")

    chart_path = args.chart or find_default_chart(audio)
    chart = parse_chart(chart_path, args.quant) if chart_path else None
    sr, data = decode_audio(audio, args.sample_rate)
    duration = len(data) / sr

    if args.tempo:
        tempo = args.tempo
        if args.chart_repeats:
            repeats = args.chart_repeats
        elif chart:
            form_seconds = len(chart.measures) * chart.beats * (4.0 / chart.beat_type) * 60.0 / tempo
            repeats = max(1, round(duration / form_seconds))
        else:
            repeats = 1
    elif chart:
        tempo, repeats = infer_tempo_and_repeats(duration, chart)
    else:
        tempo, repeats = 120.0, 1

    min_midi, max_midi, profile_clef = INSTRUMENT_PROFILES[args.instrument]
    min_midi = args.min_midi if args.min_midi is not None else min_midi
    max_midi = args.max_midi if args.max_midi is not None else max_midi
    clef = args.clef or profile_clef
    if min_midi >= max_midi:
        raise SystemExit("--min-midi must be lower than --max-midi")

    if chart:
        units_per_measure = int(chart.beats * args.quant / chart.beat_type)
        total_units = len(chart.measures) * repeats * units_per_measure
    else:
        unit_seconds = 60.0 / tempo * (4.0 / args.quant)
        total_units = math.ceil(duration / unit_seconds)

    print(f"Audio duration: {duration:.2f}s", file=sys.stderr)
    if chart_path:
        print(f"Chart: {chart_path} ({len(chart.measures)} measures x {repeats})", file=sys.stderr)
    print(f"Tempo: {tempo:.2f} BPM; range MIDI {min_midi}-{max_midi}; clef {clef}", file=sys.stderr)

    times, frame_midi, _confidence = spectral_pitch_track(
        data,
        sr,
        min_midi,
        max_midi,
        args.min_confidence,
        args.high_bias,
    )
    unit_pitches = smooth_unit_pitches(
        times,
        frame_midi,
        duration,
        tempo,
        args.quant,
        total_units,
        args.min_note_units,
        args.max_gap_units,
    )

    out = args.out or Path("out") / f"{audio.stem}.musicxml"
    title = f"{audio.stem} melody"
    composer = chart.composer if chart else ""
    build_musicxml(out, title, composer, unit_pitches, chart, tempo, args.quant, clef, repeats)
    print(f"Wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
