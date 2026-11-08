# Checksum

After any calibration change the checksum must be recalculated, otherwise the ECU will not start. The editor does this with its recalculate-checksum button.

| Parameter | Value |
| --- | --- |
| Family | “family 1 / TROIA” (as named in ECM Titanium) |
| Block detection | by the marker `55 55 00 00 56 56`; fallback — fixed bounds |
| Range | 0x38B80–0x3FFFB |
| Stored at | 0x3FFFC, 4 bytes: word A, word B |
| Constants | seeds and constants 0x8631 / 0xEFCD |

Algorithm details:

- the carry comes from the rotation of word A;
- at the end, A is adjusted by a constant;
- B is XORed with `rol(0xEFCD, 1)`.

The implementation is in the editor source (`editor/`).

The same algorithm is used by the Terrano 0281001550 (one block per dataset), see [docs/terrano](../terrano/README.md).

## Verification

The algorithm was tested on the stock file and on several “before / after Titanium re-save” pairs: results matched byte for byte. Example: a file with modified calibration and the old checksum got `7DD3 0E46` after recalculation, and the saved file was byte-identical to the one re-saved by Titanium.

## The Galletto “checksum” is not this

Galletto 1260 shows a simple 16-bit sum of all bytes in the file. It is not the ECU checksum and says nothing about whether the file is correct.
