import struct,sys
img=open(sys.argv[1],'rb').read()
W=lambda o: struct.unpack_from('<H',img,o)[0]
def hdr_at(o):
    if not 0x50000<=o<0x5FF00: return None
    if W(o)<0x8000 or not 2<=W(o+2)<=32: return None
    n1=W(o+2); ax=[W(o+4+2*i) for i in range(n1)]
    sx=[struct.unpack('<h',struct.pack('<H',v))[0] for v in ax]
    if not(all(ax[i]<ax[i+1] for i in range(n1-1)) or all(sx[i]<sx[i+1] for i in range(n1-1))): return None
    d2=o+4+2*n1
    if W(d2)>=0x8000 and 2<=W(d2+2)<=32:
        n2=W(d2+2); return ('2D',W(o),n1,W(d2),n2,d2+4+2*n2)
    return ('1D',W(o),n1,None,1,d2)
ok=lambda p: p<0xC000 and hdr_at(0x50000+p) is not None
tabs=[];o=0x50000
while o<0x5B000:
    if ok(W(o)):
        s=o
        while o<0x5B000 and ok(W(o)): o+=2
        if (o-s)//2>=3: tabs.append((s,(o-s)//2))
    else: o+=2
allm={}
for s,n in tabs:
    for k in range(n):
        p=W(s+2*k); h=hdr_at(0x50000+p); allm.setdefault(h[5],[]).append(s+2*k)
print(len(tabs),'tables', sum(n for s,n in tabs),'pointers', len(allm),'distinct maps')
for s,n in tabs: print('  table %05X  %d entries'%(s,n))
import json; json.dump({hex(k):[hex(x) for x in v] for k,v in allm.items()},open('out/mapptrs.json','w'))
