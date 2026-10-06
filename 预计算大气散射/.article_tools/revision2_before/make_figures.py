import sys, os
sys.path.insert(0, '/private/tmp/atmos-blog-deps')
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/atmos-blog-mpl')
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib import font_manager

OUT=Path(__file__).resolve().parent.parent/'atmosphere_scattering_images'
for candidate in ['/System/Library/Fonts/STHeiti Light.ttc','/System/Library/Fonts/Supplemental/Songti.ttc','/System/Library/Fonts/Supplemental/Arial Unicode.ttf']:
    if Path(candidate).exists():
        font_manager.fontManager.addfont(candidate)
        plt.rcParams['font.family']=font_manager.FontProperties(fname=candidate).get_name()
        break
plt.rcParams.update({'font.size':12,'axes.titlesize':16,'axes.labelsize':12,'figure.facecolor':'white',
    'axes.facecolor':'#f7fafc','axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,
    'grid.color':'#dce5ee','grid.alpha':0.65,'axes.unicode_minus':False,'svg.fonttype':'none'})
BLUE='#1766a3'; CYAN='#20a4c0'; ORANGE='#e89132'; GREEN='#598b70'; INK='#243e53'; RED='#c84c52'
RB=6360.; RT=6420.; H=np.sqrt(RT*RT-RB*RB)
def top(r,mu):return -r*mu+np.sqrt(np.maximum(r*r*(mu*mu-1)+RT*RT,0))
def bottom(r,mu):return -r*mu-np.sqrt(np.maximum(r*r*(mu*mu-1)+RB*RB,0))
def tex(x,n):return .5/n+x*(1-1/n)
def save(fig,name):
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight')
    fig.savefig(OUT/(name+'.png'),dpi=190,bbox_inches='tight')
    plt.close(fig)
def clean(ax,xlim=(0,10),ylim=(0,6)):
    ax.set(xlim=xlim,ylim=ylim);ax.axis('off')
def arrow(ax,a,b,color=BLUE,label=None,offset=(0,.18),lw=2.2):
    ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color=color,lw=lw))
    if label:ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],label,color=color,ha='center',va='bottom')
def point(ax,p,label):
    ax.plot(*p,'o',color=INK,ms=6);ax.text(p[0]+.12,p[1]+.13,label,color=INK)
def box(ax,xy,w,h,text,color=BLUE):
    ax.add_patch(FancyBboxPatch(xy,w,h,boxstyle='round,pad=0.10,rounding_size=0.12',fc='white',ec=color,lw=1.8))
    ax.text(xy[0]+w/2,xy[1]+h/2,text,ha='center',va='center',color=INK)

# 01: global geometry, deliberately enlarged shell.
fig,ax=plt.subplots(figsize=(9,6));clean(ax,(-1.7,2),(-1.25,1.6));ax.set_aspect('equal')
ax.add_patch(Circle((0,0),1.15,fc='#e7f5fb',ec=CYAN,lw=2));ax.add_patch(Circle((0,0),1,fc='#e0ebe2',ec=GREEN,lw=2))
p=np.array([0.,1.08])
ground_dir=np.array([.9,-np.sqrt(1-.9**2)])
ground_d=-np.dot(p,ground_dir)-np.sqrt(np.dot(p,ground_dir)**2-np.dot(p,p)+1)
q=p+ground_d*ground_dir
tangent=np.array([np.sqrt(1-1/1.08**2),1/1.08])
ax.plot([p[0],tangent[0]],[p[1],tangent[1]],color=ORANGE,lw=2.2)
out=tangent+(tangent-p)*1.4
arrow(ax,tangent,out,ORANGE)
arrow(ax,(0,0),p,INK,'$r$');arrow(ax,p,(1.48,1.35),BLUE,'顶边界方向',offset=(0,.12))
arrow(ax,p,q,RED);ax.plot(*q,'o',color=RED,ms=6)
ax.annotate('地面交点',xy=q,xytext=(-.72,1.22),color=RED,arrowprops=dict(arrowstyle='-',color=RED))
ax.text(1.0,.83,'地表切线',color=ORANGE);ax.plot(*tangent,'o',color=ORANGE,ms=6)
ax.annotate('切点',xy=tangent,xytext=(.72,.60),color=ORANGE,arrowprops=dict(arrowstyle='-',color=ORANGE))
point(ax,(0,0),'O');ax.plot(*p,'o',color=INK,ms=6);ax.text(-.08,1.3,'P',color=INK)
ax.text(-.8,-.2,'地表半径 $r_b$',color=GREEN);ax.text(-1.38,.74,'大气顶 $r_t$',color=CYAN)
ax.text(-1.4,-1.16,'示意图放大了大气厚度；实际地球模型约为半径的 1%。',fontsize=11)
ax.set_title('球形大气壳与射线边界');save(fig,'01_spherical_geometry')

