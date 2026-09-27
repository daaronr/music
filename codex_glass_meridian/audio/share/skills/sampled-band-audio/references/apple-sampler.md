# Installed Apple instruments and offline rendering

Check the local installation rather than assuming these libraries are present. Instrument maps may be in `/Library/Application Support/Logic/Sampler Instruments/`; sample assets may be in the Logic `EXS Factory Samples` directory or GarageBand `Instrument Library/Sampler/Sampler Files` directory.

A working option is Swift AVAudioEngine + AVAudioUnitSampler, loading an EXS instrument and using manual offline rendering. The included `scripts/render_exs.swift` accepts a JSON array of events with `time` (seconds), `on` (boolean), `note` (MIDI integer), and `velocity` (0–127). Supply a duration that includes the tail. Compile with a writable module cache, then render a short test first. This minimal helper handles notes, not every controller or all of Logic's instrument DSP.

```
swiftc -module-cache-path /tmp/task-swift-cache scripts/render_exs.swift -o /tmp/task-render-exs
/tmp/task-render-exs instrument.exs events.json output.wav 12 44100
```

CoreAudio component discovery may require the execution environment's approved access outside its sandbox. Request the actual permission when needed. An Apple sampler load can fail even when the files exist. Catch and exit on errors; do not leave fatal-error/crash processes running, and do not blindly rerun a failing patch. Close the AVAudioFile before declaring completion; verify that a second decoder sees nonzero frames.

Observed on the development machine: Alto Sax and Upright Jazz Bass legacy EXS maps loaded successfully. The newer Steinway Grand Piano 2 and SoCal Kit maps failed with CoreAudio -10868. Direct rendering from their installed sample zones worked as a fallback; it did not reproduce the full Logic instrument engine. Simply changing an EXS signature was not sufficient. These are local observations, not compatibility guarantees.

If implementing a direct EXS reader, validate key/velocity ranges, group conditions, release-trigger groups, sample offsets, fine tuning and sample rates. Legacy JBOS files can encode flags in chunk lengths; do not assume the newer map's layout without checking. Consolidated CAF files contain many samples; reading the entire file as one note is wrong. The [EXS format reference](https://github.com/asatamax/tonverk-elmulti-converter/blob/main/docs/EXS24_FORMAT_SPEC.md) was useful, but compare its descriptions against actual file bytes and audio.

Verify drum mapping. In the tested SoCal map, the foot hi-hat is native key 33 and high tom is 48, unlike portable GM keys 44 and 50. Articulation-controlled hi-hat groups cannot all be mixed together as if they were round-robin takes. Keep portable MIDI mappings separate from native sample-key mappings.

Other encountered traps: VSCO 2 CE's trumpet filename C3 is sounding MIDI 60/middle C, so verify sample pitch rather than trusting octave labels. The tested iReal audio had eight count-in beats while its MIDI had four. Do not propagate either offset to another project without measuring it.

Apple sample files stay installed or in ignored local working files; share the rendered performance and code, not the proprietary samples.
