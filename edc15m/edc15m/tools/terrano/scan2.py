import sys,struct,collections
d=open(sys.argv[1],'rb').read(); lo,hi=int(sys.argv[2],16),int(sys.argv[3],16)
W=lambda a: struct.unpack_from('<H',d,a)[0]; S=lambda a: struct.unpack_from('<h',d,a)[0]
def axis(a):
    n=W(a)
    if not 2<=n<=32: return None
    for f in (W,S):
        v=[f(a+2+2*i) for i in range(n)]
        if all(v[i]<v[i+1] for i in range(n-1)): return n,v
res=[];a=lo
while a<hi-8:
    d1=W(a); x=axis(a+2)
    if x and d1>=0x8000:
        n1,v1=x;b=a+4+2*n1;d2=W(b);y=axis(b+2)
        if y and d2>=0x8000:
            n2,v2=y;ds=b+4+2*n2;vals=[W(ds+2*i) for i in range(n1*n2)]
            res.append(ds); print('2D data@%05X %2dx%-2d X[%04X]=%d..%d Y[%04X]=%d..%d val %d..%d'%(ds,n1,n2,d1,v1[0],v1[-1],d2,v2[0],v2[-1],min(vals),max(vals))); a=ds+2*n1*n2; continue
        vals=[W(b+2*i) for i in range(n1)]; res.append(b)
        print('1D data@%05X %2d    X[%04X]=%d..%d val %d..%d'%(b,n1,d1,v1[0],v1[-1],min(vals),max(vals))); a=b+2*n1; continue
    a+=2
print(len(res),'found',file=sys.stderr)