# 02: consistent direction convention.
fig,ax=plt.subplots(figsize=(10,4.9));clean(ax)
p=(1.2,1.7);q=(5.2,2.5);sun=(8.7,5.)
point(ax,p,'P（观察点）');point(ax,q,'Q（散射点）');point(ax,sun,'太阳')
arrow(ax,p,q,BLUE,r'观察方向 $\boldsymbol{\omega}$')
arrow(ax,q,p,RED,r'出射光传播方向 $-\boldsymbol{\omega}$',offset=(0,-.6))
arrow(ax,q,sun,ORANGE,r'指向太阳 $\boldsymbol{s}$',offset=(-.6,.12))
arrow(ax,sun,q,RED,r'入射光传播方向 $-\boldsymbol{s}$',offset=(1,-.65))
arrow(ax,p,(1.2,4.5),INK,r'局部天顶 $\boldsymbol{n}_r$',offset=(-1,0))
ax.text(3.5,.55,r'$\mu=\boldsymbol{n}_r\!\cdot\!\boldsymbol{\omega},\quad\mu_s=\boldsymbol{n}_r\!\cdot\!\boldsymbol{s},\quad\nu=\boldsymbol{\omega}\!\cdot\!\boldsymbol{s}$',ha='center',color=INK)
ax.set_title('观察方向与光传播方向：两个负号同时消去');save(fig,'02_direction_convention')

# 03: actual density functions.
fig,ax=plt.subplots(figsize=(9,5));h=np.linspace(0,60,900)
ax.plot(np.exp(-h/8),h,lw=2.5,label='Rayleigh：$H_R=8$ km',color=BLUE)
ax.plot(np.exp(-h/1.2),h,lw=2.5,label='气溶胶：$H_M=1.2$ km',color=ORANGE)
oz=np.clip(np.where(h<25,(h-10)/15,(40-h)/15),0,1)
ax.plot(oz,h,lw=2.5,label='臭氧：10–40 km 三角形剖面',color=GREEN)
ax.set(xlabel='归一化密度 $D_i(h)$',ylabel='高度 $h$ / km',title='官方地球预设的三种密度剖面',xlim=(0,1.05),ylim=(0,60));ax.legend();save(fig,'03_density_profiles')

# 04: phase functions.
fig,axs=plt.subplots(1,2,figsize=(12,4.7));ang=np.linspace(0,180,1000);nu=np.cos(np.radians(ang))
pr=3/(16*np.pi)*(1+nu*nu)
for ax in axs:
    ax.plot(ang,pr,color=BLUE,lw=2.4,label='Rayleigh')
    for g,color in [(.5,GREEN),(.8,ORANGE),(.9,RED)]:
        pm=3/(8*np.pi)*(1-g*g)*(1+nu*nu)/((2+g*g)*(1+g*g-2*g*nu)**1.5)
        ax.plot(ang,pm,lw=2,label=f'Cornette–Shanks $g={g}$',color=color)
    ax.set(xlabel='散射角 / 度',ylabel=r'相函数 / sr$^{-1}$',xlim=(0,180))
axs[0].set_ylim(0,1.1);axs[0].set_title('线性尺度');axs[1].set_yscale('log');axs[1].set_title('对数尺度，保留前向峰');axs[1].legend(fontsize=10)
save(fig,'04_phase_functions')

# 05: multiplicative T and optical depth.
fig,axs=plt.subplots(1,2,figsize=(12,4.6));clean(axs[0]);ax=axs[0]
for x,label in [(1,'P'),(4,'Q'),(8,'I')]:point(ax,(x,2.7),label)
arrow(ax,(1,2.7),(4,2.7),BLUE,'$T(P,Q)$');arrow(ax,(4,2.7),(8,2.7),CYAN,'$T(Q,I)$')
ax.text(4.5,1.1,r'$T(P,I)=T(P,Q)\,T(Q,I)$',ha='center',fontsize=15)
ax.text(4.5,.4,'同一直线、相邻线段、无实体遮挡',ha='center');ax.set_title('分段透射率')
tau=np.linspace(0,8,400);axs[1].plot(tau,np.exp(-tau),color=BLUE,lw=2.5);axs[1].set(xlabel=r'无量纲光学厚度 $\tau_\lambda$',ylabel=r'$T_\lambda=e^{-\tau_\lambda}$',title='消光造成的指数衰减');save(fig,'05_transmittance_chain')

