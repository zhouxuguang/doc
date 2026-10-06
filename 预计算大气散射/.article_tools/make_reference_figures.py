"""Four geometric redraws inspired by Bruneton's functions.glsl diagrams.
The layout, colour, labels and added derivation panels are newly drawn.
Source: https://ebruneton.github.io/precomputed_atmospheric_scattering/atmosphere/functions.glsl.html
"""
from figure_style import *
from matplotlib.patches import Arc

checks={}

def shifted(v):
    return np.asarray(v)-np.array([0.,2.])

def shell(ax,rb,rt,xmin,xmax):
    x=np.linspace(xmin,xmax,1200)
    ground=np.sqrt(np.maximum(rb*rb-x*x,0))-2
    roof=np.sqrt(np.maximum(rt*rt-x*x,0))-2
    ax.fill_between(x,ground,roof,color='#eaf4fa',zorder=0)
    ax.fill_between(x,ax.get_ylim()[0],ground,color='#e5eee8',zorder=0)
    ax.plot(x,ground,color=GREEN,lw=1.8,zorder=1)
    ax.plot(x,roof,color=CYAN,lw=1.8,zorder=1)

def angular(ax,p,r,start,end,color,label=None,label_at=None):
    ax.add_patch(Arc(p,2*r,2*r,theta1=start,theta2=end,color=color,lw=1.3,ls=(0,(3,3))))
    if label and label_at is not None:
        text(ax,*label_at,label,color,17,ha='center')

def right_angle(ax,k,a,b,size=.14):
    a=np.asarray(a);b=np.asarray(b);k=np.asarray(k)
    q=np.array([k+size*a,k+size*(a+b),k+size*b])
    ax.plot(q[:,0],q[:,1],color=GRAY,lw=1.1)

# A: collinear P,Q,I plus the broken radial axis used by the source diagram.
fig=page('补图 A','透射率查询的球面几何','有限线段 P→Q 与大气顶路径 P→I，共享同一条观察射线。','参考图重绘',7.1,
         '参考 Bruneton 的透射率几何图重绘。径向轴采用断轴示意，大气厚度放大。')
ax=diagram(fig,(.055,.235,.565,.535),(-1.18,3.10),(-.62,4.16));ax.set_aspect('equal')
rb,rt,r=4.,5.6,4.6;P0=np.array([0.,r]);w=np.array([np.cos(np.deg2rad(20)),np.sin(np.deg2rad(20))])
mu=w[1];dt=-r*mu+np.sqrt(r*r*(mu*mu-1)+rt*rt)
I0=P0+dt*w;Q0=P0+.57*dt*w;P,Q,I=map(shifted,[P0,Q0,I0])
shell(ax,rb,rt,-1.18,3.10)
origin=(0.,-.18)
ax.plot([0,0],[origin[1],.67],color=INK,lw=1.4)
arrow(ax,(0,1.12),(0,3.96),INK,lw=1.4)
for yy in [.81,.95]:
    ax.plot([-.09,0,.09],[yy-.05,yy+.05,yy-.05],color=INK,lw=1.3)
arrow(ax,origin,(2.43,origin[1]),INK,lw=1.4)
text(ax,2.63,origin[1],'$x$',INK,16,ha='center');text(ax,.17,4.06,'$z$',INK,16,ha='center')
point(ax,origin,'O',(-.20,-.18))
arrow(ax,(-.67,origin[1]),(-.67,P[1]),GRAY,lw=1.2,style='<->',ls=(0,(4,3)))
text(ax,-.85,1.30,'$r$',INK,19,ha='center')
arrow(ax,P,I,BLUE,lw=2.6)
angular(ax,P,.46,20,90,BLUE,r'$\theta$',(.35,3.16))
point(ax,P,'P',(-.22,-.16));point(ax,Q,'Q',(.10,-.29));point(ax,I,'I',(.10,.25),BLUE)
notes=diagram(fig,(.65,.285,.29,.45),(0,5),(0,6))
card(notes,.02,3.28,4.77,2.16,'观察方向的天顶余弦',r'$\mu=\boldsymbol{n}_r\cdot\boldsymbol{\omega}=\cos\theta$',BLUE,body_size=18)
card(notes,.02,.30,4.77,2.30,'有限线段由两次查询恢复',r'$T_\lambda(P,Q)=\frac{T_\lambda(P,I)}{T_\lambda(Q,I)}$',GREEN,body_size=21)
formula(fig,r'$Q=P+d\boldsymbol{\omega},\qquad r_d^2=r^2+2r\mu d+d^2$',.145,21)
checks['A']={'top_radius_error':float(abs(np.linalg.norm(I0)-rt)),
             'collinear_cross_product':float(np.linalg.det(np.stack([Q0-P0,I0-P0]))),
             'Q_inside_shell':bool(rb<np.linalg.norm(Q0)<rt)}
