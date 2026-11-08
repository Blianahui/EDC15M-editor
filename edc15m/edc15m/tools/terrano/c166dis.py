"""C166/C167 disassembler (table checked against Infineon C166 Family Instruction Set Manual, ed. 2001-03).

decode(buf, off, pc) -> Insn or None
Insn fields: pc, size, mnem, ops (text), kind ('jmp','call','ret','cjmp','ext',''), targets (list of
(type, value)), mem (list of (access, raw16, is_byte)), ext (extension info for EXTP/EXTS/EXTR/ATOMIC)
"""
import struct

CC = ['cc_UC', 'cc_NET', 'cc_Z', 'cc_NZ', 'cc_V', 'cc_NV', 'cc_N', 'cc_NN',
      'cc_C', 'cc_NC', 'cc_SGT', 'cc_SLE', 'cc_SLT', 'cc_SGE', 'cc_UGT', 'cc_ULE']
# JMPR opcode high nibble -> condition (xD rr)
JMPR_CC = {0x0: 'cc_UC', 0x1: 'cc_NET', 0x2: 'cc_Z', 0x3: 'cc_NZ', 0x4: 'cc_V', 0x5: 'cc_NV', 0x6: 'cc_N',
           0x7: 'cc_NN', 0x8: 'cc_C', 0x9: 'cc_NC', 0xA: 'cc_SGT', 0xB: 'cc_SLE', 0xC: 'cc_SLT', 0xD: 'cc_SGE',
           0xE: 'cc_UGT', 0xF: 'cc_ULE'}

SFR = {  # word SFR address -> name (C167CR/CS subset most used in EDC15)
    0xFE00: 'DPP0', 0xFE02: 'DPP1', 0xFE04: 'DPP2', 0xFE06: 'DPP3', 0xFE08: 'CSP', 0xFE0C: 'MDH', 0xFE0E: 'MDL',
    0xFE10: 'CP', 0xFE12: 'SP', 0xFE14: 'STKOV', 0xFE16: 'STKUN', 0xFE18: 'ADDRSEL1', 0xFE1A: 'ADDRSEL2',
    0xFE1C: 'ADDRSEL3', 0xFE1E: 'ADDRSEL4', 0xFE40: 'T2', 0xFE42: 'T3', 0xFE44: 'T4', 0xFE46: 'T5', 0xFE48: 'T6',
    0xFE4A: 'CAPREL', 0xFE50: 'T0', 0xFE52: 'T1', 0xFE54: 'T0REL', 0xFE56: 'T1REL', 0xFE80: 'CC0', 0xFEA0: 'ADDAT',
    0xFEB0: 'S0TBUF', 0xFEB2: 'S0RBUF', 0xFEB4: 'S0BG', 0xFF0C: 'MDC', 0xFF0E: 'PSW', 0xFF10: 'SYSCON',
    0xFF12: 'BUSCON0', 0xFF14: 'BUSCON1', 0xFF16: 'BUSCON2', 0xFF18: 'BUSCON3', 0xFF1A: 'BUSCON4',
    0xFF1C: 'ZEROS', 0xFF1E: 'ONES', 0xFF40: 'T2CON', 0xFF42: 'T3CON', 0xFF44: 'T4CON', 0xFF46: 'T5CON',
    0xFF48: 'T6CON', 0xFF50: 'T01CON', 0xFF98: 'ADCIC', 0xFFA0: 'ADCON', 0xFFAC: 'TFR', 0xFFAE: 'WDTCON',
    0xFFB0: 'S0CON', 0xFFC0: 'P0L', 0xFFC2: 'P0H', 0xFFC4: 'P1L', 0xFFC6: 'P1H', 0xFFC8: 'DP0L',
    0xFFCA: 'DP0H', 0xFFCC: 'DP1L', 0xFFCE: 'DP1H', 0xFFD0: 'P2', 0xFFD2: 'DP2', 0xFFD4: 'P3', 0xFFD6: 'DP3',
    0xFFD8: 'P4', 0xFFDA: 'DP4', 0xFFDE: 'S0TBIC'[:0] or 'P6', 0xFFE0: 'P6', 0xFFE2: 'DP6', 0xFFE4: 'P7',
    0xFFE6: 'DP7', 0xFFE8: 'P8', 0xFFEA: 'DP8', 0xFF6C: 'S0TIC', 0xFF6E: 'S0RIC', 0xFF70: 'S0EIC',
    0xFF60: 'T2IC', 0xFF62: 'T3IC', 0xFF64: 'T4IC', 0xFF66: 'T5IC', 0xFF68: 'T6IC', 0xFF6A: 'CRIC',
    0xFFA2: 'P5', 0xFFA4: 'P5DIDIS'[:0] or 'P5', 0xFF00: 'XP0IC'[:0] or 'SFR_FF00',
}


