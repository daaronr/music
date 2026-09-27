import Foundation
import AVFoundation
struct Event: Decodable { let time: Double; let on: Bool; let note: UInt8; let velocity: UInt8 }
enum RenderError: Error { case invalidArguments, invalidEvents, stalled, status(String) }
func render() throws {
    let args = CommandLine.arguments
    guard args.count == 6, let duration = Double(args[4]), let rate = Double(args[5]), duration > 0, rate > 0 else { throw RenderError.invalidArguments }
    let events = try JSONDecoder().decode([Event].self, from: Data(contentsOf: URL(fileURLWithPath: args[2])))
    guard events.allSatisfy({ $0.time.isFinite && $0.time >= 0 && $0.time < duration && $0.note < 128 && $0.velocity < 128 }), zip(events, events.dropFirst()).allSatisfy({ $0.time <= $1.time }) else { throw RenderError.invalidEvents }
    let engine = AVAudioEngine(), sampler = AVAudioUnitSampler()
    let format = AVAudioFormat(standardFormatWithSampleRate: rate, channels: 2)!
    engine.attach(sampler); engine.connect(sampler, to: engine.mainMixerNode, format: format)
    try sampler.loadInstrument(at: URL(fileURLWithPath: args[1]))
    try engine.enableManualRenderingMode(.offline, format: format, maximumFrameCount: 4096)
    var output: AVAudioFile? = try AVAudioFile(forWriting: URL(fileURLWithPath: args[3]), settings: format.settings)
    defer { engine.stop(); output = nil }
    let buffer = AVAudioPCMBuffer(pcmFormat: engine.manualRenderingFormat, frameCapacity: 4096)!
    try engine.start()
    var index = 0, retries = 0
    let total = AVAudioFramePosition((duration * rate).rounded())
    while engine.manualRenderingSampleTime < total {
        let now = engine.manualRenderingSampleTime
        while index < events.count && AVAudioFramePosition((events[index].time * rate).rounded()) <= now {
            let e = events[index]
            if e.on { sampler.startNote(e.note, withVelocity: e.velocity, onChannel: 0) }
            else { sampler.stopNote(e.note, onChannel: 0) }
            index += 1
        }
        let until = index < events.count ? min(total, AVAudioFramePosition((events[index].time * rate).rounded())) : total
        let count = AVAudioFrameCount(max(1, min(4096, until - now)))
        switch try engine.renderOffline(count, to: buffer) {
        case .success: try output!.write(from: buffer); retries = 0
        case .cannotDoInCurrentContext:
            retries += 1
            if retries > 100 { throw RenderError.stalled }
        default: throw RenderError.status("Offline render failed")
        }
    }
    engine.stop(); output = nil
    print("Rendered \(events.count) events, \(total) frames.")
}
do { try render() }
catch { fputs("Render failed: \(error)\nUsage: render_exs instrument.exs events.json output.wav duration sampleRate\n", stderr); exit(1) }
