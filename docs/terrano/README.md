# Nissan Terrano II 2.7 TDi (TD27ETi) — Bosch EDC15

A separate project from the Frontera. **Frontera addresses do not apply here**, and the two Terrano ECU generations below do not share addresses with each other either.

Two ECU generations are found on the Terrano II R20 with the 2.7 TDi (TD27ETi, electronic distributor pump):

| | Earlier ECU | Later ECU |
| --- | --- | --- |
| Bosch part number | 0281001550 | not identified yet |
| Bosch designation | EDC MSA 15.5 | EDC15VM+ (`EDC15VMP` string in the flash) |
| Software | 1037356022 | 1037362084, 1037362770 |
| Nissan part number | 23710-7F405 / 7F406 / 7F415 / 7F417 | 23710-7F419 / 7F418 (084), 7F468 / 7F464 (770) |
| Flash dump | 256 KB | 512 KB, one 29F400 |
| CPU | C167 with mask ROM | C167 with mask ROM |
| Document | [msa15-0281001550.md](msa15-0281001550.md) | [edc15vm-1037362084.md](edc15vm-1037362084.md) |

Engine identification: searches for 1037362084 point only to the 2.7 TDi. The `EDC15VMP` string alone does not prove the engine, since EDC15VM+ drives both VP44 and VP37-type pumps. Check the label on your ECU (Bosch 0281 0xx xxx and Nissan 23710-…) before using any address.

## What both generations have in common

- The engine program is functionally the same Bosch development for the TD27: the fuel chain, the process numbers and most maps match. This was verified by aligning the code of both files function by function (see the 0281001550 document).
- Both CPUs run with a **mask ROM**: the scheduler, map interpolation, many low-level routines and very likely the immobilizer (NATS) live on the chip and are not in the flash dump. The same is true for the Frontera.
- **The pump metering controller differs:** on the EDC15VM+ it is in the flash (process #41), on 0281001550 it is in ROM.

## Tuning notes common to both

- The correct path for more fuel is driver demand, the smoke limiter and the rpm limiter. The “fuel → metering position” map should only be extended when the new fuel quantity exceeds the top of its axis (65 mg); editing it directly bypasses every limiter and the smoke control.
- There is a hard **68.00 mg** limit on the injection quantity in the calibration. Above that it must be raised too, otherwise fuel stops there regardless of the maps.
- The TD27 is known for cylinder head cracking from overheating. An exhaust gas temperature gauge is strongly advised for any fuel increase.

## Reading and writing

- Diagnostics over K-line work on the 2.7 TDi (reported with a KKL 409.1 cable).
- No tool has been confirmed to reliably read/write the EDC15VM+ through the OBD socket on this vehicle; forum reports describe OBD read problems. Reading on the bench or by removing the chips is the safe route.
- Always save the full flash and the EEPROM from your own ECU first. The EEPROM holds NATS immobilizer and adaptation data: keep it, do not modify it.
