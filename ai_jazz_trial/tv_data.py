"""The two TV-theme arrangements (15 Nov 2026) for the trial page's bonus section.

The melodies are copyrighted (Raposo 1977, Strouse 1971). David chose (15 Nov) to show the
arrangements on the public page. The source files stay outside this repo, in
~/githubs/music_trial_runs, and build_site.py copies them into web/public/ at build time.
They are not in the vote.
"""

import os

RUNS_DIR = os.path.expanduser("~/githubs/music_trial_runs")
REC = os.path.join(RUNS_DIR, "private_recordings/output")
TC = os.path.join(RUNS_DIR, "opus_threes_company/claude_threes_company/output")
AF = os.path.join(RUNS_DIR, "opus_all_in_the_family/claude_those_were_the_days/output")

TV_RECIPE = ("Rendered with the same engine and settings as the round-1 recordings (trumpet on "
             "top, alto sax on the guitar line, piano, bass and drums), from the run's own lead "
             "sheet, duo score and iReal chart. The engine's 4-bar intro replaces the written one.")

TV_PROMPT_NOTE = ("Each run got one prompt, word for word, with no follow-ups: arrange the theme's "
                  "actual melody as a post-bop tune in the round-1 style, with a two-chorus trumpet "
                  "and guitar duo solo, sheet music and an iReal Pro chart, and no lyrics. "
                  "Claude Opus 5.5 at max effort, run unattended in a clean copy of the repo "
                  "with only the round-1 material.")

TV_RUNS = [
    {
        "key": "threes_company",
        "name": "Three's Company",
        "credit": "Theme from Three's Company (Joe Raposo, 1977), arranged by Claude Opus 5.5",
        "meta": ["F major", "about 176 bpm", "A A B, 24 bars", "68 minutes, unattended"],
        "idea": ("The long notes of the tune become the bright note of a lydian chord, and the "
                 "lydian chords are chained a whole step apart (F, E♭, D♭), so each chord's triad "
                 "pair shares a triad with its neighbour. The run worked out the melody by ear from "
                 "broadcast recordings of the opening titles."),
        "lead": f"{TC}/pdf/01_LeadSheet_Concert.pdf",
        "pdfs": [
            ("Everything in one packet (16 pp.)", f"{TC}/ThreesCompany_complete_packet.pdf"),
            ("Lead sheet, concert", f"{TC}/pdf/01_LeadSheet_Concert.pdf"),
            ("Lead sheet, B♭ trumpet", f"{TC}/pdf/02_LeadSheet_Bb_Trumpet.pdf"),
            ("Head arrangement score, with analysis", f"{TC}/pdf/03_Head_Arrangement_Score_Concert.pdf"),
            ("Duo solo study score, concert, with analysis", f"{TC}/pdf/04_DuoSolo_Score_Concert_annotated.pdf"),
            ("Duo solo, chorus 1, concert", f"{TC}/pdf/05_DuoSolo_Chorus1_Score_Concert.pdf"),
            ("Duo solo, chorus 2, concert", f"{TC}/pdf/05_DuoSolo_Chorus2_Score_Concert.pdf"),
            ("Duo solo, chorus 1, B♭ trumpet", f"{TC}/pdf/06_DuoSolo_Chorus1_Score_BbTrumpet.pdf"),
            ("Duo solo, chorus 2, B♭ trumpet", f"{TC}/pdf/06_DuoSolo_Chorus2_Score_BbTrumpet.pdf"),
            ("Trumpet part, chorus 1, concert", f"{TC}/pdf/07_Solo_Chorus1_Trumpet_Concert.pdf"),
            ("Trumpet part, chorus 2, concert", f"{TC}/pdf/07_Solo_Chorus2_Trumpet_Concert.pdf"),
            ("Trumpet part, chorus 1, B♭", f"{TC}/pdf/08_Solo_Chorus1_Trumpet_Bb.pdf"),
            ("Trumpet part, chorus 2, B♭", f"{TC}/pdf/08_Solo_Chorus2_Trumpet_Bb.pdf"),
            ("Guitar part, chorus 1", f"{TC}/pdf/09_Solo_Chorus1_Guitar.pdf"),
            ("Guitar part, chorus 2", f"{TC}/pdf/09_Solo_Chorus2_Guitar.pdf"),
        ],
        "xml_dir": f"{TC}/musicxml",
        "ireal": f"{TC}/ireal/Three_s_Company_post_bop_arr_iReal_link.txt",
        "audio": (f"{REC}/threes_company_band_trumpet_alto.mp3", "Threes_Company_band_trumpet_alto.mp3", "2:28"),
    },
    {
        "key": "those_were_the_days",
        "name": "Those Were the Days",
        "credit": "Theme from All in the Family (Charles Strouse, 1971), arranged by Claude Opus 5.5",
        "meta": ["F major", "about 168 bpm", "AABA, 32 bars", "77 minutes, unattended"],
        "idea": ("Every long note of the tune sits on a falling pair of bright chords, a maj7♯11 and "
                 "then a maj7♯5 a whole step lower, so the held note changes colour while it rings. "
                 "The bridge becomes a staircase of lydian chords under the tune's chromatic line. "
                 "The run read the A sections from the published sheet's preview page and "
                 "transcribed the bridge from TV recordings, and says which phrases it is unsure of."),
        "lead": f"{AF}/pdf/Those_Were_the_Days_LeadSheet_Concert.pdf",
        "pdfs": [
            ("Everything in one file", f"{AF}/Those_Were_the_Days_All_Sheets.pdf"),
            ("Lead sheet, concert", f"{AF}/pdf/Those_Were_the_Days_LeadSheet_Concert.pdf"),
            ("Lead sheet, B♭ trumpet", f"{AF}/pdf/Those_Were_the_Days_LeadSheet_Bb_Trumpet.pdf"),
            ("Duo solo study score, concert, with analysis", f"{AF}/pdf/Those_Were_the_Days_DuoSolo_Score_Concert.pdf"),
            ("Trumpet part, concert, both choruses", f"{AF}/pdf/Those_Were_the_Days_DuoSolo_Trumpet_Concert_BothChoruses.pdf"),
            ("Trumpet part, B♭, both choruses", f"{AF}/pdf/Those_Were_the_Days_DuoSolo_Trumpet_Bb_BothChoruses.pdf"),
            ("Guitar part, both choruses", f"{AF}/pdf/Those_Were_the_Days_DuoSolo_Guitar_BothChoruses.pdf"),
        ],
        "xml_dir": f"{AF}/musicxml",
        "ireal": f"{AF}/ireal/Those_Were_the_Days_iReal_link.txt",
        "audio": (f"{REC}/those_were_the_days_band_trumpet_alto.mp3", "Those_Were_the_Days_band_trumpet_alto.mp3", "3:19"),
    },
]