save(fig,'bruneton_A_transmittance_geometry')

# B: both tangent lengths are evaluated from actual circle geometry.
fig=page('补图 B','距离参数化：ρ 与 H 从哪里来','最短路径沿天顶；最长有效路径沿地表切线，长度为 ρ+H。','参考图重绘',7.1,
         '参考 Bruneton 的透射率参数化图重绘。K 为切点，Iz、Ih 为两条极值射线的大气顶交点。')
ax=diagram(fig,(.055,.245,.575,.53),(-.95,5.18),(-.35,3.75));ax.set_aspect('equal')
rb,rt,r=4.,5.2,4.35;P0=np.array([0.,r]);rho=np.sqrt(r*r-rb*rb);hh=np.sqrt(rt*rt-rb*rb)
K0=np.array([rb*np.sqrt(1-rb*rb/(r*r)),rb*rb/r]);t=(K0-P0)/rho
Ih0=K0+hh*t;Iz0=np.array([0.,rt]);w=np.array([.96,.28]);dt=-r*w[1]+np.sqrt(r*r*(w[1]**2-1)+rt*rt);I0=P0+dt*w
P,K,Ih,Iz,I=map(shifted,[P0,K0,Ih0,Iz0,I0])
shell(ax,rb,rt,-.95,5.18)
arrow(ax,P,Iz,GREEN,lw=2.2);arrow(ax,P,I,BLUE,lw=2.5)
ax.plot([P[0],K[0]],[P[1],K[1]],color=BLUE,lw=2.4)
arrow(ax,K,Ih,ORANGE,lw=2.5)
right_angle(ax,K,-t,-K0/rb,.13)
ax.plot([K[0],K[0]-.5*K0[0]/rb],[K[1],K[1]-.5*K0[1]/rb],color=GRAY,ls='--',lw=1.1)
point(ax,P,'P',(-.22,-.12));point(ax,K,'K',(.13,-.28),ORANGE)
point(ax,Iz,r'$I_z$',(-.03,.28),GREEN);point(ax,I,'I',(.13,.20),BLUE)
point(ax,Ih,r'$I_h$',(.30,.16),ORANGE)
text(ax,-.54,2.82,r'$d_{\min}$',GREEN,17,ha='center')
text(ax,.88,2.30,r'$\rho$',BLUE,21,ha='center');text(ax,3.20,1.30,'$H$',ORANGE,21,ha='center')
text(ax,1.55,2.34,'$d$',BLUE,20,ha='center')
notes=diagram(fig,(.67,.265,.27,.485),(0,5),(0,6))
card(notes,.01,4.32,4.70,1.37,'最短距离',r'$d_{\min}=r_t-r$',GREEN,body_size=19)
card(notes,.01,2.48,4.70,1.37,'最长有效距离',r'$d_{\max}=\rho+H$',ORANGE,body_size=19)
card(notes,.01,.34,4.70,1.66,'归一化方向坐标',r'$x_\mu=\frac{d-d_{\min}}{d_{\max}-d_{\min}}$',BLUE,body_size=21)
formula(fig,r'$\rho^2+r_b^2=r^2,\qquad H^2+r_b^2=r_t^2$',.145,21)
checks['B']={'ground_tangent_radius_error':float(abs(np.linalg.norm(K0)-rb)),
             'perpendicular_dot':float(abs(t@(K0/rb))),
             'rho_length_error':float(abs(np.linalg.norm(K0-P0)-rho)),
             'H_length_error':float(abs(np.linalg.norm(Ih0-K0)-hh)),
             'top_radius_error':float(abs(np.linalg.norm(Ih0)-rt))}
