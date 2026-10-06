"""Generate the article's sixteen original technical diagrams."""
from figure_style import *

# 01: boundary geometry, with explanations separate from the ray diagram.
fig=page(2,'球形大气壳与边界交点','同一条射线的边界类型，由半径和局部方向共同决定。','几何',7,
         '大气厚度按示意需要放大；地球预设的大气厚度约为地表半径的 1%。')
ax=diagram(fig,(.07,.18,.46,.60),(-1.55,1.55),(-1.35,1.65));ax.set_aspect('equal')
ax.add_patch(Circle((0,0),1.35,fc='#eaf5fa',ec=CYAN,lw=1.8))
ax.add_patch(Circle((0,0),1,fc='#e4eee8',ec=GREEN,lw=1.8))
p=np.array([0.,1.16]);v=np.array([.94,np.sqrt(1-.94**2)])
d=-p@v+np.sqrt((p@v)**2+1.35**2-p@p);I=p+d*v
vg=np.array([.55,-np.sqrt(1-.55**2)]);dg=-p@vg-np.sqrt((p@vg)**2+1-p@p);G=p+dg*vg
K=np.array([np.sqrt(1-1/1.16**2),1/1.16]);vk=(K-p)/np.linalg.norm(K-p)
dk=-p@vk+np.sqrt((p@vk)**2+1.35**2-p@p);Kt=p+dk*vk
arrow(ax,p,I,BLUE);arrow(ax,p,G,RED);arrow(ax,p,Kt,ORANGE,ls='--')
arrow(ax,(0,0),p,INK,lw=1.6);text(ax,-.10,.57,'$r$',INK,17,ha='right')
# Draw actual center-to-boundary radii; annotations stay outside the rays.
arrow(ax,(0,0),(-.87,-.493),GREEN,lw=1.2);text(ax,-.49,-.13,'$r_b$',GREEN,17,ha='center')
arrow(ax,(0,0),(-1.20,.618),CYAN,lw=1.2);text(ax,-.79,.58,'$r_t$',CYAN,17,ha='center')
point(ax,(0,0),'O',(.10,-.18));point(ax,p,'P',(-.12,.34))
point(ax,I,'I',(.09,.07),BLUE);point(ax,G,'G',(.01,-.27),RED);point(ax,K,'K',(.16,-.19),ORANGE)
notes=diagram(fig,(.59,.20,.35,.59),(0,5),(0,6))
card(notes,.08,4.16,4.75,1.5,'I · 大气顶边界',r'$d_t$: 沿射线到 $r_t$ 球面的距离',BLUE)
card(notes,.08,2.22,4.75,1.5,'G · 地面边界',r'$d_b$: 射线首先到达地表',RED)
card(notes,.08,.28,4.75,1.5,'K · 地表切点',r'$\mu_h=-\sqrt{1-r_b^2/r^2}$',ORANGE,body_size=17)
save(fig,'01_spherical_geometry')

# 02: split forward direction and physical propagation onto parallel lanes.
fig=page(1,'观察方向与光传播方向','定义方向时先看“指向哪里”；计算散射角时再看光子的传播方向。','方向约定',6.7)
ax=diagram(fig,(.06,.27,.88,.51),(0,12),(0,5.8))
p=np.array([1.4,2.15]);q=np.array([6.,2.15]);s=np.array([10.2,4.8])
arrow(ax,p+[0,.19],q+[0,.19],BLUE,ls='--');arrow(ax,q-[0,.19],p-[0,.19],RED)
text(ax,3.7,2.92,r'观察方向 $\boldsymbol{\omega}$',BLUE,14,ha='center')
text(ax,3.7,1.23,r'光传播方向 $-\boldsymbol{\omega}$',RED,13,ha='center')
u=(s-q)/np.linalg.norm(s-q);n=np.array([-u[1],u[0]])
arrow(ax,q+.16*n,s+.16*n,ORANGE,ls='--');arrow(ax,s-.16*n,q-.16*n,RED)
text(ax,7.65,4.48,r'指向太阳 $\boldsymbol{s}$',ORANGE,14,ha='center')
text(ax,9.5,2.72,r'入射光 $-\boldsymbol{s}$',RED,13,ha='center')
arrow(ax,p,p+[0,2.5],INK,lw=1.6);text(ax,.65,3.75,r'$\boldsymbol{n}_r$',INK,18,ha='center')
point(ax,p,'P',(0,-.51));point(ax,q,'Q',(0,-.51));point(ax,s,'太阳',(0,.40),ORANGE)
formula(fig,r'$\mu=\boldsymbol{n}_r\cdot\boldsymbol{\omega},\quad \mu_s=\boldsymbol{n}_r\cdot\boldsymbol{s},\quad \nu=\boldsymbol{\omega}\cdot\boldsymbol{s}$',.155,20)
save(fig,'02_direction_convention')

