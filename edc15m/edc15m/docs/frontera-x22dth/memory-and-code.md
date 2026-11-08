# Memory and code structure

## Memory map

File offsets equal C167 linear addresses.

| Addresses | Contents |
| --- | --- |
| 0x00000–0x08AA5 | Filled with C3 in the flash. At these addresses the CPU sees its mask ROM: bootloader, vectors, scheduler, crank synchronisation, immobilizer, library. The code makes 833 calls there, to 96 distinct addresses. Map interpolation: `00:20D6` (2D) and `00:20AC` (1D). |
| 0x08AA6–0x0FFFF | Code. The 0xC000–0xFFFF range is called through the segment 7 mirror (`07:Cxxx`) because in segment 0 those addresses hold the C167 XRAM and SFRs. |
| 0x10000–0x37FFF | Application code. `55 AA` at 0x10800, entry at 0x10804. Diagnostic command dispatcher at 0x17290 (81 `jmpa` handlers from 0x1729C). |
| 0x38000–0x3FFFF | Calibration (DPP0=0E, DPP1=0F): maps and parameters, map pointer table 0x38DD0–0x391D8, fault tables 0x3AA3E–0x3B3B8 and 0x3DA0E–0x3DE3E, task stack tops 0x38030–0x38042, checksum at 0x3FFFC. |

## Tasks

All calculations are split into tasks called by the scheduler in ROM.

- 96 tasks begin with the standard prologue `mov r0,[0040h]; sub r0,#frame; mov [r0],[FD86h]`: they allocate a frame on their own stack (stack tops 0x3803C–0x38042).
- 78 entry points start directly with `cmp r0,[FD86h]`.
- Task exit: `jmps 00:07B4`. Stack overflow: `00:0276`.

A task copies the globals it needs into its work area (`C0FA–C126`, `FC66–FC6A`), computes and writes the result to one or two globals. Intermediate values are mirrored into monitoring variables `DCxx–DExx`. Their addresses are what map headers store as the “axis ID”. Example: the boost map Y axis is `DD94` = C1EC + C1D0.

## Map format

```
[ID X][nx][X1 … Xnx][ID Y][ny][Y1 … Yny][data]
```

All fields are 16-bit words. Data is stored row by row along X: index = x·ny + y. A 1D curve has no Y part.

The code fetches the map address from a pointer table, not directly:

```
mov r12,[100Ch]     ; 0x3900C → 0x446E → map 0x3C46E
mov r13, X
mov r14, Y
calls 00:20D6       ; 2D interpolation, result in r4
```

## Faults

All faults are reported through `calls 01:4002`:

- `r2 = (path << 8) | ~bit`;
- `r1` — pointer to an 8-byte debounce record.

Each path has a header in the calibration with its P-code and an enable flag. Example: path 0x1E → P0400 → flag 0x3AFEE.

## Key variables

| Variable | Meaning |
| --- | --- |
| C1CC | pedal, 0.01 % |
| C1CE | driver demand |
| C1EC | desired fuel |
| C2BE | fuel limit |
| FC36 | actual fuel (axis of almost every map) |
| C216 | MAF air mass, 0.1 mg/stroke |
| C220 / C21E | boost / atmospheric pressure, mbar |
| C224 | boost setpoint |
| C2E4 | EGR air mass setpoint |
| C214 → C252 | start-of-injection value sent to the VP44 |
| C242 | probably pump fuel temperature |
