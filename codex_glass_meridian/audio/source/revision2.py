"""Recording-only revision: elastic swing, trumpet/alto sax, Apple acoustic trio.
The score and v1 audio are not modified. Seeded performance choices are repeatable.
"""
from pathlib import Path
import json, math, sys, subprocess, re
import numpy as np
import soundfile as sf
import mido
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, PeakFilter, Compressor, Reverb
import performance as p
R=p.R; W=R/'work'/'v2'; O=R/'output'; SR=p.SR; Q=p.Q; START=p.START
DURATION=196.162177; N=round(DURATION*SR); rng=np.random.default_rng(9262026)

def leads(bars,voice):
    # Phrase boundaries are rests, not barlines. Continuous runs lean towards even.
    raw=[]
    for b,bar in enumerate(bars):
        for n in bar:
            if n['pitch'] is not None: raw.append(dict(n,beat=b*4+n['offset'],bar=b+1))
    groups=[]
    for n in raw:
        if not groups or n['beat']>groups[-1][-1]['beat']+groups[-1][-1]['dur']+.01: groups.append([])
        groups[-1].append(n)
    out=[]
    for gi,phrase in enumerate(groups):
        # The instrumentalists share the quarter-note pulse, not a subdivision grid.
        longrun=len(phrase)>=6
        ratio=(.543 if longrun else .58)+.018*math.sin(gi*1.71+(1 if voice=='sax' else 0))
        placement=(.008 if voice=='trumpet' else .016)+.006*math.sin(gi*.83)
        if longrun: placement-=.009
        for j,n in enumerate(phrase):
            arc=j/max(1,len(phrase)-1)
            # Flatten as a line gathers momentum, relax on the way out.
            r=ratio-.012*math.sin(math.pi*arc)+(.012 if j==len(phrase)-1 else 0)
            onset=START+Q*p.swing(n['beat'],r)+placement+.003*math.sin(j*1.4+gi)
            end=START+Q*p.swing(n['beat']+n['dur'],r)+placement
            last=j==len(phrase)-1
            gate=.97 if not last else .86
            dur=max(.065,(end-onset)*gate)
            base=(77 if voice=='trumpet' else 75)
            if 65<=n['bar']<=96:base+=3
            if 81<=n['bar']<=88:base+=5
            base+=5*math.sin(math.pi*arc)-3*arc
            # Shape melodic gestures; don't accent every upbeat or every barline.
            if n['accent']:base+=5
            if j and n['pitch']>phrase[j-1]['pitch']+3:base+=2
            if last:base-=3
            vel=int(np.clip(base+rng.normal(0,1.3),59,95))
            out.append({'time':round(onset,7),'duration':round(dur,7),'note':n['pitch'],'velocity':vel,'bar':n['bar'],'phrase_start':j==0,'phrase_end':last,'score_duration':n['dur'],'phrase':gi,'ratio':r,'accent':n['accent']})
    # Ensure same-note release never cuts a subsequent attack.
    for i,n in enumerate(out[:-1]):
        if out[i+1]['time']<n['time']+n['duration']:
            n['duration']=max(.04,out[i+1]['time']-n['time']-.003)
    return out

def events(ns):
    es=[]
    for n in ns:
        es += [{'time':n['time'],'on':True,'note':n['note'],'velocity':n['velocity']},{'time':n['time']+n['duration'],'on':False,'note':n['note'],'velocity':0}]
    return sorted(es,key=lambda e:(e['time'],e['on']))

