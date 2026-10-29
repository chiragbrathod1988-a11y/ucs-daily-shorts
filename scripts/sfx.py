"""Synthesised UI sound effects (whoosh / pop / coin / ding / click) placed on the edit timeline."""
import numpy as np, soundfile as sf
import sys, json
SR=48000; DUR=float(sys.argv[3]); N=int(SR*DUR); rng=np.random.default_rng(3)
L=np.zeros(N); R=np.zeros(N)
def put(t,sig,g,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig)); L[i:j]+=sig[:j-i]*g*(1-max(0,pan)); R[i:j]+=sig[:j-i]*g*(1+min(0,pan))
def bp_noise(n, f0, f1):
    x=rng.standard_normal(n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR)
    # time-varying sweep approximated by splitting in blocks
    out=np.zeros(n); B=32; edges=np.linspace(0,n,B+1).astype(int)
    for k in range(B):
        fc=f0*(f1/f0)**(k/(B-1)); mask=np.exp(-0.5*((np.log(f+1)-np.log(fc))/0.35)**2)
        y=np.fft.irfft(X*mask,n); out[edges[k]:edges[k+1]]=y[edges[k]:edges[k+1]]
    return out/np.max(np.abs(out))
def whoosh(d=0.45,up=True):
    n=int(d*SR); t=np.arange(n)/SR
    x=bp_noise(n,300,4000) if up else bp_noise(n,4000,300)
    e=np.sin(np.pi*t/d)**2; return x*e
def pop():
    n=int(0.12*SR); t=np.arange(n)/SR; f=900*np.exp(-t/0.02)+300
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.03)
def ding(f=1318.5):
    n=int(0.9*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.01*t)*np.exp(-t/0.15)+0.3*np.sin(2*np.pi*f*1.5*t))*np.exp(-t/0.35)*np.minimum(1,t/0.003)
def coin():
    a=ding(1975.5)[:int(0.12*SR)]*np.linspace(1,0.6,int(0.12*SR)); b=ding(2637.0)
    out=np.zeros(len(b)+len(a)); out[:len(a)]+=a; out[int(0.08*SR):int(0.08*SR)+len(b)]+=b; return out
def click():
    n=int(0.03*SR); t=np.arange(n)/SR; return rng.standard_normal(n)*np.exp(-t/0.004)+np.sin(2*np.pi*2200*t)*np.exp(-t/0.006)
KIND={"whoosh":(lambda: whoosh(0.45),0.22),"pop":(pop,0.33),"coin":(coin,0.16),"ding":(ding,0.18),"click":(click,0.45)}
for tt,k in json.load(open(sys.argv[1])):
    f,g=KIND[k]; put(max(0,tt-0.02),f(),g,0)
st=np.stack([L,R],1); sf.write(sys.argv[2],st.astype(np.float32),SR); print("peak",np.max(np.abs(st)))
