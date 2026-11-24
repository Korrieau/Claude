"""Collect a related image for postings/companies that have no key art.
Input: missing_jobs.json (list of job dicts with id,url,company_id). Output: cand.json {job_id:[image urls]}
Sources: saramin view-detail images, gamejob company photos/content, green-japan photos, wanted company images, og:image elsewhere."""
import json,re,subprocess,sys,html,urllib.parse
from concurrent.futures import ThreadPoolExecutor
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36'
BAD=re.compile(r'icon|logo|ico_|btn|blank|spacer|banner/share|gamejob_share|nav_wrap|ads\.|sprite|loading|profile|avatar|qr',re.I)
def get(u,ref=None):
    a=['curl','-sL','-m','25','-A',UA]+(['-e',ref] if ref else [])+[u]
    return subprocess.run(a,capture_output=True).stdout.decode('utf8','ignore')
def imgs(h,base):
    out=[]
    for m in re.finditer(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)',h): out.append(m.group(1))
    for m in re.finditer(r'<img[^>]+?(?:data-src|src)=["\']([^"\']+)',h): out.append(m.group(1))
    res=[]
    for u in out:
        u=html.unescape(u).replace('\\','/')
        if u.startswith('data:'): continue
        u=urllib.parse.urljoin(base,u)
        if BAD.search(u): continue
        if u not in res: res.append(u)
    return res
def one(j):
    u=j.get('url') or ''; h=u.split('/')[2] if '//' in u else ''
    try:
        if 'saramin' in h:
            m=re.search(r'rec_idx=(\d+)',u)
            if not m: return j['id'],[]
            d='https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx='+m.group(1)+'&rec_seq=0'
            return j['id'],imgs(get(d,u),d)
        if 'gamejob' in h:
            r=imgs(get(u),u); return j['id'],[x for x in r if 'CoPhoto' in x or 'GI_Image' in x or 'Editor' in x or 'file.gamejob' in x]
        if 'green-japan' in h:
            r=imgs(get(u),u); return j['id'],[x for x in r if '/photo/' in x and '/160/' not in x]
        if 'wanted.co.kr' in h:
            r=imgs(get(u),u); return j['id'],[x for x in r if 'images/company' in x or 'images/wdes' in x]
        if 'jobkorea' in h:
            g=re.search(r'GI_Read/(\d+)',u)
            if g:
                d=f'https://www.jobkorea.co.kr/Recruit/GI_Read_Comt_Ifrm?Gno={g.group(1)}&PageGbn=HH&blnKeepInLink=0&rPageCode='
                return j['id'],imgs(get(d,u),d)
            return j['id'],[]
        return j['id'],imgs(get(u),u)[:6]
    except Exception as e: return j['id'],[]
if __name__=='__main__':
    jobs=json.load(open(sys.argv[1]))
    with ThreadPoolExecutor(8) as ex: res=dict(ex.map(one,jobs))
    json.dump(res,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
    print(sum(1 for v in res.values() if v),'/',len(res))
