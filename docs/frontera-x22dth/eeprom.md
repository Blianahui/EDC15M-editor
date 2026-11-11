# EEPROM (24C04, 512 bytes) — flash write-enable

Besides the 256 KB flash, the ECU carries a small serial EEPROM (24C04, 512 bytes) that stores unit-specific data: immobiliser data, a VIN/serial region, and — on this ECU — a 20-byte block that gates whether a programmer is allowed to write the flash at all. None of that data is published here (see [CONTRIBUTING.md](../../CONTRIBUTING.md)); this page documents the **structure**, so that the [EEPROM editor](../../editor/EDC15M_eeprom_editor.html) can be used and checked without needing the underlying values.

Confirmed on a real unit (bench write test **and** a real engine start): Bosch 0281001791, software UU2M6S90_S. On other EDC15 units or software versions the layout may differ and must be re-verified; treat the offsets below as specific to this ECU.

## Layout

| Region | Offset | Size | Role |
| --- | --- | --- | --- |
| G1 | 0x00–0x0F | 16 B | unit label; not read by the start or write-enable path |
| G2 | 0x20–0x4B | 44 B | VIN / serial region; not read by the start or write-enable path |
| **G3** | **0x4C–0x5F** | **20 B** | **flash write-enable** — the only region that decides whether a programmer can write the flash |
| Immobiliser | 0xE2–0x117 | 54 B | immobiliser data; 0xE8–0x117 is three redundant 16-byte copies (0xE8, 0xF8, 0x108), required for the engine to start |

Addresses are EEPROM byte offsets, unrelated to the flash file's own addressing.

## G3, the write-enable block

G3 is 20 bytes, with an internal structure of its own:

| Field | Offset | Size | Notes |
| --- | --- | --- | --- |
| Programming date/serial | 0x4C | 4 B | changes between a “native” and a “donor” dump |
| V1 | 0x50 | 2 B | stored as three identical copies (0x50, 0x52, 0x54) |
| V2 | 0x56 | 2 B | stored as three identical copies (0x56, 0x58, 0x5A) |
| Marker | 0x5C | 2 B | fixed `55 AA` |
| Tail | 0x5E | 2 B | not a simple sum or a standard CRC-16 of the rest of the block (checked by brute force); its derivation is presumably inside the CPU's mask ROM, which is not in the dump |

**Finding:** whether a programmer is allowed to write the flash is controlled *only* by this 20-byte block. A dump whose G3 the programmer rejects, combined with another dump's G3, flips the result from “rejected” to “accepted” — with nothing else in the file changed.

**G3 is not read by the engine-start / immobiliser path.** A dump that starts the engine keeps starting it after its G3 is replaced with another dump's G3, as long as the immobiliser block (0xE2–0x117) is left untouched and internally consistent.

Because V1/V2 are triple-redundant (like the immobiliser copies) and the tail byte cannot be derived from the rest of the block with simple arithmetic, the editor does not try to recompute G3 — it transplants it whole from a donor dump whose G3 is already accepted by the programmer.

## Building a working EEPROM

1. Take the dump the car **starts** with as the base (native: has your consistent immobiliser data).
2. Overlay only G3 (0x4C–0x5F) from a dump the programmer **accepts for writing** (donor).
3. Leave everything else — immobiliser, VIN/serial, adaptations — from the base, untouched.

Going the other way (donor dump as the base, native immobiliser overlaid) does not work: the unit fails to identify itself to the diagnostic tester at all.

The [EEPROM editor](../../editor/EDC15M_eeprom_editor.html) automates this: it checks both input files (size, G3 internal consistency, immobiliser redundancy), transplants G3, reports every other region where the two inputs differ (so you can see what was intentionally left alone), and lets you save the result.

## Checks worth doing before trusting a result

- Both input files are exactly 512 bytes.
- V1 and V2 in G3 have three matching copies in each input file.
- The `55 AA` marker is present at 0x5C in each input file.
- The three immobiliser copies (0xE8, 0xF8, 0x108) match in the base/native file — otherwise the file is likely corrupt or misread, and the result should not be trusted to start the engine.

These are exactly the checks the editor runs and reports.
