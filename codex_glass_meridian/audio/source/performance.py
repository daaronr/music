#!/usr/bin/env python3
"""Render the written music as an expressive sample performance over iReal audio.
No melody notes are improvised or substituted. Randomness is reproducible.
"""
from pathlib import Path
import sys, json, re, math, xml.etree.ElementTree as ET
from fractions import Fraction
from functools import lru_cache
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, PeakFilter, Compressor, Reverb, Gain
R=Path(__file__).resolve().parents[1];SCORE=R.parent/'output'/'musicxml'
SR=44100;BPM=164;Q=60/BPM;START=8*Q # WAV has eight count-in beats; MIDI only four.
NAT={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
rng=np.random.default_rng(164926)

def parse(path,part=0):
 out=[]
 for m in ET.parse(path).getroot().findall('part')[part].findall('measure'):
  bar=[];offset=0.
  for n in m.findall('note'):
   dur=int(n.findtext('duration'))/12;p=n.find('pitch')
   pitch=None if p is None else 12*(int(p.findtext('octave'))+1)+NAT[p.findtext('step')]+int(p.findtext('alter','0'))
   bar.append({'offset':offset,'dur':dur,'pitch':pitch,'accent':n.find('notations/articulations/accent') is not None});offset+=dur
  assert offset==4
  out.append(bar)
 return out
H=parse(SCORE/'01_head_concert.musicxml');T=parse(SCORE/'03_duo_score_concert.musicxml');G=parse(SCORE/'03_duo_score_concert.musicxml',1)
TRUMPET=H+T+H;GUITAR=[[] for _ in H]+G+[[] for _ in H]

def swing(beat,ratio):
 whole=math.floor(beat);f=beat-whole
 return whole+(2*ratio*f if f<=.5 else ratio+2*(1-ratio)*(f-.5))
def make_events(bars,voice):
 out=[];phrase_shift=0
 for b,bar in enumerate(bars):
  if b%4==0:phrase_shift=float(rng.normal(0,.003))
  ratio=.645 if 64<=b<96 else .665
  peak=80<=b<88
  last_pitch=None
  for k,n in enumerate(bar):
   if n['pitch'] is None:last_pitch=None;continue
   slot=n['offset'];dur=n['dur'];is_last=k==len(bar)-1 or bar[k+1]['pitch'] is None
   start=START+Q*(4*b+swing(slot,ratio))
   end=START+Q*(4*b+swing(slot+dur,ratio))
   human=phrase_shift+float(rng.normal(0,.0025))+(.010 if voice=='guitar' else .003)
   start+=human;end+=human
   gate=.96 if dur<=.5 else .93
   if is_last:gate-=.06
   length=max(.07,(end-start)*gate)
   base=(94 if peak else 83 if b<32 or b>=96 else 85 if b>=64 else 78)
   if voice=='guitar':base=(89 if (40<=b<48 or 72<=b<80) else 80 if b>=64 else 74)
   if slot%1==.5:base+=4
   if n['accent']:base+=5
   if last_pitch is None:base+=2
   # Four-bar dynamic arcs, plus a modest lift towards the tops of phrases.
   base+=3*math.sin(((b%4)+slot/4)*math.pi/4)
   if voice=='trumpet' and n['pitch']>=79:base+=2
   velocity=int(np.clip(base+rng.normal(0,2),55,111))
   out.append({'time':round(start,7),'duration':round(length,7),'note':n['pitch'],'velocity':velocity,'bar':b+1,'phrase_start':last_pitch is None,'phrase_end':is_last,'score_duration':dur})
   last_pitch=n['pitch']
 return out

def prepare():
 t=make_events(TRUMPET,'trumpet');g=make_events(GUITAR,'guitar')
 (R/'work'/'performance_events.json').write_text(json.dumps({'trumpet':t,'guitar':g},indent=2))
 events=[]
 for n in g:
  events.extend([{'time':n['time'],'on':True,'note':n['note'],'velocity':n['velocity']},{'time':n['time']+n['duration'],'on':False,'note':n['note'],'velocity':0}])
 events.sort(key=lambda e:(e['time'],e['on']))
 (R/'work'/'guitar_events.json').write_text(json.dumps(events))
 # Portable MIDI of the exact humanised lead timing, separate from audio renders.
 import mido
 mf=mido.MidiFile(ticks_per_beat=960)
 tempo=mido.MidiTrack();tempo.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM)));mf.tracks.append(tempo)
 for ix,(name,ns,pg) in enumerate([('Trumpet',t,56),('Guitar',g,26)]):
  tr=mido.MidiTrack();tr.append(mido.MetaMessage('track_name',name=name));tr.append(mido.Message('program_change',channel=ix,program=pg));last=0;es=[]
  for n in ns:
   for sec,typ,v in [(n['time'],'note_on',n['velocity']),(n['time']+n['duration'],'note_off',0)]:es.append((round(sec/Q*960),typ,n['note'],v))
  for tick,typ,pitch,v in sorted(es,key=lambda z:(z[0],z[1]=='note_on')):
   tr.append(mido.Message(typ,channel=ix,note=pitch,velocity=v,time=tick-last));last=tick
  mf.tracks.append(tr)
 mf.save(R/'output'/'Glass_Meridian_expressive_leads.mid')
 expected_t=[n['pitch'] for b in TRUMPET for n in b if n['pitch'] is not None];expected_g=[n['pitch'] for b in GUITAR for n in b if n['pitch'] is not None]
 assert [n['note'] for n in t]==expected_t and [n['note'] for n in g]==expected_g
 print(f'Prepared {len(t)} trumpet notes and {len(g)} guitar notes; exact score pitch/order retained.')

