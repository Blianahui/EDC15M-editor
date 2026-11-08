import sys,pickle,json,csv,struct,collections,os
sys.path.insert(0,sys.argv[0].rsplit('/',1)[0]); import maps,analyze
A=pickle.load(open('a2.pkl','rb')); d=A.d
body,owner,calls,rom=pickle.load(open('fb.pkl','rb'))
rows,found,ptrs=pickle.load(open('cat.pkl','rb'))
R,Wr=pickle.load(open('vx.pkl','rb'))
N=json.load(open('names.json',encoding='utf-8')); MN={int(k,16):v for k,v in N['maps'].items()}; VN={int(k,16):v for k,v in N['vars'].items()}
HIGH={0x39886,0x3BB14,0x3B52E,0x3BA44,0x3B8BE,0x3B926,0x3C46E,0x3C524,0x3C5A8,0x3C876,0x3DAE0,0x3A2CE,0x3A7C4,0x3DB48,0x3A75C,0x3CD00,0x3A5D0,0x3A4D4,0x3BAAC,0x3BC22}
LOW={0x391DA,0x397F0,0x39808,0x39512,0x396D4,0x3C3FC,0x3D7A0,0x3D7C4,0x3D7DC,0x3D884,0x3DA88,0x3DA70,0x3D936,0x3DBEC,0x3DC70,0x3DDBA,0x39C94,0x3C2A6,0x3C2FA,0x3B3EC,0x3B4D2,0x3A6C4,0x3A6DC}
os.makedirs('out',exist_ok=True)
def vn(v): return VN.get(v,'')
def task_of(f):
    return A.taskkind.get(f,'') if hasattr(A,'taskkind') else ''
# map catalogue
used=collections.defaultdict(list)
for r in rows:
    if r['hdr'] in found: used[r['hdr']].append(r)
with open('out/frontera_maps.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh,delimiter=';')
    w.writerow(['header','data','type','nx','ny','X axis','Y axis','min','max','role (hypothesis)','confidence','tasks','call sites'])
    for h in sorted(used):
        m=found[h]; g=maps.grid(d,m,signed=True); flat=[v for r_ in g for v in r_]
        conf='H' if h in HIGH else ('L' if h in LOW else 'M')
        fs=sorted(set('%05X'%f for r in used[h] for f in r['func']))
        w.writerow(['0x%05X'%h,'0x%05X'%m['data'],m['kind'],m['nx'],m['ny'],' '.join(map(str,m['X'])),' '.join(map(str,m['Y'] or [])),min(flat),max(flat),MN.get(h,''),conf,' '.join(fs),' '.join('%06X'%r['site'] for r in used[h])])
with open('out/frontera_map_xref.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh,delimiter=';')
    w.writerow(['call site','routine','map header','role','function','X source','Y source','result goes to'])
    for r in sorted(rows,key=lambda r:r['site']):
        w.writerow(['0x%06X'%r['site'],'MAP2D' if r['rt']=='2D' else 'CURVE1D','0x%05X'%r['hdr'] if r['hdr'] else '(pointer from RAM)',MN.get(r['hdr'],''),' '.join('%05X'%f for f in r['func']),r['x'],r['y'],r['out']])
# processes: A entries (with fallthrough B) + standalone B
def scratch(v): return 0xC0F8<=v<=0xC127 or 0xDC00<=v<0xDF00 or v in (0xFC68,0xFC6A,0xFC66,0xE000,0xFD86)
ROLE={0x160C4:'Boost setpoint',0x1F6B8:'Boost controller (PI + pilot, deviation check, path 1D)',0x1F2AC:'Boost and atmospheric pressure sensors',
0x1E772:'EGR air mass setpoint',0x1EBB6:'EGR air mass loop (PI, check → P0400)',0x15C84:'MAF → air mass per stroke (P0100)',
0x22240:'Fuel limit: smoke + torque limiters, deratings → C2BE',0x220EC:'Preliminary smoke limiter → C2BE',0x25F98:'Pedal and driver demand',
0x2327C:'Fuel coordinator / torque model → C1EC',0x34A34:'Fuel branch → C1D0',0x18052:'Final fuel FC36 / C2C4',0x14B56:'Fuel command C1D2 for VP44',
0x12F8C:'Pump (PSG) CAN exchange: fuel and timing out, reply in',0x1854C:'VP44 timing request (0x3CD00 + corrections)',0x2C544:'Timing corrections: cold start, altitude',
0x257E4:'Start fuel',0x355B6:'Idle speed setpoint (likely)',0x36AAC:'Glow plugs (likely)',0x24C98:'Idle/start fuel logic (likely)',0x26B90:'Controller gain tables (idle/cruise?)'}
seen=set(); procs=[]
for t in A.tasks:
    if t in seen: continue
    grp=[t]
    if A.taskkind[t].startswith('A'):
        # B entry inside same prologue (within 0x30 bytes)
        for u in A.tasks:
            if u!=t and A.taskkind[u]=='B' and 0<u-t<0x30: grp.append(u)
    for g in grp: seen.add(g)
    fset=set(grp)
    # include callees
    st=list(grp)
    while st:
        f=st.pop()
        for c in calls.get(f,()):
            if c not in fset: fset.add(c); st.append(c)
    ms=sorted(set(r['hdr'] for r in rows if r['hdr'] in found and set(r['func'])&set(grp)))
    w_=sorted(v for v in Wr if Wr[v]&set(grp) and not scratch(v))
    r_=sorted(v for v in R if R[v]&set(grp) and not scratch(v) and v not in w_)
    frame=None
    i=A.ins.get(t+4)
    if i and i.mn=='sub' and i.imm: frame=i.imm
    procs.append(dict(entry=t,kind=A.taskkind[t],frame=frame,maps=ms,w=w_,r=r_,role=ROLE.get(t,'')))
with open('out/frontera_processes.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh,delimiter=';')
    called=set(x for f in calls for x in calls[f])
    w.writerow(['entry','type','frame','called from','role','maps','writes (globals)','reads (globals)'])
    for p in procs:
        w.writerow(['0x%06X'%p['entry'],p['kind'],p['frame'] or '','code' if p['entry'] in called else 'scheduler/ROM vector',p['role'],' '.join('%05X'%h for h in p['maps']),
                    ' '.join(('%04X'%v)+('='+vn(v) if vn(v) else '') for v in p['w']),' '.join(('%04X'%v)+('='+vn(v) if vn(v) else '') for v in p['r'])])
dt=json.load(open('dtc.json'))
with open('out/frontera_dtc_paths.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh,delimiter=';')
    w.writerow(['path','P-code (from table)','flag address','flag','bits','set by'])
    for o in dt: w.writerow(['0x%02X'%o['path'],o['pcode'],o['enable_addr'] and '0x%05X'%o['enable_addr'],o['enable'],' '.join('%02X'%b for b in o['bits']),' '.join(o['funcs'])])
with open('out/frontera_globals.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh,delimiter=';')
    w.writerow(['RAM address','name (verified only)','written by','read by'])
    for v in sorted(set(R)|set(Wr)):
        if scratch(v) or not (0xC000<=v<0xFE00): continue
        w.writerow(['0x%04X'%v,vn(v),' '.join('%05X'%f for f in sorted(Wr[v])),' '.join('%05X'%f for f in sorted(R[v]))])
print('procs',len(procs),'maps',len(used))
