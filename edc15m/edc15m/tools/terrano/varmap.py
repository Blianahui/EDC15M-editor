import sys,pickle,json,re,collections,difflib
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fmatch import *
# usage: varmap.py <dirA> <baseA_hex> <dirB> <baseB_hex> <fmatch.pkl> <out.json>
# each dir holds lin.pkl, starts.pkl and proctable.json of one firmware
J=os.path.join
la,FA=load(J(sys.argv[1],'lin.pkl'),J(sys.argv[1],'starts.pkl'),J(sys.argv[1],'proctable.json'),int(sys.argv[2],16))
lb,FB=load(J(sys.argv[3],'lin.pkl'),J(sys.argv[3],'starts.pkl'),J(sys.argv[3],'proctable.json'),int(sys.argv[4],16))
(match,)=pickle.load(open(sys.argv[5],'rb'))
votes=collections.defaultdict(collections.Counter); aligned=0; total=0
for a,(b,j) in match.items():
    if j<0.4: continue
    sa=FA[a]; sb=FB[b]; ta=[norm(i) for i in sa]; tb=[norm(i) for i in sb]
    sm=difflib.SequenceMatcher(None,ta,tb,autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            ia=sa[blk.a+k]; ib=sb[blk.b+k]; aligned+=1
            ma=re.findall(r'\[([0-9A-F]{4})h\]',ia.ops); mb=re.findall(r'\[([0-9A-F]{4})h\]',ib.ops)
            for x,y in zip(ma,mb): votes[x][y]+=1
            # immediates used as addresses (MOV Rn,#XXXX) for RAM areas
            ia_i=re.findall(r'#([0-9A-F]{4})h',ia.ops); ib_i=re.findall(r'#([0-9A-F]{4})h',ib.ops)
            for x,y in zip(ia_i,ib_i):
                if int(x,16)>=0xC000 and int(y,16)>=0xC000: votes[x][y]+=1
    total+=len(sa)
vm={}
for x,c in votes.items():
    y,n=c.most_common(1)[0]; tot=sum(c.values())
    vm[x]=dict(to=y,n=n,conf=round(n/tot,2))
json.dump(vm,open(sys.argv[6],'w'),indent=0)
print('aligned insns',aligned,'of',total,'; variables mapped',len(vm),'; conf>=0.9:',sum(1 for v in vm.values() if v['conf']>=0.9))
for k in ['F948','F944','F98C','F964','F976','C0C2','C0CC','C0CE','C0AA','C102','C100','C44A','D736','D7C8','D7C4','F993','C110','C112','C114','C004','C002','C006','C116','1000','1234','1236','1000']:
    print(k,vm.get(k))
