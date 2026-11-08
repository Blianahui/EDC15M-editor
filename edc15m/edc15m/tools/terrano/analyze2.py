import sys, struct, collections, pickle
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c166dis import decode
BASE=0x80000
img=open(sys.argv[1],'rb').read(); END=BASE+len(img)
os.makedirs('out', exist_ok=True)
W=lambda o: struct.unpack_from('<H',img,o)[0]
inf=lambda a: BASE<=a<END
fill=lambda a: img[a-BASE:a-BASE+2]==b'\xc3\xc3'
def dec(a):
    if not inf(a) or a&1: return None
    return decode(img,a-BASE,a)
insns={}; xcall=collections.defaultdict(set); xjump=collections.defaultdict(set)
indirect=[]; romcalls=collections.Counter()
def walk(start):
    calls=set(); stack=[start]
    while stack:
        a=stack.pop()
        while True:
            if a in insns: break
            i=dec(a)
            if i is None or fill(a): insns[a]=None; break
            insns[a]=i
            for t in i.targets:
                if t[0]=='code':
                    if i.kind=='call':
                        calls.add(t[1]); xcall[t[1]].add(a)
                        if not inf(t[1]): romcalls[t[1]]+=1
                    else:
                        xjump[t[1]].add(a)
                        if inf(t[1]): stack.append(t[1])
                elif t[0]=='ind': indirect.append(a)
            if i.kind in ('jmp','ret'): break
            a+=i.size
    return calls
def trial(start):
    seen={}; stack=[start]; n=0
    while stack and n<400:
        a=stack.pop()
        while n<400:
            if a in seen: break
            i=dec(a)
            if i is None or fill(a): return False
            seen[a]=1; n+=1
            for t in i.targets:
                if t[0]=='code' and i.kind in('jmp','cjmp') and inf(t[1]): stack.append(t[1])
            if i.kind in('jmp','ret'): break
            a+=i.size
    return n>=2
funcs=set(); work=[]
def addf(a,src):
    if inf(a) and a not in funcs and not a&1 and not fill(a):
        funcs.add(a); work.append(a); fsrc[a]=src
fsrc={}
for s in (0x9009A,0x91002,0x90082): addf(s,'entry')
def run():
    while work:
        f=work.pop()
        for c in walk(f): addf(c,'call')
run()
# pointer tables: (off16, seg16) pairs
tables=[]
for rnd in range(3):
    ptr=[]
    for o in range(0,len(img)-4,2):
        lo,hi=W(o),W(o+2)
        if hi in (9,10,11,14):
            t=(hi<<16)|lo
            if inf(t) and not t&1 and not fill(t): ptr.append(o)
    ptrs=set(ptr)
    # runs of >=3 consecutive 4-byte entries
    for o in ptr:
        if o-4 in ptrs: continue
        n=0
        while o+4*n in ptrs: n+=1
        if n>=3:
            tg=[(W(o+4*k+2)<<16)|W(o+4*k) for k in range(n)]
            good=sum(1 for t in tg if t in funcs or trial(t))
            if good==n and (BASE+o,n) not in tables:
                tables.append((BASE+o,n))
                for t in tg: addf(t,'table@%06X'%(BASE+o))
    run()
code={a:i for a,i in insns.items() if i}
print('functions',len(funcs),'insns',len(code),'bytes',sum(i.size for i in code.values()))
print('tables',[(hex(a),n) for a,n in tables])
print('ROM calls: distinct',len(romcalls),'total',sum(romcalls.values()))
print('indirect calls/jumps',len(indirect))
# DPP usage
dpp=collections.Counter()
for i in code.values():
    if i.mnem in('MOV','SCXT') and i.regs in (0,1,2,3) and i.imm is not None: dpp[(i.regs,i.imm)]+=1
print('DPP loads',sorted(dpp.items()))
ext=collections.Counter(i.ext[1] for i in code.values() if i.kind=='ext' and i.ext[1] and i.ext[1][0]!='reg')
print('EXTP/EXTS operands',sorted(ext.items(),key=lambda x:-x[1])[:30])
pickle.dump(dict(code=code,funcs=funcs,fsrc=fsrc,xcall=dict(xcall),xjump=dict(xjump),romcalls=romcalls,tables=tables,indirect=indirect),open('out/an.pkl','wb'))
