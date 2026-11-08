"""Annotated listing, map cross-reference and process table for Bosch 0281001550 (SW 1037356022).
usage: listing550.py <dump> <work_dir> <out_dir>
  work_dir holds lin.pkl, starts.pkl, proctable.json and mapuse.json (see README for the steps)"""
import sys, pickle, struct, re, collections, json, csv, bisect
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
img = open(sys.argv[1], 'rb').read()
D = os.path.join(sys.argv[2], ''); O = os.path.join(sys.argv[3], ''); os.makedirs(O, exist_ok=True)
lin = pickle.load(open(D + 'lin.pkl', 'rb')); starts = pickle.load(open(D + 'starts.pkl', 'rb'))
uses = json.load(open(D + 'mapuse.json')); procs = json.load(open(D + 'proctable.json'))

ROM = {0x276: 'rom_stack_overflow', 0x7B4: 'rom_task_exit',
       0x20D6: 'rom_map2D(R12=map,R13=X,R14=Y)->R4', 0x20AC: 'rom_curve1D(R12=map,R13=X)->R4',
       0x26FC: 'rom_metering_controller? (called right after setpoint FC56 is written)'}
VARS = {'FC3A': 'rpm', 'E08A': 'rpm (mirror, rpm axis ID)', 'FC36': 'final fuel quantity',
        'FCBA': 'fuel ceiling', 'C1D0': 'pedal', 'C234': 'atmospheric pressure',
        'FC56': 'pump metering position setpoint'}
KEY = {0x1D522: 'fuel ceiling (process #25)', 0x20166: 'driver demand', 0x1E26A: 'fuel coordinator',
       0x2A03E: 'final and injection quantity', 0x14A26: 'metering setpoint', 0x1709A: 'fuel temperature correction'}
MAPS = {0x39940: 'driver demand: rpm x pedal', 0x3CD56: 'fuel limit: atm. pressure x rpm',
        0x3D0B8: 'smoke limiter: rpm x air mass', 0x3D306: 'smoke limiter input (temperature correction)',
        0x3CAE6: 'start fuel', 0x3DEBC: 'fuel temperature correction', 0x3E3E0: 'fuel -> metering position',
        0x3F9E6: 'Titanium: phase of injection', 0x3F75E: 'signed, looks like injection timing'}

fstart = set(starts); pfn = {}
for k, p in enumerate(procs):
    for f in ('fnA', 'fnB'):
        a = int(p[f].replace(':', ''), 16)
        if a >= 0x10000:
            fstart.add(a); pfn.setdefault(a, []).append('proc#%d %s flags=%s ramB=%s' % (k, f, p['flags'], p['ramB']))
fs = sorted(a for a in fstart if a in lin)
own = lambda a: fs[bisect.bisect_right(fs, a) - 1] if a >= fs[0] else None
callers = collections.defaultdict(set)
for a, i in lin.items():
    if i.kind == 'call':
        for t in i.targets:
            if t[0] == 'code' and t[1] >= 0x10000: callers[t[1]].add(a)
jt = set(t[1] for i in lin.values() if i.kind in ('jmp', 'cjmp') for t in i.targets if t[0] == 'code')
mapat = {int(u['at'], 16): u for u in uses}
def vn(s):
    m = re.match(r'\[([0-9A-F]{4})h\]$', s or '')
    return '%s{%s}' % (s, VARS[m.group(1)]) if m and m.group(1) in VARS else (s or '')
# function -> processes reaching it directly
procof = {a: ' '.join(x.split()[0] for x in v) for a, v in pfn.items()}