save(fig,'bruneton_B_distance_parameterization')

# C: n_P changes to n_Q, but the view and solar directions stay fixed.
fig=page('补图 C','单次散射：移动采样点时哪些角度会变','太阳方向 s 与观察方向 ω 固定；局部天顶随 P→Q 改变。','参考图重绘',7.7,
         '参考 Bruneton 的单次散射几何图重绘。虚线弧标记角度；μ、μs、μs,d、ν 是对应余弦。')
ax=diagram(fig,(.055,.235,.565,.55),(-1.65,3.70),(.10,4.88));ax.set_aspect('equal')
rb,rt,r=4.,5.8,4.45;P0=np.array([0.,r]);w=np.array([np.cos(np.deg2rad(15)),np.sin(np.deg2rad(15))]);s=np.array([-.5,np.sqrt(3)/2]);d=1.65
Q0=P0+d*w;rd=np.linalg.norm(Q0);nQ=Q0/rd;P,Q=map(shifted,[P0,Q0])
shell(ax,rb,rt,-1.65,3.70)
ax.plot([0,0],[.30,P[1]],color=GRAY,lw=1.25,ls='--')
ax.plot([Q[0]-2.3*nQ[0],Q[0]],[Q[1]-2.3*nQ[1],Q[1]],color=GRAY,lw=1.25,ls='--')
arrow(ax,P,P+[0,1.25],INK,lw=1.5)
arrow(ax,Q,Q+1.60*nQ,INK,lw=1.5)
arrow(ax,P,Q,BLUE,lw=2.6);arrow(ax,Q,Q+1.38*w,BLUE,lw=1.6,ls='--')
arrow(ax,P,P+1.28*s,ORANGE,lw=2.1,ls='--');arrow(ax,Q,Q+1.85*s,ORANGE,lw=2.1,ls='--')
text(ax,-.24,4.07,r'$\boldsymbol{n}_P$',INK,17,ha='center');text(ax,2.32,4.46,r'$\boldsymbol{n}_Q$',INK,17,ha='center')
text(ax,-.98,4.03,r'$\boldsymbol{s}$',ORANGE,21,ha='center');text(ax,.45,4.65,r'$\boldsymbol{s}$',ORANGE,21,ha='center')
text(ax,3.18,3.48,r'$\boldsymbol{\omega}$',BLUE,21,ha='center')
angular(ax,P,.39,15,90,BLUE,r'$\mu$',(.38,2.90))
angular(ax,P,.73,90,120,ORANGE,r'$\mu_s$',(-.30,3.38))
angleQ=np.degrees(np.arctan2(nQ[1],nQ[0]))
angular(ax,Q,.50,angleQ,120,ORANGE,r'$\mu_{s,d}$',(Q[0],Q[1]+1.00))
angular(ax,Q,1.20,15,120,CYAN,r'$\nu$',(2.94,3.99))
normal=np.array([w[1],-w[0]])
arrow(ax,P+.28*normal,Q+.28*normal,GRAY,lw=1.1,style='<->')
text(ax,*(.5*(P+Q)+.51*normal),'$d$',BLUE,19,ha='center')
text(ax,-.23,1.02,'$r$',INK,20,ha='center');text(ax,1.43,1.05,r'$r_d$',INK,20,ha='center')
point(ax,P,'P',(-.23,-.19));point(ax,Q,'Q',(.18,-.28))
notes=diagram(fig,(.66,.275,.28,.48),(0,5),(0,6.3))
card(notes,.01,4.34,4.72,1.66,'起点的太阳天顶余弦',r'$\mu_s=\boldsymbol{n}_P\cdot\boldsymbol{s}$',ORANGE,body_size=19)
card(notes,.01,2.25,4.72,1.66,'采样点的太阳天顶余弦',r'$\mu_{s,d}=\frac{r\mu_s+d\nu}{r_d}$',ORANGE,body_size=21)
card(notes,.01,.16,4.72,1.66,'不随采样距离变化',r'$\nu=\boldsymbol{\omega}\cdot\boldsymbol{s}$',CYAN,body_size=20)
formula(fig,r'$r_d=\sqrt{r^2+2r\mu d+d^2},\qquad \mu_d=\frac{r\mu+d}{r_d}$',.14,21)
checks['C']={'mu_s_update_error':float(abs(nQ@s-(r*s[1]+d*(w@s))/rd)),
             'mu_update_error':float(abs(nQ@w-(r*w[1]+d)/rd)),
             'Q_inside_shell':bool(rb<rd<rt),
             'nu':float(w@s),'mu_s_P':float(s[1]),'mu_s_Q':float(nQ@s)}
