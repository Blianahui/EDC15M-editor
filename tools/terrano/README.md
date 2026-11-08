# Terrano tools — Bosch 0281001550 / SW 1037356022

Pure Python 3, no dependencies. Flash mapped from CPU address 0 (file offset = CPU address), code 0x10000–0x37FFF, working dataset 0x38000–0x3FFFF.

| File | Purpose |
| --- | --- |
| `c166dis.py` | C166/C167 disassembler with self-test (`python3 c166dis.py`); register names from `sfr_c167cs.json` |
| `sfr_c167cs.json` | C167CS special function register names (from the keyhana/c166-ghidra-module processor spec) |
| `linsweep.py <dump> <base> <regions> <lin.pkl>` | linear sweep of the code |
| `rd.py <dump> <base> <entries> <lo-hi> <lin.pkl> [out.pkl]` | recursive descent from comma-separated entry points, compared with the linear sweep |
| `starts.py <lin.pkl> <lo> <hi> <starts.pkl>` | heuristic function starts (call targets and instructions after a return) |
| `proctable.py <dump> 550 <lin.pkl> <out.json>` | process table (10-byte entries at 0x383F6) |
| `mapuse2.py <dump> <lin.pkl> <dataset_base> <out.json> [rom_addrs]` | every call to the ROM map interpolation, resolved through the dataset pointer table |
| `listing550.py <dump> <work_dir> <out_dir>` | annotated listing, map ↔ code cross-reference CSV, process CSV and a JSON map list |
| `scan2.py <dump> <lo> <hi>` | map scanner: finds 1D/2D map headers in a range and prints size, axes and value range |
| `dis.py <dump> <cpu_addr> [n] [base]` | disassemble n instructions at a CPU address |
| `ctx.py <dump> <target> [n]` | show the instructions leading up to calls/jumps to a target (needs `out/lin.pkl`) |

## Running

In a folder with your dump, tools in `tools/`:

```
python3 tools/c166dis.py
python3 tools/linsweep.py my_550.bin 0 10000-38000 w550/lin.pkl
python3 tools/starts.py w550/lin.pkl 10000 38000 w550/starts.pkl
python3 tools/proctable.py my_550.bin 550 w550/lin.pkl w550/proctable.json
python3 tools/mapuse2.py my_550.bin w550/lin.pkl 38000 w550/mapuse.json 20D6,20AC
python3 tools/listing550.py my_550.bin w550 out550
python3 tools/scan2.py my_550.bin 38000 40000
```

`listing550.py` writes to `out550/`:

- `terrano_0281001550.lst` — full listing with functions, processes, ROM calls and map references with their X/Y sources;
- `terrano_0281001550_map_xref.csv` — which function reads which map and from which variables;
- `terrano_0281001550_processes.csv` — process table with known roles;
- `terrano_0281001550_maps.json` — the same map references as data.

## Checked on a real dump

Run on 0281001550 / 1037356022: 40,657 instructions, 449 functions, process table at 0x383F6 with 60 entries (82 of 100 function pointers coincide with independently found function starts), 77 references to 58 maps, all key maps found with the axes given in the documentation.