# 06: single scattering light path.
fig,ax=plt.subplots(figsize=(10,5));clean(ax)
p=(1,1.5);q=(5,2.5);sun=(8.3,5)
ax.plot([1,8.7],[1.5,3.43],color=BLUE,alpha=.35,lw=8)
point(ax,p,'P');point(ax,q,'Q=P+dω');point(ax,sun,'太阳')
arrow(ax,sun,q,ORANGE,r'$E_{\odot,\lambda}\,T_{\odot,\lambda}(Q)$')
arrow(ax,q,p,BLUE,r'$T_\lambda(P,Q)$',offset=(0,-.5))
ax.add_patch(Circle(q,.32,fc='#fff1d7',ec=ORANGE,lw=2));ax.text(5.3,1.1,r'局部散射：$\beta_i^s(Q,\lambda)\,p_i(\nu)$',color=INK)
ax.text(5,.25,'沿观察路径积累，每个采样点都有“太阳→Q→P”两段衰减。',ha='center');ax.set_title('单次散射的两段光路');save(fig,'06_single_scattering_path')

# 07: nonlinear radial and directional sampling.
fig,axs=plt.subplots(1,2,figsize=(12,4.8));h=np.linspace(0,60,600);xr=np.sqrt((RB+h)**2-RB**2)/H
axs[0].plot(h,xr,color=BLUE,lw=2.5,label=r'$x_r=\rho/H$');axs[0].plot(h,h/60,'--',color=INK,label='高度线性映射')
samples=np.linspace(0,1,32);hs=np.sqrt((H*samples)**2+RB*RB)-RB;axs[0].scatter(hs,np.zeros(32),s=12,color=ORANGE,label='32 个半径样本')
axs[0].set(xlabel='高度 / km',ylabel='单位区间坐标',title='近地面获得更密的采样');axs[0].legend(fontsize=10)
r=RB+1;rho=np.sqrt(r*r-RB*RB);mh=-rho/r;mu=np.linspace(mh,1,800);xm=(top(r,mu)-(RT-r))/(rho+H-(RT-r))
axs[1].plot(mu,xm,color=BLUE,lw=2.5);axs[1].axvline(mh,color=ORANGE,ls='--');axs[1].set(xlabel=r'$\mu$',ylabel=r'$x_\mu$',title='透射率按边界距离映射（h=1 km）');save(fig,'07_transmittance_mapping')

# 08: discontinuity split.
fig,axs=plt.subplots(1,2,figsize=(12,4.8));r=RB+1;rho=np.sqrt(r*r-RB*RB);mh=-rho/r
mu0=np.linspace(-1,mh,500);mu1=np.linspace(mh+1e-9,1,1000)
d0=bottom(r,mu0);d1=top(r,mu1)
u0=.5-.5*tex((d0-(r-RB))/(rho-(r-RB)),64);u1=.5+.5*tex((d1-(RT-r))/(rho+H-(RT-r)),64)
axs[0].plot(mu0,d0,color=GREEN,label='到地面');axs[0].plot(mu1,d1,color=BLUE,label='到大气顶');axs[0].set(xlabel=r'$\mu$',ylabel='最近边界距离 / km',title='相切附近的边界距离跳变');axs[0].legend()
axs[1].plot(mu0,u0,color=GREEN);axs[1].plot(mu1,u1,color=BLUE);axs[1].axhline(.5,color=INK,ls='--');axs[1].axvline(mh,color=ORANGE,ls='--');axs[1].set(xlabel=r'$\mu$',ylabel=r'$u_\mu$',title='两半纹理避免跨地平线插值',ylim=(0,1));save(fig,'08_horizon_split')

