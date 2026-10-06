"""Two explanatory redraws for Figures 1 and 2 of the supplied 2008 paper.
Scientific schematic geometry, with Chinese labels and the article's symbols.
The source PDF and its extracted comparison pictures remain unchanged.
"""
from figure_style import *
from matplotlib.patches import Polygon

# E: four independent panels. Keep the formula out of the path drawing.
fig=page('补图 E','先分清四件事：衰减、反射、局部源、路径积分',
         '对应原论文 Figure 2。先问这个量描述一段路、一个表面，还是一个点。',
         '论文读图',10.2,
         'J 是一个点每米提供的散射增量；路径积分把这些贡献乘透射率后送到观察点。')
ax=diagram(fig,(.06,.15,.88,.635),(-.08,12.08),(0,9.4))
panels=[(0,4.95,'a  透射率：这段路保留多少光',BLUE),
        (6.25,4.95,'b  地面反射：表面向外返回光',GREEN),
        (0,.10,'c  局部源：这个点向视线补入光',CYAN),
        (6.25,.10,'d  路径积分：把各点贡献相加',ORANGE)]
for x,y,title,c in panels:
    ax.add_patch(FancyBboxPatch((x,y),5.73,4.35,boxstyle='round,pad=.025,rounding_size=.12',
                              fc='white',ec=LINE,lw=1.2))
    text(ax,x+.24,y+3.95,title,c,14)
    ax.plot([x+.24,x+5.49],[y+3.57,y+3.57],color=LINE,lw=1)

# a: incoming boundary light and removal from the selected direction.
P=np.array([.70,7.18]);B=np.array([4.76,7.68])
ax.plot([P[0],B[0]],[P[1],B[1]],color=LINE,lw=5,zorder=1)
arrow(ax,B,P,BLUE,lw=2.8)
point(ax,P,'P',(.0,-.35));point(ax,B,'B',(.0,-.35))
arrow(ax,(2.92,7.45),(3.45,8.12),GRAY,lw=1.4)
text(ax,3.50,8.15,'散射离开视线',GRAY,11.5)
ax.plot(2.16,7.36,'x',ms=10,mew=2,color=RED)
text(ax,1.94,8.00,'吸收',RED,12)
text(ax,2.86,6.37,r'$T_\lambda(P,B)=\exp(-\tau_\lambda)$',BLUE,20,ha='center')
text(ax,.24,5.56,'输出：无量纲比例，范围为 0 到 1',GRAY,12)

# b: hemispherical incident light hits the ground before reflection.
G=np.array([8.40,6.69]);P=np.array([11.13,8.10])
ax.fill_between([6.62,11.58],6.69,6.54,color='#e5eee8')
ax.plot([6.62,11.58],[6.69,6.69],color=GREEN,lw=1.7)
for start in [(7.03,8.15),(8.32,8.46),(9.57,8.22)]: incoming(ax,start,G,CYAN,radius=.16,lw=1.6)
arrow(ax,G,P,GREEN,lw=2.5)
point(ax,G,'G',(0,-.21),GREEN);point(ax,P,'P',(.0,.31))
text(ax,10.45,7.19,'反射光',GREEN,12,ha='center')
text(ax,9.12,6.10,r'$L_{\mathrm{ground},\lambda}=a_g E_\lambda/\pi$',GREEN,20,ha='center')
text(ax,6.49,5.56,'输出：地面辐亮度；到 P 还需乘透射率',GRAY,12)

# c: all incident directions feed one fixed outgoing direction at Q.
P=np.array([.68,2.20]);Q=np.array([3.44,2.66])
ax.plot([P[0],Q[0]],[P[1],Q[1]],color=LINE,lw=1.6,ls='--')
for start in [(2.35,3.35),(3.47,3.50),(4.72,3.20),(4.81,2.24),(3.98,1.97)]:
    incoming(ax,start,Q,CYAN,radius=.18,lw=1.5)
