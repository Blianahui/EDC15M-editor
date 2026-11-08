import sys,struct,bisect,re,collections
sys.path.insert(0,__file__.rsplit('/',1)[0]); import maps,analyze
def W(d,a): return struct.unpack_from('<H',d,a)[0]
def cal(v):
    """16-bit DPP address -> linear calibration address (DPP0=0E, DPP1=0F)"""
    if v<0x8000: return analyze.lin(v)
    return None
REGRE=re.compile(r'^(r\d+|rl\d|rh\d)\b')
def backsrc(A,addrs,site,reg,limit=14):
    """walk back from call site, find last instruction writing reg (word). returns (addr, text) or None"""
    k=bisect.bisect_left(addrs,site)
    for j in range(k-1,max(-1,k-limit-1),-1):
        a=addrs[j]; i=A.ins[a]
        if a+i.size!=addrs[j+1] and j+1<len(addrs) and addrs[j+1]<=site: return None  # gap
        if i.mn in ('calls','calla','callr','pcall','jmpr','jmpa','jmps','ret','rets','jb','jnb','jmpi'):
            if i.mn in ('calls','calla','callr','pcall','ret','rets'): return ('?','<call/ret>')
            # branch: continue (assume fallthrough path) but mark
        if i.mn.startswith('mov') or i.mn in ('add','sub','shl','shr','ashr','and','or','neg','cpl','scxt','pop') :
            ops=i.ops.split(',')[0].strip()
            if ops==reg or (reg.startswith('r') and ops in ('rl%s'%reg[1:],)):
                return (a,i)
    return None
def mapcat(d):
    """all parseable headers in calibration region; greedy non-overlapping from low addr, preferring pointer targets"""
    ptrs=collections.defaultdict(list)
    for a in range(0x38000,0x40000,2):
        v=W(d,a); L=cal(v)
        if L and 0x38000<=L<0x3FFC0 and L%2==0:
            ptrs[L].append(a)
    found={}
    for h in sorted(ptrs):
        m=maps.parse(d,h)
        if m and m['end']<=0x40000: found[h]=m
    return found,ptrs