# 09: exact and engine legacy A.
fig,axs=plt.subplots(1,2,figsize=(12,4.8));musmin=-.2;mus=np.linspace(musmin,1,800);dmin=RT-RB;den=H-dmin
a=(top(RB,mus)-dmin)/den;A=(top(RB,musmin)-dmin)/den;Ag=-2*musmin*RB/den
x=np.maximum(1-a/A,0)/(1+a);xg=np.maximum(1-a/Ag,0)/(1+a)
axs[0].plot(mus,x,color=BLUE,lw=2.4,label='新版文档：精确端点 A');axs[0].plot(mus,xg,color=ORANGE,lw=2,ls='--',label='GNX：近似 A');axs[0].set(xlabel=r'$\mu_s$',ylabel=r'$x_{\mu_s}$',title=r'示例：$\mu_{s,\min}=-0.2$');axs[0].legend(fontsize=10)
xx=np.linspace(0,1,32);aa=A*(1-xx)/(1+A*xx);dd=dmin+aa*den;ms=(H*H-dd*dd)/(2*RB*dd)
axs[1].plot(ms,np.zeros_like(ms),'|',ms=18,color=BLUE);axs[1].axvline(0,ls='--',color=ORANGE);axs[1].set(xlabel=r'反解的太阳天顶余弦 $\mu_s$',yticks=[],title='32 个采样点集中在太阳接近地平线处',ylim=(-.5,.5));save(fig,'09_sun_mapping')

# 10: feasible nu from Gram matrix.
fig,ax=plt.subplots(figsize=(9,5));mus=np.linspace(-1,1,800);mu=.3;b=np.sqrt((1-mu*mu)*(1-mus*mus));lo=mu*mus-b;hi=mu*mus+b
ax.fill_between(mus,lo,hi,color='#dceef8',label='三单位向量可以实现的区域');ax.plot(mus,lo,color=BLUE);ax.plot(mus,hi,color=BLUE);ax.plot(mus,mu*mus,'--',color=ORANGE,label=r'$\mu\mu_s$')
ax.set(xlabel=r'$\mu_s$',ylabel=r'$\nu$',title=r'固定 $\mu=0.3$ 时的角度可实现范围',xlim=(-1,1),ylim=(-1,1));ax.legend(fontsize=11);save(fig,'10_valid_nu_domain')

# 11: packed slices.
fig,ax=plt.subplots(figsize=(12,5.3));clean(ax,(0,16),(0,6))
for i in range(8):
    ax.add_patch(Rectangle((.8+i*1.75,2.2),1.75,2.2,fc=plt.cm.Blues(.18+i*.06),ec=BLUE,lw=1.2))
    ax.text(1.675+i*1.75,4.65,rf'$\nu_{i}$',ha='center');ax.text(1.675+i*1.75,3.3,'32 个\n'+r'$\mu_s$ 样本',ha='center',fontsize=10)
ax.text(.15,3.3,'128\n'+r'$\mu$',ha='center',fontsize=11);arrow(ax,(.8,1.6),(14.8,1.6),INK,'宽度：8 × 32 = 256',offset=(0,.1))
box(ax,(2,.25),4.2,.75,'硬件：每个 ν 切片内三线性插值',BLUE);box(ax,(8,.25),5.3,.75,'软件：相邻两个 ν 切片再线性插值',ORANGE)
ax.text(8,5.55,'深度：32 个 r 层；图示为其中一层',ha='center');ax.set_title('四维函数打包进 256 × 128 × 32 三维纹理');save(fig,'11_texture_packing')

# 12: multiple scattering including ground.
fig,ax=plt.subplots(figsize=(11,5));clean(ax)
ax.fill_between([0,10],[.9,.9],0,color='#e0ebe2');q=(5,3);p=(1,2)
point(ax,q,'Q');point(ax,p,'P');arrow(ax,q,p,BLUE,'本阶出射光')
for a in [(2,5),(7,5),(9,2.8)]:arrow(ax,a,q,CYAN)
ground=(7.5,.9);point(ax,ground,'G');arrow(ax,ground,q,ORANGE,'地面反射后入射')
ax.text(2,5.4,'来自全空间的 $L^{(n-1)}$',color=CYAN);ax.text(7.5,.25,r'$a_g E^{(n-2)}/\pi$',ha='center',color=ORANGE)
ax.text(4.7,1.2,'一次地面反射 + 一次大气散射 = 两次事件',ha='center',fontsize=11);ax.set_title('多次散射源包含天空路径与地面反射路径');save(fig,'12_multiple_scattering_paths')

