# Opel Frontera B X22DTH — Bosch EDC15M

| Parameter | Value |
| --- | --- |
| Vehicle / engine | Opel Frontera B, X22DTH 2.2 DTI, Bosch VP44 pump |
| Bosch part number | 0281001791 |
| GM part number | 90589738 |
| Software | UU2M6S90_S |
| CPU | Siemens B58748 (C167 with mask ROM) |
| Flash | 2 × AM29F010 (marked 58530), 256 KB file |
| EEPROM | 24C04, 512 bytes |
| Sister unit | 0281001793 (different software, addresses must be checked separately) |
| Same hardware generation | Terrano 0281001550, see [docs/terrano](../terrano/msa15-0281001550.md) |

All addresses in these documents are **file offsets in the flash image, from 0**. Byte order is little-endian (Intel), as on the C167. If your tool shows the file from base 0x800000, add that base.

## Documents

- [memory-and-code.md](memory-and-code.md) — memory map, task structure, map format, fault reporting.
- [chains.md](chains.md) — calculation chains: fuel, boost, EGR, injection timing, fault paths.
- [maps.md](maps.md) — key maps with verification status and the full list of 92 maps.
- [checksum.md](checksum.md) — checksum algorithm.
- [tuning-notes.md](tuning-notes.md) — practical findings from Stage 1 and EGR off, common mistakes.

Interactive version: [research/frontera-x22dth.html](../../research/frontera-x22dth.html).

## How the analysis was done

The stock dump was decoded with a custom C166 disassembler: about 53k instructions, 96 tasks with the standard prologue and 78 additional entry points, 92 calibration maps and 114 references to them. Every map is tied to the task that reads it and to the variables on its axes. Map names were cross-checked against ECM Titanium; where the code and Titanium disagree, this is noted.

## What the dump does not contain

The bootloader, interrupt vectors, task scheduler, crank synchronisation, map interpolation, PI controllers, fault reporting and the immobilizer check live in the **CPU’s internal mask ROM** (0x0000–0x8AA5). The flash holds filler at those addresses. Task order and rates therefore cannot be recovered from the dump, and ROM routines are visible only through their arguments and results.

## Open questions

- 0x3A308: the code says “EGR air-mass setpoint”, Titanium calls it “Phase of injection”.
- Units of 0x3CD30 (20.3…33.2) are not confirmed.
- The roles of tasks 0x2327C, 0x34A34, 0x18052 were derived from inputs and outputs, not traced line by line.
- For fault paths 0x12/0x13, 0x24/0x25, 0x38–0x3D the header could not be identified unambiguously.
