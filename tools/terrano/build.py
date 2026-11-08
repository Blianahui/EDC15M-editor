import sys,pickle,struct,re,collections,json,csv,bisect; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
img=open(sys.argv[1],'rb').read(); tag=sys.argv[2]
lin=pickle.load(open('out/lin.pkl','rb')); starts=pickle.load(open('out/starts.pkl','rb'))
uses=json.load(open('out/mapuse.json')); procs=json.load(open('out/proctable.json'))
W=lambda o: struct.unpack_from('<H',img,o)[0]
ROM={0x2D6:'rom_stack_overflow_error(MDL=code)',0x830:'rom_task_exit',0xCDC:'rom_map2D(R12=map,R13=X,R14=Y)->R4',0xCB2:'rom_curve1D(R12=map,R13=X)->R4',
     0x119A:'rom_map2D_b(R12=map,R13=X,R14=Y)->R4',0x10F2:'rom_muldiv?(R12,R13,R14)',0xD5A:'rom_D5A(R12,R13,R14)',
     0x12C4:'rom_filter?',0x12E6:'rom_filter?',0x1308:'rom_filter?',0x132A:'rom_filter?',0x1210:'rom_memcpy?(R12=dst,R13=src,R14=n)',
     0x12A6:'rom_memset?(R12=dst,R13=val,R14=n)',0x1E80:'rom_linearize(R1=curve,R4=raw)->R4'}
VARS={'F948':'rpm (mirror of DADE)','DADE':'rpm','F9BA':'rpm (raw)','C112':'atmospheric pressure',
      'C002':'temp. sensor ADC[1024h] (coolant?)','C004':'temp. sensor ADC[101Ch]',
      'C006':'fuel temp.? (ADC[101Ah]; C100 correction around 50 °C)','C100':'fuel temperature correction (map 563FC)','C44A':'idle + demand after anti-jerk filter','D736':'per-cylinder correction (smooth running)','C102':'injection quantity = C100+C44A+D736 (input of map 56920)','D7C8':'idle controller fuel (<= ceiling)','D7C4':'driver demand limited to remaining headroom','1000':'pointer to coding block','F98C':'max allowed fuel (output of #25)','F944':'final fuel quantity (output of #29)','F964':'pump metering position setpoint (output of #30, map 56920)','F966':'actual metering position (for monitoring)','F8AA':'actual metering position (in controller #41)','F993':'injection enable (0 = fuel zeroed)','DE10':'metering controller output (10 bit)','DE26':'metering controller output (10 bit)','C0AA':'pedal, 0.01 %','C0CC':'driver demand (filtered)','C0CE':'driver demand (unfiltered)'}
ECM={0x55296:'torque limiter',0x555F8:'injection at part throttle',0x56920:'injection (Ext.) = fuel -> metering position setpoint',0x51E50:'fuel during acceleration'}
# function starts
fstart=set(starts)
pfn={}
for k,p in enumerate(procs):
    for f in ('fnA','fnB'):
        a=int(p[f].replace(':',''),16)
        if a>=0x80000: fstart.add(a); pfn.setdefault(a,[]).append('proc#%d %s flags=%s ramB=%s'%(k,f,p['flags'],p['ramB']))
fs=sorted(fstart)
def owner(a):
    k=bisect.bisect_right(fs,a)-1
    return fs[k] if k>=0 else None
callers=collections.defaultdict(set)
for a,i in lin.items():
    if i.kind=='call':
        for t in i.targets:
            if t[0]=='code' and t[1]>=0x80000: callers[t[1]].add(a)
# map labels from previous CSV (my guesses) by data address
lab={0x563FC:'Fuel temperature correction: factor f(rpm, fuel) x (T-50°C)/4096',0x51E50:'Driver demand: fuel = f(rpm, pedal C0AA)',0x555F8:'Smoke limiter: f(rpm, air C110 after correction) - active when coding +26h=0',0x55846:'C110 input correction by temp. C004 (1:1)',0x55296:'Fuel limit vs rpm (no change with atm. pressure)',0x55026:'Start fuel f(rpm, temp. C002)',0x562AE:'Over-temperature fuel derating (zeros in stock)',0x560FA:'Factor atm. pressure x rpm (100% in stock)',0x563A2:'Lower bound of fuel limit vs rpm',0x56272:'Limp-mode fuel limiter vs rpm',0x55F02:'Limit rise step vs atm. pressure',0x55F56:'Limit fall step vs atm. pressure',0x55FAA:'Step factor vs temp. C004',0x51838:'Fuel -> torque (for bus / gearbox?)',0x55CCA:'Pressure correction vs temp. (boost path, inactive)',0x55A88:'Boost-based smoke limiter (inactive path, const 50 mg)'}
lab0={}
for r in csv.reader(open('out/terrano_084_maps.csv',encoding='utf-8-sig'),delimiter=';'):
    if r[0].startswith('0x'): lab.setdefault(int(r[0],16),r[10])
