# Calculation chains

Task addresses are code entry points. Map addresses are headers (data follows the axes, see [maps.md](maps.md)).

## Fuel quantity: pedal → limiters → VP44

| Task | What it does | Output |
| --- | --- | --- |
| 0x25F98 | Pedal: ADC → C1CC (0.01 %). Driver demand 0x39886 = f(rpm, pedal). | C1CE |
| 0x257E4 | Start fuel 0x3B418 = f(rpm, coolant). | C1CA |
| 0x220EC, 0x22240 | Fuel limit. If air mass is plausible (C0D2 ≥ 30h) — smoke limiter 0x3BB14 over rpm and C216, otherwise a fixed 60 mg (0x3BC22). Minus temperature correction 0x3BE90, rate-of-rise limit. The lower of this and the torque limiter 0x3BA44 (in limp mode 0x3BAAC, 30 mg). The contribution of copies 0x3B52E / 0x3B8BE is multiplied by factor 0x3B926 (0 in stock). Then factor C1D6, coolant correction 0x3B966, over-temperature derating 0x3BC3A and 0x3BCB0, limp-mode curves 0x3BD80 / 0x3BDE8. | C2BE |
| 0x2327C | Coordinator: driver demand, idle (0x3C21C looks like the idle speed setpoint, 800–1100), torque model: fuel→torque 0x395BA, friction 0x39662, inverse conversion 0x396D4. Reads the C2BE limit. | C1EC |
| 0x34A34, 0x18052 | Additive term C1D0 (looks like an anti-jerk damper, not verified) and the final fuel quantity. | FC36, C2C4 |
| 0x14B56, 0x12F8C | Exchange with the pump control unit (PSG) over CAN via ROM routines 7CD8 / 7D30. Sent: C1D2, C250, C252 (timing), C254. Received: 4 words into C246–C24C. | VP44 |

Fuel units (0.01 mg/stroke) are consistent across all maps and the boost axis, but no constant in the code proves them.

## Boost

| Task | What it does | Output |
| --- | --- | --- |
| 0x1F2AC | Boost and atmospheric pressure sensors. | C220, C21E |
| 0x160C4 | y = C1EC + C1D0. Base 0x3C46E (rpm, y). Altitude term 0x3C524 weighted by 0x3C5A8 (100 % at 750 mbar and below, 0 % from 950 mbar). Temperature factor 0x3C79C, dynamic term via ROM 22F2, offset 0x3C5D4 (zeros). **Upper clamp by the constant [0x3C3AA] = 2100 mbar.** | C224 |
| 0x1F6B8 | Controller: error C224 − C220, P term (ROM 21A2), I term (21C4), plus pilot duty 0x3C876 (rpm, y), clamped to 0…65.00 % (0x3C3F2 / 0x3C3F6). Deviation monitoring in window 0x3DAE0: underboost above 250 mbar — bit 4 of path 0x1D, overboost above 150 mbar — bit 5 (parameters 0x3C3B4 / 0x3C3B6). | boost valve duty |

## EGR: closed loop on air mass

| Task | What it does | Output |
| --- | --- | --- |
| 0x15C84 | MAF: two ADC samples (C00C, C00E) → characteristic 0x3A75C → average → divide by rpm → correction 0x3A744. Plausibility check — path 0x0B (P0100). | C216 |
| 0x1E772 | Setpoint 0x3A2CE (rpm, C1EC+C1D0) plus corrections for atmospheric pressure 0x3A4D4, temperature 0x3A528 and coolant 0x3A5D0 (up to +545 mg on a cold engine, i.e. EGR closed). Boost deviation correction 0x3A7D0 (zeros in stock). Limits from the block at 0x3A2A0. | C2E4 |
| 0x1EBB6 | PI controller (ROM 2430, parameters 0x3A6AC, 0x3A6B6, 0x3A6C0) on the error C2E4 − C216. Output inverted by curve 0x3A7C4 (100 % − x). Modes in C9D8 substitute a fixed duty from the block at 0x3A68A. Deviation monitoring in window 0x3DB48 — path 0x1E (P0400). | EGR valve duty |

## Start of injection (to the VP44 over CAN)

| Task | What it does | Output |
| --- | --- | --- |
| 0x2C544 | Cold start: 0x3CFA4 (rpm, fuel) × coolant weight 0x3CEFC. Altitude: 0x3D09C × atmospheric pressure weight 0x3CF50. The sum is limited by 0x3D102 (16.00), plus a limited C210. | C20E |
| 0x1854C | Base 0x3CD00 (rpm, fuel) + temperature correction 0x3CDF8 (rpm, C242) + 0x3CC08, C20E and offset 0x3CB4E. Limited via ROM 2756. Second channel (0x3CB54, 0x3CBA2) is zero in stock. | C214 → C252, C212 → C250 |

Role confirmed: the value goes into the pump message next to the fuel quantity. Units not confirmed.

## Fault paths related to these chains

| Path | P-code | Enable flag | Set by | Monitors |
| --- | --- | --- | --- | --- |
| 0x1E | P0400 | 0x3AFEE = 1 | 0x1EBB6 | EGR loop air mass deviation |
| 0x1D | P1125 | 0x3B0FE = 1 | 0x1F6B8 | underboost (bit 4), overboost (bit 5) |
| 0x0B | P0100 | 0x3AE96 = 1 | 0x15C84 etc. | MAF |
| 0x09 | P0105 | 0x3AE2E = 1 | 0x1F2AC etc. | pressure sensor |
| 0x05 | P0115 | 0x3AD1E = 1 | 0x1C55A etc. | coolant sensor |
| 0x3D | — | — | 0x22240 | checks inside the fuel limiter |

Path 0x1E → P0400 → 0x3AFEE has been confirmed in practice. The other mappings were built the same way but not verified individually.