# 03: density curves, calculated from the stated profiles.
fig=page(3,'大气密度剖面','不同成分占据不同高度范围；剖面控制局部系数，不是沿路径的光学厚度。','物理模型',6.7,
         '示例参数采用参考实现的地球预设；各密度函数均无量纲。')
ax=chart(fig,(.10,.19,.80,.51),r'归一化密度 $D_i(h)$','高度 $h$ / km')
h=np.linspace(0,60,900)
ax.plot(np.exp(-h/8),h,lw=2.8,color=BLUE)
ax.plot(np.exp(-h/1.2),h,lw=2.8,color=ORANGE)
oz=np.clip(np.where(h<25,(h-10)/15,(40-h)/15),0,1);ax.plot(oz,h,lw=2.8,color=GREEN)
ax.set(xlim=(0,1.04),ylim=(0,60),xticks=np.linspace(0,1,6))
legend(fig,[(r'Rayleigh：$H_R=8$ km',BLUE,'-'),(r'气溶胶：$H_M=1.2$ km',ORANGE,'-'),('臭氧：10–40 km',GREEN,'-')])
save(fig,'03_density_profiles')

# 04: linear plot has an explicit angular window; log plot preserves the forward peak.
fig=page(4,'Rayleigh 与气溶胶相函数','气溶胶前向峰跨越多个数量级，需要同时观察角度细节和整体动态范围。','角分布',6.7,
         r'相函数满足球面积分为 1；纵轴单位为 $\mathrm{sr}^{-1}$。角度 0° 表示前向散射。')
ang=np.linspace(0,180,1801);nu=np.cos(np.radians(ang));pr=3/(16*np.pi)*(1+nu*nu)
axes=[chart(fig,(.08,.20,.38,.44),'散射角 / 度',r'相函数 / sr$^{-1}$','20°–180° · 线性尺度'),
      chart(fig,(.57,.20,.36,.44),'散射角 / 度',r'相函数 / sr$^{-1}$','0°–180° · 对数尺度')]
for ax in axes:
    ax.plot(ang,pr,color=BLUE,lw=2.7)
    for g,c in [(.5,GREEN),(.8,ORANGE),(.9,RED)]:
        pm=3/(8*np.pi)*(1-g*g)*(1+nu*nu)/((2+g*g)*(1+g*g-2*g*nu)**1.5)
        ax.plot(ang,pm,color=c,lw=2.4)
axes[0].set(xlim=(20,180),ylim=(0,.66),xticks=[20,60,100,140,180])
axes[1].set(xlim=(0,180),yscale='log',ylim=(.002,30),xticks=[0,45,90,135,180])
legend(fig,[('Rayleigh',BLUE,'-'),('$g=0.5$',GREEN,'-'),('$g=0.8$',ORANGE,'-'),('$g=0.9$',RED,'-')])
save(fig,'04_phase_functions')

# 05: composable line segments and Beer–Lambert.
fig=page(5,'透射率的组合与指数衰减','把相邻线段的光学厚度相加，就得到透射率相乘的性质。','路径积分',6.7,
         '组合关系要求 P、Q、I 沿同一光路依次排列，且线段内部没有实体遮挡。')
