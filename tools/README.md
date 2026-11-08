# Analysis tools

Pure Python 3 scripts, no dependencies. They read **your own** flash dump and produce an annotated listing and CSV files. No dumps are included.

| Folder | Target |
| --- | --- |
| [frontera/](frontera/README.md) | Opel Frontera B X22DTH, Bosch 0281001791 (EDC15M), SW UU2M6S90_S |
| [terrano/](terrano/README.md) | Nissan Terrano II 2.7 TDi: Bosch EDC15VM+ (SW 1037362084 / 1037362770) and Bosch 0281001550 (SW 1037356022), plus tools to compare two firmware versions |

Both sets contain a C166/C167 instruction decoder with a self-test, recursive-descent code analysis, map discovery through map headers and pointer tables, map ↔ code cross-references and listing export.

Common limitations: DPP registers are assumed constant, `jmpi` through jump tables is not resolved, and the CPU mask ROM is not in the dump, so ROM routines are visible only through their arguments and results.

Opcode reference: Infineon C166 Instruction Set Manual. The opcode table was cross-checked against the [keyhana/c166-ghidra-module](https://github.com/keyhana/c166-ghidra-module) SLEIGH specification.
