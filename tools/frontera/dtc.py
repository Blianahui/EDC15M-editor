import sys,pickle,bisect,struct,collections,json
sys.path.insert(0,sys.argv[0].rsplit('/',1)[0]); import analyze
A=pickle.load(open(sys.argv[1],'rb')); d=A.d; addrs=sorted(A.ins)
body,owner,calls,rom=pickle.load(open(sys.argv[2],'rb'))
W=lambda a: struct.unpack_from('<H',d,a)[0]
paths=collections.defaultdict(list)
for s,i in A.ins.items():
    if not (i.mn=='calls' and i.tgt==0x14002): continue
    k=bisect.bisect_left(addrs,s); r1=r2=None
    for a in addrs[max(0,k-8):k]:
        j=A.ins[a]
        if j.mn=='mov' and j.ops.startswith('r2,') and isinstance(j.imm,int): r2=j.imm
        if j.mn=='mov' and j.ops.startswith('r1,') and j.mem: r1=analyze.lin(j.mem[0])
    if r2 is None or r1 is None: continue
    ent=analyze.lin(W(r1)); bit=(~r2)&0xFF
    paths[r2>>8].append(dict(site=s,bit=bit,entry=ent,func=sorted(owner.get(s,[]))[0]))
out=[]
for p,L in sorted(paths.items()):
    m=min(x['entry'] for x in L); h=None
    for c in range(m-14,m-0x60,-2):
        if W(c)==0x000C and W(c+2) in (0x0005,) : h=c; break
    ok=h is not None
    hdr=struct.unpack_from('<8H',d,h) if ok else None
    out.append(dict(path=p,pcode='P%04X'%hdr[5] if ok else '?',enable_addr=h+12 if ok else None,enable=hdr[6] if ok else None,
        bits=sorted(set(x['bit'] for x in L)),funcs=sorted(set('%05X'%x['func'] for x in L)),hdr=h))
json.dump(out,open(sys.argv[3],'w'),indent=0)
for o in out: print('path %02X %-6s en@%s=%s bits=%s funcs=%s'%(o['path'],o['pcode'],o['enable_addr'] and '%05X'%o['enable_addr'],o['enable'],['%02X'%b for b in o['bits']],o['funcs']))
