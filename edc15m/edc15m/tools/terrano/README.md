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
| `linsweep.py <dump> <base> <regions> <lin.pkl>` | linear sweep of code regions for any flash base |
| `starts.py <lin.pkl> <lo> <hi> <starts.pkl> [epilogues]` | heuristic function starts |
| `proctable.py <dump> <084\|550> <lin.pkl> <out.json>` | process table extraction (12-byte entries on 084, 10-byte on 550) |
| `fmatch_run.py <dirA> <baseA> <dirB> <baseB> <fmatch.pkl>` | function matching between two firmware versions |
| `varmap.py <dirA> <baseA> <dirB> <baseB> <fmatch.pkl> <out.json>` | maps RAM variables of firmware A to firmware B by aligning matched functions |
| `build550.py <dump_550> <work_dir> <out_dir> <terrano_084_map_xref.csv>` | 0281001550 listing, map cross-reference, process table and 084 ↔ 550 function/variable tables, with labels ported from 084 |
| `dis.py <dump> <cpu_addr> [n] [base]` | disassemble n instructions at a CPU address (base 80000 by default, 0 for 0281001550) |
| `ctx.py <dump> <target> [n]` | show the instructions leading up to calls/jumps to a target |

## Full pipeline

The steps that were one-off commands in the original analysis are now scripts too: `linsweep.py` (generic linear sweep), `starts.py` (heuristic function starts), `proctable.py` (process table) and `fmatch_run.py` (function matching). Recovered from the analysis session; checked to run end to end, but not yet re-run on real dumps.

EDC15VM+ 1037362084, in a folder with the dump, results in `out/`:

```
python3 tools/analyze2.py my_084.bin
python3 tools/sweep.py my_084.bin
python3 tools/starts.py out/lin.pkl 80000 100000 out/starts.pkl 2D6,830
python3 tools/proctable.py my_084.bin 084 out/lin.pkl out/proctable.json
python3 tools/mapuse.py my_084.bin
python3 tools/build.py my_084.bin 084
```

`build.py` writes `out/terrano_084.lst`, `out/terrano_084_map_xref.csv` and `out/terrano_084_processes.csv`. An optional `out/terrano_084_maps.csv` adds extra map labels.

0281001550 / 1037356022, compared with 084 (run the 084 steps first), work files in `w550/`:

```
python3 tools/linsweep.py my_550.bin 0 10000-38000 w550/lin.pkl
python3 tools/starts.py w550/lin.pkl 10000 38000 w550/starts.pkl
python3 tools/proctable.py my_550.bin 550 w550/lin.pkl w550/proctable.json
python3 tools/mapuse2.py my_550.bin w550/lin.pkl 38000 w550/mapuse.json 20D6,20AC
python3 tools/fmatch_run.py out 80000 w550 10000 w550/fmatch.pkl
python3 tools/varmap.py out 80000 w550 10000 w550/fmatch.pkl w550/varmap.json
python3 tools/build550.py my_550.bin w550 out550 out/terrano_084_map_xref.csv
```

`build550.py` writes the 550 listing, map cross-reference, process table and the 084 ↔ 550 function and variable tables to `out550/`.
