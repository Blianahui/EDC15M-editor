# Maps

Addresses are file offsets. “Header” is the start of the map description (axes), “Data” is the first value cell. ECM Titanium usually shows the data address, sometimes one word earlier.

Units: fuel 0.01 mg/stroke, air mass 0.1 mg/stroke, pressure in mbar absolute, temperatures in 0.1 K (2731 = 0 °C). Map values are not listed here.

## Key maps for Stage 1

| Data | Header | Titanium | What it is according to the code |
| --- | --- | --- | --- |
| 0x3BA70 | 0x3BA44 | Torque limiter 2 | fuel limit vs rpm, **active copy** |
| 0x3B8EA | 0x3B8BE | Torque limiter 1 | second copy, blended with factor 0 — no effect on fuelling |
| 0x3BB40 | 0x3BB14 | Injection at part throttle | **active smoke limiter**: rpm × air mass |
| 0x3B55A | 0x3B52E | Injection ext | smoke limiter copy, factor from 0x3B926 (0 in stock) — no effect on fuelling |
| 0x3C496 | 0x3C46E | Turbo pressure | boost setpoint, 9×7 |
| 0x3C3AA | — | — | boost setpoint ceiling (constant), 2100 mbar in stock |
| 0x398B8 | 0x39886 | Driver's wish | fuel vs pedal, 13×8 |
| 0x3CD30 | 0x3CD00 | — | VP44 start-of-injection request — **not a limiter** |
| 0x3C8A2 | 0x3C876 | — | boost valve pilot duty |
| 0x3A308 | 0x3A2CE | Phase of injection | per the code, EGR air-mass setpoint; disputed, leave alone |
| 0x39684 | 0x39662 | — | 8×5 rpm × coolant, fuel coordinator; not EGR |

## All maps read by the code

Confidence: **H** — role visible from code and values, **M** — from inputs and outputs, **L** — a guess. Axes are monitoring variables (see [memory-and-code.md](memory-and-code.md)). Tasks are the code entry points that read the map.

