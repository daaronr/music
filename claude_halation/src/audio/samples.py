"""Sample loading and a small numpy sampler.

Sources:
  * Apple GarageBand / Logic sampler instruments (.exs + AIFF/CAF), including
    Logic's "consolidated" sample files (one long PCM file per instrument).
  * University of Iowa MIS trumpet recordings (one AIFF per chromatic run),
    cut into single notes here.
"""
from __future__ import annotations

import struct
from functools import lru_cache
from pathlib import Path

import numpy as np

from exs import read_exs

SR = 44100
CACHE = Path(__file__).resolve().parents[2] / "build" / "samples"


# ------------------------------------------------------------------ file readers

def read_aiff(path: str | Path) -> np.ndarray:
    """16-bit big-endian AIFF -> float32 array [frames, channels]."""
    raw = Path(path).read_bytes()
    assert raw[:4] == b"FORM" and raw[8:12] in (b"AIFF", b"AIFC"), path
    pos, channels, data = 12, 1, None
    while pos + 8 <= len(raw):
        cid, size = raw[pos:pos + 4], struct.unpack(">I", raw[pos + 4:pos + 8])[0]
        body = raw[pos + 8:pos + 8 + size]
        if cid == b"COMM":
            channels = struct.unpack(">h", body[0:2])[0]
            bits = struct.unpack(">h", body[6:8])[0]
            assert bits == 16, (path, bits)
        elif cid == b"SSND":
            offset = struct.unpack(">I", body[0:4])[0]
            data = np.frombuffer(body[8 + offset:], dtype=">i2")
        pos += 8 + size + (size & 1)
    frames = len(data) // channels
    return (data[:frames * channels].reshape(frames, channels).astype(np.float32) / 32768.0)


@lru_cache(maxsize=None)
def caf_pcm(path: str) -> np.ndarray:
    """Memory-map a big-endian 16-bit PCM CAF (Logic consolidated files)."""
    raw = Path(path).read_bytes()[:1 << 16]
    assert raw[:4] == b"caff", path
    pos, channels, data_off = 8, 2, None
    while pos + 12 <= len(raw):
        ctype = raw[pos:pos + 4]
        size = struct.unpack(">q", raw[pos + 4:pos + 12])[0]
        if ctype == b"desc":
            channels = struct.unpack(">I", raw[pos + 12 + 24:pos + 12 + 28])[0]
        if ctype == b"data":
            data_off = pos + 12 + 4          # skip edit count
            break
        pos += 12 + size
    mm = np.memmap(path, dtype=">i2", mode="r", offset=data_off)
    frames = len(mm) // channels
    return mm[:frames * channels].reshape(frames, channels)


# ------------------------------------------------------------------ resampling helpers

def stretch(x: np.ndarray, ratio: float | np.ndarray, n_out: int) -> np.ndarray:
    """Read x at a (possibly time-varying) playback-rate ratio; linear interp."""
    if np.isscalar(ratio):
        pos = np.arange(n_out, dtype=np.float64) * ratio
    else:
        pos = np.concatenate([[0.0], np.cumsum(ratio[:-1], dtype=np.float64)])[:n_out]
    pos = pos[pos < len(x) - 1]
    i = pos.astype(np.int64)
    f = (pos - i)[:, None].astype(np.float32)
    return x[i] * (1 - f) + x[i + 1] * f


def fade(n: int, kind: str = "out") -> np.ndarray:
    t = np.linspace(0, 1, max(n, 1), dtype=np.float32)
    curve = np.sin(t * np.pi / 2) ** 2
    return curve if kind == "in" else curve[::-1]


def to_stereo(x: np.ndarray) -> np.ndarray:
    return np.repeat(x, 2, axis=1) if x.shape[1] == 1 else x


# ------------------------------------------------------------------ EXS instruments

class ExsInstrument:
    """Plays zones of an .exs instrument.  Handles consolidated files."""

    def __init__(self, exs_path: str, group_filter=None):
        self.zones, self.samples, self.groups = read_exs(exs_path)
        self.group_filter = group_filter or (lambda g: True)
        self._loaded = {}
        # in consolidated files a zone's audio must stop where the next zone's begins
        starts = {}
        for z in self.zones:
            starts.setdefault(z.sample, set()).add(z.start)
        self.region_end = {}
        for z in self.zones:
            later = [s for s in starts[z.sample] if s > z.start]
            self.region_end[id(z)] = min(later) if later else None

    def _sample_array(self, si: int) -> np.ndarray:
        if si not in self._loaded:
            rec = self.samples[si]
            path = str(Path(rec.path) / rec.filename)
            if path.endswith(".caf"):
                self._loaded[si] = caf_pcm(path)
            else:
                self._loaded[si] = read_aiff(path)
        return self._loaded[si]

    def candidates(self, note: int, vel: int):
        out = []
        for z in self.zones:
            g = self.groups[z.group] if z.group < len(self.groups) else None
            if g is not None and not self.group_filter(g):
                continue
            if not (z.key_lo <= note <= z.key_hi):
                continue
            if g is not None and not (g.vel_lo <= vel <= g.vel_hi):
                continue
            if z.vel_on and not (z.vel_lo <= vel <= z.vel_hi):
                continue
            out.append(z)
        return out

    def zone_audio(self, z, max_frames: int) -> np.ndarray:
        arr = self._sample_array(z.sample)
        end = z.end if z.end > z.start else len(arr)
        if z.loop_on and z.loop_end > end:          # consolidated pianos: the real tail
            end = z.loop_end
        hard = self.region_end.get(id(z))
        if hard is not None:
            end = min(end, hard - 64)
        seg = arr[z.start:min(end, z.start + max_frames)]
        if seg.dtype != np.float32:
            seg = seg.astype(np.float32) / 32768.0
        seg = to_stereo(seg)
        if len(seg) > 2048 and (z.start + max_frames) > end:     # region ran out: fade its tail
            seg = seg.copy()
            seg[-2048:] *= np.linspace(1, 0, 2048, dtype=np.float32)[:, None]
        return seg


def zone_gain(z) -> float:
    return 10 ** (z.volume / 20)
