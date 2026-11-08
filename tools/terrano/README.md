# Terrano tools — EDC15VM+ 1037362084 / 1037362770 and 0281001550 / 1037356022

Pure Python 3, no dependencies. Intermediate and output files go to `out/` in the current folder unless a path is given.

## EDC15VM+ (1037362084 / 770): flash at CPU 0x80000

| File | Purpose |
| --- | --- |
| `c166dis.py` | C166/C167 disassembler with self-test (`python3 c166dis.py`); register names from `sfr_c167cs.json` |
| `sfr_c167cs.json` | C167CS special function register names (from the keyhana/c166-ghidra-module processor spec) |
| `analyze2.py <dump>` | recursive descent from the entry points → `out/an.pkl` |
| `sweep.py <dump>` | linear sweep checked against the recursive result → `out/lin.pkl` |
| `mapuse.py <dump>` | every call to ROM map interpolation (`00:0CDC` 2D, `00:0CB2` 1D) with its map pointer and axis sources → `out/mapuse.json` |
| `ptrtables.py <dump>` | map pointer tables in the datasets → `out/mapptrs.json` |
| `listing.py <dump> <tag>` | annotated listing |
| `procmaps.py <tag>` | process table with the maps reachable from each process |
| `build.py <dump> <tag>` | full labelled listing, map ↔ code cross-reference CSV and process CSV |

```
python3 tools/c166dis.py
python3 tools/analyze2.py my_084.bin
python3 tools/sweep.py my_084.bin
python3 tools/mapuse.py my_084.bin
python3 tools/ptrtables.py my_084.bin
```

## Generic tools (any flash base, used for 0281001550)

| File | Purpose |
| --- | --- |
| `scan2.py <dump> <lo> <hi>` | map scanner: finds 1D/2D map headers (axis IDs ≥ 0x8000, monotonic axes) in a range and prints size, axes and value range |
| `rd.py <dump> <base> <entries> <lo-hi> <lin.pkl> [out.pkl]` | recursive descent from comma-separated entry points inside a code range, compared with a linear sweep |
| `mapuse2.py <dump> <lin.pkl> <dataset_base> <out.json> [rom_addrs]` | map interpolation calls resolved through the dataset pointer table (for 0281001550: dataset 0x38000, ROM `20D6,20AC`) |
| `fmatch.py` | helpers for comparing two firmware versions: function bodies, normalised instructions (addresses and constants masked), trigram signatures |
| `varmap.py <dirA> <baseA> <dirB> <baseB> <fmatch.pkl> <out.json>` | maps RAM variables of firmware A to firmware B by aligning matched functions |
| `build550.py <dump_550> <work_dir> <out_dir> <terrano_084_map_xref.csv>` | 0281001550 listing, map cross-reference, process table and 084 ↔ 550 function/variable tables, with labels ported from 084 |
| `dis.py <dump> <cpu_addr> [n]` | disassemble n instructions at a CPU address |
| `ctx.py <dump> <target> [n]` | show the instructions leading up to calls/jumps to a target |

## Not included yet

A few steps of the original analysis were done with one-off commands that are not in this folder:

- extracting the process table (`proctable.json`) and the list of function starts (`starts.pkl`);
- the function matching run that writes `fmatch.pkl` (the comparison itself uses the helpers in `fmatch.py`);
- the 084 map list CSV (`terrano_084_maps.csv`) used by `build.py` for ECM names.

`build.py`, `procmaps.py`, `varmap.py` and `build550.py` need these files. Everything else runs on a dump alone.
