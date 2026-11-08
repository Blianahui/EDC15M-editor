"""C166/C167 instruction decoder (Infineon C166 Family ISM). Pure python, no deps."""
import struct
CC=['cc_UC','cc_NET','cc_Z','cc_NZ','cc_V','cc_NV','cc_N','cc_NN','cc_C','cc_NC','cc_SGT','cc_SLE','cc_SLT','cc_SGE','cc_UGT','cc_ULE']
SFR={0xFE00:'DPP0',0xFE02:'DPP1',0xFE04:'DPP2',0xFE06:'DPP3',0xFE08:'CSP',0xFE0C:'MDH',0xFE0E:'MDL',0xFE10:'CP',0xFE12:'SP',
0xFE14:'STKOV',0xFE16:'STKUN',0xFE18:'ADDRSEL1',0xFE1A:'ADDRSEL2',0xFE1C:'ADDRSEL3',0xFE1E:'ADDRSEL4',
0xFE30:'PW0',0xFE32:'PW1',0xFE34:'PW2',0xFE36:'PW3',0xFE40:'T2',0xFE42:'T3',0xFE44:'T4',0xFE46:'T5',0xFE48:'T6',0xFE4A:'CAPREL',
0xFE50:'T0',0xFE52:'T1',0xFE54:'T0REL',0xFE56:'T1REL',0xFEA0:'ADDAT',0xFEAE:'WDT',0xFEB0:'S0TBUF',0xFEB2:'S0RBUF',0xFEB4:'S0BG',
0xFF00:'P0L',0xFF02:'P0H',0xFF04:'P1L',0xFF06:'P1H',0xFF0C:'BUSCON0',0xFF0E:'MDC',0xFF10:'PSW',0xFF12:'SYSCON',0xFF14:'BUSCON1',
0xFF16:'BUSCON2',0xFF18:'BUSCON3',0xFF1A:'BUSCON4',0xFF1C:'ZEROS',0xFF1E:'ONES',0xFF20:'T78CON',0xFF22:'CCM4',0xFF24:'CCM5',
0xFF26:'CCM6',0xFF28:'CCM7',0xFF30:'PWMCON0',0xFF32:'PWMCON1',0xFF40:'T2CON',0xFF42:'T3CON',0xFF44:'T4CON',0xFF46:'T5CON',
0xFF48:'T6CON',0xFF50:'T01CON',0xFF52:'CCM0',0xFF54:'CCM1',0xFF56:'CCM2',0xFF58:'CCM3',0xFF60:'T2IC',0xFF62:'T3IC',0xFF64:'T4IC',
0xFF66:'T5IC',0xFF68:'T6IC',0xFF6A:'CRIC',0xFF6C:'S0TIC',0xFF6E:'S0RIC',0xFF70:'S0EIC',0xFF72:'SSCTIC',0xFF74:'SSCRIC',0xFF76:'SSCEIC',
0xFF98:'ADCIC',0xFF9A:'ADEIC',0xFF9C:'T0IC',0xFF9E:'T1IC',0xFFA0:'ADCON',0xFFA2:'P5',0xFFA4:'P5DIDIS',0xFFA8:'TFR',0xFFAA:'WDTCON',
0xFFAC:'S0CON',0xFFB2:'SSCCON',0xFFC0:'P2',0xFFC2:'DP2',0xFFC4:'P3',0xFFC6:'DP3',0xFFC8:'P4',0xFFCA:'DP4',0xFFCC:'P6',0xFFCE:'DP6',
0xFFD0:'P7',0xFFD2:'DP7',0xFFD4:'P8',0xFFD6:'DP8',0xFF0A:'SYSCON?',0xFEC0:'PECC0',0xFEC2:'PECC1',0xFEC4:'PECC2',0xFEC6:'PECC3',
0xFEC8:'PECC4',0xFECA:'PECC5',0xFECC:'PECC6',0xFECE:'PECC7',0xFF2A:'?',
# ESFR (EXTR)
0xF100:'DP0L',0xF102:'DP0H',0xF104:'DP1L',0xF106:'DP1H',0xF1C2:'ODP2',0xF1C6:'ODP3',0xF1CE:'ODP6',0xF1D2:'ODP7',0xF1D6:'ODP8',
0xF0B0:'SSCTB',0xF0B2:'SSCRB',0xF0B4:'SSCBR',0xF050:'T7',0xF052:'T8',0xF054:'T7REL',0xF056:'T8REL',0xF0A0:'ADDAT2',
0xF030:'PT0',0xF032:'PT1',0xF034:'PT2',0xF036:'PT3',0xF038:'PP0',0xF03A:'PP1',0xF03C:'PP2',0xF03E:'PP3',0xF186:'XP0IC',0xF18E:'XP1IC',
0xF196:'XP2IC',0xF19E:'XP3IC',0xF1C0:'EXICON',0xF1DA:'P5?',0xF1E8:'?',0xF0C2:'?',0xF1A0:'?'}
for i in range(16): SFR[0xFE80+2*i]='CC%d'%i; SFR[0xFF78+2*i]='CC%dIC'%i
for i in range(16): SFR[0xFE60+2*i]='CC%d'%(16+i); SFR[0xF160+2*i]='CC%dIC'%(16+i)
for i in range(8): SFR[0xFCE0+i*2]='PEC_SRC/DST?'
SFR[0xF0B6]='?';