save(fig,'bruneton_C_single_scattering_geometry')

# D: cache the local source once, reuse it for more than one observation point.
fig=page('补图 D','多次散射的两个积分阶段','同一个 Q 的方向积分，可以服务于多个沿同一视线排列的观察点。','参考图重绘',7.2,
         '参考 Bruneton 的多次散射复用图重绘。绿色、橙色线分别表示返回 P、P′ 的光路。')
ax=diagram(fig,(.055,.255,.57,.50),(-3.42,1.92),(-.10,4.14));ax.set_aspect('equal')
rb,rt=4.,5.6;Q0=np.array([0.,4.70]);w=np.array([np.cos(np.deg2rad(14)),np.sin(np.deg2rad(14))]);P0=Q0-2.7*w;Pp0=Q0-1.28*w
P,Pp,Q=map(shifted,[P0,Pp0,Q0]);shell(ax,rb,rt,-3.42,1.92)
ax.plot([0,0],[.30,3.93],color=GRAY,ls='--',lw=1.15)
text(ax,.23,3.93,r'$\boldsymbol{n}_Q$',GRAY,17,ha='center')
arrow(ax,P,Q+1.22*w,BLUE,lw=1.7,ls='--')
text(ax,.90,3.27,r'$\boldsymbol{\omega}$',BLUE,20,ha='center')
for delta in [(-1.03,.95),(.75,1.13),(1.42,.27)]: incoming(ax,Q+np.asarray(delta),Q,CYAN,lw=1.7,radius=.28)
ax.add_patch(Circle(Q,.15,fc='white',ec=BLUE,lw=1.8,zorder=4))
normal=np.array([w[1],-w[0]])
arrow(ax,Q+.14*normal,P+.14*normal,GREEN,lw=2.4)
arrow(ax,Q+.30*normal,Pp+.30*normal,ORANGE,lw=2.4)
point(ax,P,'P',(0,-.59),GREEN);point(ax,Pp,r"$P'$",(0,.35),ORANGE);point(ax,Q,'Q',(.42,-.36),BLUE)
notes=diagram(fig,(.66,.28,.28,.46),(0,5),(0,6))
card(notes,.01,3.75,4.71,1.73,'先计算一次局部源',r'$J^{(n)}_\lambda(Q,\boldsymbol{\omega})$',BLUE,body_size=22)
card(notes,.01,.35,4.71,2.72,'分别计算到观察点的贡献',
     r'$T_\lambda(P,Q)\,J^{(n)}_\lambda\,\mathrm{d}d$'+'\n'+r"$T_\lambda(P',Q)\,J^{(n)}_\lambda\,\mathrm{d}d$",GREEN,body_size=18)
formula(fig,'二维方向积分  →  散射密度 LUT  →  一维路径积分',.145,17)
checks['D']={'collinear_cross_product':float(abs(np.linalg.det(np.stack([Q0-P0,Q0-Pp0])))),
             'points_inside_shell':bool(all(rb<np.linalg.norm(v)<rt for v in [P0,Pp0,Q0]))}
save(fig,'bruneton_D_scattering_density_reuse')

assert max(checks['A']['top_radius_error'],abs(checks['A']['collinear_cross_product']))<1e-12
assert all(v<1e-12 for v in checks['B'].values())
assert checks['C']['mu_s_update_error']<1e-12 and checks['C']['mu_update_error']<1e-12
assert checks['A']['Q_inside_shell'] and checks['C']['Q_inside_shell'] and checks['D']['points_inside_shell']
assert checks['D']['collinear_cross_product']<1e-12
(QA/'reference_geometry_validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
(QA/'reference_figure_layout_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps({'new_figures':len(audit),'text_overlaps':sum(len(v['overlaps']) for v in audit),
                  'outside_canvas':sum(len(v['outside_canvas']) for v in audit)},ensure_ascii=False))
