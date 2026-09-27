#!/usr/bin/env python3
"""Master a premix and deliver an MP3, lossless master and measured QA JSON."""
import argparse,json,math,shutil,subprocess
from pathlib import Path

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('input',type=Path);a.add_argument('output',type=Path)
    a.add_argument('--title',default='Sampled band performance')
    a.add_argument('--lufs',type=float,default=-17);a.add_argument('--true-peak',type=float,default=-1.5)
    a.add_argument('--ffmpeg',default=shutil.which('ffmpeg'));a.add_argument('--ffprobe',default=shutil.which('ffprobe'))
    a.add_argument('--overwrite',action='store_true');args=a.parse_args()
    if not args.ffmpeg or not args.ffprobe:a.error('FFmpeg and FFprobe are required.')
    if not args.input.is_file():a.error('Input audio file is missing.')
    if args.output.suffix.lower()!='.mp3':a.error('Output must end in .mp3.')
    if not -70<=args.lufs<=-5 or not -9<=args.true_peak<=-.5:a.error('Use LUFS -70 to -5 and true peak -9 to -0.5 dBTP.')
    master=args.output.with_suffix('.master.wav');qa=args.output.with_suffix('.qa.json')
    for p in [args.output,master,qa]:
        if p.resolve()==args.input.resolve():a.error('Input and outputs must be different files.')
        if p.exists() and not args.overwrite:a.error(f'Output exists: {p}. Choose another version or use --overwrite.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    def run(argv):return subprocess.run(argv,capture_output=True,text=True,check=True)
    def probe(p):return json.loads(run([args.ffprobe,'-v','error','-show_entries','format=duration:stream=codec_type,codec_name,sample_rate,channels,bit_rate','-of','json',str(p)]).stdout)
    def measure(p):
        log=run([args.ffmpeg,'-hide_banner','-nostats','-i',str(p),'-vn','-af',f'loudnorm=I={args.lufs}:TP={args.true_peak}:LRA=10:print_format=json','-f','null','-']).stderr
        start=log.rfind('{');end=log.rfind('}');result=json.loads(log[start:end+1])
        if not math.isfinite(float(result['input_i'])):raise ValueError('Audio is silent or has invalid measured loudness.')
        return result
    source=probe(args.input);d=measure(args.input)
    filt=f'loudnorm=I={args.lufs}:TP={args.true_peak}:LRA=10:measured_I={d["input_i"]}:measured_TP={d["input_tp"]}:measured_LRA={d["input_lra"]}:measured_thresh={d["input_thresh"]}:offset={d["target_offset"]}:linear=true'
    base=[args.ffmpeg,'-y' if args.overwrite else '-n','-hide_banner','-nostats']
    run(base+['-i',str(args.input),'-vn','-af',filt,'-ar','44100','-ac','2','-c:a','pcm_s24le',str(master)])
    run(base+['-i',str(master),'-vn','-c:a','libmp3lame','-b:a','320k','-metadata',f'title={args.title}',str(args.output)])
    m=measure(args.output);info=probe(args.output)
    if float(m['input_tp'])>-.5:raise ValueError('Encoded peak exceeds -0.5 dBTP; reduce mastering ceiling and re-export.')
    if abs(float(info['format']['duration'])-float(source['format']['duration']))>.15:raise ValueError('Unexpected duration change.')
    stream=next(s for s in info['streams'] if s.get('codec_type')=='audio')
    if stream['channels']!=2 or int(stream['sample_rate'])!=44100:raise ValueError('Unexpected output audio format.')
    result={'full_decode_passed':True,'output':str(args.output),'audio':info,'integrated_lufs':float(m['input_i']),'true_peak_dbtp':float(m['input_tp']),'loudness_range_lu':float(m['input_lra']),'note':'Technical audio checks only; musical content and listening quality require separate assessment.'}
    qa.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
