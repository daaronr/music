"""Bass-only revision. Reuse v2 non-bass stems exactly; retain previous exports."""
from pathlib import Path
from functools import lru_cache
from fractions import Fraction
import struct,json,math,re,subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, PeakFilter, Compressor
import revision2 as r
W=r.R/'work'/'v3'; V2=r.W; O=r.O; SR=r.SR; N=r.N

def bass_map():
    d=Path('/Library/Application Support/Logic/Sampler Instruments/02 Bass/01 Acoustic Bass/Upright Jazz Bass.exs').read_bytes()
    zones=[];groups=[];samples=[];pos=0
    while pos<len(d):
        sig,size=struct.unpack_from('<II',d,pos)
        # This installed legacy JBOS map sets a flag in the length field.
        if sig&0x80000000:size&=0x7fff
        typ=(sig>>24)&15;v=d[pos+84:pos+84+size]
        name=d[pos+20:pos+84].split(b'\0')[0].decode()
        if typ==1:
            zones.append(dict(name=name,root=v[1],fine=struct.unpack_from('b',v,2)[0],volume=struct.unpack_from('b',v,4)[0],low=v[6],high=v[7],start=struct.unpack_from('<I',v,12)[0],end=struct.unpack_from('<I',v,16)[0],group=struct.unpack_from('<i',v,88)[0],sample=struct.unpack_from('<I',v,92)[0]))
        elif typ==2:groups.append(dict(name=name,vlo=v[5],vhi=v[6],release=bool(v[73]),volume=struct.unpack_from('b',v,0)[0]))
        elif typ==3:
            folder=v[80:336].split(b'\0')[0].decode();file=v[336:592].split(b'\0')[0].decode()
            samples.append(str(Path(folder)/file))
        pos+=size+84
    assert pos==len(d)
    return zones,groups,samples

def render():
    notes=json.loads((V2/'notes.json').read_text())['bass'];zones,groups,samples=bass_map();out=np.zeros((N,2),np.float32);usage=[]
    @lru_cache(maxsize=160)
    def load(index,pitch):
        z=zones[index];x,sr=sf.read(samples[z['sample']],start=z['start'],stop=z['end'],dtype='float32',always_2d=True);x=x.mean(axis=1)
        ratio=Fraction((SR/sr)*2**((z['root']-pitch-z['fine']/100)/12)).limit_denominator(2000)
        if ratio!=1:x=resample_poly(x,ratio.numerator,ratio.denominator)
        # Keep recorded sustain and its natural pitch/wood/string fluctuations.
        x*=10**(z['volume']/20)
        return x
    for i,n in enumerate(notes):
        # Softer layers, without synthesised sub-bass or pitch substitutions.
        velocity=int(np.clip(70+(n['velocity']-89)*.55+2*math.sin(i*1.2),65,80))
        matches=[k for k,z in enumerate(zones) if z['low']<=n['note']<=z['high'] and not groups[z['group']]['release'] and groups[z['group']]['vlo']<=velocity<=groups[z['group']]['vhi']]
        assert len(matches)==1,(n,matches)
        ix=matches[0];x=load(ix,n['note']).copy()
        gap=(notes[i+1]['time']-n['time']) if i+1<len(notes) else 2.9
        held=max(.065,gap*.985)
        release=.075 if gap>.22 else .045
        count=min(len(x),round((held+release)*SR));x=x[:count];t=np.arange(count)/SR
        # Reduce the isolated click; smoothly expose the body after the pluck.
        env=np.minimum(t/.003,1)*(.66+.52*(1-np.exp(-t/.052)))
        env*=np.where(t>held,np.exp(-5*(t-held)/release),1)
        env*= (velocity/75)**.65
        x*=env.astype(np.float32)
        st=np.column_stack([x,x])*.70710678;start=round(n['time']*SR);end=min(N,start+len(st));out[start:end]+=st[:end-start]
        usage.append({'note':n['note'],'time':n['time'],'duration':held,'velocity':velocity,'sample':Path(samples[zones[ix]['sample']]).name,'source_root':zones[ix]['root'],'source_fine_cents':zones[ix]['fine']})
    sf.write(W/'bass_raw.wav',out,SR,subtype='FLOAT')
    fx=Pedalboard([HighpassFilter(cutoff_frequency_hz=28),PeakFilter(cutoff_frequency_hz=165,gain_db=2.8,q=.65),PeakFilter(cutoff_frequency_hz=620,gain_db=2.4,q=.75),PeakFilter(cutoff_frequency_hz=2300,gain_db=-2.2,q=.8),LowpassFilter(cutoff_frequency_hz=5200),Compressor(threshold_db=-21,ratio=2.1,attack_ms=7,release_ms=110)])
    out=fx(out.T,SR).T
    source_rms=r.p.active_rms(out,threshold=.001);out*=.086/source_rms
    sf.write(W/'bass_mixed.wav',out,SR,subtype='FLOAT')
    (W/'bass_sample_usage.json').write_text(json.dumps(usage,indent=2))
    facts={'bass_active_rms_target':.086,'v2_bass_active_rms_target':.056,'bass_target_level_increase_db':20*math.log10(.086/.056),'bass_source':'Installed Apple Upright Jazz Bass, softer recorded pluck layers rendered directly','bass_sample_zones_used':len(set(n['sample'] for n in usage)),'bass_velocities':[min(n['velocity'] for n in usage),max(n['velocity'] for n in usage)],'bass_peak':float(np.max(abs(out))),'bass_changes':'Recorded string decay, near-full inter-note gates, gentle attack reduction, body/upper-harmonic EQ, light compression; no synthetic sub-bass','unchanged_non_bass_stems':['trumpet','sax','piano','drums'],'score_unchanged':True,'bass_note_pitch_and_onset_unchanged':True}
    (W/'bass_render.json').write_text(json.dumps(facts,indent=2));print(facts)

