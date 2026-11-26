"""Word-level timestamps of the vocal stem with Whisper."""
import json
import sys
import whisper

model = whisper.load_model(sys.argv[3] if len(sys.argv) > 3 else "medium")
lyrics = ("Oh a lone pumpkin grew on a big pumpkin vine. He was round, he was fat, he was yellow. "
          "No funny jack o lantern shall I make, he said. I'm determined that I'll be a useful fellow. "
          "So he raised up his head when the cook came around and at once he was chosen the winner. "
          "His fondest wish came true, he was proud pumpkin pie, and the pride of the whole Thanksgiving dinner. "
          "For the glory of the Jack is in the lantern, as he sits up on the gatepost oh so high. "
          "And the glory of the turkey is the drumstick, but the glory of the pumpkin is the pie.")
r = model.transcribe(sys.argv[1], word_timestamps=True, language="en", initial_prompt=None if "noprompt" in sys.argv else lyrics,
                     condition_on_previous_text=False)
words = []
for seg in r["segments"]:
    for w in seg["words"]:
        words.append(dict(w=w["word"].strip(), s=round(w["start"], 3), e=round(w["end"], 3),
                          p=round(w.get("probability", 0), 3)))
json.dump(words, open(sys.argv[2], "w"), indent=0)
for w in words:
    print(f"{w['s']:7.2f} {w['e']:7.2f} {w['p']:.2f} {w['w']}")
