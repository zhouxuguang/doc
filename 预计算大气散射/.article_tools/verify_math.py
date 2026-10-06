import sys, json, math, re
from pathlib import Path
sys.path.insert(0, '/private/tmp/atmos-blog-deps')
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RB, RT = 6360000., 6420000.
H = np.sqrt(RT * RT - RB * RB)
def top(r, mu): return -r*mu+np.sqrt(np.maximum(r*r*(mu*mu-1)+RT*RT,0))
def bottom(r, mu): return -r*mu-np.sqrt(np.maximum(r*r*(mu*mu-1)+RB*RB,0))
def tex(x,n): return .5/n+x*(1-1/n)
def unit(u,n): return (u-.5/n)/(1-1/n)
def phase_r(nu): return 3/(16*np.pi)*(1+nu*nu)
def phase_m(nu,g): return 3/(8*np.pi)*(1-g*g)*(1+nu*nu)/((2+g*g)*(1+g*g-2*g*nu)**1.5)
results={}
nu,w=np.polynomial.legendre.leggauss(512)
results['phase']={'rayleigh_normalization':float(2*np.pi*np.dot(w,phase_r(nu)))}
for g in [0.,.5,.8,.9]:
    p=phase_m(nu,g)
    results['phase'][str(g)]={'normalization':float(2*np.pi*np.dot(w,p)),
      'mean_nu':float(2*np.pi*np.dot(w,nu*p)),
      'analytic_mean':3*g*(4+g*g)/(5*(2+g*g))}
assert max(abs(v['normalization']-1) for v in results['phase'].values() if isinstance(v,dict))<1e-10

rng=np.random.default_rng(20261005)
# Exact T-LUT map, tangent-to-zenith physical domain.
r=RB+(RT-RB)*rng.uniform(.00001,.99999,20000)
rho=np.sqrt(r*r-RB*RB);mh=-rho/r
mu=mh+(1-mh)*rng.uniform(0,1,len(r))
d=top(r,mu);xm=(d-(RT-r))/(rho+H-(RT-r))
ur=tex(rho/H,64);um=tex(xm,256)
rho2=H*unit(ur,64);r2=np.sqrt(rho2*rho2+RB*RB)
d2=RT-r2+unit(um,256)*(rho2+H-(RT-r2))
mu2=(H*H-rho2*rho2-d2*d2)/(2*r2*d2)
results['transmittance_mapping']={'samples':len(r),'r_abs_error_m':float(np.max(abs(r-r2))),
  'mu_abs_error':float(np.max(abs(mu-mu2))), 'endpoint_uv':[float(tex(0,256)),float(tex(1,256))]}
assert np.max(abs(mu-mu2))<1e-9

# Scattering mu halves including their horizon limits.
errs=[]
for ground in [True,False]:
    if ground:
        mu=-1+(mh+1)*rng.uniform(0,1,len(r));d=bottom(r,mu);dmin=r-RB;dmax=rho
        u=.5-.5*tex((d-dmin)/(dmax-dmin),64)
        dd=dmin+(dmax-dmin)*unit(1-2*u,64)
        back=-(rho*rho+dd*dd)/(2*r*dd)
    else:
        mu=mh+(1-mh)*rng.uniform(0,1,len(r));d=top(r,mu);dmin=RT-r;dmax=rho+H
        u=.5+.5*tex((d-dmin)/(dmax-dmin),64)
        dd=dmin+(dmax-dmin)*unit(2*u-1,64)
        back=(H*H-rho*rho-dd*dd)/(2*r*dd)
    errs.append(float(np.max(abs(mu-back))))
results['scattering_mu_mapping']={'samples_per_half':len(r),'errors':errs,
 'horizon_uv':[.5-.5*tex(1,64),.5+.5*tex(1,64)]}
assert max(errs)<1e-8

musmin=-.5;den=H-(RT-RB);A=(top(RB,musmin)-(RT-RB))/den
mus=rng.uniform(musmin,1,20000);a=(top(RB,mus)-(RT-RB))/den
x=np.maximum(1-a/A,0)/(1+a);aa=A*(1-x)/(1+A*x)
dd=RT-RB+aa*den;back=(H*H-dd*dd)/(2*RB*dd)
results['solar_mapping']={'samples':len(mus),'mu_s_error':float(np.max(abs(mus-back))),
 'A_reference':float(A),'A_gnx':float(-2*musmin*RB/den)}
assert np.max(abs(mus-back))<1e-10
results['gnx_solar_actual_cutoff']={}
for rt in [6420000.,6460000.]:
    hh=np.sqrt(rt*rt-RB*RB);dc=rt-RB-2*musmin*RB
    mc=(hh*hh-dc*dc)/(2*RB*dc)
    results['gnx_solar_actual_cutoff'][str(int(rt))]={'mu_cutoff':float(mc),
       'zenith_deg':float(np.degrees(np.arccos(mc)))}

