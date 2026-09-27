"""Technical verification; not a substitute for a musician's listening review."""
import json,sys
import numpy as np
import soundfile as sf
from scipy.signal import find_peaks
from scipy.fft import rfft,irfft,next_fast_len
import revision2 as r
ns=json.loads((r.W/'notes.json').read_text());results={}
for voice in ['trumpet','sax','bass']:
 x,sr=sf.read(r.W/(voice+'_raw.wav'),dtype='float32',always_2d=True);x=x.mean(axis=1)
 candidates=[n for n in ns[voice] if n['duration']>.24]
 chosen=[candidates[i] for i in np.linspace(0,len(candidates)-1,min(25,len(candidates)),dtype=int)]
 tests=[]
 for n in chosen:
  a=round((n['time']+.065)*sr);length=round(min(.15,n['duration']-.085)*sr);y=x[a:a+length].copy();y-=np.mean(y)
  ft=rfft(y,n=next_fast_len(len(y)*2));ac=irfft(ft*ft.conj())[:len(y)];ac/=max(ac[0],1e-10)
  expected=440*2**((n['note']-69)/12);lo=round(sr/(expected*1.075));hi=round(sr/(expected*.925));lag=lo+np.argmax(ac[lo:hi+1])
  if 0<lag<len(ac)-1:
   delta=.5*(ac[lag-1]-ac[lag+1])/(ac[lag-1]-2*ac[lag]+ac[lag+1]);lag+=delta
  detected=sr/lag;cents=1200*np.log2(detected/expected)
  tests.append({'note':n['note'],'time':n['time'],'cents_from_expected':round(float(cents),2),'periodicity':round(float(ac[round(lag)]),3)})
 results[voice]={'notes_checked':len(tests),'median_absolute_cents':float(np.median([abs(n['cents_from_expected']) for n in tests])),'checks':tests}
 assert results[voice]['median_absolute_cents']<25,(voice,results[voice])
for voice in ['trumpet','sax']:
 ratios=[n['ratio'] for n in ns[voice]];results[voice]['eighth_placement_range']=list(map(float,[min(ratios),max(ratios)]))
results['note_counts']={v:len(n) for v,n in ns.items()}
results['limitations']='Pitch checks search near the intended pitch; verifies local tuning, not a comprehensive musical or listening review.'
(r.O/'pitch_timing_qa_v2.json').write_text(json.dumps(results,indent=2))
print({v:{k:n for k,n in d.items() if k!='checks'} for v,d in results.items() if isinstance(d,dict)})