def rw(n): return 'r%d'%n
def rb(n): return ('rl%d'%(n>>1)) if n%2==0 else ('rh%d'%(n>>1))

class Ins:
    __slots__=('ext','a','size','mn','ops','kind','tgt','mem','memw','imm','cc','text','raw','regs')
    def __init__(s,a): s.a=a; s.size=2; s.mn='?'; s.ops=''; s.kind=None; s.tgt=None; s.mem=[]; s.memw=[]; s.imm=None; s.cc=None; s.raw=b''; s.regs=None
    def __repr__(s): return '%06X %-8s %s'%(s.a,s.mn,s.ops)

ARI={0:'add',1:'addc',2:'sub',3:'subc',4:'cmp',5:'xor',6:'and',7:'or'}

def regname(r,byte=False,extr=False):
    if r>=0xF0: return rb(r&15) if byte else rw(r&15)
    a=(0xF000 if extr else 0xFE00)+2*r
    return SFR.get(a,'%04Xh'%a)
def regaddr(r,extr=False):
    if r>=0xF0: return None
    return (0xF000 if extr else 0xFE00)+2*r
def bitoff(b,extr=False):
    if b>=0xF0: return rw(b&15),None
    if b<0x80: a=0xFD00+2*b
    else: a=(0xF100 if extr else 0xFF00)+2*(b-0x80)
    return SFR.get(a,'%04Xh'%a),a

