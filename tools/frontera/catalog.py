import sys,pickle,bisect,collections,json,struct
sys.path.insert(0,sys.argv[0].rsplit('/',1)[0]); import analyze,xref,maps
A=pickle.load(open(sys.argv[1],'rb')); d=A.d; addrs=sorted(A.ins)
body,owner,calls,rom=pickle.load(open(sys.argv[2],'rb'))
found,ptrs=xref.mapcat(d)
W=lambda a: struct.unpack_from('<H',d,a)[0]
called=collections.defaultdict(set)
for f in calls:
    for c in calls[f]: called[c].add(f)
def roots_of(f,seen=None):
    seen=seen if seen is not None else set()
    if f in seen: return set()
    seen.add(f)
    if not called[f]: return {f}
    r=set()
    for c in called[f]: r|=roots_of(c,seen)
    return r
def src(site,reg):
    r=xref.backsrc(A,addrs,site,reg)
    if not r: return '?'
    if r[0]=='?': return '?'
    i=r[1]
    return '%s %s'%(i.mn,i.ops)
def after(site):
    k=bisect.bisect_left(addrs,site)
    out=[]
    for a in addrs[k+1:k+4]:
        i=A.ins[a]
        if 'r4' in i.ops.split(',')[-1]: out.append('%s %s'%(i.mn,i.ops))
        if i.mn.startswith('call') or i.mn.startswith('j'): break
    return '; '.join(out[:2])
rows=[]
for rt,kind in ((0x20D6,'2D'),(0x20AC,'1D')):
    for s in A.romsites[rt]:
        r=xref.backsrc(A,addrs,s,'r12'); hdr=None; ptrloc=None
        if r and r[0]!='?':
            i=r[1]
            if i.mem and not i.ext:
                L=analyze.lin(i.mem[0]); ptrloc=L
                if 0x38000<=L<0x40000: hdr=xref.cal(W(L))
            elif i.imm is not None: hdr=xref.cal(i.imm)
        fs=sorted(owner.get(s,[]))
        rts=set()
        for f in fs: rts|=roots_of(f)
        rows.append(dict(site=s,rt=kind,hdr=hdr,ptr=ptrloc,func=fs,roots=sorted(rts),x=src(s,'r13'),y=src(s,'r14') if kind=='2D' else '',out=after(s)))
pickle.dump((rows,found,ptrs),open(sys.argv[3],'wb'))
print(len(rows),'map lookups;', sum(1 for r in rows if r['hdr'] in found),'resolved')