ax=diagram(fig,(.06,.21,.49,.53),(0,10),(0,6))
for x,l in [(1,'P'),(4.4,'Q'),(9,'I')]: point(ax,(x,3.1),l)
arrow(ax,(1,3.1),(4.4,3.1),BLUE);arrow(ax,(4.4,3.1),(9,3.1),CYAN)
text(ax,2.7,3.95,r'$T_\lambda(P,Q)$',BLUE,18,ha='center')
text(ax,6.7,3.95,r'$T_\lambda(Q,I)$',CYAN,18,ha='center')
card(ax,.35,.52,9.3,1.25,r'$T_\lambda(P,I)=T_\lambda(P,Q)\,T_\lambda(Q,I)$',color=INK,size=19)
ax=chart(fig,(.65,.22,.28,.49),r'光学厚度 $\tau_\lambda$',r'$T_\lambda$', 'Beer–Lambert 定律')
tau=np.linspace(0,8,500);ax.plot(tau,np.exp(-tau),color=BLUE,lw=2.8);ax.set(xlim=(0,8),ylim=(0,1.04))
save(fig,'05_transmittance_chain')

# 06: distinguish incoming attenuation, local source and outgoing attenuation.
fig=page(6,'单次散射：太阳 → Q → 观察点','太阳光在 Q 处改变传播方向，再沿观察射线到达 P。','单次散射',6.7,
         '对整条观察路径的所有 Q 积分；两段透射率与局部散射系数都随采样点变化。')
ax=diagram(fig,(.06,.26,.58,.50),(0,10),(0,5.8))
p=(1.1,1.75);q=(5.8,1.75);s=(8.8,5.1)
ax.plot([p[0],9.4],[p[1],p[1]],color=BLUE,lw=8,alpha=.08)
arrow(ax,q,p,BLUE,lw=2.7);incoming(ax,s,q,ORANGE,lw=2.7)
ax.add_patch(Circle(q,.25,fc='#fff0db',ec=ORANGE,lw=2,zorder=4))
point(ax,p,'P');point(ax,q,'Q',(.15,-.55));point(ax,s,'太阳',(.05,.42),ORANGE)
text(ax,6.30,4.42,'① 太阳入射',ORANGE,14,ha='center')
text(ax,3.3,2.45,'③ 向 P 传播',BLUE,14,ha='center')
text(ax,6.85,.67,'② 局部散射',GREEN,14,ha='center')
notes=diagram(fig,(.69,.28,.25,.48),(0,5),(0,6))
card(notes,.05,3.3,4.7,2.1,'太阳到 Q',r'$E_{\odot,\lambda}T_{\odot,\lambda}(Q)$',ORANGE,body_size=18)
card(notes,.05,.42,4.7,2.1,'Q 到观察点 P',r'$T_\lambda(P,Q)$',BLUE,body_size=19)
formula(fig,r'$L^{(1)}_\lambda=p_R(\nu)C_{R,\lambda}+p_M(g,\nu)C_{M,\lambda}$',.14,20)
save(fig,'06_single_scattering_path')

# 07: radial and angular distance parameterizations.
fig=page(7,'透射率 LUT：用距离分配采样','半径用地表切线距离编码，方向用到大气顶的边界距离编码。','二维 LUT',7.0,
         '坐标范围为 [0,1]；写入纹理前还要应用纹素中心修正。右图取 h=1 km。')
ax=chart(fig,(.09,.28,.36,.39),'高度 $h$ / km','单位区间坐标', '半径映射')
h=np.linspace(0,60,600);xr=np.sqrt((RB+h)**2-RB**2)/H
ax.plot(h,xr,color=BLUE,lw=2.7);ax.plot(h,h/60,color=GRAY,lw=1.8,ls='--');ax.set(xlim=(0,60),ylim=(0,1.03))
# Sample markers sit in a separate strip below the axis labels.
strip=diagram(fig,(.09,.14,.36,.025),(0,60),(0,1))
xs=np.linspace(0,1,32);hs=np.sqrt((H*xs)**2+RB*RB)-RB
strip.scatter(hs,np.ones_like(hs)*.5,color=ORANGE,s=13,clip_on=False)
ax=chart(fig,(.59,.28,.34,.39),r'方向余弦 $\mu$',r'$x_\mu$', '到大气顶的距离映射')
r=RB+1;rho=np.sqrt(r*r-RB*RB);mh=-rho/r;mu=np.linspace(mh,1,800)
xm=(top(r,mu)-(RT-r))/(rho+H-(RT-r));ax.plot(mu,xm,color=BLUE,lw=2.7)
ax.axvline(mh,color=ORANGE,ls='--',lw=1.5);ax.set(xlim=(mh-.02,1),ylim=(0,1.03))
legend(fig,[(r'$x_r=\rho/H$',BLUE,'-'),('高度线性映射',GRAY,'--'),('32 个半径采样位置',ORANGE,'-')],y=.777)
save(fig,'07_transmittance_mapping')

