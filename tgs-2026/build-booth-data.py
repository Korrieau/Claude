import json,re,collections
d=json.load(open('runs2.json'))
code_re=re.compile(r'^(\d{2})-([NSCWE])(\d{2,4})$')
ent_re=re.compile(r'^((?:\d{2}-[NSCWE]\d{2,4}))\s+(.{2,})$')

# 1) names from exhibitor list (both pages)
names={}
for pi in (0,1):
    for i in d[pi]:
        m=ent_re.match(i['t'])
        if m:
            c,n=m.group(1),m.group(2).strip()
            n=re.sub(r'\s+',' ',n)
            if c not in names or len(n)>len(names[c]): names[c]=n

# 2) positions: page0 halls 1-8 strip, page1 halls 9-11
pos={}
for i in d[0]:
    m=code_re.match(i['t'])
    if m and 85<=i['x']<=240 and 190<=i['y']<=1090:
        pos.setdefault(i['t'],(0,i['x'],i['y']))
for i in d[1]:
    m=code_re.match(i['t'])
    if m and 340<=i['y']<=515:
        pos.setdefault(i['t'],(1,i['x'],i['y']))

HALLS8={'01':(978,1090),'02':(855,978),'03':(766,855),'04':(614,766),'05':(534,614),
        '06':(430,534),'07':(278,430),'08':(196,278)}
HALLS911={'09':(100,415),'10':(416,600),'11':(601,765)}

out=[]
for code,(pg,x,y) in sorted(pos.items()):
    h=code[:2]
    if pg==0:
        if h not in HALLS8: continue
        y0,y1=HALLS8[h]
        # nx: 0=West edge of hall -> 1=East edge   (y high = West)
        nx=(y1-y)/(y1-y0)
        ny=(x-85)/(240-85)   # 0 = South, 1 = North
    else:
        if h not in HALLS911: continue
        x0,x1=HALLS911[h]
        nx=(x-x0)/(x1-x0)
        ny=(y-368)/(512-368)
    out.append({"code":code,"hall":int(h),"name":names.get(code,""),
                "nx":round(min(max(nx,0),1),4),"ny":round(min(max(ny,0),1),4)})
named=[o for o in out if o['name']]
print("positioned",len(out),"with names",len(named))
byhall=collections.Counter(o['hall'] for o in out)
print(sorted(byhall.items()))
json.dump(out,open('booths.json','w'),ensure_ascii=False,indent=0)
# unmatched names (in list but no position)
missing=[c for c in names if c not in pos]
print("names without position:",len(missing), missing[:20])
