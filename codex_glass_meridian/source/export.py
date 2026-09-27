#!/usr/bin/env python3
from pathlib import Path
import subprocess, json
ROOT=Path(__file__).resolve().parents[1]
MUSESCORE='/Applications/MuseScore 3.app/Contents/MacOS/mscore'
r=subprocess.run([MUSESCORE,'-s','-m','-c',str(ROOT/'qa'/'musescore_config'),'-S',str(ROOT/'source'/'engraving.mss'),'-j',str(ROOT/'source'/'export_jobs.json')],capture_output=True,text=True,timeout=90)
(ROOT/'qa'/'export.log').write_text(r.stdout+'\n'+r.stderr)
if r.returncode:raise SystemExit(r.stderr)
jobs=json.loads((ROOT/'source'/'export_jobs.json').read_text())
(ROOT/'source'/'duo_export_job.json').write_text(json.dumps([j for j in jobs if '03_duo_score' in j['in']],indent=2))
r2=subprocess.run([MUSESCORE,'-s','-m','-c',str(ROOT/'qa'/'musescore_config'),'-S',str(ROOT/'source'/'engraving_duo.mss'),'-j',str(ROOT/'source'/'duo_export_job.json')],capture_output=True,text=True,timeout=60)
with (ROOT/'qa'/'export.log').open('a') as f:f.write(r2.stdout+'\n'+r2.stderr)
if r2.returncode:raise SystemExit(r2.stderr)
print('Exported six PDFs and native MuseScore scores.')
