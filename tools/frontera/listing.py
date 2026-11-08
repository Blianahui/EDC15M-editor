import sys,pickle,struct,collections,re,json
sys.path.insert(0,sys.argv[0].rsplit('/',1)[0]); import analyze,xref,maps,c166
A=pickle.load(open(sys.argv[1],'rb')); d=A.d
body,owner,calls,rom=pickle.load(open(sys.argv[2],'rb'))
rows,found,ptrs=pickle.load(open(sys.argv[3],'rb'))
names=json.load(open(sys.argv[4],encoding='utf-8')) if len(sys.argv)>4 else {}
VAR={int(k,16):v for k,v in names.get('vars',{}).items()}
MAPN={int(k,16):v for k,v in names.get('maps',{}).items()}
ROMN={int(k,16):v for k,v in names.get('rom',{}).items()}
FN={int(k,16):v for k,v in names.get('funcs',{}).items()}
W=lambda a: struct.unpack_from('<H',d,a)[0]
called=collections.defaultdict(set)
for f in calls:
    for c in calls[f]: called[c].add(f)
mapsite={r['site']:r for r in rows}
def mapdesc(h):
    m=found.get(h)
    if not m: return 'MAP_%05X?'%h
    s='MAP_%05X %s %dx%d'%(h,m['kind'],m['nx'],m['ny'])
    if h in MAPN: s+=' "%s"'%MAPN[h]
    return s
def memnote(i,M):
    if M is None: return ''
    if M>=0xF000 and M not in VAR:
        return ''
    if M in VAR: return '%04X=%s'%(M,VAR[M])
    if i.ext and i.ext[1] is not None:
        if i.ext[0]=='extp': L=analyze.lin(M,extp=i.ext[1])
        else: L=analyze.lin(M,exts=i.ext[1])
        return 'ext->%05X'%L
    if M<0x8000:
        L=analyze.lin(M)
        if L+1<len(d):
            v=W(L); P=xref.cal(v)
            if P in found: return 'cal %05X -> ptr %s'%(L,mapdesc(P))
            return 'cal %05X = %04X (%d)'%(L,v,struct.unpack('<h',struct.pack('<H',v))[0])
    if 0xC000<=M<0xF000: return ''
    return ''
def fname(f):
    if f in FN: return FN[f]
    if f in getattr(A,'taskkind',{}): return 'task_%06X'%f
    if f in A.hfuncs: return 'hsub_%06X'%f
    return 'sub_%06X'%f
out=[]
out.append('; Opel Frontera B X22DTH  Bosch 0281001791  GM 90589738  SW UU2M6S90_S  (EDC15M, C167 mask-ROM)')
out.append('; file offset == C167 linear address. 0x0000-0x8AA5 = mask ROM of CPU (not in dump). seg 7 is alias of seg 0.')
out.append('; DPP0=0Eh (0x38000) DPP1=0Fh (0x3C000) DPP2=04h DPP3=03h (system page). Map data X-major: idx = x*ny + y.')
out.append('; ROM helpers: %s'%', '.join('%04X=%s'%(k,v) for k,v in sorted(ROMN.items())))
out.append('')
prev_end=None
for a in sorted(A.ins):
    i=A.ins[a]
    if a in A.funcs:
        out.append('')
        out.append(';'+'='*100)
        tk=getattr(A,'taskkind',{}).get(a)
        out.append('%s:   ; %s%s callers: %s'%(fname(a), ('TASK '+tk+' ') if tk else '', 'heuristic entry,' if a in A.hfuncs else '', ', '.join(fname(c) for c in sorted(called[a])[:6]) or '(entered from ROM/indirect)'))
        ms=sorted(set(r['hdr'] for r in rows if a in r['func'] and r['hdr']))
        if ms: out.append(';   maps: '+'; '.join(mapdesc(h) for h in ms))
    elif prev_end is not None and a!=prev_end:
        out.append('        ; ---- gap %06X-%06X ----'%(prev_end,a))
    notes=[]
    for M in i.mem:
        n=memnote(i,M)
        if n: notes.append(n)
    if i.imm is not None and isinstance(i.imm,int) and i.mn.startswith('mov') and i.imm in VAR: notes.append('#%04X=&%s'%(i.imm,VAR[i.imm]))
    if i.mn in ('calls','jmps','calla','callr','pcall'):
        t=i.tgt if i.mn in ('calls','jmps','callr') else ((a&0xFF0000)|i.tgt)
        n=analyze.norm(t)
        if n is None and (t>>16) in (0,7) and (t&0xFFFF)<analyze.MISSING_END:
            notes.append('ROM %s'%ROMN.get(t&0xFFFF,'?'))
            r=mapsite.get(a)
            if r and r['hdr']: notes.append('%s  X=%s Y=%s'%(mapdesc(r['hdr']),r['x'],r['y']))
        elif n in A.funcs: notes.append('-> '+fname(n))
    txt='%06X  %-12s %-7s %s'%(a,d[a:a+i.size].hex(' '),i.mn,i.ops)
    if notes: txt='%-62s ; %s'%(txt,' | '.join(notes))
    out.append(txt)
    prev_end=a+i.size
open(sys.argv[5],'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('lines',len(out))
