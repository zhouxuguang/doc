"""Four scientific diagrams for the expanded main-text explanations.
Only new SVG/PNG assets are generated; source code and frame captures are read-only.
"""
from figure_style import *
from matplotlib.colors import LinearSegmentedColormap

checks={}

# G: distinguish physical normalization, texel centres and interpolation.
fig=page('补图 G','LUT 的两条路：预计算反解，运行时编码',
         '参数化决定每个纹素代表哪种物理状态；纹素中心修正决定硬件怎样采样。',
         '算法拆解',8.5,
         '下方用 N=4 的单轴例子讲纹素中心。实际大气 LUT 的每一轴各有自己的尺寸与映射。')
ax=diagram(fig,(.06,.205,.88,.60),(-.1,12.1),(0,8.4))
card(ax,.02,6.02,3.40,1.60,'物理状态',r'$(r,\mu,\mu_s,\nu)$',BLUE,body_size=20)
card(ax,4.16,6.02,3.48,1.60,'距离、分支与归一化',r'$x\in[0,1]$',CYAN,body_size=20)
card(ax,8.40,6.02,3.43,1.60,'纹理中心与打包',r'$u=\mathcal{U}_N(x)$',GREEN,body_size=20)
arrow(ax,(3.45,6.85),(4.10,6.85),BLUE);arrow(ax,(7.67,6.85),(8.34,6.85),BLUE)
text(ax,5.98,8.02,'运行时：从真实相机状态编码，查询已有纹理',BLUE,13,ha='center')
arrow(ax,(10.15,5.50),(1.68,5.50),GREEN,lw=1.8)
text(ax,5.98,5.00,'预计算：从当前纹素反解物理状态，计算积分后写回',GREEN,13,ha='center')
text(ax,.10,3.60,'物理 x',INK,13,ha='left');text(ax,.10,1.60,'纹理 u',INK,13,ha='left')
base=1.45;length=10.0
ax.plot([base,base+length],[3.60,3.60],color=GRAY,lw=1.1)
for k in range(4):
    x=k/3;u=tex(x,4);xp=base+length*x;up=base+length*u
    ax.plot(xp,3.60,'o',ms=6,color=BLUE)
    text(ax,xp,4.00,['0','1/3','2/3','1'][k],BLUE,13,ha='center')
    ax.add_patch(Rectangle((base+length*k/4,1.36),length/4,.48,fc=LIGHT,ec=LINE,lw=1))
    ax.plot(up,1.60,'o',ms=6,color=GREEN)
    text(ax,up,1.03,f'{u:.3f}',GREEN,13,ha='center')
    ax.plot([xp,up],[3.42,1.87],color=LINE,lw=1.0,ls='--')
x=.4;u=tex(x,4)
ax.plot(base+length*x,3.60,'o',ms=8,color=ORANGE)
ax.plot(base+length*u,1.60,'o',ms=8,color=ORANGE)
arrow(ax,(base+length*x,3.39),(base+length*u,1.89),ORANGE,lw=2.2)
text(ax,8.52,2.91,r'$x=0.4\ \longrightarrow\ u=0.425$',ORANGE,19,ha='center',bbox=dict(fc='white',ec='none',pad=3))
text(ax,8.52,2.39,'落在第 1、2 号纹素中心之间',GRAY,12,ha='center',bbox=dict(fc='white',ec='none',pad=3))
formula(fig,r'$Nu-\frac{1}{2}=1.2\quad\Longrightarrow\quad F=0.8F_1+0.2F_2$',.125,21)
checks['G']={'x':x,'u':float(u),'hardware_index':float(4*u-.5),
             'round_trip_error':float(abs((u-.125)/.75-x))}
save(fig,'explain_G_lut_encoding_and_texel_centers')

# H: angular quadrature has two different geometric weights.
fig=page('补图 H','角积分的权重：立体角与接收面投影',
         '相同的角度步长不代表相同立体角。辐照度还要乘接收面的余弦。',
         '数学与数值',8.0,
         '图中曲线只表示几何权重，实际积分还要乘入射光、散射系数和相函数。')