def decode(d,a,extr=False):
    """d: bytes of whole image (file offset == linear addr), a: address. returns Ins or None"""
    if a+2>len(d): return None
    i=Ins(a); op=d[a]; b1=d[a+1]
    hi,lo=op>>4,op&15
    def w(off): return d[a+off]|(d[a+off+1]<<8)
    def need4():
        i.size=4
        return a+4<=len(d)
    n,m=b1>>4,b1&15
    # arithmetic block 0x00..0x7F with lo in 0..9
    if op<0x80 and lo<=9:
        base=ARI[hi]; byte=lo&1; mn=base+('b' if byte else '')
        R=rb if byte else rw
        k=lo&~1
        if k==0: i.mn=mn; i.ops='%s, %s'%(R(n),R(m)); i.regs=(n,m)
        elif k==2:
            if not need4(): return None
            M=w(2); i.mn=mn; i.ops='%s, [%04Xh]'%(regname(b1,byte,extr),M); i.mem=[M]
        elif k==4:
            if hi==4: return None
            if not need4(): return None
            M=w(2); i.mn=mn; i.ops='[%04Xh], %s'%(M,regname(b1,byte,extr)); i.mem=[M]; i.memw=[M]
        elif k==6:
            if not need4(): return None
            if byte: i.imm=d[a+2]
            else: i.imm=w(2)
            i.mn=mn; i.ops='%s, #%Xh'%(regname(b1,byte,extr),i.imm)
        elif k==8:
            if m&8==0: i.mn=mn; i.ops='%s, #%d'%(R(n),m&7); i.imm=m&7
            elif m&4==0: i.mn=mn; i.ops='%s, [r%d]'%(R(n),m&3)
            else: i.mn=mn; i.ops='%s, [r%d+]'%(R(n),m&3)
        i.kind='alu'; return i
    # shifts
    if lo==0xC and op in (0x0C,0x1C,0x2C,0x3C,0x4C,0x5C,0x6C,0x7C,0xAC,0xBC):
        nm={0:'rol',1:'rol',2:'ror',3:'ror',4:'shl',5:'shl',6:'shr',7:'shr',0xA:'ashr',0xB:'ashr'}[hi]
        i.mn=nm
        if hi&1: i.ops='%s, #%d'%(rw(m),n)
        else: i.ops='%s, %s'%(rw(n),rw(m))
        return i
    if lo==0xE: bo,ba=bitoff(b1,extr); i.mn='bclr'; i.ops='%s.%d'%(bo,hi); i.mem=[ba] if ba else []; i.memw=i.mem; return i
    if lo==0xF: bo,ba=bitoff(b1,extr); i.mn='bset'; i.ops='%s.%d'%(bo,hi); i.mem=[ba] if ba else []; i.memw=i.mem; return i
    if lo==0xD:
        rel=b1-256 if b1>=128 else b1
        i.mn='jmpr'; i.cc=hi; i.tgt=a+2+2*rel; i.ops='%s, %06X'%(CC[hi],i.tgt); i.kind='jcc' if hi else 'jmp'; return i
    if op in (0x2A,0x3A,0x4A,0x5A,0x6A,0x7A):
        if not need4(): return None
        nm={0x2A:'bcmp',0x3A:'bmovn',0x4A:'bmov',0x5A:'bor',0x6A:'band',0x7A:'bxor'}[op]
        q=d[a+3]>>4; z=d[a+3]&15
        so,sa=bitoff(b1,extr); do,da=bitoff(d[a+2],extr)
        i.mn=nm; i.ops='%s.%d, %s.%d'%(do,z,so,q); i.mem=[x for x in (sa,da) if x]; i.memw=[da] if (da and op!=0x2A) else []; return i
    if op in (0x8A,0x9A,0xAA,0xBA):
        if not need4(): return None
        if d[a+3]&15: return None
        nm={0x8A:'jb',0x9A:'jnb',0xAA:'jbc',0xBA:'jnbs'}[op]
        r=d[a+2]; rel=r-256 if r>=128 else r
        bo,ba=bitoff(b1,extr); i.mn=nm; i.tgt=a+4+2*rel; i.ops='%s.%d, %06X'%(bo,d[a+3]>>4,i.tgt); i.kind='jcc'; i.mem=[ba] if ba else []
        if op in (0xAA,0xBA): i.memw=i.mem
        return i
    if op in (0x0A,0x1A):
        if not need4(): return None
        bo,ba=bitoff(b1,extr)
        if op==0x0A: mask,data=d[a+2],d[a+3]; i.mn='bfldl'
        else: data,mask=d[a+2],d[a+3]; i.mn='bfldh'
        i.ops='%s, #%02Xh, #%02Xh'%(bo,mask,data); i.mem=[ba] if ba else []; i.memw=i.mem; return i
    # moves
    if op==0xF0: i.mn='mov'; i.ops='%s, %s'%(rw(n),rw(m)); i.regs=(n,m); return i
    if op==0xF1: i.mn='movb'; i.ops='%s, %s'%(rb(n),rb(m)); return i
    if op==0xE0: i.mn='mov'; i.ops='%s, #%Xh'%(rw(m),n); i.imm=n; return i
    if op==0xE1: i.mn='movb'; i.ops='%s, #%Xh'%(rb(m),n); i.imm=n; return i
    if op in (0xE6,0xE7):
        if not need4(): return None
        i.imm=w(2) if op==0xE6 else d[a+2]
        i.mn='mov' if op==0xE6 else 'movb'; i.ops='%s, #%04Xh'%(regname(b1,op==0xE7,extr),i.imm); return i
    if op in (0xA8,0xA9,0x98,0x99,0xB8,0xB9,0x88,0x89,0xC8,0xC9,0xD8,0xD9,0xE8,0xE9):
        byte=op&1; R=rb if byte else rw; i.mn='movb' if byte else 'mov'
        f={0xA8:'%s, [r{m}]',0x98:'%s, [r{m}+]',0xB8:'[r{m}], %s',0x88:'[-r{m}], %s',0xC8:'[r{n}], [r{m}]',0xD8:'[r{n}+], [r{m}]',0xE8:'[r{n}], [r{m}+]'}[op&0xFE]
        if op&0xFE in (0xC8,0xD8,0xE8): i.ops=f.format(n=n,m=m)
        else: i.ops=f.format(m=m)%R(n)
        return i
    if op in (0xD4,0xF4,0xC4,0xE4):
        if not need4(): return None
        byte=op in (0xF4,0xE4); R=rb if byte else rw; o=w(2); i.imm=o
        i.mn='movb' if byte else 'mov'
        if op in (0xD4,0xF4): i.ops='%s, [r%d+#%04Xh]'%(R(n),m,o)
        else: i.ops='[r%d+#%04Xh], %s'%(m,o,R(n))
        i.kind='idx'; return i
    if op in (0x84,0xA4,0x94,0xB4):
        if not need4(): return None
        if n!=0: return None
        M=w(2); byte=op in (0xA4,0xB4); i.mn='movb' if byte else 'mov'; i.mem=[M]
        if op in (0x84,0xA4): i.ops='[r%d], [%04Xh]'%(m,M)
        else: i.ops='[%04Xh], [r%d]'%(M,m); i.memw=[M]
        return i
    if op in (0xF2,0xF3,0xF6,0xF7,0xD2,0xD5,0xC2,0xC5):
        if not need4(): return None
        M=w(2); i.mem=[M]
        nm={0xF2:'mov',0xF3:'movb',0xF6:'mov',0xF7:'movb',0xD2:'movbs',0xD5:'movbs',0xC2:'movbz',0xC5:'movbz'}[op]
        byte_reg = op in (0xF3,0xF7,0xD5,0xC5)
        i.mn=nm
        if op in (0xF2,0xF3,0xD2,0xC2): i.ops='%s, [%04Xh]'%(regname(b1,byte_reg,extr),M)
        else: i.ops='[%04Xh], %s'%(M,regname(b1,byte_reg,extr)); i.memw=[M]
        return i
    if op in (0xD0,0xC0): i.mn='movbs' if op==0xD0 else 'movbz'; i.ops='%s, %s'%(rw(m),rb(n)); return i
    if op in (0x91,0xB1,0x81,0xA1):
        if m!=0: return None
        i.mn={0x91:'cpl',0xB1:'cplb',0x81:'neg',0xA1:'negb'}[op]; i.ops=(rb if op in (0xB1,0xA1) else rw)(n); return i
    if op in (0xA0,0xB0,0x80,0x90): i.mn={0xA0:'cmpd1',0xB0:'cmpd2',0x80:'cmpi1',0x90:'cmpi2'}[op]; i.ops='%s, #%Xh'%(rw(m),n); return i
    if op in (0xA6,0xB6,0x86,0x96,0xA2,0xB2,0x82,0x92):
        if not need4(): return None
        if n!=0xF: return None
        i.mn={0xA:'cmpd1',0xB:'cmpd2',0x8:'cmpi1',0x9:'cmpi2'}[hi]
        if lo==6: i.imm=w(2); i.ops='%s, #%04Xh'%(rw(m),i.imm)
        else: M=w(2); i.mem=[M]; i.ops='%s, [%04Xh]'%(rw(m),M)
        return i
    # control
    if op==0xEA:
        if not need4(): return None
        if m!=0: return None
        i.cc=n; i.tgt=w(2); i.mn='jmpa'; i.ops='%s, %04X'%(CC[n],i.tgt); i.kind='jcc_abs' if n else 'jmp_abs'; return i
    if op==0xCA:
        if not need4(): return None
        if m!=0: return None
        i.cc=n; i.tgt=w(2); i.mn='calla'; i.ops='%s, %04X'%(CC[n],i.tgt); i.kind='call_abs'; return i
    if op==0x9C: i.mn='jmpi'; i.cc=n; i.ops='%s, [r%d]'%(CC[n],m); i.kind='jmpi'; return i
    if op==0xAB: i.mn='calli'; i.cc=n; i.ops='%s, [r%d]'%(CC[n],m); i.kind='calli'; return i
    if op==0xBB:
        rel=b1-256 if b1>=128 else b1; i.tgt=a+2+2*rel; i.mn='callr'; i.ops='%06X'%i.tgt; i.kind='call'; return i
    if op in (0xFA,0xDA):
        if not need4(): return None
        i.tgt=(b1<<16)|w(2); i.mn='jmps' if op==0xFA else 'calls'; i.ops='%02X:%04X'%(b1,w(2)); i.kind='jmp' if op==0xFA else 'call'; return i
    if op==0xE2:
        if not need4(): return None
        i.tgt=w(2); i.mn='pcall'; i.ops='%s, %04X'%(regname(b1),i.tgt); i.kind='call_abs'; return i
    if op==0xCB and b1==0x00: i.mn='ret'; i.kind='ret'; return i
    if op==0xDB and b1==0x00: i.mn='rets'; i.kind='ret'; return i
    if op==0xFB and b1==0x88: i.mn='reti'; i.kind='ret'; return i
    if op==0xEB: i.mn='retp'; i.ops=regname(b1); i.kind='ret'; return i
    if op==0x9B: i.mn='trap'; i.ops='#%02Xh'%(b1>>1); return i
    if op in (0x4B,0x5B,0x6B,0x7B):
        if n!=m: return None
        i.mn={0x4B:'div',0x5B:'divu',0x6B:'divl',0x7B:'divlu'}[op]; i.ops=rw(n); return i
    if op in (0x0B,0x1B): i.mn='mul' if op==0x0B else 'mulu'; i.ops='%s, %s'%(rw(n),rw(m)); return i
    if op==0x2B: i.mn='prior'; i.ops='%s, %s'%(rw(n),rw(m)); return i
    if op==0xFC: i.mn='pop'; i.ops=regname(b1); return i
    if op==0xEC: i.mn='push'; i.ops=regname(b1); return i
    if op in (0xC6,0xD6):
        if not need4(): return None
        i.mn='scxt'
        if op==0xC6: i.imm=w(2); i.ops='%s, #%04Xh'%(regname(b1),i.imm)
        else: M=w(2); i.mem=[M]; i.ops='%s, [%04Xh]'%(regname(b1),M)
        return i
    if op==0xCC and b1==0: i.mn='nop'; return i
    if op==0xD1:
        if m!=0: return None
        mode=n>>2; cnt=(n&3)+1
        if mode==0: i.mn='atomic'; i.ops='#%d'%cnt; return i
        if mode==2: i.mn='extr'; i.ops='#%d'%cnt; i.kind='extr'; i.imm=cnt; return i
        return None
    if op==0xDC:
        mode=n>>2; cnt=(n&3)+1
        i.mn=['exts','extp','extsr','extpr'][mode]; i.ops='%s, #%d'%(rw(m),cnt); i.kind='ext_r'; i.imm=cnt; return i
    if op==0xD7:
        if not need4(): return None
        if m!=0: return None
        mode=n>>2; cnt=(n&3)+1
        i.mn=['exts','extp','extsr','extpr'][mode]
        if mode&1: pg=d[a+2]|((d[a+3]&3)<<8); i.ops='#%03Xh, #%d'%(pg,cnt); i.imm=(pg,cnt)
        else: sg=d[a+2]; i.ops='#%02Xh, #%d'%(sg,cnt); i.imm=(sg,cnt)
        i.kind='ext_i'; return i
    four={b'\xb5\x4a\xb5\xb5':'einit',b'\x87\x78\x87\x87':'idle',b'\x97\x68\x97\x97':'pwrdn',b'\xb7\x48\xb7\xb7':'srst',b'\xa7\x58\xa7\xa7':'srvwdt',b'\xa5\x5a\xa5\xa5':'diswdt'}
    if a+4<=len(d) and bytes(d[a:a+4]) in four:
        i.size=4; i.mn=four[bytes(d[a:a+4])]; return i
    return None