# 08: do not interpolate across the ground/non-ground horizon split.
fig=page(8,'地平线两侧：边界距离与纹理分区','接近切线时两侧路径都很长，但边界类型不同，必须分别编码。','四维 LUT',6.7,
         '左侧到地面，右侧到大气顶；uμ 在两侧分别逼近 0 和 1，不跨越地平线插值。')
r=RB+1;rho=np.sqrt(r*r-RB*RB);mh=-rho/r
mg=np.linspace(mh-.075,mh-1e-9,500);mt=np.linspace(mh+1e-9,mh+.075,500)
dg=bottom(r,mg);dt=top(r,mt)
ug=.5-.5*tex((dg-(r-RB))/(rho-(r-RB)),64)
ut=.5+.5*tex((dt-(RT-r))/(rho+H-(RT-r)),64)
ax=chart(fig,(.09,.23,.36,.45),r'$\mu-\mu_h$','边界距离 / km','两种边界的路径长度')
ax.plot(mg-mh,dg,color=RED,lw=2.7);ax.plot(mt-mh,dt,color=BLUE,lw=2.7);ax.axvline(0,color=GRAY,ls=':',lw=1.2)
ax.set(xlim=(-.075,.075),ylim=(0,max(dt)*1.06),xticks=[-.075,-.05,-.025,0,.025,.05,.075])
ax=chart(fig,(.59,.23,.34,.45),r'$\mu-\mu_h$',r'$u_\mu$','纹理上下半区分开存储')
ax.plot(mg-mh,ug,color=RED,lw=2.7);ax.plot(mt-mh,ut,color=BLUE,lw=2.7)
ax.axvline(0,color=GRAY,ls=':',lw=1.2);ax.axhline(.5,color=LINE,ls='--');ax.set(xlim=(-.075,.075),ylim=(0,1),xticks=[-.075,-.05,-.025,0,.025,.05,.075])
legend(fig,[('命中地面',RED,'-'),('不命中地面',BLUE,'-')],y=.765)
save(fig,'08_horizon_split')

# 09: exact reference mapping versus the legacy approximation.
fig=page(9,'太阳方向映射：把分辨率留给日出日落','通过到大气顶的距离变换，非均匀采样太阳天顶余弦。','太阳坐标',6.7,
         '示例 μs,min=−0.2，rb=6360 km、rt=6420 km；公式与引擎差异见正文。')
dmin=RT-RB;dmax=H
mus=np.linspace(-.24,1,1000);a=(top(RB,mus)-dmin)/(dmax-dmin)
A=(top(RB,-.2)-dmin)/(dmax-dmin);Aa=-2*(-.2)*RB/(dmax-dmin)
xexact=np.maximum(1-a/A,0)/(1+a);xapprox=np.maximum(1-a/Aa,0)/(1+a)
ax=chart(fig,(.09,.24,.39,.45),r'$\mu_s$',r'$x_{\mu_s}$','正映射')
ax.plot(mus,xexact,color=BLUE,lw=2.7);ax.plot(mus,xapprox,color=ORANGE,lw=2,ls='--');ax.set(xlim=(-.24,1),ylim=(0,1.02))
ax=chart(fig,(.61,.30,.31,.34),r'太阳天顶余弦 $\mu_s$','', '32 个太阳方向采样位置')
xs=np.linspace(0,1,32);av=A*(1-xs)/(1+A*xs);dv=dmin+np.minimum(av,A)*(dmax-dmin)
ms=(H*H-dv*dv)/(2*RB*dv)
ax.plot(ms,np.ones(32)*.6,ls='none',marker='|',ms=15,mew=1.5,color=BLUE,zorder=3)
ax.set(xlim=(-.24,1.03),ylim=(0,1),yticks=[]);ax.spines['left'].set_visible(False);ax.grid(axis='y',visible=False)
legend(fig,[('新版参考实现：精确 A',BLUE,'-'),('当前引擎：近似 A',ORANGE,'--')],y=.765)
save(fig,'09_sun_mapping')

