import struct
def W(d,a): return struct.unpack_from('<H',d,a)[0]
def S(d,a): return struct.unpack_from('<h',d,a)[0]
def axis(d,a,maxn=32):
    n=W(d,a)
    if not 2<=n<=maxn: return None
    for f in (W,S):
        v=[f(d,a+2+2*i) for i in range(n)]
        if all(v[i]<v[i+1] for i in range(n-1)): return n,v,(f is S)
    return None
def isvar(v): return v>=0xC000 or v==0
def parse(d,h):
    """h = header start (X var word). returns dict or None"""
    xv=W(d,h)
    if not isvar(xv): return None
    ax=axis(d,h+2)
    if not ax: return None
    nx,X,xs=ax; p=h+4+2*nx
    yv=W(d,p); ay=axis(d,p+2) if isvar(yv) else None
    if ay:
        ny,Y,ys=ay; ds=p+4+2*ny
        return dict(h=h,kind='2D',xv=xv,nx=nx,X=X,xs=xs,yv=yv,ny=ny,Y=Y,ys=ys,data=ds,end=ds+2*nx*ny)
    return dict(h=h,kind='1D',xv=xv,nx=nx,X=X,xs=xs,yv=None,ny=1,Y=None,ys=False,data=p,end=p+2*nx)
def grid(d,m,signed=False):
    f=S if signed else W
    v=[f(d,m['data']+2*k) for k in range(m['nx']*m['ny'])]
    # X-major: index = x*ny + y
    return [[v[x*m['ny']+y] for y in range(m['ny'])] for x in range(m['nx'])]
