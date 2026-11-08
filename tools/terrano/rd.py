"""Recursive descent from entry + check vs linear sweep. args: image base_hex entry_hex... ; code regions given via env-ish defaults"""
import sys,pickle,collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c166dis import decode
img=open(sys.argv[1],'rb').read(); BASE=int(sys.argv[2],16); entries=[int(x,16) for x in sys.argv[3].split(',')]
lo,hi=[int(x,16) for x in sys.argv[4].split('-')]
lin=pickle.load(open(sys.argv[5],'rb'))
inr=lambda a: lo<=a<hi
insns={}
def walk(s):
    st=[s]; calls=set()
    while st:
        a=st.pop()
        while inr(a) and a not in insns:
            if img[a-BASE:a-BASE+2]==b'\xc3\xc3': insns[a]=None; break
            i=decode(img,a-BASE,a)
            insns[a]=i
            if i is None: break
            for t in i.targets:
                if t[0]=='code' and inr(t[1]):
                    (calls.add(t[1]) if i.kind=='call' else st.append(t[1]))
            if i.kind in('jmp','ret'): break
            a+=i.size
    return calls
fs=set(entries); work=list(entries)
while work:
    f=work.pop()
    for c in walk(f):
        if c not in fs: fs.add(c); work.append(c)
code={a:i for a,i in insns.items() if i}
bad=[hex(a) for a,v in insns.items() if v is None];print('bad at',bad[:10]);pickle.dump((code,fs),open(sys.argv[6],'wb')) if len(sys.argv)>6 else None;print('RD functions',len(fs),'insns',len(code),'bad',sum(1 for v in insns.values() if v is None),'agree with linear',sum(1 for a in code if a in lin))
