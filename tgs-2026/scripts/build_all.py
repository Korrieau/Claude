import json,re,collections,math
RE=json.load(open('rects.json')); runs=json.load(open('runs2.json'))
cr=re.compile(r'^(\d{2})-([NSCWE])(\d{2,4})$')
ent=re.compile(r'^((?:\d{2}-[NSCWE]\d{2,4}))\s+(.{2,})$')
names={}
for pg in runs:
    for i in pg:
        m=ent.match(i['t'])
        if m:
            c,n=m.group(1),re.sub(r'\s+',' ',m.group(2).strip())
            if c not in names or len(n)>len(names[c]): names[c]=n

def match(page, xr, yr, minw=4.5, minh=3.2, tol=7.0):
    """code -> own rect, matched by top-left corner proximity."""
    R=[r for r in RE[str(page+1)]
       if (r['x1']-r['x0'])>=minw and (r['y1']-r['y0'])>=minh
       and xr[0]-6<=r['x0'] and r['x1']<=xr[1]+6 and yr[0]-6<=r['y0'] and r['y1']<=yr[1]+6]
    lab={}
    for i in runs[page]:
        if cr.match(i['t']) and xr[0]<=i['x']<=xr[1] and yr[0]<=i['y']<=yr[1]:
            lab.setdefault(i['t'],(i['x'],i['y']))
    out={}; unmatched=[]
    for t,(lx,ly) in lab.items():
        best=None
        for r in R:
            dx=abs(r['x0']-(lx-1.8)); dy=abs(r['y0']-(ly-0.7))
            if dx>tol or dy>tol: continue
            d=dx+dy
            if best is None or d<best[0]: best=(d,r)
        if best: out[t]=best[1]
        else: unmatched.append(t)
    return out,unmatched,len(lab)

def blocks(m):
    g=collections.defaultdict(list)
    for t,r in m.items():
        g[(round(r['x0'],2),round(r['y0'],2),round(r['x1'],2),round(r['y1'],2))].append(t)
    return g

m18,u18,n18=match(0,(85,242),(188,1092))
print("halls1-8: matched",len(m18),"/",n18,"unmatched",len(u18))
mh1,uh1,nh1=match(0,(330,530),(850,1095))
print("hall1 inset: matched",len(mh1),"/",nh1,"unmatched",len(uh1))
m911,u911,n911=match(1,(98,780),(356,524))
print("halls9-11: matched",len(m911),"/",n911,"unmatched",len(u911))
mi9,ui9,ni9=match(1,(60,790),(524,832))
print("9-11 inset: matched",len(mi9),"/",ni9,"unmatched",len(ui9))
json.dump({"m18":{k:v for k,v in m18.items()},"mh1":mh1,"m911":m911,"mi9":mi9,
           "un":u18+uh1+u911+ui9}, open('matched.json','w'))

# ---- fallback for unmatched: smallest containing rect
def fallback(page,xr,yr,got):
    R=[r for r in RE[str(page+1)] if (r['x1']-r['x0'])>=4 and (r['y1']-r['y0'])>=3
       and xr[0]-6<=r['x0'] and r['x1']<=xr[1]+6 and yr[0]-6<=r['y0'] and r['y1']<=yr[1]+6]
    add={}
    for i in runs[page]:
        t=i['t']
        if not cr.match(t) or t in got: continue
        if not(xr[0]<=i['x']<=xr[1] and yr[0]<=i['y']<=yr[1]): continue
        b=None
        for r in R:
            if r['x0']-2<=i['x']<=r['x1']+2 and r['y0']-2<=i['y']<=r['y1']+2:
                a=(r['x1']-r['x0'])*(r['y1']-r['y0'])
                if b is None or a<b[0]: b=(a,r)
        if b: add[t]=b[1]
    return add
m18.update(fallback(0,(85,242),(188,1092),m18))
mh1.update(fallback(0,(330,530),(850,1095),mh1))
m911.update(fallback(1,(98,780),(356,524),m911))
mi9.update(fallback(1,(60,790),(524,832),mi9))
print("after fallback:",len(m18),len(mh1),len(m911),len(mi9))

KO=json.load(open('ko.json')) if __import__('os').path.exists('ko.json') else {}
GAMES=json.load(open('games.json')) if __import__('os').path.exists('games.json') else {}
CAT_RULES=json.load(open('catrules.json'))
CFLAG=json.load(open('cflag.json'))
def country(nm,cat):
    for c in sorted(CFLAG,key=len,reverse=True):
        if nm.endswith(" "+c) or nm==c:
            return CFLAG[c], (nm[:len(nm)-len(c)].strip() if nm!=c else nm)
    if cat=="kr": return CFLAG["Korea"], nm
    return CFLAG["Japan"], nm
def cat(nm,hall):
    s=nm.lower()
    for k in ["kr","platform","jp","pavilion","hw","indie"]:
        if any(w.lower() in s for w in CAT_RULES[k]): return k
    return "hw" if hall>=9 else "etc"

