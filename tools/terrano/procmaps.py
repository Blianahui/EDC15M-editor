import sys,pickle,json,csv,collections,bisect; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
lin=pickle.load(open('out/lin.pkl','rb')); starts=pickle.load(open('out/starts.pkl','rb'))
uses=json.load(open('out/mapuse.json')); procs=json.load(open('out/proctable.json'))
fs=set(starts)
for p in procs:
    for f in('fnA','fnB'):
        a=int(p[f].replace(':',''),16)
        if a>=0x80000: fs.add(a)
fs=sorted(fs)
own=lambda a: fs[bisect.bisect_right(fs,a)-1]
edges=collections.defaultdict(set)
for a,i in lin.items():
    for t in i.targets:
        if t[0]=='code' and t[1]>=0x80000:
            g=own(t[1]); s=own(a)
            if g!=s: edges[s].add(g)
fmaps=collections.defaultdict(set)
for u in uses:
    if u['map']: fmaps[own(int(u['at'],16))].add('%05X'%u['map']['data'])
def reach(f):
    seen=set([f]); st=[f]
    while st:
        x=st.pop()
        for y in edges[x]:
            if y not in seen: seen.add(y); st.append(y)
    return seen
tag=sys.argv[1]
with open('out/terrano_%s_processes.csv'%tag,'w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['#','Entry @','Flags','RAM A','Function A','RAM B (task list?)','Function B','Maps reachable from functions A and B'])
    for k,p in enumerate(procs):
        ms=set()
        for fld in('fnA','fnB'):
            a=int(p[fld].replace(':',''),16)
            if a>=0x80000:
                for g in reach(a): ms|=fmaps[g]
        w.writerow([k,'0x'+p['off'],p['flags'],p['ramA'],p['fnA'],p['ramB'],p['fnB'],' '.join(sorted(ms))])
        if ms: print(k,p['fnA'],p['fnB'],p['ramB'],len(ms),' '.join(sorted(ms))[:120])
allm=set(m for s in fmaps.values() for m in s); cov=set()
for p in procs:
    for fld in('fnA','fnB'):
        a=int(p[fld].replace(':',''),16)
        if a>=0x80000:
            for g in reach(a): cov|=fmaps[g]
print('maps referenced in code',len(allm),'reachable from process table',len(cov))
