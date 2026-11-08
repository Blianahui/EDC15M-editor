import sys,pickle,struct,re; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
lin=pickle.load(open('out/lin.pkl','rb'))
addrs=sorted(lin); idx={a:k for k,a in enumerate(addrs)}
img=open(sys.argv[1],'rb').read()
W=lambda o: struct.unpack_from('<H',img,o)[0]
def back(a,n=10):
    k=idx[a]; out=[]
    for j in range(max(0,k-n),k):
        out.append(lin[addrs[j]])
    return out
tgt=int(sys.argv[2],16); show=int(sys.argv[3]) if len(sys.argv)>3 else 4
k=0
for a in addrs:
    i=lin[a]
    if i.mnem in('CALLS','JMPS') and i.targets[0][1]==tgt:
        k+=1
        if k>show: break
        print('-----')
        for p in back(a,8): print('   ',p)
        print(' >>',i)
