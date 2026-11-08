# Contributing

By contributing you agree that your contribution is released under the project license, [GPL-3.0](LICENSE).

## Welcome

- New or corrected map definitions in `defs/` for any EDC15 ECU.
- Address confirmations: which software version and how it was checked (code, WinOLS, Titanium, dyno).
- Fixes to the editor and scripts.
- Documentation: code analysis, calculation chains, fault paths.

## Not accepted

- Firmware dumps, stock or modified, in any form: binary, hex text, archive.
- Full map values copied from a dump.
- EEPROM dumps, immobilizer codes, VINs, ways to disable the immobilizer.
- Files and definitions taken from commercial tools (Titanium drivers, WinOLS damos, etc.).

## Describing a map

For each map, give:

- header address and data address (file offset, from 0);
- type (1D / 2D) and size;
- what is on the axes and in which units;
- the role and how it is known: **H** — visible from code and values, **M** — from inputs and outputs, **L** — a guess;
- the Bosch part number and software version it was checked on.

## How to submit

1. Fork the repository.
2. Make your changes on a separate branch.
3. Open a pull request with a short description: what changed and how it was verified.

Questions and findings without code are welcome as issues.
