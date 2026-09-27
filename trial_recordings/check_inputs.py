"""Sanity checks before rendering: iReal chord roots agree with the chord
symbols in each run's MusicXML, the written parts parse, and the Halation
rules reproduce the original Halation performance."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "engine"))
sys.path.insert(0, str(HERE))

from chords import parse_ireal  # noqa: E402
from xmlread import harmony_roots  # noqa: E402
import arrange  # noqa: E402
import tunes  # noqa: E402

for key, t in tunes.ALL.items():
    form = parse_ireal(t.ireal_url, 32)
    xml_roots = harmony_roots(t.solo_xml, t.solo_parts[0], list(range(64)))
    bad = []
    for b in range(64):
        want = [c.root_pc for c in form[b % 32]]
        got = xml_roots[b]
        if got and got != want:
            bad.append((b + 1, want, got))
    lead_roots = harmony_roots(t.head_xml, t.head_part, t.head_out[t.head_out_form_bars:])
    print(f"{t.name}: iReal vs solo-score chord roots: {len(bad)} mismatching bars {bad[:5]}")
    print(f"   ending chords {t.ending_chords} vs lead-sheet roots {lead_roots}")
    perf = arrange.build(t)
    print(f"   notes: trumpet {len(perf['trumpet'])} alto {len(perf['alto'])} piano {len(perf['piano'])} "
          f"bass {len(perf['bass'])} drums {len(perf['drums'])}  length {perf['length']:.1f}s  info {perf['info']}")

# Halation: compare with the original build (run in its own process)
code = ("import sys, json; sys.path.insert(0, '/Users/yosemite/githubs/music/claude_halation/src/audio');"
        "import perform; p = perform.build();"
        "print(json.dumps({k: [[round(n.t, 4), n.midi, round(n.dur, 4)] for n in p[k]] for k in "
        "('trumpet', 'alto', 'bass', 'piano', 'drums')}))")
orig = json.loads(subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True).stdout)
new = arrange.build(tunes.HALATION)
for k in ("trumpet", "alto", "bass", "piano", "drums"):
    a = orig[k]
    b = [[round(n.t, 4), n.midi, round(n.dur, 4)] for n in new[k]]
    same = sum(1 for x, y in zip(a, b) if x == y)
    diffs = [(x, y) for x, y in zip(a, b) if x != y][:3]
    print(f"Halation reproduction {k}: {same}/{len(a)} identical (new has {len(b)}) first diffs {diffs}")
