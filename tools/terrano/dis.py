import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c166dis import decode
img=open(sys.argv[1],'rb').read(); BASE=0x80000
a=int(sys.argv[2],16); n=int(sys.argv[3]) if len(sys.argv)>3 else 30
for _ in range(n):
    i=decode(img,a-BASE,a)
    if not i: print('%06X  ?? %s'%(a,img[a-BASE:a-BASE+2].hex())); a+=2; continue
    print(i); a+=i.size
