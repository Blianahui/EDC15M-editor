"""Heuristic function starts: call targets inside the code range, plus the first instruction
after a return (or after a jump to a ROM epilogue).
usage: starts.py <lin.pkl> <lo_hex> <hi_hex> <out starts.pkl> [epilogue_rom_addrs]
  0281001550:    starts.py w550/lin.pkl 10000 38000 w550/starts.pkl"""
import sys,pickle
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
lin=pickle.load(open(sys.argv[1],'rb')); lo,hi=int(sys.argv[2],16),int(sys.argv[3],16)
epi={int(x,16) for x in sys.argv[5].split(',')} if len(sys.argv)>5 else set()
starts=set(); prev=None
for a in sorted(lin):
    i=lin[a]
    if i.kind=='call':
        for t in i.targets:
            if t[0]=='code' and lo<=t[1]<hi: starts.add(t[1])
    if prev and a==prev.pc+prev.size and (prev.kind=='ret' or (prev.mnem=='JMPS' and prev.targets[0][1] in epi)):
        starts.add(a)
    prev=i
print('heuristic function starts',len(starts))
pickle.dump(starts,open(sys.argv[4],'wb'))
