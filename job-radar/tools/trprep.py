"""Weekly translation prep: pick foreign postings that still lack Korean details and
write a compact input file (only duty/requirement/preferred lines) to keep tokens low.
Usage: python3 tools/trprep.py OUT.json [--all] [--max=60]   (run from job-radar/, after data/ is synced from the app DB)
Priority (default): Korea-related titles, IP/goods job_type, or added in the last 8 days with fit-relevant roles."""
import json,glob,re,sys,datetime
SEC=[('duties',r'工作职责|岗位职责|职位描述|岗位描述|職務内容|業務内容|仕事内容|Responsibilities|What you.?ll do|About the role|Job Description|职责'),
     ('quals',r'任职要求|岗位要求|任职资格|応募資格|必須|必须|Requirements|Qualifications|What we.?re looking for|You have|Must'),
     ('prefs',r'加分|优先|歓迎|尚可|Preferred|Nice to have|Bonus|Plus')]
CUT=re.compile(r'(概要|募集背景|この仕事で得られるもの|配属部署|会社概要|About (us|the company)).*',re.S)
def parse(t):
  out={'duties':[],'quals':[],'prefs':[]};cur=None
  for line in t.split('\n'):
    l=line.strip(' \t•·-*▶■□◆◇○●▪✔✓※>|・【】')
    if not l: continue
    hit=None
    if len(l)<=40:
      for k,p in SEC:
        if re.search(p,l,re.I): hit=k;break
    if hit: cur=hit; continue
    if cur and 4<len(l)<=220 and len(out[cur])<5: out[cur].append(l[:100])
  return out
J={}
for f in sorted(glob.glob('data/jobpacks/*.json')): J.update(json.load(open(f))['items'])
for f in glob.glob('data/jobs/*.json'): J[f.split('/')[-1][:-5]]=json.load(open(f))
B={}
for f in glob.glob('data/bodypacks/*.json'): B.update(json.load(open(f))['items'])
DONE=set()
for f in glob.glob('data/trpacks/*.json'): DONE|=set(json.load(open(f))['items'])
KR=re.compile(r'한국|韩|Korea|韓国')
week=(datetime.date.today()-datetime.timedelta(days=8)).isoformat()
allmode='--all' in sys.argv
out=[]
for k,j in J.items():
  if k in DONE or j.get('closed') or j.get('lang_original_label','한국어')=='한국어' or (j.get('duties') or []): continue
  rank=0 if KR.search(j['title']+j.get('title_original','')) else 1 if j.get('job_type')=='ip' else 2 if (j.get('added','')>=week and j.get('job_type') in('bizpm','publish','service','local','mkt')) else 3
  if rank==3 and not allmode: continue
  raw=(B.get(k,{}).get('raw') or j.get('raw') or '')
  p=parse(raw)
  x={'id':k,'t':j['title'],'_r':rank,'_a':j.get('added','')}
  if any(p.values()): x.update({a:b for a,b in p.items() if b})
  else: x['text']=[CUT.sub('',re.sub(r'\s+',' ',raw))[:420]]
  out.append(x)
MAX=int(next((a.split('=')[1] for a in sys.argv if a.startswith('--max=')),'60'))
out.sort(key=lambda x:(x['_r'],x['_a']),reverse=False)
out=sorted(out,key=lambda x:(x['_r'],-int((x['_a'] or '0').replace('-',''))))[:MAX]
for x in out: x.pop('_r');x.pop('_a')
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False)
print('to translate',len(out),'chars',sum(len(json.dumps(x,ensure_ascii=False)) for x in out))