# Directions from spherical coordinates must obey Gram-matrix feasibility.
mu=rng.uniform(-1,1,20000);ms=rng.uniform(-1,1,20000);phi=rng.uniform(0,2*np.pi,20000)
nn=mu*ms+np.sqrt((1-mu*mu)*(1-ms*ms))*np.cos(phi)
det=1+2*mu*ms*nn-mu*mu-ms*ms-nn*nn
results['direction_domain']={'samples':len(mu),'min_gram_determinant':float(det.min())}
assert det.min()>-1e-12

def density(h): return np.stack([np.exp(-h/8000),np.exp(-h/1200),np.clip(np.where(h<25000,h/15000-2/3,8/3-h/15000),0,1)],axis=-1)
coeff=np.array([1.24062e-6*.55**-4,4.44e-6,1.0e-6])
def tau_segment(p,q,intervals=10000):
    x=np.linspace(0,1,intervals+1);v=p[None,:]+x[:,None]*(q-p)[None,:]
    h=np.linalg.norm(v,axis=1)-RB
    f=density(h)@coeff
    return np.trapezoid(f,x)*np.linalg.norm(q-p)
p=np.array([0.,0.,RB+1000]);direction=np.array([np.sqrt(1-.1**2),0,.1])
q=p+direction*10000;end=p+direction*70000
t_pq=tau_segment(p,q);t_qe=tau_segment(q,end);t_pe=tau_segment(p,end);t_qp=tau_segment(q,p)
results['beer_lambert']={'reverse_tau_abs_error':float(abs(t_pq-t_qp)),
 'composition_T_abs_error':float(abs(np.exp(-t_pe)-np.exp(-t_pq)*np.exp(-t_qe))),
 'T_PQ':float(np.exp(-t_pq))}
assert abs(t_pq-t_qp)<1e-12
assert results['beer_lambert']['composition_T_abs_error']<1e-7

results['trapezoid_500']={}
for label,m in [('zenith',1.),('horizontal',0.),('horizon',-math.sqrt(1-RB*RB/(RB+1000)**2))]:
    r0=RB+1000;dt=top(r0,m)
    def optical(n):
        dx=np.linspace(0,dt,n+1);hs=np.sqrt(r0*r0+2*r0*m*dx+dx*dx)-RB
        return np.trapezoid(density(hs),dx,axis=0)
    coarse=optical(500);fine=optical(20000)
    results['trapezoid_500'][label]={'relative_errors_R_M_O':list(abs(coarse-fine)/fine)}

# Finite-segment scattering identity for homogeneous extinction and a varying source.
b=.00002;D=80000.;dq=21000.;n=200000
def j(x):return .0004*(1+.4*np.sin(x/11000))
def integrate(lo,hi,origin):
    x=np.linspace(lo,hi,n+1);return np.trapezoid(np.exp(-b*(x-origin))*j(x),x)
SP=integrate(0,D,0);SQ=integrate(dq,D,dq);direct=integrate(0,dq,0)
sub=SP-np.exp(-b*dq)*SQ
results['finite_scattering']={'direct':float(direct),'subtraction':float(sub),
 'relative_error':float(abs(sub-direct)/direct)}
assert abs(sub-direct)/direct<1e-9

x=np.linspace(-1,1,10001)
exact=(np.arccos(-x)+x*np.sqrt(np.maximum(1-x*x,0)))/np.pi
smooth=.5+.75*x-.25*x**3
results['sun_disk']={'max_visible_fraction_abs_error':float(np.max(abs(exact-smooth))),
 'endpoint_value':[float(smooth[0]),float(smooth[-1])],
 'endpoint_derivative':[0.,0.]}

results['fp16']={}
for tau in [10,15,18,20]:
    value=np.exp(-tau);f=float(np.float16(value))
    results['fp16'][str(tau)]={'T':float(value),'fp16':f,'relative_error':float(abs(f-value)/value)}
results['memory']={'scattering_texture_bytes':256*128*32*8,
 'runtime_bytes':2*256*128*32*8+256*64*8+64*16*8,
 'peak_bytes':5*256*128*32*8+256*64*8+2*64*16*8}
results['schedule_N5']={'draw_steps':2+32+4*(32+1+32),'min_recording_frames_at_24':math.ceil((2+32+4*65)/24)}

text=(ROOT/'预计算大气散射技术详解.md').read_text()
results['article_current']={'han_characters':len(re.findall(r'[\u4e00-\u9fff]',text))}
path=ROOT/'.article_tools/qa/math_validation.json';path.write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
