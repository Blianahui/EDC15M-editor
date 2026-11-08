# Map definitions

One JSON file per “ECU part number + software version”. Naming: `<vehicle>_<ecu>_<software>.json`.

| File | ECU | Software |
| --- | --- | --- |
| `frontera_defs.json` | Bosch 0281001791 (EDC15M) | UU2M6S90_S |
| `terrano_0281001550_defs.json` | Bosch 0281001550 (EDC MSA 15.5) | 1037356022 |

Definitions contain only map addresses, sizes, axes, units and roles, plus checksum parameters (the `ck` block). They do not and must not contain map values.

To add definitions for your ECU, see [CONTRIBUTING.md](../CONTRIBUTING.md).
