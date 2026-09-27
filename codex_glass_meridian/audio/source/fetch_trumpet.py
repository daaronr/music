from pathlib import Path
import json, urllib.request, urllib.parse, concurrent.futures, hashlib
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'work'/'vsco_trumpet_manifest.json').read_text())
keys=['_C3_','_D#3_','_G3_','_A#3_','_D4_','_F4_','_A4_','_C5_']
selected=[r for r in rows if r['type']=='blob' and any(k in r['path'] for k in keys) and ('/sus/' in r['path'] or '/stac/' in r['path'])]
dest=R/'assets'/'vsco_trumpet';dest.mkdir(parents=True,exist_ok=True)
def one(row):
 p=dest/Path(row['path']).name
 u='https://raw.githubusercontent.com/sgossner/VSCO-2-CE/master/'+urllib.parse.quote(row['path'])
 if not p.exists():p.write_bytes(urllib.request.urlopen(u,timeout=45).read())
 assert p.stat().st_size==row['size']
 return {'file':p.name,'url':u,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:results=list(ex.map(one,selected))
(R/'source'/'sample_manifest.json').write_text(json.dumps(results,indent=2))
print(f'Downloaded and verified {len(results)} WAV samples, {sum(x["bytes"] for x in results)/1e6:.1f} MB')
