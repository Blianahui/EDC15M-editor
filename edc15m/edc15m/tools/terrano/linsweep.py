"""Generic linear sweep of code regions.
usage: linsweep.py <dump> <base_hex> <regions> <out lin.pkl>
  regions: comma-separated file-offset ranges, e.g. 10000-38000 (0281001550)
  or 10000-40000,60000-70000 with base 80000 (EDC15VM+ 084)"""
import sys,pickle
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c166dis import decode
img=open(sys.argv[1],'rb').read(); BASE=int(sys.argv[2],16)
regions=[tuple(int(x,16) for x in r.split('-')) for r in sys.argv[3].split(',')]
lin={}
for s,e in regions:
    a=s
    while a<e:
        if img[a:a+2]==b'\xc3\xc3': a+=2; continue
        i=decode(img,a,BASE+a)
        if i is None: a+=2; continue
        lin[BASE+a]=i; a+=i.size
print('linear insns',len(lin))
d=os.path.dirname(sys.argv[4])
if d: os.makedirs(d,exist_ok=True)
pickle.dump(lin,open(sys.argv[4],'wb'))
