import json,glob,os,re,io,urllib.request,subprocess,concurrent.futures as cf,hashlib,sys
from bs4 import BeautifulSoup
from PIL import Image
D='/home/user/Claude/job-radar/data/'
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36'}
def get(u,ref=None,raw=False):
  h=dict(H); 
  if ref: h['Referer']=ref
  b=urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=40).read()
  return b if raw else b.decode('utf-8','ignore')
targets=[]
for f in glob.glob(D+'jobs/*.json'):
  j=json.load(open(f)); targets.append((os.path.basename(f)[:-5],j['url']))
for f in glob.glob(D+'jobpacks/*.json'):
  for k,j in json.load(open(f))['items'].items(): targets.append((k,j['url']))
def src(u):
  m=re.search(r'GI_No=(\d+)',u)
  if 'gamejob' in u and m: return ('https://www.gamejob.co.kr/Recruit/GI_Read_Comt_Ifrm?gno='+m.group(1),'https://www.gamejob.co.kr/')
  m=re.search(r'rec_idx=(\d+)',u)
  if 'saramin' in u and m: return (f'https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx={m.group(1)}&rec_seq=0','https://www.saramin.co.kr/')
  m=re.search(r'jobkorea.co.kr/Recruit/GI_Read/(\d+)',u)
  if m: return ('https://www.jobkorea.co.kr/Recruit/GI_Read_Comt_Ifrm?Gno='+m.group(1),'https://www.jobkorea.co.kr/')
  return None
targets=[(k,src(u)) for k,u in targets if src(u)]
done=json.load(open('bodies.json')) if os.path.exists('bodies.json') else {}
targets=[t for t in targets if t[0] not in done]
print('targets',len(targets),flush=True)
def ocr(urls,ref):
  out=[]
  for u in urls[:6]:
    try:
      b=get(u,ref,raw=True); im=Image.open(io.BytesIO(b)).convert('L')
      if im.size[0]<200 or im.size[1]<150: continue
      if im.size[0]>1400: im=im.resize((1400,int(im.size[1]*1400/im.size[0])))
      parts=[]
      for y in range(0,im.size[1],2000):
        p=f'img/{hashlib.md5((u+str(y)).encode()).hexdigest()}.png'; im.crop((0,y,im.size[0],min(im.size[1],y+2000))).save(p)
        r=subprocess.run(['tesseract',p,'-','-l','kor+eng','--psm','4'],capture_output=True,text=True,timeout=120); parts.append(r.stdout); os.remove(p)
      out.append('\n'.join(parts))
    except Exception as e: pass
  return '\n'.join(out)
def work(t):
  k,(u,ref)=t
  try:
    s=BeautifulSoup(get(u,ref),'html.parser')
    for x in s(['script','style','noscript']): x.decompose()
    txt=s.get_text('\n',strip=True)
    txt=re.sub(r'\n{2,}','\n',txt)
    imgs=[]
    for i in s.select('img'):
      src_=i.get('src') or i.get('data-src') or ''
      if src_.startswith('//'): src_='https:'+src_
      if src_.startswith('http') and not re.search(r'logo|icon|btn|blank|template/toptype|spacer',src_,re.I): imgs.append(src_)
    o=''
    if len(txt)<400 and imgs: o=ocr(imgs,ref)
    return k,{'text':txt,'ocr':o,'imgs':imgs[:6]}
  except Exception as e: return k,{'err':str(e)[:60]}
n=0
with cf.ThreadPoolExecutor(6) as ex:
  for k,v in ex.map(work,targets):
    done[k]=v; n+=1
    if n%50==0: json.dump(done,open('bodies.json','w'),ensure_ascii=False); print(n,flush=True)
json.dump(done,open('bodies.json','w'),ensure_ascii=False); print('done',n,flush=True)