import json as _j, os as _o
try:
    for _k, _v in _j.load(open(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)), 'sfr_c167cs.json'))).items():
        SFR.setdefault(int(_k, 16), _v)
except Exception:
    pass


def gpr(n, byte=False):
    if byte:
        return ('RL%d' if n % 2 == 0 else 'RH%d') % (n // 2)
    return 'R%d' % n


def reg_name(rr, byte=False, extr=False):
    """8-bit 'reg' operand."""
    if rr >= 0xF0:
        return gpr(rr & 0xF, byte)
    base = 0xF000 if extr else 0xFE00
    a = base + 2 * rr
    nm = SFR.get(a)
    return nm if nm else ('ESFR_%04X' % a if extr else 'SFR_%04X' % a)


def bitoff_name(q, extr=False):
    if q < 0x80:
        return 'BRAM_%04X' % (0xFD00 + 2 * q), 0xFD00 + 2 * q
    if q < 0xF0:
        a = (0xF100 if extr else 0xFF00) + 2 * (q - 0x80)
        return (SFR.get(a) or 'SFR_%04X' % a), a
    return 'R%d' % (q & 0xF), None


class Insn:
    __slots__ = ('pc', 'size', 'mnem', 'ops', 'kind', 'targets', 'mem', 'ext', 'raw', 'cond', 'imm', 'regs')

    def __init__(s, pc, size, mnem, ops='', kind='', targets=None, mem=None, ext=None):
        s.pc, s.size, s.mnem, s.ops, s.kind = pc, size, mnem, ops, kind
        s.targets = targets or []
        s.mem = mem or []
        s.ext = ext
        s.raw = b''
        s.cond = None
        s.imm = None
        s.regs = None

    def __repr__(s):
        return '%06X  %-24s %-7s %s' % (s.pc, s.raw.hex(' '), s.mnem, s.ops)


# group ALU opcodes: base -> (mnem word, mnem byte)
ALU = {0x00: 'ADD', 0x10: 'ADDC', 0x20: 'SUB', 0x30: 'SUBC', 0x40: 'CMP', 0x50: 'XOR', 0x60: 'AND', 0x70: 'OR'}
BITOPS = {0x2A: 'BCMP', 0x3A: 'BMOVN', 0x4A: 'BMOV', 0x5A: 'BOR', 0x6A: 'BAND', 0x7A: 'BXOR'}
BJMP = {0x8A: 'JB', 0x9A: 'JNB', 0xAA: 'JBC', 0xBA: 'JNBS'}


def h16(v):
    return '#%04Xh' % v


def decode(buf, off, pc, extr=False):
    if off >= len(buf):
        return None
    op = buf[off]
    b1 = buf[off + 1] if off + 1 < len(buf) else 0
    if off + 4 <= len(buf):
        w = struct.unpack_from('<H', buf, off + 2)[0]
        b2, b3 = buf[off + 2], buf[off + 3]
    else:
        w = b2 = b3 = 0
    n, m = b1 >> 4, b1 & 0xF
    lo = op & 0x0F
    hi = op & 0xF0
    I = None

    # ---- ALU block 0x00-0x79 (cols 0..9 of rows 0..7) ----
    if hi <= 0x70 and lo <= 0x9 and not (hi == 0x40 and lo in (4, 5)):
        base = ALU[hi]
        byte = lo & 1
        mn = base + ('B' if byte else '')
        k = lo & 0xE
        if k == 0:
            I = Insn(pc, 2, mn, '%s, %s' % (gpr(n, byte), gpr(m, byte)))
        elif k == 2:
            I = Insn(pc, 4, mn, '%s, [%04Xh]' % (reg_name(b1, byte, extr), w), mem=[('r', w, byte)])
        elif k == 4:
            I = Insn(pc, 4, mn, '[%04Xh], %s' % (w, reg_name(b1, byte, extr)), mem=[('w', w, byte)])
        elif k == 6:
            if byte:
                I = Insn(pc, 4, mn, '%s, #%02Xh' % (reg_name(b1, 1, extr), b2))
                I.imm = b2
            else:
                I = Insn(pc, 4, mn, '%s, %s' % (reg_name(b1, 0, extr), h16(w)))
                I.imm = w
            I.regs = b1
        elif k == 8:
            if m & 0x8:
                inc = '+' if m & 0x4 else ''
                I = Insn(pc, 2, mn, '%s, [R%d%s]' % (gpr(n, byte), m & 3, inc))
            else:
                I = Insn(pc, 2, mn, '%s, #%d' % (gpr(n, byte), m & 7))
        if I:
            I.raw = bytes(buf[off:off + I.size])
            return I

    if lo == 0xD:  # JMPR cc, rel
        rel = b1 - 256 if b1 & 0x80 else b1
        t = (pc + 2 + 2 * rel) & 0xFFFFFF
        t = (pc & 0xFF0000) | (t & 0xFFFF)
        cc = JMPR_CC[op >> 4]
        I = Insn(pc, 2, 'JMPR', '%s, %06Xh' % (cc, t), 'jmp' if cc == 'cc_UC' else 'cjmp', [('code', t)])
        I.cond = cc
    elif lo == 0xE or lo == 0xF:  # BCLR / BSET bitoff.q
        nm, _ = bitoff_name(b1, extr)
        I = Insn(pc, 2, 'BCLR' if lo == 0xE else 'BSET', '%s.%d' % (nm, op >> 4))
    elif op in (0x0A, 0x1A):
        nm, _ = bitoff_name(b1, extr)
        if op == 0x0A:
            mask, data = b2, b3  # 0A QQ @@ ##
        else:
            data, mask = b2, b3  # 1A QQ ## @@  (manual)
        I = Insn(pc, 4, 'BFLDL' if op == 0x0A else 'BFLDH', '%s, #%02Xh, #%02Xh' % (nm, mask, data))
    elif op in (0x0B, 0x1B):
        I = Insn(pc, 2, 'MUL' if op == 0x0B else 'MULU', '%s, %s' % (gpr(n), gpr(m)))
    elif op in (0x0C, 0x2C, 0x4C, 0x6C, 0xAC):
        I = Insn(pc, 2, {0x0C: 'ROL', 0x2C: 'ROR', 0x4C: 'SHL', 0x6C: 'SHR', 0xAC: 'ASHR'}[op], '%s, %s' % (gpr(n), gpr(m)))
    elif op in (0x1C, 0x3C, 0x5C, 0x7C, 0xBC):
        I = Insn(pc, 2, {0x1C: 'ROL', 0x3C: 'ROR', 0x5C: 'SHL', 0x7C: 'SHR', 0xBC: 'ASHR'}[op], '%s, #%d' % (gpr(m), n))
    elif op in BITOPS:  # xA QQ ZZ qz : op1 = ZZ.z, op2 = QQ.q
        q, z = b3 >> 4, b3 & 0xF
        nq, _ = bitoff_name(b1, extr)
        nz, _ = bitoff_name(b2, extr)
        I = Insn(pc, 4, BITOPS[op], '%s.%d, %s.%d' % (nz, z, nq, q))
    elif op in BJMP:  # 8A QQ rr q0
        rel = b2 - 256 if b2 & 0x80 else b2
        t = (pc & 0xFF0000) | ((pc + 4 + 2 * rel) & 0xFFFF)
        nq, _ = bitoff_name(b1, extr)
        I = Insn(pc, 4, BJMP[op], '%s.%d, %06Xh' % (nq, b3 >> 4, t), 'cjmp', [('code', t)])
    elif op == 0x2B:
        I = Insn(pc, 2, 'PRIOR', '%s, %s' % (gpr(n), gpr(m)))
    elif op in (0x4B, 0x5B, 0x6B, 0x7B):
        I = Insn(pc, 2, {0x4B: 'DIV', 0x5B: 'DIVU', 0x6B: 'DIVL', 0x7B: 'DIVLU'}[op], gpr(n))
    elif op in (0x80, 0x90, 0xA0, 0xB0):
        I = Insn(pc, 2, {0x80: 'CMPI1', 0x90: 'CMPI2', 0xA0: 'CMPD1', 0xB0: 'CMPD2'}[op], '%s, #%d' % (gpr(m), n))
    elif op in (0x82, 0x92, 0xA2, 0xB2):
        I = Insn(pc, 4, {0x82: 'CMPI1', 0x92: 'CMPI2', 0xA2: 'CMPD1', 0xB2: 'CMPD2'}[op], '%s, [%04Xh]' % (gpr(m), w), mem=[('r', w, 0)])
    elif op in (0x86, 0x96, 0xA6, 0xB6):
        I = Insn(pc, 4, {0x86: 'CMPI1', 0x96: 'CMPI2', 0xA6: 'CMPD1', 0xB6: 'CMPD2'}[op], '%s, %s' % (gpr(m), h16(w)))
        I.imm = w
    elif op in (0x81, 0x91, 0xA1, 0xB1):
        byte = op in (0xA1, 0xB1)
        I = Insn(pc, 2, {0x81: 'NEG', 0x91: 'CPL', 0xA1: 'NEGB', 0xB1: 'CPLB'}[op], gpr(n, byte))
    elif op in (0x84, 0xA4):
        I = Insn(pc, 4, 'MOV' if op == 0x84 else 'MOVB', '[R%d], [%04Xh]' % (m, w), mem=[('r', w, op == 0xA4)])
    elif op in (0x94, 0xB4):
        I = Insn(pc, 4, 'MOV' if op == 0x94 else 'MOVB', '[%04Xh], [R%d]' % (w, m), mem=[('w', w, op == 0xB4)])
    elif op in (0x87, 0x97, 0xA5, 0xB5, 0xA7, 0xB7):
        I = Insn(pc, 4, {0x87: 'IDLE', 0x97: 'PWRDN', 0xA5: 'DISWDT', 0xB5: 'EINIT', 0xA7: 'SRVWDT', 0xB7: 'SRST'}[op])
    elif op in (0x88, 0x89):
        byte = op == 0x89
        I = Insn(pc, 2, 'MOVB' if byte else 'MOV', '[-R%d], %s' % (m, gpr(n, byte)))
    elif op in (0x98, 0x99):
        byte = op == 0x99
        I = Insn(pc, 2, 'MOVB' if byte else 'MOV', '%s, [R%d+]' % (gpr(n, byte), m))
    elif op in (0xA8, 0xA9):
        byte = op == 0xA9
        I = Insn(pc, 2, 'MOVB' if byte else 'MOV', '%s, [R%d]' % (gpr(n, byte), m))
    elif op in (0xB8, 0xB9):
        byte = op == 0xB9
        I = Insn(pc, 2, 'MOVB' if byte else 'MOV', '[R%d], %s' % (m, gpr(n, byte)))
    elif op in (0xC8, 0xC9, 0xD8, 0xD9, 0xE8, 0xE9):
        byte = op & 1
        f = {0xC8: '[R%d], [R%d]', 0xD8: '[R%d+], [R%d]', 0xE8: '[R%d], [R%d+]'}[op & 0xFE]
        I = Insn(pc, 2, 'MOVB' if byte else 'MOV', f % (n, m))
    elif op == 0x9B:
        I = Insn(pc, 2, 'TRAP', '#%02Xh' % (b1 >> 1), 'call')
    elif op == 0x9C:
        I = Insn(pc, 2, 'JMPI', '%s, [R%d]' % (CC[n], m), 'jmp' if n == 0 else 'cjmp', [('ind', m)])
        I.cond = CC[n]
    elif op == 0xAB:
        I = Insn(pc, 2, 'CALLI', '%s, [R%d]' % (CC[n], m), 'call', [('ind', m)])
    elif op == 0xBB:
        rel = b1 - 256 if b1 & 0x80 else b1
        t = (pc & 0xFF0000) | ((pc + 2 + 2 * rel) & 0xFFFF)
        I = Insn(pc, 2, 'CALLR', '%06Xh' % t, 'call', [('code', t)])
    elif op in (0xC0, 0xD0):  # MOVBZ/MOVBS Rw_n, Rb_m : C0 mn
        I = Insn(pc, 2, 'MOVBZ' if op == 0xC0 else 'MOVBS', '%s, %s' % (gpr(m), gpr(n, True)))
    elif op in (0xC2, 0xD2):
        I = Insn(pc, 4, 'MOVBZ' if op == 0xC2 else 'MOVBS', '%s, [%04Xh]' % (reg_name(b1, 0, extr), w), mem=[('r', w, 1)])
    elif op in (0xC5, 0xD5):
        I = Insn(pc, 4, 'MOVBZ' if op == 0xC5 else 'MOVBS', '[%04Xh], %s' % (w, reg_name(b1, 1, extr)), mem=[('w', w, 0)])
    elif op in (0xC4, 0xE4):
        byte = op == 0xE4
        I = Insn(pc, 4, 'MOVB' if byte else 'MOV', '[R%d+#%04Xh], %s' % (m, w, gpr(n, byte)))
        I.imm = w
    elif op in (0xD4, 0xF4):
        byte = op == 0xF4
        I = Insn(pc, 4, 'MOVB' if byte else 'MOV', '%s, [R%d+#%04Xh]' % (gpr(n, byte), m, w))
        I.imm = w
    elif op == 0xC6:
        I = Insn(pc, 4, 'SCXT', '%s, %s' % (reg_name(b1, 0, extr), h16(w)))
        I.imm = w
        I.regs = b1
    elif op == 0xD6:
        I = Insn(pc, 4, 'SCXT', '%s, [%04Xh]' % (reg_name(b1, 0, extr), w), mem=[('r', w, 0)])
    elif op == 0xCA:  # CALLA cc, caddr : CA c0 MM MM
        t = (pc & 0xFF0000) | w
        I = Insn(pc, 4, 'CALLA', '%s, %06Xh' % (CC[n], t), 'call', [('code', t)])
    elif op == 0xEA:
        t = (pc & 0xFF0000) | w
        I = Insn(pc, 4, 'JMPA', '%s, %06Xh' % (CC[n], t), 'jmp' if n == 0 else 'cjmp', [('code', t)])
        I.cond = CC[n]
    elif op == 0xDA:
        t = (b1 << 16) | w
        I = Insn(pc, 4, 'CALLS', '%02Xh, %04Xh' % (b1, w), 'call', [('code', t)])
    elif op == 0xFA:
        t = (b1 << 16) | w
        I = Insn(pc, 4, 'JMPS', '%02Xh, %04Xh' % (b1, w), 'jmp', [('code', t)])
    elif op == 0xE2:
        t = (pc & 0xFF0000) | w
        I = Insn(pc, 4, 'PCALL', '%s, %06Xh' % (reg_name(b1, 0, extr), t), 'call', [('code', t)])
    elif op == 0xCB:
        I = Insn(pc, 2, 'RET', '', 'ret')
    elif op == 0xDB:
        I = Insn(pc, 2, 'RETS', '', 'ret')
    elif op == 0xEB:
        I = Insn(pc, 2, 'RETP', reg_name(b1, 0, extr), 'ret')
    elif op == 0xFB:
        I = Insn(pc, 2, 'RETI', '', 'ret')
    elif op == 0xCC:
        I = Insn(pc, 2, 'NOP')
    elif op == 0xEC:
        I = Insn(pc, 2, 'PUSH', reg_name(b1, 0, extr))
    elif op == 0xFC:
        I = Insn(pc, 2, 'POP', reg_name(b1, 0, extr))
    elif op == 0xD1:  # ATOMIC / EXTR #irang2 : D1 :00##-0 / :10##-0
        cnt = ((b1 >> 4) & 3) + 1
        sub = b1 >> 6
        nm = {0: 'ATOMIC', 2: 'EXTR'}.get(sub)
        if nm and (b1 & 0xF) == 0:
            I = Insn(pc, 2, nm, '#%d' % cnt, 'ext', ext=(nm, None, cnt))
    elif op == 0xD7:  # EXTP/EXTS #pag/#seg
        cnt = ((b1 >> 4) & 3) + 1
        sub = b1 >> 6
        nm = ['EXTS', 'EXTP', 'EXTSR', 'EXTPR'][sub]
        if sub & 1:  # page
            pag = b2 | ((b3 & 3) << 8)
            I = Insn(pc, 4, nm, '#%03Xh, #%d' % (pag, cnt), 'ext', ext=(nm, ('page', pag), cnt))
        else:
            I = Insn(pc, 4, nm, '#%02Xh, #%d' % (b2, cnt), 'ext', ext=(nm, ('seg', b2), cnt))
    elif op == 0xDC:
        cnt = ((b1 >> 4) & 3) + 1
        sub = b1 >> 6
        nm = ['EXTS', 'EXTP', 'EXTSR', 'EXTPR'][sub]
        I = Insn(pc, 2, nm, 'R%d, #%d' % (m, cnt), 'ext', ext=(nm, ('reg', m), cnt))
    elif op in (0xE0, 0xE1):
        byte = op == 0xE1
        I = Insn(pc, 2, 'MOVB' if byte else 'MOV', '%s, #%d' % (gpr(m, byte), n))
        I.imm = n
    elif op in (0xF0, 0xF1):
        byte = op == 0xF1
        I = Insn(pc, 2, 'MOVB' if byte else 'MOV', '%s, %s' % (gpr(n, byte), gpr(m, byte)))
    elif op in (0xE6, 0xE7):
        byte = op == 0xE7
        v = b2 if byte else w
        I = Insn(pc, 4, 'MOVB' if byte else 'MOV', '%s, %s' % (reg_name(b1, byte, extr), ('#%02Xh' % v) if byte else h16(v)))
        I.imm = v
        I.regs = b1
    elif op in (0xF2, 0xF3):
        byte = op == 0xF3
        I = Insn(pc, 4, 'MOVB' if byte else 'MOV', '%s, [%04Xh]' % (reg_name(b1, byte, extr), w), mem=[('r', w, byte)])
        I.regs = b1
    elif op in (0xF6, 0xF7):
        byte = op == 0xF7
        I = Insn(pc, 4, 'MOVB' if byte else 'MOV', '[%04Xh], %s' % (w, reg_name(b1, byte, extr)), mem=[('w', w, byte)])
    if I is None:
        return None
    if off + I.size > len(buf):
        return None
    I.raw = bytes(buf[off:off + I.size])
    return I


# ---------------- self test against manual encodings ----------------
def _selftest():
    cases = [
        (b'\x00\x12', 'ADD', 'R1, R2'), (b'\x08\x1a', 'ADD', 'R1, [R2]'), (b'\x08\x1e', 'ADD', 'R1, [R2+]'),
        (b'\x08\x15', 'ADD', 'R1, #5'), (b'\x06\xf3\x34\x12', 'ADD', 'R3, #1234h'),
        (b'\x0a\x80\xf0\x30', 'BFLDL', 'SFR_FF00, #F0h, #30h'), (b'\x1a\x80\x30\xf0', 'BFLDH', 'SFR_FF00, #F0h, #30h'),
        (b'\x4a\x10\x20\x35', 'BMOV', 'BRAM_FD40.5, BRAM_FD20.3'), (b'\x8a\x10\x02\x30', 'JB', 'BRAM_FD20.3, 000108h'),
        (b'\xc0\x31', 'MOVBZ', 'R1, RH1'), (b'\xd4\x12\x00\x10', 'MOV', 'R1, [R2+#1000h]'),
        (b'\xd7\x40\x34\x00', 'EXTP', '#034h, #1'), (b'\xd7\x10\x0d\x00', 'EXTS', '#0Dh, #2'),
        (b'\xda\x09\x26\xd8', 'CALLS', '09h, D826h'), (b'\xe6\x00\x34\x00', 'MOV', 'DPP0, #0034h'),
        (b'\x2d\xfe', 'JMPR', 'cc_Z, 0000FEh'), (b'\x9b\x08', 'TRAP', '#04h'), (b'\xcb\x00', 'RET', ''),
    ]
    bad = 0
    for raw, mn, ops in cases:
        i = decode(raw, 0, 0x100)
        got = (i.mnem, i.ops) if i else None
        if got != (mn, ops):
            print('FAIL', raw.hex(), got, (mn, ops)); bad += 1
    # every defined opcode decodes, undefined ones don't
    undefined = {0x3B, 0x44, 0x45, 0x83, 0x85, 0x8B, 0x8C, 0x93, 0x95, 0xA3, 0xB3, 0xC1, 0xC3, 0xC7, 0xD3, 0xE3, 0xE5, 0xF5, 0xF8, 0xF9}
    for op in range(256):
        raw = bytes([op, 0x00, 0x00, 0x00])
        if op in (0x87,): raw = b'\x87\x78\x87\x87'
        i = decode(raw, 0, 0)
        if (i is None) != (op in undefined):
            print('opcode table mismatch %02X' % op, i); bad += 1
    print('selftest', 'OK' if not bad else '%d FAIL' % bad)


if __name__ == '__main__':
    _selftest()
