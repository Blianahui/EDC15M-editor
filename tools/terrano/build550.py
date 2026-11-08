import sys,pickle,struct,re,collections,json,csv,bisect,ast
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# usage: build550.py <dump_0281001550> <work_dir> <out_dir> <terrano_084_map_xref.csv>
# work_dir holds lin.pkl, starts.pkl, mapuse.json, proctable.json, varmap.json, fmatch.pkl of the 550 firmware
IMG=sys.argv[1]; D=os.path.join(sys.argv[2],''); O=os.path.join(sys.argv[3],''); os.makedirs(O,exist_ok=True)
img=open(IMG,'rb').read(); W=lambda o: struct.unpack_from('<H',img,o)[0]
lin=pickle.load(open(D+'lin.pkl','rb')); starts=pickle.load(open(D+'starts.pkl','rb'))
uses=json.load(open(D+'mapuse.json')); procs=json.load(open(D+'proctable.json'))
vm=json.load(open(D+'varmap.json')); (match,)=pickle.load(open(D+'fmatch.pkl','rb'))
# 084 labels
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'build.py'),encoding='utf-8').read()
VARS84=ast.literal_eval(re.search(r'VARS=(\{.*?\})\n',src,re.S).group(1))
VARS={}
for k,v in VARS84.items():
    m=vm.get(k)
    if m and m['conf']>=0.8: VARS[m['to']]=v+' [084:%s]'%k
VARS['E08A']='rpm (mirror, rpm axis ID)'
ROM={0x276:'rom_stack_overflow_error(MDL=code)',0x7B4:'rom_task_exit',0x20D6:'rom_map2D(R12=map,R13=X,R14=Y)->R4',0x20AC:'rom_curve1D(R12=map,R13=X)->R4',0x26FC:'rom_actuator_setpoint? (right after metering setpoint FC56 is written)'}
# map labels from 084 xref via pointer-table mapping
lab84={}
for r in csv.reader(open('out/terrano_084_map_xref.csv',encoding='utf-8-sig'),delimiter=';'):
    if r[0].startswith('0x'): lab84.setdefault(r[13],(r[3],r[4],r[0]))
maplab={}
for u in uses:
    m=u['map']
    if not m or not (u['how'] or '').startswith('tab['): continue
    t550=u['how'][4:8]
    for k,v in vm.items():
        if v['to']==t550 and 'tab[%s]'%k in lab84:
            ecm,my,a84=lab84['tab[%s]'%k]; maplab[m['data']]=(ecm,my,a84)
# functions
fstart=set(starts); pfn={}
for k,p in enumerate(procs):
    for f in('fnA','fnB'):
        a=int(p[f].replace(':',''),16)
        if a>=0x10000: fstart.add(a); pfn.setdefault(a,[]).append('proc#%d %s flags=%s ramB=%s'%(k,f,p['flags'],p['ramB']))
fs=sorted(fstart); own=lambda a: fs[bisect.bisect_right(fs,a)-1]
inv={b:(a,j) for a,(b,j) in match.items() if j>=0.4}
KEY={0x98D3A:'fuel ceiling (#25 in 084)',0x9C708:'driver demand (#36)',0x9A7E8:'fuel coordinator (#32)',0xAE798:'final and injection quantity (#29)',0x9EF38:'metering setpoint (#30)',0xAFBCE:'fuel temperature correction',0x98B68:'fuel ceiling initialisation'}
callers=collections.defaultdict(set)
for a,i in lin.items():
    if i.kind=='call':
        for t in i.targets:
            if t[0]=='code' and t[1]>=0x10000: callers[t[1]].add(a)
jt=set(t[1] for i in lin.values() if i.kind in('jmp','cjmp') for t in i.targets if t[0]=='code')
mapat={int(u['at'],16):u for u in uses}
def vn(s):
    m=re.match(r'\[([0-9A-F]{4})h\]$',s or '')
    return '%s{%s}'%(s,VARS[m.group(1)]) if m and m.group(1) in VARS else (s or '')
