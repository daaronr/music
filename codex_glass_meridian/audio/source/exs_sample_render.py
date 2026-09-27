"""Minimal offline reader for local Apple EXS zones used in this performance.
Binary field reference: asatamax/tonverk-elmulti-converter docs/EXS24_FORMAT_SPEC.md.
Handles sample/zone mappings; it does not implement Logic's complete instrument DSP.
"""
import struct,json,math,sys
from pathlib import Path
from functools import lru_cache
from fractions import Fraction
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import revision2 as r
FILES={'piano':'01 Acoustic Pianos/Steinway Grand Piano 2.exs','drums':'03 Drums & Percussion/04 Drum Kit Designer/Drum Kit Designer/Stereo/SoCal Kit.exs'}

def parse(voice):
 d=(Path('/Library/Application Support/Logic/Sampler Instruments')/FILES[voice]).read_bytes();pos=0;zones=[];groups=[];samples=[]
 while pos<len(d):
  sig,size=struct.unpack_from('<II',d,pos);typ=(sig>>24)&15;name=d[pos+20:pos+84].split(b'\0')[0].decode();v=d[pos+84:pos+84+size]
  if typ==1:
   zones.append(dict(name=name,flags=v[0],root=v[1],fine=struct.unpack_from('b',v,2)[0],pan=struct.unpack_from('b',v,3)[0],volume=struct.unpack_from('b',v,4)[0],low=v[6],high=v[7],vlo=v[9],vhi=v[10],start=struct.unpack_from('<I',v,12)[0],end=struct.unpack_from('<I',v,16)[0],group=struct.unpack_from('<i',v,88)[0],sample=struct.unpack_from('<I',v,92)[0]))
  if typ==2:groups.append(dict(name=name,volume=struct.unpack_from('b',v,0)[0],vlo=v[5],vhi=v[6],release=bool(v[73]),kind=v[84] if len(v)>84 else 0))
  if typ==3:
   path=v[80:336].split(b'\0')[0].decode();file=v[336:592].split(b'\0')[0].decode()
   samples.append(dict(name=name,path=str(Path(path)/file),rate=struct.unpack_from('<I',v,8)[0]))
  pos+=size+84
 return zones,groups,samples

if __name__=='__main__' and sys.argv[1]=='inspect':
 for voice in FILES:
  z,g,s=parse(voice);print(voice,'samples',s,'groups',g)
  print('zones',z[:5]);print('matching C4 or ride',[x for x in z if x['low']<=(60 if voice=='piano' else 51)<=x['high']][:8])

def render(voice):
 zones,groups,samples=parse(voice);notes=json.loads((r.W/'notes.json').read_text())[voice]
 out=np.zeros((r.N,2),np.float32);used=[];counts={}
 @lru_cache(maxsize=256)
 def get(index,pitch):
  z=zones[index];x,sr=sf.read(samples[z['sample']]['path'],start=z['start'],stop=z['end'],dtype='float32',always_2d=True)
  assert len(x)>0
  if x.shape[1]==1:x=np.repeat(x,2,axis=1)
  shift=0 if z['flags']&2 else z['root']-pitch
  factor=(r.SR/sr)*2**((shift+z['fine']/100)/12)
  if abs(factor-1)>1e-8:
   rat=Fraction(factor).limit_denominator(2000);x=resample_poly(x,rat.numerator,rat.denominator,axis=0)
  group=groups[z['group']];x*=10**((z['volume']+group['volume'])/20)
  return x
 for n in notes:
  candidates=[]
  mapped_note=({44:33,50:48}.get(n['note'],n['note']) if voice=='drums' else n['note'])
  for i,z in enumerate(zones):
   g=groups[z['group']]
   if g['release'] or (voice=='piano' and z['group']>=16):continue
   if z['low']<=mapped_note<=z['high'] and z['vlo']<=n['velocity']<=z['vhi'] and g['vlo']<=n['velocity']<=g['vhi']:candidates.append(i)
  assert candidates,(voice,n)
  k=(n['note'],n['velocity']);counts[k]=counts.get(k,0)+1;index=candidates[(counts[k]-1)%len(candidates)]
  x=get(index,n['note']).copy();z=zones[index]
  if voice=='piano':
   held=n['duration'];release=.22;length=min(len(x),round((held+release)*r.SR));x=x[:length]
   t=np.arange(length)/r.SR;env=np.minimum(t/.0015,1)*np.where(t>held,np.exp(-5*(t-held)/release),1)
   x*=env[:,None]*(n['velocity']/83)**.75
  else:
   # One-shot drum samples retain their natural decay, independent of MIDI gates.
   fade=min(round(.025*r.SR),len(x));x[-fade:]*=np.linspace(1,0,fade)[:,None]
   x*=(n['velocity']/75)**.65
  start=round(n['time']*r.SR);end=min(r.N,start+len(x));out[start:end]+=x[:end-start]
  used.append({'note':n['note'],'zone':index,'sample':samples[z['sample']]['name'],'root':z['root'],'start':z['start'],'end':z['end']})
 sf.write(r.W/(voice+'_raw.wav'),out,r.SR,subtype='FLOAT');(r.W/(voice+'_samples.json')).write_text(json.dumps(used))
 print(voice,len(notes),'notes',len(set(x['zone'] for x in used)),'sample zones','peak',float(np.max(abs(out))))
if __name__=='__main__' and sys.argv[1]!='inspect':render(sys.argv[1])
