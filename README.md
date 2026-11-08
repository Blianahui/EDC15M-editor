# EDC15M — map editor and firmware analysis for Bosch EDC15

An open project around the Bosch EDC15 diesel ECUs of the early 2000s:

- **Map editor** that runs in the browser: open your own dump, edit maps, compare with stock, recalculate the checksum, save. Nothing to install and nothing is uploaded; everything runs locally.
- **Firmware analysis**: memory map, code structure, calculation chains (fuel, boost, EGR, injection timing), map list tied to the code, fault paths.

Website: **https://edc15m.pages.dev**

## Supported ECUs

| Vehicle | Engine | ECU | Software | Status |
| --- | --- | --- | --- | --- |
| Opel Frontera B | X22DTH 2.2 DTI | Bosch 0281001791, EDC15M, CPU Siemens B58748 (C167) | UU2M6S90_S | editor + full analysis |
| Nissan Terrano | 2.7 TDi | Bosch EDC15VM+, 29F400 flash | 1037362084 family | in progress, see [docs/terrano](docs/terrano/README.md) |

Addresses **do not carry over** between ECUs. Even neighbouring software versions place maps differently.

## Repository layout

```
index.html                 website landing page
editor/                    map editor (EDC15M_map_editor.html) and its definitions
defs/                      map definition files per ECU
research/                  interactive Frontera analysis page
docs/frontera-x22dth/      Frontera analysis as text
docs/terrano/              Terrano work
tools/                     analysis scripts (C166 disassembler etc.)
```

## Using the editor

1. Read the flash of your ECU (with a programmer or over K-line).
2. Open https://edc15m.pages.dev → “Map editor”.
3. Load your file as the main file and the stock file for comparison.
4. Edit the maps, recalculate the checksum, save the file.
5. Before flashing, cross-check the changed cells in another tool (WinOLS, ECM Titanium).

## What is not here and never will be

- **Firmware dumps** (stock or modified). They are the manufacturer’s code and calibration. Everyone reads the dump from their own ECU.
- **Map values.** Definitions contain only addresses, sizes, axes and roles.
- **Immobilizer data, EEPROM dumps** and ways to disable the immobilizer.

Pull requests containing such files will be closed.

## Contributing

Found a map, confirmed an address, have definitions for another software version? Open an issue or a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Disclaimer

This project is for research and for vehicles not used on public roads. Changing the calibration can damage the engine, the injection pump, the clutch or the ECU itself. Disabling emission controls on a road vehicle is illegal in many countries. Everything here is provided as is, without any warranty. Use at your own risk.

## License

[GNU General Public License v3.0](LICENSE). Copyright (C) 2026 edc15m contributors.

You may use, modify and redistribute this project, including commercially, as long as derivative works are released under the same license with their source code.

Bosch, Opel, Nissan, ECM Titanium, WinOLS and other names belong to their respective owners. This project is not affiliated with them.
