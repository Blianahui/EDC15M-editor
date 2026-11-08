import sys,pickle,copy; sys.path.insert(0,sys.argv[0].rsplit('/',1)[0]); import analyze,c166
A=pickle.load(open(sys.argv[1],'rb')); d=A.d
def covmap():
    cov=bytearray(len(d))
    for a,i in A.ins.items():
        for k in range(i.size): cov[a+k]=1
    return cov
def trial(a):
    B=analyze.A(d); B.run([a])
    if B.bad: return None
    # all new insns must not overlap existing insns misaligned
    for p,i in B.ins.items():
        if p in A.ins: continue
        for k in range(i.size):
            if cov[p+k]: return None
    if len(B.ins)<3: return None
    # reject if contains too many 'nop'-like or zero-ops
    z=sum(1 for i in B.ins.values() if i.mn=='add' and i.ops=='r0, r0')
    if z>2: return None
    return B
hfuncs=[]
for rnd in range(6):
    cov=covmap(); added=0
    a=analyze.MISSING_END
    while a<0x38000:
        if cov[a] or d[a]==0xC3: a+=2; continue
        # candidate start
        B=trial(a)
        if B:
            A.run([a]); A.funcs.add(a); hfuncs.append(a); added+=1
            cov=covmap()
            a+=2; continue
        # skip linearly to next terminator
        i=c166.decode(d,a)
        if not i: a+=2; continue
        a+=i.size
    print('round',rnd,'added',added,'insns',len(A.ins))
    if not added: break
A.hfuncs=set(hfuncs)
pickle.dump(A,open(sys.argv[2],'wb'))
cov=covmap()
code=sum(1 for x in range(analyze.MISSING_END,0x38000) if d[x]!=0xC3)
print('covered',sum(cov),'of non-C3',code,'funcs',len(A.funcs),'hfuncs',len(hfuncs),'jmpi',len(A.jmpi),'calli',len(A.calli))
print('rom targets',len(A.romcalls),'sites',sum(A.romcalls.values()))
print('rom top',[(hex(a),n) for a,n in A.romcalls.most_common(30)])
