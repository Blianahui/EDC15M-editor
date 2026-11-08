"""usage: dis.py <dump> <cpu_addr_hex> [n] [base_hex]
base: CPU address of file offset 0 (default 0, as on 0281001550)"""
import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c166dis import decode
img=open(sys.argv[1],'rb').read(); BASE=int(sys.argv[4],16) if len(sys.argv)>4 else 0
a=int(sys.argv[2],16); n=int(sys.argv[3]) if len(sys.argv)>3 else 30
for _ in range(n):
    i=decode(img,a-BASE,a)
    if not i: print('%06X  ?? %s'%(a,img[a-BASE:a-BASE+2].hex())); a+=2; continue
    print(i); a+=i.size