def mix():
    blend=np.zeros((N,2),np.float32)
    for v in ['trumpet','sax','piano','drums','bass']:
        path=(W if v=='bass' else V2)/(v+'_mixed.wav');x,sr=sf.read(path,dtype='float32',always_2d=True);assert sr==SR and len(x)==N;blend+=x
    blend[-int(1.6*SR):]*=np.linspace(1,0,int(1.6*SR))[:,None]
    sf.write(W/'mix_premaster.wav',blend,SR,subtype='FLOAT')

def master():
    ff='/usr/local/bin/ffmpeg'
    def run(args):return subprocess.run([ff,'-y','-hide_banner','-nostats']+args,capture_output=True,text=True,check=True)
    def measure(path):
        log=run(['-i',str(path),'-af','loudnorm=I=-17:TP=-1.5:LRA=10:print_format=json','-f','null','-']).stderr
        return json.loads(re.search(r'\{\s*"input_i".*?\}',log,re.S)[0])
    src=W/'mix_premaster.wav';d=measure(src)
    filt=f'loudnorm=I=-17:TP=-1.5:LRA=10:measured_I={d["input_i"]}:measured_TP={d["input_tp"]}:measured_LRA={d["input_lra"]}:measured_thresh={d["input_thresh"]}:offset={d["target_offset"]}:linear=true'
    log=run(['-i',str(src),'-af',filt,'-ar','44100','-c:a','pcm_s24le',str(W/'master_24bit.wav')]).stderr;(W/'master.log').write_text(log)
    facts=json.loads((W/'bass_render.json').read_text());facts['duration_seconds']=N/SR
    for label,extra in [('full_band',[]),('duo_only',['-ss',str(r.START+128*r.Q),'-t',str(256*r.Q),'-af',f'afade=t=in:d=0.02,afade=t=out:st={256*r.Q-.15}:d=0.15'])]:
        dest=O/f'Glass_Meridian_{label}_trumpet_sax_v3.mp3'
        run(['-i',str(W/'master_24bit.wav')]+extra+['-codec:a','libmp3lame','-b:a','320k','-metadata','title=Glass Meridian - trumpet and alto sax, fuller upright bass','-metadata','artist=Codex / OpenAI - programmed sample performance','-metadata','genre=Jazz',str(dest)])
        qa=measure(dest);assert float(qa['input_tp'])<-.5
        facts[label]={'full_decode_passed':True,'integrated_lufs':float(qa['input_i']),'true_peak_dbtp':float(qa['input_tp']),'bytes':dest.stat().st_size};print(dest.name,facts[label])
    (O/'recording_details_v3.json').write_text(json.dumps(facts,indent=2))
if __name__=='__main__':render();mix();master()
