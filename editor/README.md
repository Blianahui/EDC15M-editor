# EDC15M map editor

A single HTML file that runs in the browser with no server and no internet connection. Map definitions for both supported ECUs are embedded into the file.

## Supported ECUs

| ECU | Definitions | Checksum |
| --- | --- | --- |
| Opel Frontera X22DTH, Bosch 0281001791 | 92 maps + key constants | recalculated |
| Nissan Terrano II 2.7 TDi, Bosch 0281001550 | 58 maps | recalculated (both datasets) |

When a dump is opened, the editor checks which set of definitions matches the map headers in the file and switches to it automatically. The ECU can also be chosen manually in the toolbar. Definitions you edit are stored in the browser separately for each ECU.

## Files

| File | Purpose |
| --- | --- |
| `EDC15M_map_editor.html` | the editor |
| `frontera_defs.json` | map definitions for Frontera X22DTH (0281001791, UU2M6S90_S) and checksum parameters |
| `terrano_0281001550_defs.json` | map definitions for Terrano II 2.7 TDi (0281001550, SW 1037356022): the 58 maps the code reads |

A copy of the definitions is kept in `defs/`.

## Features

- open your own dump plus a comparison file (stock), see both tables side by side with changed cells highlighted;
- edit values in physical units or as raw numbers, add / subtract buttons;
- undo up to 200 steps, Ctrl+Z;
- recalculate and verify the checksum (algorithm: [docs/frontera-x22dth/checksum.md](../docs/frontera-x22dth/checksum.md));
- export the list of changes as CSV;
- English / Russian interface.

## Workflow

1. Load your file as the main file and the stock file for comparison.
2. Edit the maps.
3. Recalculate the checksum.
4. Save the file.
5. Cross-check the changed cells in another tool before flashing.

## Language

The interface is available in English and Russian. Switch with the “Language / Язык” selector in the toolbar; the choice is remembered in the browser. By default the editor follows the browser language.

The source text of the interface is Russian; English is applied through a phrase table at the end of the file. When adding new interface text, add its translation to that table.
