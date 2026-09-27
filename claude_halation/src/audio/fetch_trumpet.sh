#!/bin/bash
# Download the University of Iowa MIS B-flat trumpet (non-vibrato, mf + ff)
# recordings: "may be downloaded and used for any projects, without restrictions".
DEST="$(dirname "$0")/../../build/samples/iowa_trumpet"
BASE="https://theremin.music.uiowa.edu/sound%20files/MIS/Brass/Bbtrumpet"
mkdir -p "$DEST"
for f in \
  Trumpet.novib.mf.E3B3.aiff Trumpet.novib.mf.C4B4.aiff Trumpet.novib.mf.C5B5.aiff Trumpet.novib.mf.C6D6.aiff \
  Trumpet.novib.ff.E3B3.aiff Trumpet.novib.ff.C4B4.aiff Trumpet.novib.ff.C5B5.aiff Trumpet.novib.ff.C6Eb6.aiff
do
  if [ ! -s "$DEST/$f" ]; then
    curl -sSfL -o "$DEST/$f" "$BASE/$f" || echo "failed: $f"
  fi
done
ls -la "$DEST"