with open(O + 'terrano_0281001550.lst', 'w', encoding='utf-8') as f:
    f.write(';; Nissan Terrano II 2.7 TDi  Bosch 0281001550  SW 1037356022 - disassembly of C167 flash (256 KB)\n')
    f.write(';; Flash at CPU 0x000000 (file offset = address). Mask ROM covers CPU 0x0000-0xFFFF: CALLS 00:xxxx go to ROM (not in dump).\n')
    f.write(';; Code 0x10000-0x37FFF (0x10000-0x13FFF: boot/service, vectors at 0x10120). Active dataset 0x38000-0x3FFFF via DPP0/DPP1=0x0E/0x0F.\n')
    f.write(';; Process table 0x383F6 (60 entries x 10 bytes).\n\n')
    for a in sorted(lin):
        i = lin[a]
        if a in fstart:
            f.write('\n;==================== sub_%06X' % a)
            if a in KEY: f.write('   ' + KEY[a])
            if a in pfn: f.write('   <-- ' + '; '.join(pfn[a]))
            if callers[a]: f.write('   called from: ' + ', '.join('%06X' % c for c in sorted(callers[a])[:6]) + (' ...' if len(callers[a]) > 6 else ''))
            f.write('\nsub_%06X:\n' % a)
        elif a in jt: f.write('loc_%06X:\n' % a)
        c = []
        if i.mnem in ('CALLS', 'JMPS') and i.targets[0][1] < 0x10000: c.append(ROM.get(i.targets[0][1], 'rom_%04X' % i.targets[0][1]))
        u = mapat.get(a)
        if u and u['map']:
            m = u['map']; d = m['data']; s = 'MAP %05X %s' % (d, m['kind'])
            if d in MAPS: s += ' "%s"' % MAPS[d]
            s += '  X(%s)=%s' % (m['id1'], vn(u['r13']))
            if m['kind'] == '2D': s += '  Y(%s)=%s' % (m['id2'], vn(u['r14']))
            c.append(s)
        else:
            for mm in re.finditer(r'\[([0-9A-F]{4})h\]', i.ops):
                if mm.group(1) in VARS: c.append('%s=%s' % (mm.group(1), VARS[mm.group(1)]))
        f.write('    %-60s%s\n' % (repr(i), ('; ' + ' | '.join(c)) if c else ''))

rows = []
for u in uses:
    m = u['map']
    if not m: continue
    a = int(u['at'], 16); fn = own(a)
    rows.append(dict(data=m['data'], hdr=m['hdr'], kind=m['kind'], nx=m['n1'], ny=m.get('n2', 1), xid=m['id1'], yid=m.get('id2', ''),
                     label=MAPS.get(m['data'], ''), site=a, func=fn, proc=procof.get(fn, ''), xsrc=vn(u['r13']),
                     ysrc=vn(u['r14']) if m['kind'] == '2D' else '', how=u['how']))
with open(O + 'terrano_0281001550_map_xref.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['Map (data)', 'Header', 'Type', 'Size', 'X axis ID', 'Y axis ID', 'Label', 'Call @', 'Function', 'Process', 'X source', 'Y source', 'Pointer'])
    for r in rows:
        w.writerow(['0x%05X' % r['data'], '0x%05X' % r['hdr'], r['kind'], '%dx%d' % (r['nx'], r['ny']), r['xid'], r['yid'], r['label'],
                    '0x%06X' % r['site'], 'sub_%06X' % r['func'] if r['func'] else '', r['proc'], r['xsrc'], r['ysrc'], r['how']])
with open(O + 'terrano_0281001550_processes.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f, delimiter=';'); w.writerow(['#', 'Entry @', 'Flags', 'RAM A', 'Function A', 'RAM B (list)', 'Function B', 'Known role'])
    for k, p in enumerate(procs):
        role = ' / '.join(KEY[x] for x in (int(p['fnA'].replace(':', ''), 16), int(p['fnB'].replace(':', ''), 16)) if x in KEY)
        w.writerow([k, '0x' + p['off'], p['flags'], p['ramA'], p['fnA'], p['ramB'], p['fnB'], role])
json.dump([{k: v for k, v in r.items()} for r in rows], open(O + 'terrano_0281001550_maps.json', 'w'), indent=0)
print('functions', len(fs), 'map references', len(rows), 'distinct maps', len({r['data'] for r in rows}))
