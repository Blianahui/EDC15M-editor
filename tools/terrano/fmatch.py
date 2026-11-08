import sys,pickle,json,re,collections,bisect,difflib
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def load(linp,startsp,procp,base):
    lin=pickle.load(open(linp,'rb')); st=set(pickle.load(open(startsp,'rb')))
    for p in json.load(open(procp)):
        for f in('fnA','fnB'):
            a=int(p[f].replace(':',''),16)
            if a>=base: st.add(a)
    A=sorted(lin); S=sorted(s for s in st if s in lin)
    funcs={}
    for k,s in enumerate(S):
        e=S[k+1] if k+1<len(S) else A[-1]+1
        i0=bisect.bisect_left(A,s); i1=bisect.bisect_left(A,e)
        funcs[s]=[lin[a] for a in A[i0:i1]]
    return lin,funcs
def norm(i):
    o=re.sub(r'\[[0-9A-F]{4}h\]','[M]',i.ops)
    o=re.sub(r'#[0-9A-F]{2,4}h','#I',o)
    o=re.sub(r'\b[0-9A-F]{6}h\b','L',o)
    o=re.sub(r'\b[0-9A-F]{2}h, [0-9A-F]{4}h','S',o)
    o=re.sub(r'(BRAM_|SFR_|ESFR_)[0-9A-F]{4}','B',o)
    return i.mnem+' '+o
def sig(seq):
    t=[norm(i) for i in seq]
    return t,set(zip(t,t[1:],t[2:]))
