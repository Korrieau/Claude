"""Download candidates from cand.json, score them, write the best per company (per job for headhunt) as art/c/<key>.webp.
Score favours colourful pictures over logos and text-only posting images. Tall posting images are cropped from the top."""
import json,sys,os,subprocess,hashlib
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageStat
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36'
RELAX='--relax' in sys.argv
cand=json.load(open(sys.argv[1])); jobs={j['id']:j for j in json.load(open(sys.argv[2]))}; out_dir=sys.argv[3]; tmp=sys.argv[4]
os.makedirs(out_dir,exist_ok=True); os.makedirs(tmp,exist_ok=True)
def dl(u):
    f=os.path.join(tmp,hashlib.md5(u.encode()).hexdigest())
    if not os.path.exists(f): subprocess.run(['curl','-sL','-m','25','-A',UA,'-o',f,u])
    return f
def crop169(im):
    W,H=im.size
    if W/H>16/9: nw=int(H*16/9); l=(W-nw)//2; return im.crop((l,0,l+nw,H))
    nh=int(W*9/16); t=0 if H>W*1.2 else (H-nh)//3; return im.crop((0,t,W,t+nh))
def score(f):
    try: im=Image.open(f); im.load(); im=im.convert('RGB')
    except Exception: return None
    W,H=im.size
    if W<480 or H<200: return None
    c=crop169(im); s=c.resize((96,54))
    hsv=s.convert('HSV'); st=ImageStat.Stat(hsv); sat=st.mean[1]
    px=list(s.get_flattened_data()) if hasattr(s,'get_flattened_data') else list(s.getdata()); white=sum(1 for p in px if min(p)>225)/len(px); flat=ImageStat.Stat(s.convert('L')).stddev[0]
    if white>(0.9 if RELAX else 0.55) or flat<(6 if RELAX else 18): return None
    return sat*0.6+flat*0.8-white*80+(10 if W>=900 else 0), c
groups={}
for jid,us in cand.items():
    j=jobs.get(jid); 
    if not j or not us: continue
    key=('j-'+jid) if j.get('company_id') in ('headhunt',None,'') else j['company_id']
    groups.setdefault(key,[]).extend(us[:5])
def best(item):
    key,us=item; top=None
    for u in list(dict.fromkeys(us))[:8]:
        r=score(dl(u))
        if r and (not top or r[0]>top[0]): top=r
    if top:
        safe=''.join(ch if ch.isalnum() or ch in '-_' else '_' for ch in key)
        top[1].resize((640,360),Image.LANCZOS).save(os.path.join(out_dir,safe+'.webp'),'WEBP',quality=62,method=6)
        return key,safe
    return key,None
prev=json.load(open(os.path.join(out_dir,'_map.json'))) if RELAX and os.path.exists(os.path.join(out_dir,'_map.json')) else {}
todo=[(k,v) for k,v in groups.items() if k not in prev]
with ThreadPoolExecutor(8) as ex: res=dict(ex.map(best,todo))
res={**prev,**res}
json.dump({k:v for k,v in res.items() if v},open(os.path.join(out_dir,'_map.json'),'w'),ensure_ascii=False)
print('picked',sum(1 for v in res.values() if v),'of',len(res))
