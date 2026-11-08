import sys,re,struct,pickle; sys.path.insert(0,sys.argv[0].rsplit('/',1)[0]); import analyze,c166
d=open(sys.argv[1],'rb').read()
A=analyze.A(d)
ents=[0x10804,0x17290]+[0x1729C+4*k for k in range(0x51)]
tasksA=[m.start() for m in re.finditer(rb'\xf2\xf0[\x3a-\x44]\x00\x26\xf0..\x84\x00\x86\xfd',d[:0x38000],re.S) if m.start()%2==0]
tasksB=[m.start() for m in re.finditer(rb'\x42\xf0\x86\xfd\x9d',d[:0x38000]) if m.start()%2==0 and not (d[m.start()-4:m.start()-2]==b'\xf2\xf0')]
A.run(ents+tasksA+tasksB)
A.tasks=sorted(set(tasksA+tasksB)); A.taskkind={t:('A[%02X]'%d[t+2] if t in tasksA else 'B') for t in A.tasks}
pickle.dump(A,open(sys.argv[2],'wb'))
print('tasksA',len(tasksA),'tasksB',len(tasksB),'insns',len(A.ins),'funcs',len(A.funcs))
