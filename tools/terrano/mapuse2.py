import sys,pickle,struct,re,collections,json
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
img=open(sys.argv[1],'rb').read(); lin=pickle.load(open(sys.argv[2],'rb')); DS=int(sys.argv[3],16); out=sys.argv[4]
ROMS=[int(x,16) for x in sys.argv[5].split(',')] if len(sys.argv)>5 else None
W=lambda o: struct.unpack_from('<H',img,o)[0]
A=sorted(lin); idx={a:k for k,a in enumerate(A)}
def hdr(o):
    if not DS<=o<DS+0x8000-8 or W(o)<0x8000 or not 2<=W(o+2)<=32: return None
    n1=W(o+2); d2=o+4+2*n1
    if W(d2)>=0x8000 and 2<=W(d2+2)<=32:
        n2=W(d2+2); return dict(kind='2D',id1='%04X'%W(o),n1=n1,id2='%04X'%W(d2),n2=n2,data=d2+4+2*n2,hdr=o)
    return dict(kind='1D',id1='%04X'%W(o),n1=n1,data=d2,hdr=o)
def src(i,r):
    m=re.match(r'R%d, (.*)$'%r,i.ops); return m.group(1) if m and i.mnem in('MOV','MOVBZ','MOVBS') else None
def resolve(s):
    m=re.match(r'\[([0-9A-F]{4})h\]$',s or '')
    if m:
        p=int(m.group(1),16)
        if p<0x8000:
            q=W(DS+p)
            if q<0x8000: return hdr(DS+q),'tab[%04X]'%p
    m=re.match(r'#([0-9A-F]{4})h$',s or '')
    if m and int(m.group(1),16)<0x8000: return hdr(DS+int(m.group(1),16)),'imm'
    return None,None
uses=[]; per=collections.Counter(); tot=collections.Counter()
for a in A:
    i=lin[a]
    if i.mnem=='CALLS' and i.targets[0][1]<0x10000 and (ROMS is None or i.targets[0][1] in ROMS):
        k=idx[a]; regs={}
        for j in range(k-1,max(0,k-14),-1):
            p=lin[A[j]]
            if p.kind in('ret','jmp') or p.mnem in('CALLS','CALLA','CALLR'): break
            for r in (12,13,14):
                if r not in regs:
                    s=src(p,r)
                    if s: regs[r]=s
                    elif re.match(r'R%d\b'%r,p.ops) and p.mnem not in('CMP','CMPB'): regs[r]='(computed)'
        mp,how=resolve(regs.get(12)); t=i.targets[0][1]; tot[t]+=1
        if mp: per[t]+=1
        uses.append(dict(at='%06X'%a,rom='%04X'%t,r12=regs.get(12),r13=regs.get(13),r14=regs.get(14),map=mp,how=how))
for t,n in per.most_common(): print('ROM %04X: %d of %d calls take a map pointer'%(t,n,tot[t]))
json.dump(uses,open(out,'w'),indent=0)
