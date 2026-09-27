from pathlib import Path
import subprocess,json,re
R=Path(__file__).resolve().parents[1];O=R/'output';W=R/'work';FF='/usr/local/bin/ffmpeg'
log=(W/'loudness_pass1.log').read_text();d=json.loads(re.search(r'\{\s*"input_i".*?\}',log,re.S)[0])
filt=f'loudnorm=I=-17:TP=-1.2:LRA=10:measured_I={d["input_i"]}:measured_TP={d["input_tp"]}:measured_LRA={d["input_lra"]}:measured_thresh={d["input_thresh"]}:offset={d["target_offset"]}:linear=true:print_format=json'
master=W/'master_24bit.wav'
p=subprocess.run([FF,'-y','-hide_banner','-nostats','-i',str(W/'mix_premaster.wav'),'-af',filt,'-ar','44100','-c:a','pcm_s24le',str(master)],capture_output=True,text=True,check=True)
(W/'mastering.log').write_text(p.stderr)
base=[FF,'-y','-hide_banner','-loglevel','error','-i',str(master)]
subprocess.run(base+['-codec:a','libmp3lame','-b:a','320k','-id3v2_version','3','-metadata','title=Glass Meridian - full band performance','-metadata','artist=Codex / OpenAI - programmed sample performance','-metadata','album=Glass Meridian','-metadata','genre=Jazz','-metadata','comment=Original written head and two trumpet/guitar duo choruses; VSCO trumpet, Apple sampled guitar, iReal Pro rhythm section.',str(O/'Glass_Meridian_full_band.mp3')],check=True)
info=json.loads((O/'recording_details.json').read_text());start=info['section_starts_seconds'][1];length=info['duo_end_seconds']-start
subprocess.run(base+['-ss',str(start),'-t',str(length),'-af',f'afade=t=in:st=0:d=0.03,afade=t=out:st={length-.22}:d=0.22','-codec:a','libmp3lame','-b:a','320k','-id3v2_version','3','-metadata','title=Glass Meridian - two-chorus trumpet and guitar duo','-metadata','artist=Codex / OpenAI - programmed sample performance','-metadata','album=Glass Meridian','-metadata','genre=Jazz',str(O/'Glass_Meridian_duo_only.mp3')],check=True)
for name in ['Glass_Meridian_full_band','Glass_Meridian_duo_only']:
 p=subprocess.run([FF,'-hide_banner','-nostats','-i',str(O/(name+'.mp3')),'-af','loudnorm=I=-17:TP=-1.2:LRA=10:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 (W/(name+'_qa.log')).write_text(p.stderr)
 vals=json.loads(re.search(r'\{\s*"input_i".*?\}',p.stderr,re.S)[0]);info[name]={'lufs':float(vals['input_i']),'true_peak_dbtp':float(vals['input_tp']),'loudness_range_lu':float(vals['input_lra']),'bytes':(O/(name+'.mp3')).stat().st_size,'full_decode_passed':True}
 assert float(vals['input_tp'])<-.5
 print(name,info[name])
info['format']='320 kb/s stereo MP3, 44.1 kHz';info['quality_note']='Sampled and programmed performance, not a live band; technical validation and pitch spot checks completed.'
(O/'recording_details.json').write_text(json.dumps(info,indent=2))