with open(O+'terrano_550_356022.lst','w') as f:
    f.write(';; Nissan Terrano II 2.7 TDi  Bosch 0281001550  SW 1037356022 - disassembly of C167 flash (256 KB)\n')
    f.write(';; Flash at CPU 0x000000 (file offset = address). Mask ROM covers CPU 0x0000-0xFFFF: CALLS 00:xxxx go to ROM (not in dump).\n')
    f.write(';; Code 0x10000-0x37FFF (0x10000-0x13FFF: boot/service, vectors at 0x10120). Active dataset 0x38000-0x3FFFF via DPP0/DPP1=0x0E/0x0F.\n')
    f.write(';; Process table 0x383F6 (60 entries x 10 bytes). Labels [084:xxxx] are ported from SW 1037362084 by code alignment.\n\n')
    for a in sorted(lin):
        i=lin[a]
        if a in fstart:
            f.write('\n;==================== sub_%06X'%a)
            if a in pfn: f.write('   <-- '+'; '.join(pfn[a]))
            if a in inv:
                a84,j=inv[a]; f.write('   = 084 sub_%06X (J=%.2f)%s'%(a84,j,(' '+KEY[a84]) if a84 in KEY else ''))
            if callers[a]: f.write('   called from: '+', '.join('%06X'%c for c in sorted(callers[a])[:6])+(' ...' if len(callers[a])>6 else ''))
            f.write('\nsub_%06X:\n'%a)
        elif a in jt: f.write('loc_%06X:\n'%a)
        c=[]
        if i.mnem in('CALLS','JMPS') and i.targets[0][1]<0x10000: c.append(ROM.get(i.targets[0][1],'rom_%04X'%i.targets[0][1]))
        u=mapat.get(a)
        if u and u['map']:
            m=u['map']; d=m['data']; s='MAP %05X %s'%(d,m['kind'])
            if d in maplab: s+=' "%s" = 084 %s'%((maplab[d][0] or maplab[d][1])[:60],maplab[d][2])
            s+='  X(%s)=%s'%(m['id1'],vn(u['r13']))
            if m['kind']=='2D': s+='  Y(%s)=%s'%(m['id2'],vn(u['r14']))
            c.append(s)
        else:
            for mm in re.finditer(r'\[([0-9A-F]{4})h\]',i.ops):
                if mm.group(1) in VARS: c.append('%s=%s'%(mm.group(1),VARS[mm.group(1)]))
        f.write('    %-60s%s\n'%(repr(i),('; '+' | '.join(c)) if c else ''))
with open(O+'terrano_550_map_xref.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['Map (data)','Header','Type','ECM name (from 084)','Label (from 084)','Same map in 084','Call @','Function','Process','X axis: ID','X: source','Y axis: ID','Y: source','Pointer'])
    for u in uses:
        m=u['map']
        if not m: continue
        a=int(u['at'],16); fn=own(a); ml=maplab.get(m['data'],('','',''))
        w.writerow(['0x%05X'%m['data'],'0x%05X'%m['hdr'],m['kind'],ml[0],ml[1],ml[2],'0x%06X'%a,'sub_%06X'%fn,'; '.join(pfn.get(fn,[])),m['id1'],vn(u['r13']),m.get('id2',''),vn(u['r14']) if m['kind']=='2D' else '',u['how']])
with open(O+'terrano_550_processes.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['#','Entry @','Flags','RAM A','Function A','= in 084','RAM B (list)','Function B','= in 084'])
    def eq(s):
        a=int(s.replace(':',''),16); 
        if a in inv: return 'sub_%06X J=%.2f %s'%(inv[a][0],inv[a][1],KEY.get(inv[a][0],''))
        return ''
    for k,p in enumerate(procs): w.writerow([k,'0x'+p['off'],p['flags'],p['ramA'],p['fnA'],eq(p['fnA']),p['ramB'],p['fnB'],eq(p['fnB'])])
with open(O+'terrano_084_to_550_functions.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['084 function','550 function','Similarity (trigram Jaccard)','Purpose'])
    for a,(b,j) in sorted(match.items()):
        if j>=0.4: w.writerow(['sub_%06X'%a,'sub_%06X'%b,'%.2f'%j,KEY.get(a,'')])
with open(O+'terrano_084_to_550_variables.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['084','550','Votes','Confidence','Purpose (from 084)'])
    for k,v in sorted(vm.items()): w.writerow([k,v['to'],v['n'],v['conf'],VARS84.get(k,'')])
print('functions',len(fstart),'labeled maps',len(maplab),'vars ported',len(VARS),'matched funcs',len(inv))