| Header | Data | Type | Size | X axis | Y axis | Role | Conf. | Tasks |
|---|---|---|---|---|---|---|---|---|
| 0x391DA | 0x391E2 | 1D | 2×1 | DC5C | — | Curve f(DC5C) | L | 2327C 2329C |
| 0x39512 | 0x3953A | 2D | 8×8 | E08A | E23C | Idle controller / torque map = f(rpm, E23C) | L | 2327C 2329C |
| 0x395BA | 0x395E2 | 2D | 8×8 | E08A | E238 | Likely: fuel → torque = f(rpm, fuel) | M | 2327C 2329C |
| 0x39662 | 0x39684 | 2D | 8×5 | E08A | C002 | Likely: friction torque = f(rpm, coolant) | M | 2327C 2329C |
| 0x396D4 | 0x39706 | 2D | 13×8 | E08A | E240 | Likely: torque ↔ fuel conversion | L | 2327C 2329C |
| 0x397F0 | 0x397FE | 1D | 5×1 | C206 | — | Curve f(C206) (2.50) | L | 2327C 2329C |
| 0x39808 | 0x39816 | 1D | 5×1 | DC98 | — | Curve f(DC98) (1.0) | L | 2327C 2329C |
| 0x39886 | 0x398B8 | 2D | 13×8 | E08A | C1CC | Driver demand: fuel = f(rpm, pedal %)  [Titanium: Fuel during acceleration] | H | 25F98 25FB6 2605C 2615C 26192 261C2 26352 2637E 263AA |
| 0x39C94 | 0x39C9C | 1D | 2×1 | E08A | — | Constant curve 5100 rpm | L | 26B90 26BA6 |
| 0x39F6C | 0x39F7A | 1D | 5×1 | DCC0 | — | — | M | 26B90 26BA6 |
| 0x39F84 | 0x39F92 | 1D | 5×1 | DCC0 | — | — | M | 26B90 26BA6 |
| 0x39F9C | 0x39FAA | 1D | 5×1 | DCC0 | — | — | M | 26B90 26BA6 |
| 0x39FB4 | 0x39FC2 | 1D | 5×1 | DCC0 | — | — | M | 26B90 26BA6 |
| 0x39FCC | 0x39FDA | 1D | 5×1 | DCC0 | — | — | M | 26B90 26BA6 |
| 0x39FE4 | 0x39FF2 | 1D | 5×1 | DCC0 | — | — | M | 26B90 26BA6 |
| 0x39FFC | 0x3A018 | 2D | 5×5 | DCC0 | DCC2 | — | M | 26B90 26BA6 |
| 0x3A04A | 0x3A066 | 2D | 5×5 | DCC0 | DCC2 | — | M | 26B90 26BA6 |
| 0x3A098 | 0x3A0B4 | 2D | 5×5 | DCC0 | DCC2 | — | M | 26B90 26BA6 |
| 0x3A0E6 | 0x3A102 | 2D | 5×5 | DCC0 | DCC2 | — | M | 26B90 26BA6 |
| 0x3A134 | 0x3A150 | 2D | 5×5 | DCC0 | DCC2 | — | M | 26B90 26BA6 |
| 0x3A182 | 0x3A19E | 2D | 5×5 | DCC0 | DCC2 | — | M | 26B90 26BA6 |
| 0x3A2CE | 0x3A308 | 2D | 13×12 | E08A | DD40 | EGR air mass setpoint = f(rpm, fuel), 0.1 mg/stroke  [Titanium: Phase of injection — label is wrong] | H | 1E772 1E78A |
| 0x3A4D4 | 0x3A4E0 | 1D | 4×1 | C21E | — | EGR setpoint correction for atm. pressure | H | 1E772 1E78A |
| 0x3A528 | 0x3A538 | 2D | 2×2 | E08A | C004 | EGR setpoint factor = f(rpm, temperature) | M | 1E772 1E78A |
| 0x3A5D0 | 0x3A5F2 | 2D | 5×8 | E08A | C002 | EGR setpoint offset = f(rpm, coolant): EGR closed when cold | H | 1E772 1E78A |
| 0x3A6C4 | 0x3A6D4 | 2D | 2×2 | C220 | C21E | Substitute air mass value | L | 15C84 |
| 0x3A6DC | 0x3A6FC | 2D | 6×6 | DD54 | DD52 | Substitute air mass value 2 | L | 15C84 |
| 0x3A744 | 0x3A754 | 2D | 2×2 | C004 | C21E | MAF correction = f(T, atm.) (1.0) | M | 15C84 |
| 0x3A75C | 0x3A778 | 1D | 12×1 | DD50 | — | MAF characteristic (raw → flow) | H | 15C84 |
| 0x3A7C4 | 0x3A7CC | 1D | 2×1 | DD5A | — | EGR duty inversion: 100 % − x | H | 1EBB6 1EBD0 |
| 0x3A7D0 | 0x3A7EC | 2D | 6×4 | FC3A | DD40 | Boost deviation weight for EGR (0) | M | 1E772 1E78A |
| 0x3A81C | 0x3A844 | 2D | 9×7 | FC3A | FC36 | Reference boost for EGR (0) | M | 1E772 1E78A |
| 0x3A8C2 | 0x3A8CE | 1D | 4×1 | DE14 | — | Boost deviation curve for EGR (0) | M | 1E772 1E78A |
| 0x3B3EC | 0x3B404 | 1D | 10×1 | C002 | — | Start related = f(coolant) | L | 2574A 25B8A |
| 0x3B418 | 0x3B442 | 2D | 8×9 | E08A | C002 | Start fuel = f(rpm, coolant) | M | 257E4 257FC |
| 0x3B4D2 | 0x3B4DA | 1D | 2×1 | C002 | — | Start related = f(coolant) | L | 257E4 257FC |
| 0x3B52E | 0x3B55A | 2D | 10×8 | E08A | C216 | Smoke limiter “ext” = f(rpm, air), blended with factor 0x3B926 (=0)  [Titanium: Injection ext] | H | 22240 22260 |
| 0x3B6F6 | 0x3B706 | 2D | 2×2 | E08A | C218 | Substitute ext limiter when MAF implausible (0) | M | 22240 22260 |
| 0x3B8BE | 0x3B8EA | 1D | 20×1 | E08A | — | Torque limiter “ext”, blended with factor 0x3B926 (=0)  [Titanium: Torque limiter 1] | H | 22240 22260 |
| 0x3B926 | 0x3B948 | 1D | 15×1 | C2E0 | — | Blend factor for ext limiters = f(C118), all 0 in stock | H | 22240 22260 |
| 0x3B966 | 0x3B992 | 2D | 8×10 | E08A | C002 | Fuel limit correction = f(rpm, coolant) | M | 22240 22260 |
| 0x3BA44 | 0x3BA70 | 1D | 20×1 | E08A | — | Torque limiter (fuel vs rpm), ACTIVE copy  [Titanium: Torque limiter 2] | H | 22240 22260 |
| 0x3BAAC | 0x3BAB8 | 1D | 4×1 | E08A | — | Limp-mode torque limiter (30 mg): pedal/sensor fault | H | 22240 22260 |
| 0x3BB14 | 0x3BB40 | 2D | 10×8 | E08A | C216 | Smoke limiter = f(rpm, air mass), ACTIVE copy  [Titanium: Injection at part throttle] | H | 220EC 22240 22260 |
| 0x3BC22 | 0x3BC32 | 2D | 2×2 | E08A | C218 | Substitute smoke limiter when MAF implausible (60 mg) | H | 220EC 22240 22260 |
| 0x3BC3A | 0x3BC5A | 2D | 6×6 | DCA6 | C2B0 | Over-temperature fuel derating = f(coolant+offset, C2B0) | M | 22240 22260 |
| 0x3BCB0 | 0x3BCD0 | 2D | 6×6 | C006 | C2B0 | Over-temperature fuel derating = f(temperature C006, C2B0) | M | 22240 22260 |
| 0x3BD80 | 0x3BD92 | 1D | 7×1 | E08A | — | Limp-mode fuel ceiling = f(rpm), set 1 | M | 22240 22260 |
| 0x3BDE8 | 0x3BDFA | 1D | 7×1 | E08A | — | Limp-mode fuel ceiling = f(rpm), set 2 | M | 22240 22260 |
| 0x3BE50 | 0x3BE58 | 1D | 2×1 | C21E | — | Atm. pressure offset for over-temperature protection (0) | M | 22240 22260 |
| 0x3BE90 | 0x3BEA8 | 2D | 4×4 | E08A | FC36 | Fuel derating = f(rpm, fuel) × (C242 − threshold)/4096 (temperature) | M | 22240 22260 |
| 0x3C21C | 0x3C238 | 2D | 5×5 | C002 | C004 | Likely idle speed setpoint = f(coolant, air temperature) | M | 35516 355B6 |
| 0x3C292 | 0x3C29E | 1D | 4×1 | C01A | — | Idle setpoint correction = f(C01A) | M | 355B6 |
| 0x3C2A6 | 0x3C2B8 | 1D | 7×1 | C002 | — | Coolant curve 40.8…8.0 (idle/start?) | L | 24C98 24CB8 |
| 0x3C2FA | 0x3C308 | 1D | 5×1 | E034 | — | Idle related = f(E034) (0) | L | 355B6 |
| 0x3C3FC | 0x3C41E | 2D | 8×5 | E08A | DDC4 | Boost pressure related = f(rpm, DDC4) | L | 1F2AC 1F2C6 |
| 0x3C46E | 0x3C496 | 2D | 9×7 | E08A | DD94 | Boost setpoint, base = f(rpm, fuel)  [Titanium: Turbo pressure] | H | 160C4 160E4 |
| 0x3C524 | 0x3C548 | 2D | 8×6 | FC3A | DD94 | Altitude boost setpoint reduction = f(rpm, fuel) | H | 160C4 160E4 |
| 0x3C5A8 | 0x3C5C0 | 1D | 10×1 | C21E | — | Weight of 0x3C524 = f(atm. pressure) | H | 160C4 160E4 |
| 0x3C5D4 | 0x3C614 | 2D | 14×14 | E08A | C21E | Boost offset = f(rpm, atm.) × C1D8 (zeros) | M | 160C4 160E4 |
| 0x3C79C | 0x3C7A4 | 1D | 2×1 | C004 | — | Boost setpoint factor = f(temperature) (1.0) | M | 160C4 160E4 |
| 0x3C7E0 | 0x3C806 | 2D | 8×7 | E08A | DD98 | Boost duty limit/linearisation | M | 1F6B8 1F6D8 |
| 0x3C876 | 0x3C8A2 | 2D | 10×8 | E08A | DDAA | Boost valve pilot duty = f(rpm, fuel), 0.01 % | H | 1F6B8 1F6D8 |
| 0x3CB54 | 0x3CB64 | 2D | 2×2 | E08A | FC36 | Timing, channel 2 = f(rpm, fuel) (0) | M | 1854C 1856A |
| 0x3CBA2 | 0x3CBB2 | 2D | 2×2 | E08A | FC36 | Timing, channel 2, part = f(rpm, fuel) (0) | M | 1854C 1856A |
| 0x3CBF0 | 0x3CBFE | 1D | 5×1 | C002 | — | Weight of 0x3CBA2 = f(coolant) (0) | M | 1854C 1856A |
| 0x3CC08 | 0x3CC34 | 2D | 10×8 | E08A | C212 | Timing offset = f(rpm, channel 2) (0) | M | 1854C 1856A |
| 0x3CD00 | 0x3CD30 | 2D | 10×10 | E08A | FC36 | VP44 start-of-injection request = f(rpm, fuel) | H | 1854C 1856A |
| 0x3CDF8 | 0x3CE28 | 2D | 10×10 | E08A | C242 | Timing correction = f(rpm, temperature C242) | M | 1854C 1856A |
| 0x3CEFC | 0x3CF12 | 1D | 9×1 | C20C | — | Weight of 0x3CFA4 = f(coolant) | M | 2C544 2C55A |
| 0x3CF50 | 0x3CF58 | 1D | 2×1 | C21E | — | Weight of 0x3D09C = f(atm. pressure) | M | 2C544 2C55A |
| 0x3CFA4 | 0x3CFD4 | 2D | 10×10 | E08A | FC36 | Cold start timing advance = f(rpm, fuel) | M | 2C544 2C55A |
| 0x3D09C | 0x3D0BA | 2D | 4×7 | E08A | FC36 | Altitude timing advance = f(rpm, fuel) | M | 2C544 2C55A |
| 0x3D102 | 0x3D112 | 2D | 2×2 | E08A | C20C | Ceiling for summed timing corrections (16.00) | M | 2C544 2C55A |
| 0x3D3E0 | 0x3D3FC | 2D | 6×4 | FC3A | FC36 | Timing correction = f(rpm, fuel) (0) | M | 2C544 2C55A |
| 0x3D42C | 0x3D448 | 2D | 6×4 | FC3A | C1EC | Timing correction = f(rpm, fuel) (0) | M | 2C544 2C55A |
| 0x3D478 | 0x3D484 | 1D | 4×1 | DE30 | — | Weighting curve (0) | M | 2C544 2C55A |
| 0x3D48C | 0x3D498 | 1D | 4×1 | DE3A | — | Weighting curve (0) | M | 2C544 2C55A |
| 0x3D720 | 0x3D72C | 1D | 4×1 | C002 | — | Post-start glow time = f(coolant)? | M | 36AAC 36ABE |
| 0x3D774 | 0x3D78C | 1D | 10×1 | C002 | — | Glow time = f(coolant)? | M | 36AAC 36ABE |
| 0x3D7A0 | 0x3D7B4 | 2D | 2×4 | C01A | C002 | Glow = f(voltage?, coolant)? | L | 36AAC 36ABE |
| 0x3D7C4 | 0x3D7D4 | 2D | 2×2 | E08A | FC36 | Glow (0) | L | 36AAC 36ABE |
| 0x3D7DC | 0x3D804 | 2D | 8×8 | C004 | C002 | Glow f(T, coolant) (0) | L | 36AAC 36ABE |
| 0x3D884 | 0x3D8AC | 2D | 8×8 | E08A | FC36 | Glow f(rpm, fuel) (0) | L | 36AAC 36ABE |
| 0x3D936 | 0x3D956 | 2D | 6×6 | E08A | FC36 | rpm × fuel window 0/65.00 → C050 | L | 15ADC |
| 0x3DA70 | 0x3DA7E | 1D | 5×1 | C002 | — | Coolant curve (0) | L | 24012 24028 |
| 0x3DA88 | 0x3DA96 | 1D | 5×1 | C002 | — | Coolant curve 0…100 % (fan?) | L | 35112 35124 3513E |
| 0x3DAE0 | 0x3DB00 | 2D | 6×6 | FC3A | FC36 | Boost deviation monitoring window = f(rpm, fuel) | H | 1F6B8 1F6D8 |
| 0x3DB48 | 0x3DB68 | 2D | 6×6 | FC3A | FC36 | EGR/air mass monitoring window = f(rpm, fuel) → P0400 | H | 1EBB6 1EBD0 |
| 0x3DBEC | 0x3DC04 | 2D | 4×4 | FC3A | FC36 | Plausibility window = f(rpm, fuel) | L | 33294 332A6 332C0 |
| 0x3DC70 | 0x3DC78 | 1D | 2×1 | DC26 | — | Linear scaling f(DC26) | L | 20000 20004 |
| 0x3DDBA | 0x3DDCE | 1D | 8×1 | C004 | — | Substitute temperature f(C004) | L | 373B4 373C6 373E0 |
