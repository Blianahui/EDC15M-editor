"""Self-test: opcode coverage vs keyhana c166.sinc opcode list + BFLD byte order check on a decoded image."""
import sys,re; sys.path.insert(0,__file__.rsplit('/',1)[0]); import c166
SLEIGH_UNDEF={0x3B,0x44,0x45,0x83,0x85,0x8B,0x8C,0x93,0x95,0xA3,0xB3,0xC1,0xC3,0xC7,0xD3,0xE3,0xE5,0xF5,0xF8,0xF9}
SPECIAL={0x87,0x97,0xA5,0xA7,0xB5,0xB7}   # only valid as exact 4-byte EINIT/IDLE/PWRDN/DISWDT/SRVWDT/SRST
undef=set()
for op in range(256):
    ok=any(c166.decode(bytes([op,b1])+t,0) for b1 in range(256) for t in (b'\x00\x00',b'\x00\x10',b'\xcc\xcc'))
    if not ok: undef.add(op)
assert undef-SPECIAL==SLEIGH_UNDEF, (sorted(undef-SPECIAL-SLEIGH_UNDEF), sorted(SLEIGH_UNDEF-undef))
for b,mn in ((b'\xb5\x4a\xb5\xb5','einit'),(b'\xa7\x58\xa7\xa7','srvwdt'),(b'\xcb\x00','ret'),(b'\xdb\x00','rets'),(b'\xfb\x88','reti')):
    assert c166.decode(b,0).mn==mn
i=c166.decode(bytes.fromhex('da00d620'),0); assert i.mn=='calls' and i.tgt==0x20D6
i=c166.decode(bytes.fromhex('0aaaf010'),0); assert i.ops=='CCM1, #F0h, #10h'   # BFLDL: mask=byte2, data=byte3
i=c166.decode(bytes.fromhex('1a880102'),0); assert i.ops.endswith('#02h, #01h')  # BFLDH: data=byte2, mask=byte3
print('c166 decoder self-test OK')
