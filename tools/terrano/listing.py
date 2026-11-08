import sys,pickle,struct,re,collections,json; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
lin=pickle.load(open('out/lin.pkl','rb'))
img=open(sys.argv[1],'rb').read(); out=sys.argv[2]
W=lambda o: struct.unpack_from('<H',img,o)[0]
uses=json.load(open('out/mapuse.json'))
ROM={0x2D6:'rom_epilogue_2D6',0x830:'rom_epilogue_830',0xCDC:'rom_map2D',0xCB2:'rom_curve1D',0x119A:'rom_map2D_b',
     0x10F2:'rom_muldiv',0xD5A:'rom_fn_D5A',0x12C4:'rom_filt_12C4',0x12E6:'rom_filt_12E6',0x1308:'rom_filt_1308',
     0x132A:'rom_filt_132A',0x1210:'rom_memcpy?',0x12A6:'rom_memset?',0xC06:'rom_fn_C06'}
ECM={0x55296:'ECM: torque limiter',0x555F8:'ECM: injection at part throttle',0x56920:'ECM: injection (Ext.)',0x51E50:'ECM: fuel during acceleration'}
# functions: call targets + entries
funcs=set([0x9009A,0x91002,0x90082]); callers=collections.defaultdict(set)
for a,i in lin.items():
    if i.kind=='call':
        for t in i.targets:
            if t[0]=='code' and t[1]>=0x80000: funcs.add(t[1]); callers[t[1]].add(a)
jt=set(t[1] for i in lin.values() if i.kind in('jmp','cjmp') for t in i.targets if t[0]=='code')
mapat={int(u['at'],16):u for u in uses}
def tabnote(i):
    notes=[]
    for m in re.finditer(r'\[([0-9A-F]{4})h\]',i.ops):
        p=int(m.group(1),16)
        if 0x1000<=p<0x1400:
            q=W(0x50000+p)
            if q<0xC000:
                o=0x50000+q
                if W(o)>=0x8000 and 2<=W(o+2)<=32: notes.append('ptr tab %05X -> map hdr %05X'%(0x50000+p,o))
    return notes
with open(out,'w') as f:
    f.write('; Nissan Terrano EDC15VM+ SW 1037362084 - C167 flash disassembly (flash at CPU 0x80000; file offset = addr-0x80000)\n')
    f.write('; DPP0=0x34/0x3C selects dataset 1 (file 0x50000) / 2 (file 0x70000); seg 00 calls go to on-chip mask ROM (not in dump)\n\n')
    for a in sorted(lin):
        i=lin[a]
        if a in funcs:
            f.write('\n;================ FUNCTION sub_%06X   (callers: %s)\n'%(a,', '.join('%06X'%c for c in sorted(callers[a])[:8])+(' ...' if len(callers[a])>8 else '')))
            f.write('sub_%06X:\n'%a)
        elif a in jt: f.write('loc_%06X:\n'%a)
        c=[]
        if i.mnem in('CALLS','JMPS') and i.targets[0][1]<0x80000: c.append(ROM.get(i.targets[0][1],'rom_%04X'%i.targets[0][1]))
        if a in mapat and mapat[a]['map']:
            m=mapat[a]['map']; d=m['data']
            c.append('MAP data %05X %s %s%s  X=%s%s'%(d,m['kind'],m['id1'],('x'+m['id2']) if m.get('id2') else '','%s'%mapat[a]['r13'],(' Y=%s'%mapat[a]['r14']) if m['kind']=='2D' else ''))
            if d in ECM: c.append(ECM[d])
        c+=tabnote(i)
        f.write('    %-58s%s\n'%(repr(i),('; '+' | '.join(c)) if c else ''))
print('functions',len(funcs))
json.dump({'funcs':sorted(funcs)},open('out/funcs2.json','w'))