mapat={int(u['at'],16):u for u in uses}
jt=set(t[1] for i in lin.values() if i.kind in('jmp','cjmp') for t in i.targets if t[0]=='code')
def vn(s):
    if not s: return ''
    m=re.match(r'\[([0-9A-F]{4})h\]$',s)
    if m and m.group(1) in VARS: return '%s{%s}'%(s,VARS[m.group(1)])
    return s
with open('out/terrano_%s.lst'%tag,'w') as f:
    f.write(';; Nissan Terrano II 2.7 TDi (?) Bosch EDC15VM+  SW %s - disassembly of C167 flash code\n'%tag)
    f.write(';; Flash is mapped at CPU 0x80000 (file offset = address - 0x80000). Code: 0x90000-0xBFFFF, 0xE0000-0xEFFFF.\n')
    f.write(';; Calibration: dataset 1 at 0xD0000 (file 0x50000), dataset 2 at 0xF0000 (file 0x70000), selected by DPP0=0x34/0x3C.\n')
    f.write(';; Data pointers [0000h-3FFFh] -> DPP0 page (0xD0000+x). CALLS 00:xxxx go to on-chip mask ROM (not in this dump).\n')
    f.write(';; Function starts: call targets + process table (dataset 0x50446) + code after return (heuristic).\n\n')
    for a in sorted(lin):
        i=lin[a]
        if a in fstart:
            f.write('\n;==================== sub_%06X'%a)
            if a in pfn: f.write('   <-- '+'; '.join(pfn[a]))
            if callers[a]: f.write('   called from: '+', '.join('%06X'%c for c in sorted(callers[a])[:6])+(' ...' if len(callers[a])>6 else ''))
            f.write('\nsub_%06X:\n'%a)
        elif a in jt: f.write('loc_%06X:\n'%a)
        c=[]
        if i.mnem in('CALLS','JMPS') and i.targets[0][1]<0x80000: c.append(ROM.get(i.targets[0][1],'rom_%04X'%i.targets[0][1]))
        u=mapat.get(a)
        if u and u['map']:
            m=u['map']; d=m['data']
            s='MAP %05X %s'%(d,m['kind'])
            if d in ECM: s+=' "%s"'%ECM[d]
            elif lab.get(d): s+=' (%s)'%lab[d][:50]
            s+='  X(%s)=%s'%(m['id1'],vn(u['r13']))
            if m['kind']=='2D': s+='  Y(%s)=%s'%(m['id2'],vn(u['r14']))
            c.append(s)
        for mm in re.finditer(r'\[([0-9A-F]{4})h\]',i.ops):
            v=mm.group(1)
            if v in VARS and not (u and u['map']): c.append('%s=%s'%(v,VARS[v]))
            p=int(v,16)
            if 0x1000<=p<0x1400:
                q=W(0x50000+p)
                if q<0xC000 and W(0x50000+q)>=0x8000 and 2<=W(0x50000+q+2)<=32: c.append('dataset ptr %05X -> map hdr %05X'%(0x50000+p,0x50000+q))
        f.write('    %-60s%s\n'%(repr(i),('; '+' | '.join(c)) if c else ''))
# xref CSV
with open('out/terrano_%s_map_xref.csv'%tag,'w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';')
    w.writerow(['Map (data)','Header','Type','ECM name','Label (hypothesis)','Call @','Function','Process','ROM routine','X axis: ID','X: source','Y axis: ID','Y: source','Pointer in dataset'])
    for u in uses:
        m=u['map']
        if not m: continue
        a=int(u['at'],16); fn=owner(a)
        w.writerow(['0x%05X'%m['data'],'0x%05X'%m['hdr'],m['kind'],ECM.get(m['data'],''),lab.get(m['data'],''),'0x%06X'%a,'sub_%06X'%fn,'; '.join(pfn.get(fn,[])),u['fn'],
                    m['id1'],vn(u['r13']),m.get('id2',''),vn(u['r14']) if m['kind']=='2D' else '',u['how']])
with open('out/terrano_%s_processes.csv'%tag,'w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['#','Entry @','Flags','RAM A','Function A','RAM B (list)','Function B','Maps read by function B'])
    bymap=collections.defaultdict(set)
    for u in uses:
        if u['map']: bymap[owner(int(u['at'],16))].add('%05X'%u['map']['data'])
    for k,p in enumerate(procs):
        fb=int(p['fnB'].replace(':',''),16); fa=int(p['fnA'].replace(':',''),16)
        w.writerow([k,'0x'+p['off'],p['flags'],p['ramA'],p['fnA'],p['ramB'],p['fnB'],' '.join(sorted(bymap.get(fb,set())|bymap.get(fa,set())))])
print('functions',len(fstart))
