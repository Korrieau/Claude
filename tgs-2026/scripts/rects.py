import json
from pypdf import PdfReader
from pypdf.generic import ContentStream

def mul(a,b):
    return [a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
            a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3],
            a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5]]
def pt(m,x,y): return (m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5])

def parse(page, reader):
    cs = ContentStream(page.get_contents(), reader)
    cm=[1,0,0,1,0,0]; stack=[]
    fill=(0,0,0); stroke=(0,0,0)
    pend=[]   # pending subpaths: list of ('re', x,y,w,h) or ('m'/'l', pts)
    out=[]
    cur=[]
    def cmyk2rgb(c,m,y,k):
        return (round(255*(1-min(1,c+k))), round(255*(1-min(1,m+k))), round(255*(1-min(1,y+k))))
    for ops,op in cs.operations:
        o = op.decode() if isinstance(op,bytes) else op
        try:
            if o=='q': stack.append((list(cm),fill,stroke))
            elif o=='Q':
                if stack: cm,fill,stroke = stack.pop(); cm=list(cm)
            elif o=='cm': cm = mul([float(x) for x in ops], cm)
            elif o=='rg': fill = tuple(round(255*float(x)) for x in ops)
            elif o=='RG': stroke = tuple(round(255*float(x)) for x in ops)
            elif o=='g': v=round(255*float(ops[0])); fill=(v,v,v)
            elif o=='G': v=round(255*float(ops[0])); stroke=(v,v,v)
            elif o=='k': fill = cmyk2rgb(*[float(x) for x in ops])
            elif o=='K': stroke = cmyk2rgb(*[float(x) for x in ops])
            elif o in ('sc','scn'):
                nums=[float(x) for x in ops if isinstance(x,(int,float)) or hasattr(x,'as_numeric')]
                if len(nums)==3: fill=tuple(round(255*v) for v in nums)
                elif len(nums)==4: fill=cmyk2rgb(*nums)
                elif len(nums)==1: v=round(255*nums[0]); fill=(v,v,v)
            elif o=='re':
                x,y,w,h=[float(v) for v in ops]
                cur.append(('re',x,y,w,h))
            elif o=='m':
                cur.append(('m',float(ops[0]),float(ops[1])))
            elif o=='l':
                cur.append(('l',float(ops[0]),float(ops[1])))
            elif o in ('f','F','f*','b','b*','B','B*'):
                for s in cur:
                    if s[0]=='re':
                        _,x,y,w,h=s
                        p1=pt(cm,x,y); p2=pt(cm,x+w,y+h)
                        out.append({"x0":min(p1[0],p2[0]),"y0":min(p1[1],p2[1]),
                                    "x1":max(p1[0],p2[0]),"y1":max(p1[1],p2[1]),"c":list(fill)})
                cur=[]
            elif o in ('n','S','s','W','W*'):
                if o in ('n','S','s'): cur=[]
        except Exception:
            cur=[]
    return out

r=PdfReader('map.pdf')
res={}
for i in (0,1):
    rects=parse(r.pages[i], r)
    res[str(i+1)]=rects
    print('page',i+1,'filled rects',len(rects))
json.dump(res,open('rects.json','w'))