# 10: Gram constraint for physically realizable angles.
fig=page(10,'三个方向余弦的可实现范围','固定 μ 后，ν 仍受太阳方向 μs 约束，三个坐标不能任意组合。','角度约束',6.7,
         '示例 μ=0.3。边界对应两方向在局部切平面中的方位差为 0 或 π。')
ax=chart(fig,(.11,.20,.78,.49),r'太阳方向余弦 $\mu_s$',r'$\nu=\boldsymbol{\omega}\cdot\boldsymbol{s}$')
ms=np.linspace(-1,1,801);m=.3;c=m*ms;w=np.sqrt(1-m*m)*np.sqrt(1-ms*ms)
ax.fill_between(ms,c-w,c+w,color=BLUE,alpha=.12);ax.plot(ms,c-w,color=BLUE,lw=2.5);ax.plot(ms,c+w,color=BLUE,lw=2.5)
ax.plot(ms,c,color=ORANGE,lw=2,ls='--');ax.set(xlim=(-1,1),ylim=(-1.04,1.04))
legend(fig,[('可实现边界',BLUE,'-'),(r'中心 $\mu\mu_s$',ORANGE,'--')],y=.765)
save(fig,'10_valid_nu_domain')

# 11: storage layout, dimension annotations stay outside the texture.
fig=page(11,'四维散射数据如何打包进三维纹理','x 轴拼接 ν 切片，每个切片内部沿 μs 插值；z 轴保存半径层。','存储布局',7.0,
         '运行时分别采样相邻 ν 切片再手动插值，避免跨切片的硬件三线性插值。')
ax=diagram(fig,(.06,.18,.88,.60),(0,14),(0,6))
for i in range(8):
    x=1.3+i*1.5
    ax.add_patch(Rectangle((x,2.65),1.5,2.1,fc=BLUE,ec='white',lw=2,alpha=.09+.025*i))
    for j in range(1,32): ax.plot([x+j*1.5/32]*2,[2.65,4.75],color=BLUE,alpha=.12,lw=.5)
    ax.plot([x,x],[2.65,4.75],color=BLUE,alpha=.35,lw=1.2)
    text(ax,x+.75,5.18,rf'$\nu_{i}$',BLUE,17,ha='center')
arrow(ax,(.82,2.65),(.82,4.75),INK,lw=1.3,style='<->')
text(ax,.37,3.70,r'128 · $\mu$',INK,12,ha='center',rotation=90)
arrow(ax,(1.3,2.15),(13.3,2.15),INK,lw=1.3,style='<->')
text(ax,7.3,1.74,r'256 = 8 个 $\nu$ 切片 × 32 个 $\mu_s$ 样本',INK,14,ha='center')
card(ax,1.3,.23,5.7,1.0,r'$z$: 32 个半径 $r$ 层',color=GREEN,size=15)
card(ax,7.6,.23,5.7,1.0,r'$x=(i_\nu+u_{\mu_s})/8$',color=BLUE,size=17)
save(fig,'11_texture_packing')

# 12: incoming directions and reflected illumination are sources for one more event.
fig=page(12,'多次散射的局部源项','把各方向的上一阶入射辐亮度汇总，再发生一次散射。','递推物理',7.0,
         r'阶次按散射或反射事件计数：地面反射增加一阶，Q 处的体积散射再增加一阶。')
ax=diagram(fig,(.06,.26,.52,.49),(0,10),(0,6))
q=(5.4,2.8);p=(1.1,2.8);g=(8.3,.9)
for a in [(3.4,5.3),(7.5,5.2),(9.,3.8)]: incoming(ax,a,q,CYAN,lw=2)
incoming(ax,g,q,ORANGE,lw=2.5);arrow(ax,q,p,BLUE,lw=2.6)
ax.add_patch(Circle(q,.26,fc='#ecf4f9',ec=BLUE,lw=1.8,zorder=4))
point(ax,p,'P');point(ax,q,'Q',(.10,-.53));point(ax,g,'G',(0,-.40),ORANGE)
text(ax,2.0,5.60,r'各方向 $L^{(n-1)}_\lambda$',CYAN,15)
text(ax,2.8,3.52,r'向观察点传播',BLUE,13,ha='center')
notes=diagram(fig,(.64,.27,.30,.49),(0,5),(0,6))
card(notes,.02,3.33,4.80,2.15,'地面反射后到 Q',r'$T_\lambda(Q,G)\,\frac{a_g}{\pi}E^{(n-2)}_\lambda$',ORANGE,body_size=17)
card(notes,.02,.42,4.80,2.15,'局部散射源',r'$J^{(n)}_\lambda=\int_{4\pi}\mathcal{B}_\lambda I_\lambda^{(n-1)}\,\mathrm{d}\Omega$',BLUE,body_size=17)
formula(fig,'入射已有 n−1 次事件  +  Q 处再散射一次  =  第 n 阶',.145,16)
save(fig,'12_multiple_scattering_paths')

