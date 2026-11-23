import json,re,os,glob
D='/home/user/Claude/job-radar/data/'
SEC=[('duties',r'담당\s*업무|주요\s*업무|업무\s*내용|하는\s*일|이런\s*일|직무\s*내용|Responsibilities|What you.?ll do|仕事内容|岗位职责|工作职责|职位描述'),
     ('quals',r'자격\s*요건|지원\s*자격|필수\s*(조건|요건|역량)|이런\s*분을|자격요건|Requirements|Qualifications|What we.?re looking for|必须|任职要求|岗位要求|応募資格|必須'),
     ('prefs',r'우대\s*(사항|조건|요건)|이런\s*분이면|Preferred|Nice to have|Bonus|加分|优先|歓迎'),
     ('conds',r'근무\s*(조건|환경|형태|지|시간)|복리\s*후생|혜택|전형\s*절차|채용\s*절차|Benefits|待遇|福利')]
def parse(txt):
  out={k:[] for k,_ in SEC}; cur=None
  for line in txt.split('\n'):
    l=line.strip(' \t•·-*▶▷■□◆◇○●▪✔✓※>|')
    if not l: continue
    hit=None
    if len(l)<=30:
      for k,p in SEC:
        if re.search(p,l,re.I): hit=k;break
    if hit: cur=hit; continue
    if cur and 3<len(l)<=160 and len(out[cur])<14: out[cur].append(l)
  return out
def clean(t):
  t=re.sub(r'\n{2,}','\n',t); t=re.sub(r'[ \t]{2,}',' ',t)
  return t.strip()
bodies=json.load(open('bodies.json')) if os.path.exists('bodies.json') else {}
full=json.load(open('../foreign_full.json')) if os.path.exists('../foreign_full.json') else {}
items={}
for k,v in bodies.items():
  if 'err' in v: continue
  t=v.get('text',''); o=v.get('ocr','')
  use_ocr=len(o)>len(t)*1.2 and len(o)>200
  raw=clean(o if use_ocr else t)
  raw=re.sub(r'^(채용공고 상세페이지|채용공고 상세)\s*','',raw)
  if len(raw)<60: continue
  p=parse(raw); it={'raw':raw[:9000]}
  if use_ocr: it['ocr']=True
  for a,b in [('duties','duties'),('quals','quals'),('prefs','prefs')]:
    if p[a]: it[b]=p[a]
  items[k]=it
for k,v in full.items():
  if k in items: continue
  raw=clean(v); p=parse(raw); it={'raw':raw[:9000]}
  items[k]=it
print('bodies',len(items),'with duties',sum(1 for v in items.values() if v.get('duties')),'ocr',sum(1 for v in items.values() if v.get('ocr')))
# pack
os.makedirs(D+'bodypacks',exist_ok=True)
for f in glob.glob(D+'bodypacks/*.json'): os.remove(f)
packs=[];cur={};size=0
for k in sorted(items):
  s=len(json.dumps(items[k],ensure_ascii=False).encode())
  if size+s>200000: packs.append(cur);cur={};size=0
  cur[k]=items[k];size+=s
packs.append(cur)
for n,p in enumerate(packs,1): json.dump({'items':p},open(D+f'bodypacks/b{n:03d}.json','w'),ensure_ascii=False)
print('packs',len(packs))