left=chart(fig,(.10,.315,.355,.425),'方位角 φ / °','天顶角 θ / °','全方向源项：16 × 32 个方向样本')
th=np.linspace(0,np.pi,17);ph=np.linspace(0,2*np.pi,33);tm=.5*(th[1:]+th[:-1]);pm=.5*(ph[1:]+ph[:-1])
weight=np.repeat(np.sin(tm)[:,None],32,axis=1)
cmap=LinearSegmentedColormap.from_list('angular_weight',['#f4f8fc','#91cfda','#2297ad'])
left.pcolormesh(np.rad2deg(ph),np.rad2deg(th),weight,cmap=cmap,vmin=0,vmax=1,
                edgecolors='white',linewidth=.35)
left.set(xlim=(0,360),ylim=(180,0),xticks=[0,90,180,270,360],yticks=[0,45,90,135,180])
left.grid(False)
for j in (0,7):
    left.add_patch(Rectangle((225,np.rad2deg(th[j])),11.25,11.25,fc='none',ec=ORANGE,lw=1.8))
left.annotate('极区权重 0.098',xy=(230.625,5.625),xytext=(62,22),fontsize=11.5,color=INK,
              arrowprops=dict(arrowstyle='->',color=ORANGE,lw=1.2))
left.annotate('近赤道权重 0.995',xy=(230.625,84.375),xytext=(40,116),fontsize=11.5,color=INK,
              bbox=dict(fc='white',ec='none',alpha=.88,pad=3),
              arrowprops=dict(arrowstyle='->',color=ORANGE,lw=1.2))
right=chart(fig,(.57,.315,.355,.425),'天顶角 θ / °','几何权重 / 无量纲','源项用全球面，地面照明用上半球')
t=np.linspace(0,np.pi,721);td=np.rad2deg(t)
right.plot(td,np.sin(t),color=BLUE,lw=2.5,label=r'$\sin\theta$')
right.plot(td,np.where(t<=np.pi/2,np.sin(t)*np.cos(t),np.nan),color=GREEN,lw=2.5,
           label=r'$\sin\theta\cos\theta$')
right.plot([90,180],[0,0],color=GREEN,lw=1.2,ls='--')
right.axvline(90,color=GRAY,lw=1.1,ls=':')
right.set(xlim=(0,180),ylim=(-.025,1.12),xticks=[0,45,90,135,180],yticks=[0,.25,.5,.75,1])
right.legend(loc='upper right',frameon=False,fontsize=12)
notes=diagram(fig,(.06,.125,.88,.12),(-.08,12.08),(0,1.6))
card(notes,0,.10,5.73,1.30,'局部散射源：没有表面投影余弦',
     r'$J_\lambda\approx\sum I_\lambda\mathcal{B}_\lambda\sin\theta\,\Delta\theta\Delta\phi$',BLUE,body_size=17)
card(notes,6.25,.10,5.73,1.30,'水平面辐照度：额外乘 cos θ',
     r'$E_\lambda\approx\sum_{\theta<\pi/2}L_\lambda\cos\theta\sin\theta\,\Delta\theta\Delta\phi$',GREEN,body_size=16)
checks['H']={'polar_midpoint_sine':float(np.sin(tm[0])),
             'equatorial_midpoint_sine':float(np.sin(tm[7])),
             'midpoint_solid_angle_sum_sr':float(np.sum(weight)*(np.pi/16)*(2*np.pi/32))}
save(fig,'explain_H_solid_angle_and_irradiance_weights')

# I: the standard n=2 round and the exact moment when each shared texture changes.
fig=page('补图 I','纹理复用：旧入射场读完，才能覆盖成新一阶',
         '用 n=2 的一轮标准递推说明覆盖与累加。当前引擎的辐照度绑定差异见第 6.5 节。',
         '工程调度',8.7,
         '密度必须先完成全部 32 层；辐照度读完旧散射后，才开始写新的散射层。')
ax=diagram(fig,(.06,.235,.88,.555),(-.08,12.08),(0,7.1))
cols=[2.05,5.27,8.49]
for x,title,body in zip(cols,[r'① 求 $J^{(2)}$',r'② 求 $E^{(1)}$',r'③ 求 $L^{(2)}$'],
                        ['32 层密度 Pass','1 次辐照度 Pass','32 层路径积分 Pass']):
    card(ax,x,5.74,3.06,1.08,title,body,BLUE,body_size=11.7)