# 13: chronological stages; input versions are explicit, no diagonal edges through boxes.
fig=page(13,'一轮递推：先消费旧阶次，再更新临时纹理','三个 Pass 按执行顺序排列；每个框分别列出读取内容和写入结果。','预计算调度',7.5,
         r'$n=2$ 时由 $C_R$、$C_M$ 恢复 $L^{(1)}$；必须先读取旧 $E$，再覆盖 $\Delta E$。累计辐照度另存。')
ax=diagram(fig,(.06,.18,.88,.60),(0,12),(0,6.5))
stages=[('01','散射密度',r'$L^{(n-1)}_\lambda,\ E^{(n-2)}_\lambda,\ T_\lambda$',
         '对入射方向积分',r'$\Delta J\leftarrow J^{(n)}_\lambda$','保存本阶的局部源项',BLUE),
        ('02','间接辐照度',r'$L^{(n-1)}_\lambda$',
         '对上半球积分',r'$\Delta E\leftarrow E^{(n-1)}_\lambda$',r'累计到天空辐照度 $E_{\mathrm{sky}}$',GREEN),
        ('03','多次散射',r'$J^{(n)}_\lambda,\ T_\lambda$',
         '沿观察路径积分',r'$\Delta L\leftarrow L^{(n)}_\lambda$',r'累计到散射纹理 $\mathcal{C}$',ORANGE)]
for i,(num,title,inp,action,out,desc,color) in enumerate(stages):
    x=.10+4*i;w=3.68
    ax.add_patch(FancyBboxPatch((x,.65),w,5.45,boxstyle='round,pad=.02,rounding_size=.13',fc=LIGHT,ec=LINE,lw=1.2))
    text(ax,x+.27,5.62,num,color,18);text(ax,x+.95,5.62,title,color,16)
    text(ax,x+.28,4.83,'读取',GRAY,12)
    # Longest input is two lines to keep it inside its column.
    if i==0:
        text(ax,x+w/2,4.20,r'$L^{(n-1)}_\lambda,\ E^{(n-2)}_\lambda$',INK,17,ha='center')
        text(ax,x+w/2,3.60,r'$T_\lambda$',INK,17,ha='center')
    else: text(ax,x+w/2,4.10,inp,INK,18,ha='center')
    text(ax,x+w/2,2.95,action,GRAY,13,ha='center')
    ax.plot([x+.25,x+w-.25],[2.52,2.52],color=LINE,lw=1.2)
    text(ax,x+w/2,1.91,out,color,18,ha='center')
    text(ax,x+w/2,1.13,desc,INK,12,ha='center')
    if i<2: arrow(ax,(x+w+.03,4.9),(x+4-.03,4.9),GRAY,lw=1.5)
save(fig,'13_precompute_dependencies')

# 14: an interval decomposition of the scattering subtraction identity.
fig=page(14,'有限距离空气透视：累计积分的尾段相减',r'$\mathcal{S}(P)$ 和 $\mathcal{S}(Q)$ 使用同一个物理方向、同一个边界 B。','运行时查询',6.7,
         'Q 位于 P 到 B 的同一有效线段内；差分结果是 [P,Q] 上产生并到达 P 的辐亮度。')
ax=diagram(fig,(.06,.27,.88,.49),(0,12),(0,6))
for x,l in [(1.1,'P'),(5.2,'Q'),(10.8,'B')]:
    ax.plot([x,x],[.55,5.0],color=LINE,ls='--',lw=1.3);text(ax,x,5.45,l,INK,15,ha='center')
