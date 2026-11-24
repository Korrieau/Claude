"""Build the next translation pack from compact model output.
Usage: python3 tools/trpack.py OUT1.json [OUT2.json ...]
Each input: {"<job id>": {"s": summary, "d": [duties], "q": [quals], "p": [prefs]}} (Korean).
Writes data/trpacks/tNNN.json (≤180KB each); upload with ArtifactData set (collection trpacks)."""
import json,glob,sys,datetime,os
M={}
for f in sys.argv[1:]: M.update(json.load(open(f)))
today=datetime.date.today().isoformat()
items={k:{'summary':v.get('s',''),'duties':v.get('d',[]),'quals':v.get('q',[]),'prefs':v.get('p',[]),'at':today,'by':'weekly'} for k,v in M.items()}
os.makedirs('data/trpacks',exist_ok=True)
n=max([int(os.path.basename(f)[1:4]) for f in glob.glob('data/trpacks/t*.json')]+[0])+1
packs=[{}];s=0
for k,v in items.items():
  b=len(json.dumps(v,ensure_ascii=False).encode())+len(k)+10
  if s+b>180000: packs.append({}); s=0
  packs[-1][k]=v; s+=b
for p in packs:
  if not p: continue
  f=f'data/trpacks/t{n:03d}.json'; json.dump({'items':p,'updated':today},open(f,'w'),ensure_ascii=False); print(f,len(p)); n+=1
