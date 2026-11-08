# Frontera tools — EDC15M 0281001791 / UU2M6S90_S

| File | Purpose |
| --- | --- |
| `c166.py` | C166/C167 instruction decoder (all opcodes; the undefined set matches keyhana c166.sinc; BFLDL/BFLDH byte order checked on this code) |
| `test_isa.py` | decoder self-test |
| `analyze.py` | recursive code traversal; file offset = linear address; 0x0000–0x8AA5 = mask ROM; segment 7 = mirror of segment 0; DPP 0E/0F/04/03 |
| `run1.py` | traversal from entry points: start 0x10804, dispatcher 0x17290, task prologues `mov r0,[00xxh]; sub r0,#; mov [r0],[FD86h]` and entries `cmp r0,[FD86h]` |
| `run2.py` | adds functions heuristically (entries after ret/rets that decode cleanly) |
| `funcs.py` | function bodies and call graph |
| `maps.py` | map header parser `[ID X][nx][X][ID Y][ny][Y][data]`, data row by row along X |
| `xref.py`, `catalog.py` | link calls to `00:20D6` (2D) / `00:20AC` (1D) with maps through pointer tables; sources of r13/r14 |
| `varx.py` | who writes and who reads each global variable |
| `dtc.py` | calls to `01:4002` → fault path, bits, P-code and enable flag from the table |
| `export.py`, `listing.py` | CSV and annotated listing; labels come from `names.json` |
| `names.json` | labels for ROM routines, variables and maps |

## Running

From a folder containing your dump saved as `frontera.bin`, with these scripts in `tools/`:

```
python3 tools/test_isa.py
python3 tools/run1.py frontera.bin a1.pkl
python3 tools/run2.py a1.pkl a2.pkl
python3 -c "import sys,pickle;sys.path.insert(0,'tools');import funcs;A=pickle.load(open('a2.pkl','rb'));b,o=funcs.bodies(A);c,r=funcs.callgraph(A,b);pickle.dump((b,o,c,r),open('fb.pkl','wb'))"
python3 tools/catalog.py a2.pkl fb.pkl cat.pkl
python3 tools/varx.py a2.pkl fb.pkl vx.pkl
python3 tools/dtc.py a2.pkl fb.pkl dtc.json
cp tools/names.json .
python3 tools/export.py
mkdir -p out
python3 tools/listing.py a2.pkl fb.pkl cat.pkl names.json out/frontera_UU2M6S90_listing.asm
```

Listing labels: `task_` — task entry (A[40] — standard prologue with stack [0040h], B — entry with frame check), `sub_` — function found through a call, `hsub_` — function found heuristically (entry not proven).

These scripts are written for this exact software version (entry points, ROM addresses). For other EDC15M versions, adjust the entry points in `run1.py` first.