# 13: exact dependency DAG with three passes.
fig,ax=plt.subplots(figsize=(12,6));clean(ax,(0,12),(0,7))
box(ax,(.4,5.2),3,1,r'$L^{(n-1)}$'+'\n上一阶大气散射');box(ax,(.4,3.2),3,1,r'$E^{(n-2)}$'+'\n上一轮 delta irradiance',ORANGE)
box(ax,(4.5,4.2),3.1,1.2,r'$J^{(n)}$'+'\n散射密度积分');box(ax,(8.5,4.2),3.0,1.2,r'$L^{(n)}$'+'\n沿射线积分')
box(ax,(4.5,1.5),3.1,1.2,r'$E^{(n-1)}$'+'\n半球积分',ORANGE)
arrow(ax,(3.4,5.7),(4.5,4.8));arrow(ax,(3.4,3.7),(4.5,4.6),ORANGE);arrow(ax,(7.6,4.8),(8.5,4.8));arrow(ax,(1.9,5.2),(4.5,2.2),CYAN)
ax.text(10,2.3,'写入 delta L\n累计到最终散射纹理',ha='center');ax.text(6.05,.8,'写入 delta E；累计到最终天空辐照度纹理',ha='center',fontsize=11)
ax.text(6,6.65,'执行顺序：先 J，再 E，最后 L；旧输入读取完成后才覆盖。',ha='center',fontsize=12);ax.set_title('第 n 阶预计算的依赖与覆盖顺序');save(fig,'13_precompute_dependencies')

# 14: finite segment subtraction.
fig,ax=plt.subplots(figsize=(11,4.8));clean(ax)
for p,label in [((1,3),'P'),((4.5,3),'Q'),((9,3),'B（同一边界）')]:point(ax,p,label)
arrow(ax,(1,3),(9,3),BLUE,r'$\mathcal{S}(P,\omega)$',offset=(0,.7))
arrow(ax,(4.5,2.55),(9,2.55),ORANGE,r'$T(P,Q)\,\mathcal{S}(Q,\omega)$',offset=(0,-.8))
ax.plot([1,4.5],[3,3],color=GREEN,lw=10,alpha=.3);ax.text(2.7,1.3,'只保留 P→Q 的路径内散射',ha='center',color=GREEN)
ax.text(5,.4,r'$L_{PQ}^{\rm ins}=\mathcal{S}(P,\omega)-T(P,Q)\mathcal{S}(Q,\omega)$',ha='center',fontsize=16);ax.set_title('空气透视：两个累计积分的差');save(fig,'14_aerial_perspective_subtraction')

# 15: shadow prefix/suffix.
fig,axs=plt.subplots(2,1,figsize=(11,5.4));
for ax in axs:clean(ax,(0,10),(0,3));ax.plot([1,9],[1.5,1.5],color=CYAN,lw=9,alpha=.3)
axs[0].plot([6.5,9],[1.5,1.5],color=INK,lw=9);point(axs[0],(1,1.5),'P');point(axs[0],(6.5,1.5),'Q');point(axs[0],(9,1.5),'地面')
axs[0].text(4.5,2.5,'看地面：用末端阴影长度截去 Q→地面的贡献',ha='center');axs[0].text(7.8,.45,r'$\ell_{\rm sh}$',ha='center')
axs[1].plot([1,3.5],[1.5,1.5],color=INK,lw=9);point(axs[1],(1,1.5),'P');point(axs[1],(3.5,1.5),'Q');point(axs[1],(9,1.5),'大气顶')
axs[1].text(4.5,2.5,'看天空：用起始阴影长度跳过 P→Q 的贡献',ha='center');axs[1].text(2.1,.45,r'$\ell_{\rm sh}$',ha='center');save(fig,'15_shadow_segments')

# 16: color pipeline and spectral mode separation.
fig,ax=plt.subplots(figsize=(12,5.8));clean(ax,(0,12),(0,6))
box(ax,(.3,3.7),2,1.3,r'$L_\lambda$'+'\n光谱辐亮度');box(ax,(3,3.7),2.2,1.3,'CIE 积分\nXYZ');box(ax,(6,3.7),2.2,1.3,'矩阵转换\n线性 sRGB');box(ax,(9.3,3.7),2.2,1.3,'曝光、色调映射\n显示编码')
arrow(ax,(2.3,4.35),(3,4.35));arrow(ax,(5.2,4.35),(6,4.35));arrow(ax,(8.2,4.35),(9.3,4.35))
box(ax,(.7,1.1),4.5,1.25,'三波长模式\n运行时近似完成光谱到颜色转换',BLUE)
box(ax,(6.2,1.1),5,1.25,'多波长预积分模式\n预计算期间积成颜色；运行时使用同样纹理',ORANGE)
ax.text(6,.35,'三个光谱样本与三个显示颜色通道具有不同语义。',ha='center',color=INK);ax.set_title('物理光谱结果到显示颜色的完整链路');save(fig,'16_color_pipeline')
print('Generated 16 SVG + 16 PNG diagrams in',OUT)