ax.add_patch(Circle(Q,.17,fc='#d5eef0',ec=CYAN,lw=1.2,zorder=4))
arrow(ax,Q,P,BLUE,lw=2.4)
point(ax,P,'P',(0,-.35));text(ax,Q[0]-.29,Q[1]-.35,'Q',INK,14,ha='center')
text(ax,.86,3.22,'送往观察点',BLUE,12)
text(ax,2.86,1.46,r'$J_\lambda=\int_{4\pi} I_\lambda\sum_i\beta_i^s p_i\,\mathrm{d}\Omega$',CYAN,18,ha='center')
text(ax,.24,.69,'输出：辐亮度 / m；尚未沿视线累加',GRAY,12)

# d: separate points are accumulated with their own T(P,Q).
P=np.array([6.95,2.22]);B=np.array([11.45,2.80])
arrow(ax,P,B,GRAY,lw=1.3,ls='--')
for j,t in enumerate([.31,.58,.84]):
    Q=P+t*(B-P)
    ax.plot(*Q,'o',ms=7,color=CYAN)
    arrow(ax,(Q[0]+.29,Q[1]+.52),Q,CYAN,lw=1.4)
    text(ax,Q[0],Q[1]+.91,r'$Q_{'+str(j+1)+'}$',INK,14,ha='center')
arrow(ax,(10.62,2.46),(7.03,1.96),ORANGE,lw=2.4)
point(ax,P,'P',(-.21,-.35));point(ax,B,'B',(.08,-.32))
text(ax,9.12,1.46,r'$\mathcal{S}_\lambda(P)=\int_0^{d_B}T_\lambda(P,Q_d)J_\lambda(Q_d)\,\mathrm{d}d$',ORANGE,16.5,ha='center')
text(ax,6.49,.69,'输出：路径辐亮度；这才是天空的一部分',GRAY,12)
save(fig,'paper_E_four_transport_quantities')

# F: geometric shadow splitting; the right panel retains actual terrain dashed.
fig=page('补图 F','Figure 1 的关键：地形阴影与球形参考场景',
         r'左图逐条判断真实地形遮挡；右图复用球形 LUT，并用 $Q_s$ 限定保留区间。',
         '论文读图',8.1,
         '蓝色：保留的视线路径。红色虚线：被截去的路径。图中边界与地形只作示意。')
ax=diagram(fig,(.06,.235,.88,.54),(-.08,12.08),(0,5.4))
terrain=np.array([[0,.25],[.8,.45],[1.7,.36],[2.8,.55],[4.,1.05],
                  [4.55,2.20],[4.96,2.06],[5.50,.48]])
P=np.array([.8,3.7]);B=np.array([4.,1.05]);ts=(P[1]-2.2)/(P[1]-B[1]);Qs=P+ts*(B-P)
Qdark=P+.82*(B-P);Qlit=P+.33*(B-P)
for dx,title in [(0,'真实地形：影中也可能收到间接光'),(6.25,'参考场景：源项按球形地表预计算')]:
    ax.add_patch(FancyBboxPatch((dx,.12),5.73,5.15,boxstyle='round,pad=.02,rounding_size=.10',
                              fc='white',ec=LINE,lw=1.2,zorder=-2))
    text(ax,dx+.22,4.87,title,INK,14)
    ax.fill_between([dx+.12,dx+5.60],.30,4.42,color='#eff7fc',zorder=0)
    ax.plot([dx+.12,dx+5.60],[4.42,4.42],color=CYAN,lw=1.4)
    text(ax,dx+4.75,4.18,'大气顶',CYAN,11.5)
    arrow(ax,(dx+5.27,3.64),(dx+4.24,3.64),ORANGE,lw=2.1)
    text(ax,dx+4.78,3.98,'太阳来光',ORANGE,11.5,ha='center')