# VSCO uses C3 for MIDI 60, confirmed from the samples themselves (about 262 Hz).
def root_from_name(name):
 match=re.search(r'_([A-G])(#?)(\d)_v',name);l,sharp,octave=match.groups()
 return (int(octave)+2)*12+NAT[l]+bool(sharp)
SAMPLES={}
for p in (R/'assets'/'vsco_trumpet').glob('*.wav'):
 art='stac' if '_stac_' in p.name else 'sus';layer=int(re.search(r'_v(\d)_',p.name)[1]);rr=int(re.search(r'_rr(\d)',p.name)[1])
 SAMPLES[(art,root_from_name(p.name),layer,rr)]=p

@lru_cache(maxsize=256)
def sample(art,root,layer,rr,pitch):
 p=SAMPLES[(art,root,layer,rr)];x,sr=sf.read(p,dtype='float32',always_2d=True);assert sr==SR
 x=x.mean(axis=1)
 # Only leading silence is removed. Recorded breath/noise within the note remains.
 level=np.convolve(x*x,np.ones(128)/128,mode='same');threshold=float(np.max(level))*.003
 active=np.flatnonzero(level>threshold);first=max(0,int(active[0])-88);x=x[first:]
 region=x[int(.025*SR):int((.17 if art=='stac' else .45)*SR)]
 rms=float(np.sqrt(np.mean(region*region)))
 x=x*(.12/max(rms,.005))
 ratio=Fraction(2**((root-pitch)/12)).limit_denominator(2000)
 y=resample_poly(x,ratio.numerator,ratio.denominator).astype(np.float32)
 return y

def trumpet():
 ns=json.loads((R/'work'/'performance_events.json').read_text())['trumpet']
 dur=sf.info(R/'work'/'ireal_backing_164.wav').duration
 output=np.zeros((round(dur*SR),2),dtype=np.float32)
 rr_counts={};selected=[]
 for i,n in enumerate(ns):
  short=n['score_duration']<=.5;art='stac' if short else 'sus'
  roots=sorted({key[1] for key in SAMPLES if key[0]==art});root=min(roots,key=lambda k:abs(k-n['note']))
  if short:layer=1 if n['velocity']<80 else 2 if n['velocity']<95 else 3
  else:layer=1 if n['velocity']<94 else 3
  rr_counts[(root,layer)]=rr_counts.get((root,layer),0)+1;rr=1+(rr_counts[(root,layer)]%2) if short else 1
  x=sample(art,root,layer,rr,n['note'])
  held=n['duration'];release=.035 if short else .065
  count=round((held+release)*SR);count=min(count,len(x));a=x[:count].copy()
  tt=np.arange(count)/SR
  # Tiny inflections on occasional phrase starts and tails, far less than a semitone.
  cents=np.zeros(count)
  if n['phrase_start'] and i%3==0 and not short:cents-=18*np.exp(-tt/.026)
  if n['phrase_end'] and not short:cents-=10*np.clip((tt-held+.04)/.10,0,1)
  if np.any(cents):
   pos=np.cumsum(2**(cents/1200))-1;a=np.interp(pos,np.arange(count),a).astype(np.float32)
  env=np.minimum(tt/.004,1)
  env*=np.where(tt>held,np.maximum(0,1-(tt-held)/release),1)
  if not short:env*=.90+.12*np.sin(np.minimum(tt/max(held,.1),1)*np.pi)
  amp=(n['velocity']/92)**1.35
  a*=env.astype(np.float32)*amp
  pan=-.20 # trumpet slightly left, guitar slightly right
  stereo=np.column_stack([a*math.sqrt((1-pan)/2),a*math.sqrt((1+pan)/2)])
  start=round(n['time']*SR);end=min(len(output),start+len(a));output[start:end]+=stereo[:end-start]
  selected.append({'bar':n['bar'],'note':n['note'],'sample':SAMPLES[(art,root,layer,rr)].name,'shift_semitones':n['note']-root})
 fx=Pedalboard([HighpassFilter(cutoff_frequency_hz=135),PeakFilter(cutoff_frequency_hz=2800,gain_db=-1.8,q=.8),LowpassFilter(cutoff_frequency_hz=10500),Compressor(threshold_db=-17,ratio=1.6,attack_ms=15,release_ms=100),Reverb(room_size=.20,damping=.72,wet_level=.11,dry_level=.94,width=.72)])
 output=fx(output.T,SR).T
 sf.write(R/'work'/'trumpet_processed.wav',output,SR,subtype='FLOAT')
 (R/'work'/'trumpet_sample_usage.json').write_text(json.dumps(selected,indent=2))
 print('Trumpet rendered; peak',round(float(np.max(abs(output))),4),'all notes sampled within',max(abs(x['shift_semitones']) for x in selected),'semitones of recorded root.')