for j in range(2):arrow(ax,(cols[j]+3.07,6.26),(cols[j+1]-.02,6.26),GRAY,lw=1.5)
rows=[('deltaR',4.67,[(r'$C_R$','读取',GREEN),(r'$C_R$','读取',GREEN),(r'$L^{(2)}$','覆盖',ORANGE)]),
      ('deltaE',3.40,[(r'$E^{(0)}$','读取',GREEN),(r'$E^{(1)}$','覆盖',ORANGE),(r'$E^{(1)}$','保持',GRAY)]),
      ('density',2.13,[(r'$J^{(2)}$','覆盖',ORANGE),(r'$J^{(2)}$','保持',GRAY),(r'$J^{(2)}$','读取',GREEN)]),
      ('累计 RGB',.86,[(r'$C_R$','保持',GRAY),(r'$C_R$','保持',GRAY),
                     (r'$C_R+L^{(2)}/p_R$','加法混合',BLUE)])]
for label,y,cells in rows:
    text(ax,.15,y,label,INK,13)
    for x,(value,action,c) in zip(cols,cells):
        ax.add_patch(FancyBboxPatch((x,y-.43),3.06,.90,boxstyle='round,pad=.03,rounding_size=.07',
                                  fc=LIGHT,ec=LINE,lw=.8))
        text(ax,x+1.53,y+.12,value,c,19,ha='center')
        text(ax,x+1.53,y-.23,action,GRAY,11,ha='center')
fig.text(.06,.152,r'第一次读取：$L^{(1)}=p_R C_R+p_M C_M$。后续读取：deltaR 已是完整 $L^{(n-1)}$。',
         fontsize=13,color=INK)
save(fig,'explain_I_delta_texture_lifetime')

# J: exact 2-D schematic example of the height-fitting branch of the planet shader.
a,b,rb=4.8,3.1,4.0;hc,he=.20,.08
def ep(theta):return np.array([a*np.cos(theta),b*np.sin(theta)])
def en(q):
    v=q/np.array([a*a,b*b]);return v/np.linalg.norm(v)
pc=ep(np.deg2rad(55));qc=ep(np.deg2rad(35));up=en(pc);nq=en(qc)
P=pc+hc*up;Q=qc+he*nq;d=np.linalg.norm(Q-P);w=(Q-P)/d
rc,rq=rb+hc,rb+he;mu_fit=(rq*rq-rc*rc-d*d)/(2*rc*d)
tangent=np.array([up[1],-up[0]])
wp=np.sqrt(1-mu_fit*mu_fit)*tangent+mu_fit*up
Pp=rc*up;Qp=Pp+d*wp
fig=page('补图 J','椭球场景如何查询球形大气 LUT',
         '真实场景提供两端大地高度与距离；代理射线按球面几何重新构造。',
         '地球集成',8.4,
         '扁率和高度均被夸大。图示完全采用 μfit 的分支；实际混合与钳位条件见式（81）。')
fig.text(.12,.777,'真实椭球：沿大地法线量高度',fontsize=14,color=INK)
fig.text(.57,.777,'球形代理：按半径与距离拟合',fontsize=14,color=INK)
axs=[diagram(fig,(.06,.285,.405,.46),(-.30,5.17),(-.35,4.98)),
     diagram(fig,(.535,.285,.405,.46),(-.30,5.17),(-.35,4.98))]
for axis in axs:
    axis.set_aspect('equal')
    point(axis,(0,0),'O',(.03,-.18))
    arrow(axis,(4.53,3.87),(4.19,4.59),ORANGE,lw=1.8)
    text(axis,4.65,4.50,r'$\boldsymbol{s}$',ORANGE,18,ha='center')