# Actual terrain and its direct solar shadow below the silhouette height.
actual=terrain.copy();actual[:,0]+=.12
poly=np.vstack([[.12,.30],actual,[5.62,.30]])
ax.add_patch(Polygon(poly,fc='#e5eee8',ec='none',zorder=1))
ax.plot(actual[:,0],actual[:,1],color=GREEN,lw=1.7)
ax.fill_between(actual[:6,0],actual[:6,1],2.2,color='#dae2e9',alpha=.7,zorder=.8)
ax.plot([.12,4.67],[2.2,2.2],color=GRAY,lw=1.2,ls=':')
offset=np.array([.12,0]);PP=P+offset;BB=B+offset;QQs=Qs+offset
ax.plot([PP[0],BB[0]],[PP[1],BB[1]],color=BLUE,lw=2.6)
arrow(ax,Qlit+offset,PP,BLUE,lw=2.1)
arrow(ax,(4.20,Qlit[1]),Qlit+offset,ORANGE,lw=1.6)
R=np.array([1.00,2.75]);incoming(ax,(2.03,2.75),R,ORANGE,radius=.10,lw=1.5)
ax.plot(*R,'o',ms=5,color=CYAN)
arrow(ax,R,Qdark+offset,CYAN,lw=1.8)
ax.plot(*(Qdark+offset),'o',ms=5,color=CYAN)
arrow(ax,Qdark+offset,PP,BLUE,lw=1.5,ls='--')
point(ax,PP,'P',(-.24,.16));point(ax,BB,'B',(.27,-.24))
point(ax,QQs,r'$Q_s$',(.20,.31),RED)
text(ax,.43,1.55,'太阳直射被挡住',GRAY,11.5)
text(ax,.43,1.17,'间接光仍可绕行',CYAN,11.5)

# Spherical reference ground, with the actual terrain shown only as a dashed cue.
dx=6.25;ground=np.array([[0,.22],[1,.34],[2,.42],[3,.47],[4,.45],[4.78,.40],[5.50,.24]])
ground[:,0]+=dx+.12
ax.fill_between(ground[:,0],.30,ground[:,1],color='#e5eee8',zorder=1)
ax.plot(ground[:,0],ground[:,1],color=GREEN,lw=1.8)
ax.plot(actual[:,0]+dx,actual[:,1],color=GRAY,lw=1.2,ls='--')
offset=np.array([dx+.12,0]);PP=P+offset;BB=B+offset;QQs=Qs+offset
Bb=P+1.245*(B-P)+offset
ax.plot([PP[0],QQs[0]],[PP[1],QQs[1]],color=BLUE,lw=2.8)
ax.plot([QQs[0],Bb[0]],[QQs[1],Bb[1]],color=RED,lw=2.0,ls='--')
point(ax,PP,'P',(-.24,.16));point(ax,QQs,r'$Q_s$',(.20,.31),RED)
point(ax,BB,'B',(.25,.02),GRAY);point(ax,Bb,r'$\bar B$',(.29,-.05),GREEN)
for t in [.20,.40]:
    Q=P+t*(B-P)+offset
    incoming(ax,(Q[0]+.76,Q[1]+.48),Q,CYAN,radius=.12,lw=1.4)
text(ax,dx+.35,1.31,'实际地形（虚线）',GRAY,11.5)
text(ax,dx+.35,.96,'球形地表（绿线）',GREEN,11.5)
fig.text(.06,.206,'直射被挡住，高阶入射场仍可能非零。',fontsize=12,color=CYAN)
fig.text(.52,.206,'把高阶源改成预计算值，是这里的近似。',fontsize=12,color=BLUE)
formula(fig,r'$L^{\mathrm{ins}}_{P Q_s,\lambda}\approx\mathcal{S}_\lambda(P)-T_\lambda(P,Q_s)\mathcal{S}_\lambda(Q_s)$',.145,21)
save(fig,'paper_F_terrain_shadow_approximation')

QA.joinpath('paper_reading_figure_layout_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(audit),'overlaps':sum(len(x['overlaps']) for x in audit),
                  'outside_canvas':sum(len(x['outside_canvas']) for x in audit)},ensure_ascii=False))