def mkblocks(m, proj, hall_of, zoom=False, forcecat=None):
    out=[]
    for k,codes in blocks(m).items():
        codes=sorted(codes)
        nm=[names.get(c,"") for c in codes]
        first=next((n for n in nm if n),"")
        hall=hall_of(codes[0])
        c=forcecat or cat(first,hall)
        (cc,fl,cn),clean = country(first,c) if first else (CFLAG["Japan"],"")
        x,y,w,h=proj(k)
        o={"codes":codes,"hall":hall,"x":round(x,1),"y":round(y,1),"w":round(w,1),"h":round(h,1),
           "n":KO.get(clean,clean) or codes[0],"en":clean,"extra":[n for n in nm if n][1:],
           "g":GAMES.get(codes[0],[]),"c":c,"cc":cc,"fl":fl,"cn":cn}
        if not clean: o["n"]=""
        if zoom: o["zoom"]=1
        out.append(o)
    return out
json.dump({"m18":m18,"mh1":mh1,"m911":m911,"mi9":mi9},open('matched.json','w'))
print("ready")

# ================= compose =================
OX18,OY18=20,60
B=[]
B+=mkblocks(m18, lambda k:(3*k[1]-560+OX18, 3*k[0]-245+OY18, 3*(k[3]-k[1]), 3*(k[2]-k[0])),
            lambda c:int(c[:2]))
h1k=list(blocks(mh1).keys())
IX0=min(k[0] for k in h1k); IX1=max(k[2] for k in h1k)
IY0=min(k[1] for k in h1k); IY1=max(k[3] for k in h1k)
X0,X1,Y0,Y1=2440.0,2790.0,OY18+55.8,OY18+447.0
B+=mkblocks(mh1, lambda k:(X0+(k[1]-IY0)/(IY1-IY0)*(X1-X0), Y0+(k[0]-IX0)/(IX1-IX0)*(Y1-Y0),
                           (k[3]-k[1])/(IY1-IY0)*(X1-X0), (k[2]-k[0])/(IX1-IX0)*(Y1-Y0)),
            lambda c:1)
A9,B9=148.9,-274.2+150
B+=mkblocks(m911, lambda k:(3*k[0]+A9, 3*k[1]+B9, 3*(k[2]-k[0]), 3*(k[3]-k[1])),
            lambda c:int(c[:2]))
base=[b for b in B if b['hall']>=9]
OXi=min(b['x'] for b in base); Wi=max(b['x']+b['w'] for b in base)-OXi
OYi=max(b['y']+b['h'] for b in base)+120
inset=mkblocks(mi9, lambda k:(0,0,0,0), lambda c:int(c[:2]), zoom=True, forcecat="indie")
inset.sort(key=lambda b:b['codes'][0])
CW,CH,GAP=110,48,7
cols=max(6,int(Wi//(CW+GAP)))
for i,b in enumerate(inset):
    r,c=divmod(i,cols)
    b['x']=round(OXi+c*(CW+GAP),1); b['y']=round(OYi+r*(CH+GAP),1); b['w']=CW; b['h']=CH
B+=inset
rows=math.ceil(len(inset)/cols)
prev=json.load(open('map.json'))
d={"booths":B,"marks":prev["marks"],"zones":prev["zones"],
   "insetBox":{"x":round(OXi-26,1),"y":round(OYi-48,1),
     "w":round(cols*(CW+GAP)-GAP+52,1),"h":round(rows*(CH+GAP)-GAP+74,1),
     "t":"확대도 부스 "+str(len(inset))+"곳 · 인디/소형 (배치는 번호순)"}}
H={}
for b in B:
    if b.get('zoom'): continue
    a=H.setdefault(b['hall'],[1e9,1e9,-1e9,-1e9])
    a[0]=min(a[0],b['x']);a[1]=min(a[1],b['y']);a[2]=max(a[2],b['x']+b['w']);a[3]=max(a[3],b['y']+b['h'])
d["halls"]={str(h):{"x":round(v[0],1),"y":round(v[1],1),"w":round(v[2]-v[0],1),"h":round(v[3]-v[1],1)} for h,v in sorted(H.items())}
a=next(m for m in d['marks'] if m['t'].startswith("→ 9–11"))
b2=next(m for m in d['marks'] if m['t'].startswith("← 1–8홀에서"))
d['link']=[a['p'],b2['p']]
d["w"]=round(max(max(b['x']+b['w'] for b in B), d['insetBox']['x']+d['insetBox']['w'], max(m['p'][0] for m in d['marks'])+130)+30)
d["h"]=round(max(max(b['y']+b['h'] for b in B), d['insetBox']['y']+d['insetBox']['h'])+30)
json.dump(d,open('map.json','w'),ensure_ascii=False)
cs={c for b in B for c in b['codes']}
print("FINAL booths",len(B),"codes",len(cs),"canvas",d['w'],d['h'])
for t in ["08-C13","07-C04","02-N12","08-C12"]:
    for b in B:
        if t in b['codes']: print("  ",t,"->",b['n'],"|",b['c'],"| h",b['hall']); break
