"""Minimal reader for Logic/GarageBand EXS24 instrument files (.exs).

Only what a playback sampler needs: zones (key/velocity ranges, root key,
tuning, sample start/end, loop) and the sample records they point to.
Layout follows ConvertWithMoss (git-moss) EXS24Block/Zone/Sample readers.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

TYPE_INSTRUMENT, TYPE_ZONE, TYPE_GROUP, TYPE_SAMPLE, TYPE_PARAMS = 0, 1, 2, 3, 4


@dataclass
class Zone:
    name: str
    key: int
    fine: int
    coarse: int
    pan: int
    volume: int
    key_lo: int
    key_hi: int
    vel_lo: int
    vel_hi: int
    vel_on: bool
    pitch: bool
    oneshot: bool
    start: int
    end: int
    loop_start: int
    loop_end: int
    loop_on: bool
    group: int
    sample: int


@dataclass
class SampleRec:
    name: str
    wave_start: int
    length: int
    rate: int
    bits: int
    channels: int
    path: str
    filename: str


@dataclass
class Group:
    name: str
    raw: bytes
    volume: int = 0
    exclusive: int = 0
    vel_lo: int = 0
    vel_hi: int = 127
    release_trigger: int = 0
    rr_pos: int = -1
    enable_type: int = 0
    ctl_value: int = 0
    ctl_lo: int = 0
    ctl_hi: int = 127
    start_note: int = 0
    end_note: int = 127


def _cstr(b: bytes) -> str:
    return b.split(b"\0", 1)[0].decode("latin-1")


def read_exs(path: str | Path):
    data = Path(path).read_bytes()
    pos = 0
    zones, samples, groups = [], [], []
    while pos + 84 <= len(data):
        big = data[pos] == 0
        e = ">" if big else "<"
        typ = data[pos + 3] & 0x0F
        flag80 = data[pos + 3] & 0x80
        size = struct.unpack(e + "I", data[pos + 4:pos + 8])[0]
        if flag80:
            size &= 0x7FFF
        name = _cstr(data[pos + 20:pos + 84])
        body = data[pos + 84:pos + 84 + size]
        if typ == TYPE_ZONE:
            b = body
            opts = b[0]
            u32 = lambda o: struct.unpack(e + "I", b[o:o + 4])[0]
            s8 = lambda v: v - 256 if v > 127 else v
            loop_opts = b[33]
            # skip: 42 bytes after loop direction (35) -> flex at 77, coarse at 80, output 82, group 88
            coarse = s8(b[80])
            zones.append(Zone(name=name, key=b[1], fine=s8(b[2]), coarse=coarse, pan=s8(b[3]),
                              volume=s8(b[4]), key_lo=b[6], key_hi=b[7], vel_lo=b[9], vel_hi=b[10],
                              vel_on=bool(opts & 8), pitch=(opts & 2) == 0, oneshot=bool(opts & 1),
                              start=u32(12), end=u32(16), loop_start=u32(20), loop_end=u32(24),
                              loop_on=bool(loop_opts & 1), group=u32(88), sample=u32(92)))
        elif typ == TYPE_SAMPLE:
            b = body
            u32 = lambda o: struct.unpack(e + "I", b[o:o + 4])[0]
            fpath = _cstr(b[80:336]) if len(b) >= 336 else ""
            fname = _cstr(b[336:592]) if len(b) >= 592 else name
            samples.append(SampleRec(name=name, wave_start=u32(0), length=u32(4), rate=u32(8),
                                     bits=u32(12), channels=u32(16), path=fpath, filename=fname or name))
        elif typ == TYPE_GROUP:
            b = body
            s8 = lambda v: v - 256 if v > 127 else v
            g = Group(name=name, raw=body, volume=s8(b[0]), exclusive=b[4], vel_lo=b[5], vel_hi=b[6],
                      release_trigger=b[73] if len(b) > 73 else 0)
            if len(b) >= 92:
                rr = struct.unpack(e + "I", b[80:84])[0]
                g.rr_pos = -1 if rr == 0xFFFFFFFF else rr
                g.enable_type, g.ctl_value, g.ctl_lo, g.ctl_hi = b[84], b[85], b[86], b[87]
                g.start_note, g.end_note = b[88], b[89]
            groups.append(g)
        pos += 84 + size
    return zones, samples, groups


if __name__ == "__main__":
    import sys
    zones, samples, groups = read_exs(sys.argv[1])
    print(f"{len(zones)} zones, {len(samples)} samples, {len(groups)} groups")
    for s in samples[:8]:
        print("  sample", s)
    for z in zones[:12]:
        print("  zone", z)
    keys = sorted({(z.key_lo, z.key_hi) for z in zones})
    print("  key ranges:", keys[:40])
    print("  vel ranges:", sorted({(z.vel_lo, z.vel_hi) for z in zones})[:20])
    for gi, g in enumerate(groups):
        nz = sum(1 for z in zones if z.group == gi)
        keys = sorted({(z.key_lo, z.key_hi) for z in zones if z.group == gi})
        print(f"  group {gi:>2} {g.name[:34]:<34} vel {g.vel_lo:>3}-{g.vel_hi:<3} rr={g.rr_pos:<3} "
              f"en={g.enable_type} ctl={g.ctl_value}:{g.ctl_lo}-{g.ctl_hi} rel={g.release_trigger} "
              f"excl={g.exclusive} zones={nz} keys={keys[:3]}{'...' if len(keys) > 3 else ''}")
