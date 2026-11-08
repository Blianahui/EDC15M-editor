import sys,pickle,struct,re,collections,json; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
lin=pickle.load(open('out/lin.pkl','rb'))
img=open(sys.argv[1],'rb').read()
W=lambda o: struct.unpack_from('<H',img,o)[0]
addrs=sorted(lin); idx={a:k for k,a in enumerate(addrs)}
LOOK={0xCDC:'map2D',0xCB2:'curve1D',0x119A:'map2D_b',0xD5A:'fn0D5A',0x10F2:'muldiv'}
def hdr(o):
    if not 0x50000<=o<0x5FF00 or W(o)<0x8000 or not 2<=W(o+2)<=32: return None
    n1=W(o+2); d2=o+4+2*n1
    if W(d2)>=0x8000 and 2<=W(d2+2)<=32:
        n2=W(d2+2); return dict(kind='2D',id1='%04X'%W(o),n1=n1,id2='%04X'%W(d2),n2=n2,data=d2+4+2*n2,hdr=o)
    return dict(kind='1D',id1='%04X'%W(o),n1=n1,data=d2,hdr=o)
def src(i,reg):
    """describe source of register write"""
    m=re.match(r'R%d, (.*)$'%reg,i.ops)
    return m.group(1) if m and i.mnem in('MOV','MOVBZ','MOVBS') else None
def resolve(s):
    m=re.match(r'\[([0-9A-F]{4})h\]$',s or '')
    if m:
        p=int(m.group(1),16)
        if p<0xC000:
            q=W(0x50000+p)
            if q<0xC000: return hdr(0x50000+q),'tab[%04X]'%p
    m=re.match(r'#([0-9A-F]{4})h$',s or '')
    if m:
        p=int(m.group(1),16)
        if p<0xC000: return hdr(0x50000+p),'imm'
    return None,None
uses=[];pairs=collections.Counter()
for a in addrs:
    i=lin[a]
    if i.mnem=='CALLS' and i.targets[0][1] in LOOK:
        k=idx[a]; regs={}
        for j in range(k-1,max(0,k-14),-1):
            p=lin[addrs[j]]
            if p.kind in('ret','jmp') or p.mnem in('CALLS','CALLA','CALLR'): break
            for r in (12,13,14):
                if r not in regs:
                    s=src(p,r)
                    if s: regs[r]=s
                    elif re.match(r'R%d\b'%r,p.ops) and p.mnem not in('CMP','CMPB'): regs[r]='(computed)'
        mp,how=resolve(regs.get(12))
        u=dict(at='%06X'%a,fn=LOOK[i.targets[0][1]],r12=regs.get(12),r13=regs.get(13),r14=regs.get(14),map=mp,how=how)
        uses.append(u)
        if mp:
            if u['r13']: pairs[(mp['id1'],u['r13'])]+=1
            if mp['kind']=='2D' and u['r14']: pairs[(mp['id2'],u['r14'])]+=1
res=sum(1 for u in uses if u['map']); print('lookup calls',len(uses),'resolved to map',res)
print('by fn',collections.Counter(u['fn'] for u in uses))
print('axis-id <-> input variable:')
for (ax,v),n in sorted(pairs.items(),key=lambda x:(x[0][0],-x[1])): print('  ',ax,v,n)
json.dump(uses,open('out/mapuse.json','w'),indent=1,default=str)
