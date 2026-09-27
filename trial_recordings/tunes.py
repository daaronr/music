"""The three trial tunes, described only by facts taken from each run's own files."""
from pathlib import Path

from arrange import Tune

M = Path(__file__).resolve().parents[1]


def _url(path):
    txt = (M / path).read_text().strip()
    return txt if txt.startswith("irealbook://") else "irealbook://" + txt


HALATION = Tune(
    name="Halation", tempo=184,
    ireal_url=_url("claude_halation/ireal/Halation_iReal_link.txt"),
    head_xml=str(M / "claude_halation/musicxml/Halation_LeadSheet_C.musicxml"), head_part=0,
    head_in=list(range(32)),
    head_out=list(range(30)) + [32],            # bars 1-30, then the 2nd ending
    head_out_form_bars=30, ending_chords=["F^7#11"],
    solo_xml=str(M / "claude_halation/musicxml/Halation_Solo_BothChoruses_Score_Concert.musicxml"),
    solo_parts=(0, 1),
    sections={0: "A", 8: "B", 16: "A'", 24: "C"},
)

PARALLAX = Tune(
    name="Parallax", tempo=176,
    ireal_url=_url("claude_parallax/output/Parallax_iReal_link.txt"),
    head_xml=str(M / "claude_parallax/output/Parallax_lead_sheet_concert.musicxml"), head_part=0,
    head_in=list(range(4, 36)),                 # lead sheet bars 5-36 (bars 1-4 are the guitar intro)
    head_out=list(range(4, 36)) + list(range(36, 40)),   # head, then the written 4-bar coda
    head_out_form_bars=32, ending_chords=["Ab-9", "Db13#11", "Eb^7#11", "Eb^7#11"],
    solo_xml=str(M / "claude_parallax/output/Parallax_duo_solo_score_concert.musicxml"),
    solo_parts=(0, 1),
    sections={0: "A", 8: "A", 16: "B", 24: "A"},
)

GLASS_MERIDIAN = Tune(
    name="Glass Meridian", tempo=164,
    ireal_url=_url("codex_glass_meridian/output/ireal/glass_meridian.irealbook"),
    head_xml=str(M / "codex_glass_meridian/output/musicxml/01_head_concert.musicxml"), head_part=0,
    head_in=list(range(32)),
    head_out=list(range(32)),                   # ends on its own last bar, F6/9
    head_out_form_bars=31, ending_chords=["F69"],
    solo_xml=str(M / "codex_glass_meridian/output/musicxml/03_duo_score_concert.musicxml"),
    solo_parts=(0, 1),
    sections={0: "A", 8: "A2", 16: "B", 24: "C"},
)

ALL = {"halation": HALATION, "parallax": PARALLAX, "glass_meridian": GLASS_MERIDIAN}