x=np.linspace(0,a,700);yy=b*np.sqrt(np.maximum(1-x*x/(a*a),0))
axs[0].fill_between(x,-.35,yy,color='#e5eee8');axs[0].plot(x,yy,color=GREEN,lw=1.8)
axs[0].plot([0,P[0]],[0,P[1]],color=LINE,lw=1.2,ls='--')
arrow(axs[0],P,Q,BLUE,lw=2.4);arrow(axs[0],P,P+.78*up,INK,lw=1.5)
axs[0].plot([pc[0],P[0]],[pc[1],P[1]],color=RED,lw=3)
axs[0].plot([qc[0],Q[0]],[qc[1],Q[1]],color=RED,lw=3)
point(axs[0],P,'P',(-.24,.28));point(axs[0],Q,'Q',(.35,-.09))
text(axs[0],*(P+.83*up+np.array([.10,.08])),r'$\boldsymbol{u}$',INK,18,ha='center')
text(axs[0],*(.5*(P+Q)+np.array([.17,.27])),'$d$',BLUE,18,ha='center')
text(axs[0],1.15,3.65,r'$h_c$',RED,18)
arrow(axs[0],(1.55,3.49),.5*(pc+P),RED,lw=1.1,style='-')
text(axs[0],4.60,2.78,r'$h_e$',RED,18)
arrow(axs[0],(4.54,2.57),.5*(qc+Q),RED,lw=1.1,style='-')
text(axs[0],1.4,.86,'真实地表',GREEN,12,ha='center')
x=np.linspace(0,rb,700);yy=np.sqrt(np.maximum(rb*rb-x*x,0))
axs[1].fill_between(x,-.35,yy,color='#e5eee8');axs[1].plot(x,yy,color=GREEN,lw=1.8)
axs[1].plot([0,Pp[0]],[0,Pp[1]],color=GRAY,lw=1.2,ls='--')
axs[1].plot([0,Qp[0]],[0,Qp[1]],color=GRAY,lw=1.2,ls='--')
arrow(axs[1],Pp,Qp,BLUE,lw=2.4);arrow(axs[1],Pp,Pp+.70*up,INK,lw=1.5)
point(axs[1],Pp,r'$P_{\rm proxy}$',(-.42,.16));point(axs[1],Qp,r'$Q_{\rm proxy}$',(.45,.10))
text(axs[1],*(Pp+.74*up+np.array([.10,.08])),r'$\boldsymbol{u}$',INK,18,ha='center')
text(axs[1],*(.5*(Pp+Qp)+np.array([.20,.27])),'$d$',BLUE,18,ha='center')
text(axs[1],.75,2.30,'$r_c$',GRAY,18,ha='center');text(axs[1],2.35,1.18,'$r_q$',GRAY,18,ha='center')
text(axs[1],1.40,.86,'参考球面',GREEN,12,ha='center')
notes=diagram(fig,(.06,.13,.88,.115),(-.08,12.08),(0,1.4))
card(notes,0,.1,5.73,1.2,'保留：高度、距离和切向方位',r'$r_c=r_b+h_c,\quad r_q=r_b+h_e$',BLUE,body_size=18)
card(notes,6.25,.1,5.73,1.2,'拟合：改变观察天顶余弦',r'$\mu_{\rm fit}=\frac{r_q^2-r_c^2-d^2}{2r_c d}$',ORANGE,body_size=20)
checks['J']={'distance_preserved_error':float(abs(np.linalg.norm(Qp-Pp)-d)),
             'endpoint_radius_error':float(abs(np.linalg.norm(Qp)-rq)),
             'direction_length_error':float(abs(np.linalg.norm(wp)-1)),
             'mu_dir':float(np.dot(w,up)),'mu_fit':float(mu_fit),
             'sun_dot_difference':float(np.dot(wp-w,np.array([-.422618,.906308])))}
assert max(checks['J'][k] for k in ['distance_preserved_error','endpoint_radius_error','direction_length_error'])<1e-12
save(fig,'explain_J_ellipsoid_to_spherical_proxy')

QA.joinpath('explanatory_figure_layout_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
QA.joinpath('explanatory_figure_validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(audit),'overlaps':sum(len(x['overlaps']) for x in audit),
                  'outside_canvas':sum(len(x['outside_canvas']) for x in audit)},ensure_ascii=False))
