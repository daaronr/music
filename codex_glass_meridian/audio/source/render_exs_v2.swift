import Foundation
import AVFoundation
struct Event: Decodable { let time: Double; let on: Bool; let note: UInt8; let velocity: UInt8 }
let args=CommandLine.arguments
if args.count != 6 { fatalError("render_exs instrument.exs events.json output.wav duration sampleRate") }
let events=try JSONDecoder().decode([Event].self,from:Data(contentsOf:URL(fileURLWithPath:args[2])))
let duration=Double(args[4])!, rate=Double(args[5])!
let engine=AVAudioEngine(), sampler=AVAudioUnitSampler()
let format=AVAudioFormat(standardFormatWithSampleRate:rate,channels:2)!
engine.attach(sampler); engine.connect(sampler,to:engine.mainMixerNode,format:format)
do { try sampler.loadInstrument(at:URL(fileURLWithPath:args[1])) } catch { print("Instrument load failed: \(error)"); exit(2) }
sampler.masterGain = 0
try engine.enableManualRenderingMode(.offline,format:format,maximumFrameCount:4096)
var output: AVAudioFile? = try AVAudioFile(forWriting:URL(fileURLWithPath:args[3]),settings:format.settings)
let buffer=AVAudioPCMBuffer(pcmFormat:engine.manualRenderingFormat,frameCapacity:4096)!
try engine.start()
var index=0;let total=AVAudioFramePosition(duration*rate)
while engine.manualRenderingSampleTime<total {
    let now=engine.manualRenderingSampleTime
    while index<events.count && AVAudioFramePosition((events[index].time*rate).rounded())<=now {
        let e=events[index]
        if e.on { sampler.startNote(e.note,withVelocity:e.velocity,onChannel:0) }
        else { sampler.stopNote(e.note,onChannel:0) }
        index+=1
    }
    var until=total
    if index<events.count { until=min(until,AVAudioFramePosition((events[index].time*rate).rounded())) }
    let count=AVAudioFrameCount(max(1,min(4096,until-now)))
    let status=try engine.renderOffline(count,to:buffer)
    switch status {
    case .success: try output!.write(from:buffer)
    case .cannotDoInCurrentContext: continue
    default: fatalError("Offline render status \(status)")
    }
}
engine.stop(); output=nil; print("Rendered \(events.count) events with \(args[1])")
