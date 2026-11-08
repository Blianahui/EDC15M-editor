# Nissan Terrano II 2.7 TDi — Bosch 0281001550 (EDC MSA 15.5)

| Parameter | Value |
| --- | --- |
| Vehicle / engine | Nissan Terrano II (R20), 2.7 TDi (TD27ETi), electronic distributor pump |
| Bosch part number | 0281001550 |
| Bosch designation | EDC MSA 15.5 |
| Software | 1037356022 |
| Nissan part numbers | 23710-7F405 / 7F406 / 7F415 / 7F417 |
| Flash dump | 256 KB |
| CPU | C167 with mask ROM |
| EEPROM | 24C02 according to one listing, check on the board |

**Same hardware generation as the Frontera 0281001791**: two flash chips, C167 with mask ROM, the same memory layout and the same ROM routine addresses. Frontera findings and tools carry over here much better than material for other EDC15 variants. Map addresses do **not** carry over.

Some listings label 0281001550 files as “Jeep Cherokee 2.7 TD” with Nissan numbers 23710-7F405; these are Terrano files under a different name.

Interactive version: [research/terrano-0281001550.html](../../research/terrano-0281001550.html). Analysis tools: [tools/terrano](../../tools/terrano/README.md).

## Memory

The flash is mapped from CPU address 0, so **file offset = CPU address** in the 0x10000–0x3FFFF range.

| Addresses | Contents |
| --- | --- |
| 0x00000–0x0FFFF | mask ROM as seen by the CPU; calls `00:xxxx` go there |
| 0x00000–0x07FFF (file) | second dataset, Nissan 7F406 (see below) |
| 0x10000–0x13FFF | loader and services; 19-entry vector table at 0x10120 pointing into ROM (timers, ADC, serial port, reset) |
| 0x10000–0x37FFF | code: about 40.7k instructions, ~450 functions |
| 0x2F1A0 | dispatcher with 81 entries (looks like K-line diagnostics) |
| 0x38000–0x3FFFF | working dataset, Nissan 7F405; DPP0/DPP1 = 0x0E/0x0F |
| 0x383F6 | process table: 60 entries of 10 bytes |
| 0x38F04 | map pointer table |

ROM routines (same addresses as on the Frontera):

| ROM | Purpose |
| --- | --- |
| `20D6` | 2D map interpolation (R12 = map, R13 = X, R14 = Y, result in R4) |
| `20AC` | 1D curve interpolation |
| `0276` | stack overflow handler |
| `07B4` | task exit |
| `26FC` | pump metering position controller (receives setpoint `FC56`) |

Tasks use the same prologue as on the Frontera: `mov r0,[0040h]; sub r0,#frame; mov [r0],[FD86h]`.

## Two datasets

- **0x38000–0x3FFFF (7F405)** is the one the code uses: `DPP0 = 0x0E`, `DPP1 = 0x0F` at startup.
- **0x00000–0x07FFF (7F406)** has the same layout and differs in 812 bytes, mostly the “fuel → metering” map (0x063E0) and two rpm × fuel maps (0x07722, 0x079E6). No code switches to it, and the CPU sees ROM at these addresses, so it is most likely unused (an inference, not verified).

Addresses of the same map in the two sets differ by 0x38000. ECM Titanium shows the set-2 addresses (0x0xxxx) and writes to both sets.

The last 4 bytes of each dataset (0x07FFC and 0x3FFFC) differ and look like checksums. The algorithm has not been identified yet.

## Fuel chain

| Process | Function | What it does | Output |
| --- | --- | --- | --- |
| #34 | 0x20166 | driver demand: map 0x39940 = f(rpm, pedal `C1D0`) | |
| #25 | 0x1D522 (+0x1D35C) | fuel ceiling: rpm limiter 0x3CD56, smoke limiter 0x3D0B8 with its input 0x3D306, start fuel 0x3CAE6 and 13 more maps (0x3CA50–0x3DE62) | `FCBA` |
| #30 | 0x1E26A | fuel coordinator: combines demand and limits; reads 8 maps at 0x3919A–0x39630 | |
| | 0x2A03E | final and injection quantity | `FC36` |
| #24 | 0x1709A | fuel temperature correction, map 0x3DEBC | |
| #29 | 0x14A26 | metering setpoint: map 0x3E3E0 converts fuel and rpm into the pump metering position | `FC56` → ROM `26FC` |

**The metering position controller is in ROM.** The flash computes setpoint `FC56` and passes it straight to `CALLS 00:26FC`. There is no PI controller in the flash and no PWM/CAPCOM2 writes, so the controller gains cannot be changed from the flash. For tuning this does not matter: the whole fuel chain up to the metering setpoint is in the flash.

Process numbers and functions were found in this firmware directly; their roles were identified by aligning the code with a later Terrano firmware where the chain was traced line by line.

Variables: rpm `FC3A` (axis ID `E08A`), final fuel `FC36`, fuel ceiling `FCBA`, pedal `C1D0`, atmospheric pressure `C234`, metering setpoint `FC56`.

## Key maps

| Data (working set) | Data (set 2, ECM Titanium) | Size | Meaning |
| --- | --- | --- | --- |
| 0x39940 | 0x01940 | 12×8 | driver demand: rpm × pedal (Titanium: fuel during acceleration) |
| 0x3CD56 | 0x04D56 | 16×25 | fuel limit: atm. pressure × rpm (Titanium: 4 “torque limiter” curves = rows 0, 4, 8, 12; all rows identical in stock) |
| 0x3D0B8 | 0x050B8 | 16×13 | smoke limiter: fuel vs rpm and air mass |
| 0x3D306 | 0x05306 | 16×16 | smoke limiter input (temperature correction, 1:1) |
| 0x3CAE6 | 0x04AE6 | 11×10 | start fuel |
| 0x3DEBC | 0x05EBC | 9×8 | fuel temperature correction |
| 0x3E3E0 | 0x063E0 | 16×14 | fuel → metering position (Titanium: injection (Ext.)); **differs between the sets** |
| 0x3F9E6 | 0x079E6 | 16×10 | Titanium: phase of injection; read by process #45 together with other injection maps |
| 0x3F75E | 0x0775E | 16×13 | signed values, looks like injection timing (process #44) |

The code reads 58 maps in total (77 references); the full list with axis IDs, functions and processes is on the interactive page and in `terrano_0281001550_map_xref.csv` produced by the tools.

## Tuning notes

- Raise driver demand, the smoke limiter and the rpm limiter. Edit the “fuel → metering” map 0x3E3E0 only to extend it when the new fuel exceeds the top of its axis (65 mg): editing it directly bypasses every limiter and smoke control.
- There is a hard **68 mg** fuel limit in the parameter block; it limits fuel independently of all maps listed by ECM.
- After editing the metering map in Titanium, check that 0x3E3E0 changed by the same percentage and was not overwritten with the values of 0x063E0, because the two copies differ.
- ECM’s second “phase of injection” at 0x04842 (0x3C842 in the working set, 13×16) has no axis header and is referenced by no code or pointer table. Possibly read by ROM; its role cannot be verified from the flash.
- The TD27 is known for cylinder head cracking from overheating. An exhaust gas temperature gauge is strongly advised for any fuel increase.

## Reading and writing

- Diagnostics over K-line work on the 2.7 TDi (reported with a KKL 409.1 cable).
- 0281001550 is usually read by removing the flash chips (or on the bench). Always save the full flash and the EEPROM from your own ECU first. The EEPROM holds NATS immobilizer and adaptation data: keep it, do not modify it.