rows=[(4.48,1.1,10.8,BLUE,r'$\mathcal{S}_\lambda(P)$'),(2.90,5.2,10.8,ORANGE,r'$T_\lambda(P,Q)\mathcal{S}_\lambda(Q)$'),(1.25,1.1,5.2,GREEN,r'$L^{\mathrm{ins}}_{PQ,\lambda}$')]
for y,x1,x2,c,l in rows:
    ax.plot([x1,x2],[y,y],color=c,lw=9,alpha=.17);arrow(ax,(x1,y),(x2,y),c,lw=2.4)
    text(ax,(x1+x2)/2,y+.50,l,c,18,ha='center')
formula(fig,r'$L^{\mathrm{ins}}_{PQ,\lambda}=\mathcal{S}_\lambda(P)-T_\lambda(P,Q)\mathcal{S}_\lambda(Q)$',.145,20)
save(fig,'14_aerial_perspective_subtraction')

# 15: different conventions for sky prefix and finite-distance suffix shadows.
fig=page(15,'shadow_length 对应哪一段路径','标量长度只有在阴影位置约定明确时，才能代表实际阴影区间。','阴影近似',6.7,
         '真实阴影可能由多个不连续区间组成；参考接口用单个前缀或末端区间近似。')
for bounds,split,title,shadow_side in [((.06,.27,.42,.46),7.6,'有限距离：阴影位于末端','suffix'),
                                        ((.54,.27,.40,.46),4.2,'天空查询：阴影位于前缀','prefix')]:
    ax=diagram(fig,bounds,(0,12),(0,5.8));text(ax,6,5.18,title,INK,14,ha='center')
    p=1.;b=10.8;y=2.5
    ax.plot([p,b],[y,y],color=CYAN,lw=8,alpha=.20)
    sh=(split,b) if shadow_side=='suffix' else (p,split)
    lit=(p,split) if shadow_side=='suffix' else (split,b)
    ax.plot(list(sh),[y,y],color=INK,lw=8,alpha=.7)
    text(ax,sum(lit)/2,3.40,'受光段',CYAN,13,ha='center');text(ax,sum(sh)/2,3.40,'阴影段',INK,13,ha='center')
    point(ax,(p,y),'P',(0,-.39));point(ax,(b,y),'Q' if shadow_side=='suffix' else 'B',(0,-.39))
    ax.plot([split,split],[y-.18,y+.18],color=INK,lw=1.5)
    arrow(ax,(sh[0],1.39),(sh[1],1.39),INK,lw=1.2,style='<->')
    text(ax,sum(sh)/2,.75,r'$\ell_{\mathrm{shadow}}$',INK,18,ha='center')
save(fig,'15_shadow_segments')

# 16: reference spectral-to-display conversion, with two implementation options.
fig=page(16,'从光谱辐亮度到最终显示颜色','物理积分、色度转换与显示映射是不同步骤，单位和数据语义应逐步对应。','颜色流程',7.0,
         '本图描述参考实现的颜色流程；GNXEngine 当前直接使用三波长通道，尚未完成此转换。')
ax=diagram(fig,(.06,.18,.88,.61),(0,12.6),(0,6.3))
steps=[(r'$L_\lambda$','光谱辐亮度',BLUE),('XYZ','CIE 色匹配积分',CYAN),('线性 sRGB','XYZ → RGB 矩阵',GREEN),('显示颜色','曝光 → 色调映射 → 编码',ORANGE)]
for i,(title,body,c) in enumerate(steps):
    x=.03+i*3.17
    card(ax,x,3.9,2.68,1.84,title,body,c,size=17,body_size=10.5 if i==3 else 11.5)
    if i<3: arrow(ax,(x+2.79,4.82),(x+3.06,4.82),GRAY,lw=1.5)
card(ax,.03,.62,5.73,2.17,'三波长模式','三个代表波长预计算\n运行时使用参考实现的颜色转换系数',BLUE,size=15,body_size=12)
card(ax,6.42,.62,5.73,2.17,'多波长模式','分组计算并积分到颜色通道\n运行时直接查询已转换的 LUT',GREEN,size=15,body_size=12)
save(fig,'16_color_pipeline')

(QA/'figure_layout_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps({'figures':len(audit),'text_overlaps':sum(len(v['overlaps']) for v in audit),
                  'outside_canvas':sum(len(v['outside_canvas']) for v in audit)},ensure_ascii=False))
