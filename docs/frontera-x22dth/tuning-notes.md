# Tuning notes

Practical findings from Stage 1 and EGR off on this ECU: what worked and what turned out to be wrong. No specific values or ready-made files are given here. The vehicle this was done on is not used on public roads.

## What actually limits power

- **Boost is capped by the constant 0x3C3AA = 2100 mbar.** Task 0x160C4 takes min(setpoint, [0x3C3AA]). Raising only the boost map 0x3C496 does nothing above 2100.
- **Boost deviation monitoring** (path 0x1D, P1125): underboost above 250 mbar or overboost above 150 mbar. If the setpoint is raised beyond what the turbo can actually deliver, the ECU goes into limp mode.
- **The active fuel limiters are 0x3BB40 and 0x3BA70** (Titanium: “Injection at part throttle” and “Torque limiter 2”). The copies 0x3B55A (“Injection ext”) and 0x3B8EA (“Torque limiter 1”) are blended in only with a factor from curve 0x3B926, which is 0 in stock. Editing only the copies has no effect on fuelling.

## Common mistakes

- **0x3CD30 is not a boost limiter.** It is the start-of-injection request for the VP44. Do not edit it as a limiter.
- **0x3C8A2 is not a fuel limiter.** It is the boost valve pilot duty.
- **0x3A308** is, according to the code, the EGR air-mass setpoint; Titanium calls it “Phase of injection”. While its role is disputed, better leave it alone.
- **0x39684** (8×5, rpm × coolant, read by coordinator 0x2327C) is not EGR, although it looks like it.
- **The area 0x3A440–0x3A4D2** is not read by any visible code. Its contents are unknown; do not write there.

## EGR: valve permanently closed in software

Where a blanking plate cannot be fitted, the valve can be kept closed by the code.

| Address | Meaning |
| --- | --- |
| 0x3A68A | rpm threshold for mode 9 (controller off, fixed duty on the valve) |
| 0x3A698 | duty in “closed” modes, 1.00 % in stock |
| 0x3A680 / 0x3A682 | air mass deviation threshold for P0400 |
| 0x3AFEE | enable flag for path 0x1E (P0400) |
| 0x3B510 | fault mask → limp mode (bit 14 — EGR, bit 15 — boost) |

1 % means “closed”: the controller inverts its output as 100 % − x. EGR monitoring runs only in modes 0 and 3 and is skipped in mode 9. Do not unplug the valve connector: an open circuit sets electrical faults on the same path 0x1E.

## Limp mode

If an active fault remains after mask 0x3B510, task 0x22240 smoothly lowers the fuel limit to the limp-mode curves (0x3BDE8, 0x3BD80: about 30 mg up to 2500–3000 rpm, dropping to 0 by 3500–4000), and the boost controller applies a fixed 30 % (0x3C3B2).

Symptom: drives as if on 30 mg and will not rev past ~3500 rpm.

## After flashing

- Mechanical boost gauge: a peak above 2100 mbar means the 0x3C3AA change works.
- Smoke at full load: roll back 0x3BB40 first.
- Scan for faults after 20–30 minutes of driving, especially P0100.

## When flashing is expensive

On this ECU each flash may require resoldering the EEPROM, so there is no quick rollback. Therefore:

1. Compare the final file with stock in the editor (show changed maps only).
2. Verify the checksum in the editor.
3. Cross-check the changed cells in another tool.
