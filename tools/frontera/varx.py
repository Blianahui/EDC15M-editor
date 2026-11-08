import sys,pickle,collections
sys.path.insert(0,sys.argv[0].rsplit('/',1)[0])
A=pickle.load(open(sys.argv[1],'rb')); body,owner,calls,rom=pickle.load(open(sys.argv[2],'rb'))
R=collections.defaultdict(set); Wr=collections.defaultdict(set)
for a,i in A.ins.items():
    fs=owner.get(a,set())
    ops=i.ops
    for M in i.mem:
        if M is None or M<0xC000 or M>=0xFE00: continue
        tgt=Wr if M in i.memw else R
        for f in fs: tgt[M].add(f)
        # mov [mem], reg -> write; mov reg,[mem] -> read; covered by memw
    # pointer writes  mov rX,#C2xx ; mov [rX],...  -> approximate via immediates
    if i.mn=='mov' and isinstance(i.imm,int) and 0xC000<=i.imm<0xFE00:
        for f in fs: Wr[i.imm].add(f)  # address taken (usually followed by store)
pickle.dump((R,Wr),open(sys.argv[3],'wb'))
