#!/bin/bash
# Rebuild "The Glory of the Pumpkin (Disco-Trap Remix)" from the 2023 sing-along video.
# Prefers the matching GarageBand stereo export when it's available locally.
# Needs: ffmpeg + rubberband (Homebrew), the "stems" venv (demucs, librosa, soundfile, pyloudnorm,
# torch, whisper via miniforge site-packages), MuseScore score in ~/Documents/MuseScore3/Scores.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/Users/yosemite/.venvs/stems/bin/python
W="$HERE/work"
S="$HERE/src"
VIDEO="/Users/yosemite/Dropbox/large_videos/The Glory of the Pumpkin -  Thanksgiving sing-along - SD 480p.mov"
BOUNCE=${PUMPKIN_GARAGEBAND_BOUNCE:-"$HOME/Dropbox/music_recordings/pumpkin - 21:11:2022, 23C.mp3"}
SCORE="/Users/yosemite/Documents/MuseScore3/Scores/Glory_of_the_pumpkin.mscz"
mkdir -p "$W" "$HERE/output"

# 1. source audio and the score
if [[ -s "$BOUNCE" ]]; then
  # Align this specific bounce to the video timing used by the hand-checked anchors.
  /opt/homebrew/bin/ffmpeg -hide_banner -loglevel error -y -i "$BOUNCE" -vn -ac 2 \
    -af "aresample=44100,atrim=start_sample=1056,asetpts=PTS-STARTPTS,apad=whole_len=4173090,atrim=end_sample=4173090" \
    -c:a pcm_f32le "$W/video_audio.wav"
else
  /opt/homebrew/bin/ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" -vn -ac 2 -ar 44100 "$W/video_audio.wav"
fi
mkdir -p "$W/mscz"
unzip -o -q "$SCORE" -d "$W/mscz"
$PY "$S/parse_score.py" "$W/mscz/Glory_of_the_pumpkin.mscx" "$W/score.json" > /dev/null

# 2. stems (vocals / drums / bass / other)
$PY -m demucs -n htdemucs_ft -d mps --float32 -o "$W/demucs" "$W/video_audio.wav"
rm -rf "$W/stems"
cp -R "$W/demucs/htdemucs_ft/video_audio" "$W/stems"

# 3. where every syllable was sung: Whisper words + pitch-track onsets -> smooth tempo map
$PY "$S/words.py" "$W/stems/vocals.wav" "$W/words.json" medium > /dev/null
$PY "$S/stem_report.py" "$W/stems" > /dev/null
$PY "$S/notes.py" "$W/stems" > /dev/null
$PY "$S/anchors.py" "$W/score.json" "$W/words.json" "$W/stems" > /dev/null
$PY "$S/tempo_fit.py" "$W/stems" > /dev/null

# 4. vocal onto the 128 BPM grid, then chord-aware pitch correction
$PY "$S/warp_vocal.py" all vocal_grid.wav
$PY "$S/tune_vocal.py" soft
rm -f "$W/vocal_soft_oct_down.wav"

# 5. arrangement, mix, master
$PY "$S/song.py"
/opt/homebrew/bin/ffmpeg -hide_banner -loglevel error -y -i "$HERE/output/Glory_of_the_Pumpkin_Disco_Trap_Remix.wav" \
  -codec:a libmp3lame -b:a 320k -metadata title="The Glory of the Pumpkin (Disco-Trap Remix)" \
  -metadata artist="David Reinstein" "$HERE/output/Glory_of_the_Pumpkin_Disco_Trap_Remix.mp3"

# 6. checks
$PY "$S/check_mix.py"
$PY "$S/check_flow.py"
