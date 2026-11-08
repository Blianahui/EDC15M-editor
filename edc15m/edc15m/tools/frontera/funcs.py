import sys,collections,bisect
sys.path.insert(0,__file__.rsplit('/',1)[0]); import analyze
def bodies(A):
    """intraprocedural membership: func -> set(insn addrs); insn -> set(funcs)"""
    owner=collections.defaultdict(set); body={}
    for f in sorted(A.funcs):
        seen=set(); q=[f]
        while q:
            p=q.pop()
            if p in seen or p not in A.ins: continue
            seen.add(p); i=A.ins[p]; nxt=p+i.size
            if i.mn=='jmpr':
                q.append(i.tgt)
                if i.cc: q.append(nxt)
                continue
            if i.mn in ('jb','jnb','jbc','jnbs'): q+= [i.tgt,nxt]; continue
            if i.mn=='jmpa':
                t=analyze.norm((p&0xFF0000)|i.tgt)
                if t: q.append(t)
                if i.cc: q.append(nxt)
                continue
            if i.mn=='jmps':
                t=analyze.norm(i.tgt)
                if t and t not in A.funcs: q.append(t)
                continue
            if i.mn=='jmpi':
                if i.cc: q.append(nxt)
                continue
            if i.kind=='ret' or i.mn in ('srst',): continue
            q.append(nxt)
        body[f]=seen
        for p in seen: owner[p].add(f)
    return body,owner
def callgraph(A,body):
    calls=collections.defaultdict(set); rom=collections.defaultdict(collections.Counter)
    for f,b in body.items():
        for p in b:
            i=A.ins[p]
            if i.mn in ('calls','calla','callr','pcall','jmps'):
                if i.mn=='callr': t=i.tgt
                elif i.mn in ('calls','jmps'): t=i.tgt
                else: t=(p&0xFF0000)|i.tgt
                n=analyze.norm(t)
                if n in A.funcs: calls[f].add(n)
                elif n is None and ((t>>16) in (0,7)) and (t&0xFFFF)<analyze.MISSING_END: rom[f][t&0xFFFF]+=1
    return calls,rom
