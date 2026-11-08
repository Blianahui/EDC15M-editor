import sys,struct,collections,pickle
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c166dis import decode
BASE=0x80000
img=open(sys.argv[1],'rb').read()
an=pickle.load(open('out/an.pkl','rb')); rd=an['code']
regions=[(0x10000,0x40000),(0x60000,0x70000)]
lin={}
for s,e in regions:
    a=s
    while a<e:
        if img[a:a+2]==b'\xc3\xc3': a+=2; continue
        i=decode(img,a,BASE+a)
        if i is None: a+=2; continue
        lin[BASE+a]=i; a+=i.size
# agreement with recursive descent
agree=sum(1 for a in rd if a in lin); print('RD insns',len(rd),'found in linear',agree)
print('linear insns',len(lin),'bytes',sum(i.size for i in lin.values()))
# undefined-opcode density per 4KB block as data indicator
blocks=collections.Counter(); und=collections.Counter()
for s,e in regions:
    a=s
    while a<e:
        if img[a:a+2]==b'\xc3\xc3': a+=2; continue
        i=decode(img,a,BASE+a); blocks[(BASE+a)>>12]+=1
        if i is None: und[(BASE+a)>>12]+=1; a+=2
        else: a+=i.size
for b in sorted(blocks):
    r=und[b]/blocks[b]
    if r>0.02: print('block %05X000 undefined-rate %.2f'%(b,r))
pickle.dump(lin,open('out/lin.pkl','wb'))