def active_rms(x,threshold=.008):
 blocks=x[:len(x)//1024*1024].reshape(-1,1024,2);power=np.mean(blocks**2,axis=(1,2));return float(np.sqrt(np.mean(power[power>threshold**2])))

def mix():
 bed,sr=sf.read(R/'work'/'ireal_backing_164.wav',dtype='float32',always_2d=True);assert sr==SR
 t,_=sf.read(R/'work'/'trumpet_processed.wav',dtype='float32',always_2d=True)
 g,_=sf.read(R/'work'/'guitar_raw.wav',dtype='float32',always_2d=True);assert len(g)>0
 n=len(bed);g=np.pad(g,((0,max(0,n-len(g))),(0,0)))[:n]
 gf=Pedalboard([HighpassFilter(cutoff_frequency_hz=105),LowpassFilter(cutoff_frequency_hz=4400),PeakFilter(cutoff_frequency_hz=230,gain_db=1.8,q=.8),Compressor(threshold_db=-25,ratio=2,attack_ms=12,release_ms=110),Reverb(room_size=.20,damping=.76,wet_level=.12,dry_level=.93,width=.72)])
 g=gf(g.T,SR).T;gmono=g.mean(axis=1);pan=.28;g=np.column_stack([gmono*math.sqrt((1-pan)/2),gmono*math.sqrt((1+pan)/2)])
 # Match active soloist loudness without flattening their phrase dynamics.
 trms=active_rms(t);grms=active_rms(g)
 tg=.072/trms;gg=.065/grms
 # The piano-bass-drums bed stays supportive; lift it only across the ending.
 bg=np.full(n,.44,dtype=np.float32);music_end=START+128*4*Q
 end_ix=int(music_end*SR);bg[end_ix:]=np.linspace(.44,.70,n-end_ix)
 blend=bed*bg[:,None]+t*tg+g*gg
 # Fade the existing room decay, keeping the final band chord intact.
 fade=round(1.3*SR);blend[-fade:]*=np.linspace(1,0,fade)[:,None]
 sf.write(R/'work'/'guitar_processed.wav',g,SR,subtype='FLOAT')
 sf.write(R/'work'/'mix_premaster.wav',blend,SR,subtype='FLOAT')
 facts={'tempo':BPM,'sample_rate':SR,'duration_seconds':n/SR,'count_in_beats':8,'music_start_seconds':START,'form':['head','duo chorus I','duo chorus II','head out'],'section_starts_seconds':[START+128*Q*k for k in range(4)],'duo_end_seconds':START+384*Q,'trumpet_engine':'VSCO 2 CE multi-sample offline renderer','guitar_engine':'Apple AVAudioUnitSampler, installed Vintage Strat EXS24','backing_engine':'iReal Pro Jazz - Medium Up Swing, piano/acoustic bass/Real Drums','trumpet_gain':tg,'guitar_gain':gg,'backing_gain':.44,'premaster_peak':float(np.max(abs(blend))),'active_trumpet_rms':trms*tg,'active_guitar_rms':grms*gg,'score_pitches_preserved':True,'seed':164926}
 (R/'output'/'recording_details.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':{'prepare':prepare,'trumpet':trumpet,'mix':mix}[sys.argv[1]]()
