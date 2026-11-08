"""Extract the process (task) table.
usage: proctable.py <dump> 550 <lin.pkl> <out proctable.json> [probe_offset_hex]
  0281001550: 10-byte entries, found around 0x38400 (table at 0x383F6, 60 entries)
Each row: off, ramA, flags, fnA, ramB, fnB (functions as SEG:OFFS)."""
import sys,pickle,struct,collections,json
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
img=open(sys.argv[1],'rb').read(); kind=sys.argv[2]; lin=pickle.load(open(sys.argv[3],'rb'))
W=lambda o: struct.unpack_from('<H',img,o)[0]
if kind=='550':
    STEP=10; probe=int(sys.argv[5],16) if len(sys.argv)>5 else 0x38400
    def parse(o):
        a,b,c,dd,e=[W(o+2*k) for k in range(5)]; seg=b&0xFF
        return a,b>>8,seg,(seg<<16)|c,dd,(seg<<16)|e
    def ok(o):
        a,fl,seg,fa,dd,fb=parse(o)
        g=lambda x: seg==0 or x in lin
        return 0xF000<=a<0xFE00 and 0xF000<=dd<0xFE00 and seg<=3 and g(fa) and g(fb)
    def row(o):
        a,fl,seg,fa,dd,fb=parse(o)
        return dict(off='%05X'%o,ramA='%04X'%a,flags='%02X'%fl,fnA='%02X:%04X'%(seg,fa&0xFFFF),ramB='%04X'%dd,fnB='%02X:%04X'%(seg,fb&0xFFFF))
else:
    sys.exit('only the 0281001550 layout (550) is supported')
s=probe
while ok(s-STEP): s-=STEP
e=probe
while ok(e): e+=STEP
rows=[row(o) for o in range(s,e,STEP)]
print('process table %05X..%05X entries %d'%(s,e,len(rows)))
print('flags',collections.Counter(r['flags'] for r in rows).most_common())
json.dump(rows,open(sys.argv[4],'w'),indent=0)
