"""Match functions of firmware A to firmware B by code shape (trigram Jaccard on normalised instructions).
usage: fmatch_run.py <dirA> <baseA_hex> <dirB> <baseB_hex> <out fmatch.pkl>
  each dir holds lin.pkl, starts.pkl and proctable.json of one firmware
  084 -> 550:  fmatch_run.py out 80000 w550 10000 w550/fmatch.pkl"""
import sys,pickle,json,collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fmatch import *
J=os.path.join
la,FA=load(J(sys.argv[1],'lin.pkl'),J(sys.argv[1],'starts.pkl'),J(sys.argv[1],'proctable.json'),int(sys.argv[2],16))
lb,FB=load(J(sys.argv[3],'lin.pkl'),J(sys.argv[3],'starts.pkl'),J(sys.argv[3],'proctable.json'),int(sys.argv[4],16))
print('functions A',len(FA),'B',len(FB))
SA={a:sig(v) for a,v in FA.items() if len(v)>=6}; SB={a:sig(v) for a,v in FB.items() if len(v)>=6}
inv={}
for b,(t,g) in SB.items():
    for x in g: inv.setdefault(x,[]).append(b)
match={}
for a,(t,g) in SA.items():
    cnt={}
    for x in g:
        for b in inv.get(x,()): cnt[b]=cnt.get(b,0)+1
    best=None
    for b,c in sorted(cnt.items(),key=lambda x:-x[1])[:5]:
        gb=SB[b][1]; j=c/len(g|gb)
        if not best or j>best[1]: best=(b,j)
    if best: match[a]=best
pickle.dump((match,),open(sys.argv[5],'wb'))
h=collections.Counter(round(j,1) for b,j in match.values()); print('similarity histogram',sorted(h.items()))
