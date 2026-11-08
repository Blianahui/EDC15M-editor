"""Recursive-descent analyzer for EDC15M (Frontera 0281001791) flash image."""
import sys,struct,re,collections,pickle
sys.path.insert(0,__file__.rsplit('/',1)[0]); import c166
DPP=[0x0E,0x0F,0x04,0x03]
MISSING_END=0x8AA6
def norm(t):
    """normalize code target to file address; None if outside flash/missing"""
    seg=t>>16
    if seg==7: t&=0xFFFF
    if t<MISSING_END: return None
    if t>=0x38000: return None
    return t
def lin(mem16,extp=None,exts=None):
    if exts is not None: return (exts<<16)|mem16
    if extp is not None: return (extp<<14)|(mem16&0x3FFF)
    return (DPP[mem16>>14]<<14)|(mem16&0x3FFF)

class A:
    def __init__(s,d):
        s.d=d; s.ins={}; s.funcs=set(); s.callers=collections.defaultdict(set); s.romcalls=collections.Counter()
        s.romsites=collections.defaultdict(list); s.jmpi=[]; s.calli=[]; s.bad=set(); s.missing_calls=collections.Counter()
        s.datarefs=collections.defaultdict(list)  # linear addr -> [(insn addr, 'r'/'w')]
    def run(s,entries):
        work=list(entries); s.funcs|=set(entries)
        seen=set()
        while work:
            a=work.pop()
            if a in seen: continue
            q=[a]
            while q:
                p=q.pop()
                if p in s.ins or p is None: continue
                ext=None; extn=0; extr=0
                while True:
                    if p in s.ins: break
                    if p>=0x38000 or p<MISSING_END: break
                    i=s.d and c166.decode(s.d,p,extr=extr>0)
                    if i is None: s.bad.add(p); break
                    s.ins[p]=i
                    # ext prefixes
                    i.ext=None
                    if extn>0: i.ext=ext; extn-=1
                    else: ext=None
                    if extr>0: extr-=1
                    if i.mn in ('extp','extpr','exts','extsr') and i.kind=='ext_i':
                        val,cnt=i.imm; ext=(i.mn[:4],val); extn=cnt
                        if i.mn.endswith('r'): extr=cnt
                    elif i.kind=='ext_r': ext=(i.mn[:4],None); extn=i.imm
                    if i.mn=='extr': extr=i.imm
                    # data refs
                    for M in i.mem:
                        if M is None: continue
                        if M>=0xFE00 or (0xF000<=M<0xF200 and i.mn): L=M
                        elif i.ext and i.ext[0]=='extp' and i.ext[1] is not None: L=lin(M,extp=i.ext[1])
                        elif i.ext and i.ext[0]=='exts' and i.ext[1] is not None: L=lin(M,exts=i.ext[1])
                        else: L=lin(M)
                        s.datarefs[L].append((p,'w' if M in i.memw else 'r'))
                    nxt=p+i.size
                    k=i.kind
                    if i.mn in ('calls','jmps'):
                        t=norm(i.tgt)
                        if (i.tgt>>16)==0 and i.tgt<MISSING_END or ((i.tgt>>16)==7 and (i.tgt&0xFFFF)<MISSING_END):
                            s.romcalls[i.tgt&0xFFFF]+=1; s.romsites[i.tgt&0xFFFF].append(p)
                        elif t is None: s.missing_calls[i.tgt]+=1
                        else:
                            if i.mn=='calls': s.funcs.add(t); s.callers[t].add(p); work.append(t)
                            else: q.append(t)
                        if i.mn=='jmps': break
                        p=nxt; continue
                    if i.mn in ('calla','pcall','callr'):
                        t=i.tgt if i.mn=='callr' else ((p&0xFF0000)|i.tgt)
                        t=norm(t) if t is not None else None
                        if t is None and i.mn!='callr':
                            tt=i.tgt
                            if (p>>16)==0 and tt<MISSING_END: s.romcalls[tt]+=1; s.romsites[tt].append(p)
                        if t is not None: s.funcs.add(t); s.callers[t].add(p); work.append(t)
                        p=nxt; continue
                    if i.mn=='jmpr':
                        q.append(i.tgt)
                        if i.cc==0: break
                        p=nxt; continue
                    if i.mn in ('jb','jnb','jbc','jnbs'): q.append(i.tgt); p=nxt; continue
                    if i.mn=='jmpa':
                        t=norm((p&0xFF0000)|i.tgt)
                        if t is not None: q.append(t)
                        if i.cc==0: break
                        p=nxt; continue
                    if i.mn=='jmpi':
                        s.jmpi.append(p)
                        if i.cc==0: break
                        p=nxt; continue
                    if i.mn=='calli': s.calli.append(p); p=nxt; continue
                    if k=='ret' or i.mn in ('srst','idle','pwrdn'): break
                    p=nxt
            seen.add(a)