def prepare():
    t=leads(p.TRUMPET,'trumpet');s=leads(p.GUITAR,'sax')
    for ns,bars in [(t,p.TRUMPET),(s,p.GUITAR)]:
        assert [n['note'] for n in ns]==[n['pitch'] for bar in bars for n in bar if n['pitch'] is not None]
    parts={'trumpet':t,'sax':s}
    mf=mido.MidiFile(R/'work'/'ireal_timing_164.mid')
    for tr in mf.tracks:
        if tr.name not in ['Piano','Bass']:continue
        beat=0;active={};notes=[]
        for msg in tr:
            beat+=msg.time/mf.ticks_per_beat
            if msg.type=='note_on' and msg.velocity:
                active[msg.note]=(beat,msg.velocity)
            elif msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0):
                if msg.note in active:
                    start,vel=active.pop(msg.note);notes.append({'beat':start,'dur':beat-start,'note':msg.note,'velocity':vel})
        ns=[]; chord_decisions={}
        for n in sorted(notes,key=lambda z:(z['beat'],z['note'])):
            b=n['beat']-4;bar=int(b//4)
            if tr.name=='Piano':
                key=round(n['beat'],3)
                if key not in chord_decisions:
                    chord_decisions[key]=rng.random()>(.20 if 32<=bar<96 else .07)
                if not chord_decisions[key] and b<512:continue
                # iReal has heavily delayed offbeats (~.72). Re-interpret those
                # as lightly swung comping, keeping its voicings and harmonic rhythm.
                f=b%1
                if .58<f<.9:b=math.floor(b)+.565+.012*math.sin(bar*.91)
                offset=.009+.004*math.sin(bar*.7)
                vel=int(np.clip(n['velocity']*.70+5,34,92));dur=min(n['dur']*Q,.55) if b<512 else n['dur']*Q
            else:
                offset=-.003+.0025*math.sin(b*1.33)
                vel=int(np.clip(n['velocity']*.80+9,45,100));dur=min(n['dur']*Q,.335) if b<512 else n['dur']*Q
            ns.append({'time':START+b*Q+offset,'duration':max(.08,dur),'note':n['note'],'velocity':vel})
        parts[tr.name.lower()]=ns
    # Composed drum part: steady ride, variable skip notes, sparse conversational
    # snare, feathered kick and feet on 2/4. No forced triplet lattice.
    drums=[]
    def hit(beat,key,v,length=.11,lag=0):
        drums.append({'time':max(0,START+beat*Q+lag),'duration':length,'note':key,'velocity':int(np.clip(v,15,105))})
    for beat in range(-8,0):hit(beat,37,45 if beat%4==0 else 32,.09)
    skips=[(1.60,), (3.59,), (1.57,3.60), (), (2.58,), (1.59,3.56), (3.61,), (1.58,)]
    snare=[(),(2.52,),(.53,),(3.52,),(),(1.53,2.53),(),(.52,3.52)]
    for bar in range(128):
        energy=1 if 64<=bar<96 else 0
        for beat in range(4):
            v=[59,67,57,65][beat]+3*math.sin(bar*.73)+energy*3
            hit(4*bar+beat,51,v,.19,-.001+float(rng.normal(0,.0015)))
            if beat in [1,3]:hit(4*bar+beat,44,49+energy*3,.08,-.008)
            if beat in [0,2]:hit(4*bar+beat,36,25+energy*3,.11,-.004)
        for k,slot in enumerate(skips[bar%8]):hit(4*bar+slot,51,43+energy*4+3*math.sin(bar),.15)
        for slot in snare[(bar+bar//8)%8]:hit(4*bar+slot,38,33+energy*7+5*math.sin(bar),.12,.008)
        # Phrase-end answers in the openings left by either horn.
        if bar%8==7:
            for j,slot in enumerate([2.50,3.03,3.52]):hit(4*bar+slot,38 if j<2 else 50,42+j*5+energy*4,.14,.004)
        if bar in [32,64,80,96]:hit(4*bar,49,49 if bar!=80 else 62,1.2)
    hit(512,36,65,.3);hit(512,49,67,2.8)
    parts['drums']=drums
    (W/'notes.json').write_text(json.dumps(parts,indent=2))
    for voice,ns in parts.items():(W/(voice+'_events.json')).write_text(json.dumps(events(ns)))
    out=mido.MidiFile(ticks_per_beat=960)
    meta=mido.MidiTrack();meta.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(164)));out.tracks.append(meta)
    for channel,(voice,pg) in enumerate([('trumpet',56),('sax',65),('piano',0),('bass',32),('drums',0)]):
        ch=9 if voice=='drums' else channel;tr=mido.MidiTrack();tr.append(mido.MetaMessage('track_name',name=voice));tr.append(mido.Message('program_change',channel=ch,program=pg));last=0
        for e in events(parts[voice]):
            tick=round(e['time']/Q*960);tr.append(mido.Message('note_on' if e['on'] else 'note_off',channel=ch,note=e['note'],velocity=e['velocity'],time=tick-last));last=tick
        out.tracks.append(tr)
    out.save(O/'Glass_Meridian_trumpet_sax_v2.mid')
    print({k:len(v) for k,v in parts.items()})

def trumpet():
    ns=json.loads((W/'notes.json').read_text())['trumpet'];out=np.zeros((N,2),np.float32);rrs={};usage=[]
    for i,n in enumerate(ns):
        # Connected eighths use sustained recordings; shorter tongue only at
        # selected accents and releases. Avoid the old repeated staccato bounce.
        short=n['score_duration']<=.5 and (n['phrase_end'] or n['accent'])
        art='stac' if short else 'sus';layer=(2 if n['velocity']>=84 else 1) if short else 1
        roots=sorted({k[1] for k in p.SAMPLES if k[0]==art});root=min(roots,key=lambda k:abs(k-n['note']))
        rrs[(root,layer)]=rrs.get((root,layer),0)+1;rr=1+rrs[(root,layer)]%2 if short else 1
        x=p.sample(art,root,layer,rr,n['note']);held=n['duration'];release=.030 if short else .043
        count=min(len(x),round((held+release)*SR));tt=np.arange(count)/SR;a=x[:count].copy()
        env=np.minimum(tt/(.006 if n['phrase_start'] else .010),1)
        env*=np.where(tt>held,np.maximum(0,1-(tt-held)/release),1)
        env*=.94+.07*np.sin(np.minimum(tt/max(held,.1),1)*math.pi)
        a*=env.astype(np.float32)*(n['velocity']/88)**1.5
        pan=-.18;st=np.column_stack([a*math.sqrt((1-pan)/2),a*math.sqrt((1+pan)/2)])
        start=round(n['time']*SR);end=min(N,start+count);out[start:end]+=st[:end-start]
        usage.append({'note':n['note'],'sample':p.SAMPLES[(art,root,layer,rr)].name,'shift':n['note']-root,'articulation':art})
    fx=Pedalboard([HighpassFilter(cutoff_frequency_hz=140),PeakFilter(cutoff_frequency_hz=2400,gain_db=-3,q=.7),LowpassFilter(cutoff_frequency_hz=8500)])
    out=fx(out.T,SR).T;sf.write(W/'trumpet_raw.wav',out,SR,subtype='FLOAT')
    (W/'trumpet_samples.json').write_text(json.dumps(usage));print('Trumpet: sustain',sum(n['articulation']=='sus' for n in usage),'short',sum(n['articulation']=='stac' for n in usage))

def mix():
    targets={'trumpet':.042,'sax':.038,'piano':.043,'bass':.056,'drums':.038}
    filters={
      'sax':[HighpassFilter(cutoff_frequency_hz=145),PeakFilter(cutoff_frequency_hz=1600,gain_db=-2,q=.7),LowpassFilter(cutoff_frequency_hz=7500)],
      'piano':[HighpassFilter(cutoff_frequency_hz=140),LowpassFilter(cutoff_frequency_hz=9000)],
      'bass':[HighpassFilter(cutoff_frequency_hz=36),LowpassFilter(cutoff_frequency_hz=3000)],
      'drums':[HighpassFilter(cutoff_frequency_hz=45),PeakFilter(cutoff_frequency_hz=5500,gain_db=-2,q=.8)],'trumpet':[]}
    blend=np.zeros((N,2),np.float32);facts={}
    for voice,target in targets.items():
        x,sr=sf.read(W/(voice+'_raw.wav'),dtype='float32',always_2d=True);assert sr==SR and len(x)>N-10
        x=np.pad(x,((0,max(0,N-len(x))),(0,0)))[:N]
        if filters[voice]:x=Pedalboard(filters[voice])(x.T,SR).T
        if voice=='sax':
            mono=x.mean(axis=1);pan=.22;x=np.column_stack([mono*math.sqrt((1-pan)/2),mono*math.sqrt((1+pan)/2)])
        if voice=='piano':x[:,1]*=.84
        rms=p.active_rms(x,threshold=.001);assert rms>0
        gain=target/rms;x*=gain
        # The horns ease back when they interlock; foreground changes follow the
        # score's entrances and rests rather than pushing both at the listener.
        if voice in ['trumpet','sax']:
            ns=json.loads((W/'notes.json').read_text())[voice]
            envelope=np.ones(N,dtype=np.float32)
            for n in ns:
                if n['phrase_end'] and n['duration']>.3:
                    a=round((n['time']+n['duration']*.60)*SR);b=round((n['time']+n['duration'])*SR)
                    envelope[a:b]*=np.linspace(1,.82,b-a)
            x*=envelope[:,None]
        # Small room shared by the band, with bass kept dry and centered.
        wet=.06 if voice in ['trumpet','sax'] else .035 if voice=='piano' else .015 if voice=='drums' else 0
        if wet:x=Pedalboard([Reverb(room_size=.19,damping=.76,wet_level=wet,dry_level=.98,width=.68)])(x.T,SR).T
        sf.write(W/(voice+'_mixed.wav'),x,SR,subtype='FLOAT');blend+=x
        facts[voice]={'source_active_rms':rms,'gain':gain,'target_active_rms':target,'peak':float(np.max(abs(x)))}
    blend[-int(1.6*SR):]*=np.linspace(1,0,int(1.6*SR))[:,None]
    sf.write(W/'mix_premaster.wav',blend,SR,subtype='FLOAT')
    facts.update({'duration_seconds':N/SR,'tempo':164,'music_start_seconds':START,'section_starts_seconds':[START+128*Q*k for k in range(4)],'duo_end_seconds':START+384*Q,'premaster_peak':float(np.max(abs(blend))),'score_pitches_preserved':True,'sax_plays_written_guitar_part_at_original_concert_pitch':True,'ireal_audio_used':False,'rhythm_notes':'iReal piano voicings and bass, rephrased; newly programmed drums','sound_sources':{'trumpet':'VSCO 2 CE','sax':'Apple Alto Sax EXS','piano':'Apple Steinway Grand Piano 2 EXS','bass':'Apple Upright Jazz Bass EXS','drums':'Apple SoCal Kit EXS'},'lead_level_change_from_v1_db':{'trumpet':20*math.log10(.042/.072),'second_voice':20*math.log10(.038/.065)}})
    (O/'recording_details_v2.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))

def master():
    ff='/usr/local/bin/ffmpeg';src=W/'mix_premaster.wav'
    def run(args):return subprocess.run([ff,'-y','-hide_banner','-nostats']+args,capture_output=True,text=True,check=True)
    def measure(path):
        log=run(['-i',str(path),'-af','loudnorm=I=-17:TP=-1.5:LRA=10:print_format=json','-f','null','-']).stderr
        return json.loads(re.search(r'\{\s*"input_i".*?\}',log,re.S)[0])
    d=measure(src)
    filt=f'loudnorm=I=-17:TP=-1.5:LRA=10:measured_I={d["input_i"]}:measured_TP={d["input_tp"]}:measured_LRA={d["input_lra"]}:measured_thresh={d["input_thresh"]}:offset={d["target_offset"]}:linear=true'
    run(['-i',str(src),'-af',filt,'-ar','44100','-c:a','pcm_s24le',str(W/'master_24bit.wav')])
    facts=json.loads((O/'recording_details_v2.json').read_text())
    for label,extra in [('full_band',[]),('duo_only',['-ss',str(START+128*Q),'-t',str(256*Q),'-af',f'afade=t=in:d=0.02,afade=t=out:st={256*Q-.15}:d=0.15'])]:
        dest=O/f'Glass_Meridian_{label}_trumpet_sax_v2.mp3'
        run(['-i',str(W/'master_24bit.wav')]+extra+['-codec:a','libmp3lame','-b:a','320k','-metadata','title=Glass Meridian - trumpet and alto sax, elastic swing','-metadata','artist=Codex / OpenAI - programmed sample performance','-metadata','genre=Jazz',str(dest)])
        qa=measure(dest);assert float(qa['input_tp'])<-.5
        facts[label]={'full_decode_passed':True,'integrated_lufs':float(qa['input_i']),'true_peak_dbtp':float(qa['input_tp']),'bytes':dest.stat().st_size}
        print(dest.name,facts[label])
    (O/'recording_details_v2.json').write_text(json.dumps(facts,indent=2))
if __name__=='__main__':globals()[sys.argv[1]]()
