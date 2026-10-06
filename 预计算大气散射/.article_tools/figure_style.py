"""Reproducible vector/numerical figures for the atmosphere-scattering article.
Actual engine screenshots and paper figures are deliberately not touched.
"""
import sys, os, json
sys.path.insert(0, '/private/tmp/atmos-blog-deps')
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/atmos-blog-mpl')
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D
from matplotlib.text import Text

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'atmosphere_scattering_images'
QA = ROOT / '.article_tools/qa'
OUT.mkdir(exist_ok=True); QA.mkdir(exist_ok=True)
font = '/System/Library/Fonts/STHeiti Light.ttc'
font_manager.fontManager.addfont(font)
plt.rcParams.update({
    'font.family': font_manager.FontProperties(fname=font).get_name(),
    'font.size': 12.5, 'mathtext.fontset': 'stix', 'text.color': '#20354b',
    'axes.labelcolor': '#20354b', 'xtick.color': '#657b8e', 'ytick.color': '#657b8e',
    'axes.edgecolor': '#b8c8d7', 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.facecolor': 'white', 'figure.facecolor': 'white', 'axes.grid': True,
    'grid.color': '#dce5ee', 'grid.alpha': .8, 'grid.linewidth': .65,
    'axes.axisbelow': True, 'axes.unicode_minus': False, 'svg.fonttype': 'none',
    'savefig.facecolor': 'white', 'lines.solid_capstyle': 'round'})
BLUE='#286da8'; CYAN='#2297ad'; ORANGE='#d68a31'; GREEN='#518772'
INK='#20354b'; GRAY='#657b8e'; RED='#c25a60'; LIGHT='#f3f7fb'; LINE='#dce5ee'
RB=6360.; RT=6420.; H=np.sqrt(RT*RT-RB*RB)
audit=[]
def top(r,mu): return -r*mu+np.sqrt(np.maximum(r*r*(mu*mu-1)+RT*RT,0))
def bottom(r,mu): return -r*mu-np.sqrt(np.maximum(r*r*(mu*mu-1)+RB*RB,0))
def tex(x,n): return .5/n+x*(1-1/n)
def page(number,title,subtitle,category,height=6.7,footer=''):
    fig=plt.figure(figsize=(12.4,height))
    title_font=font_manager.FontProperties(fname='/System/Library/Fonts/STHeiti Medium.ttc')
    fig.text(.06,.944,f'{number:02d}  {title}' if isinstance(number,int) else f'{number}  {title}',fontsize=21,fontproperties=title_font,va='top')
    fig.text(.06,.876,subtitle,fontsize=12.5,color=GRAY,va='top')
    fig.text(.94,.936,category,fontsize=11,color=BLUE,ha='right',va='top',
             bbox=dict(boxstyle='round,pad=.45',fc=LIGHT,ec='none'))
    fig.add_artist(Line2D([.06,.94],[.834,.834],transform=fig.transFigure,color=LINE,lw=1.2))
    if footer: fig.text(.06,.047,footer,fontsize=11.5,color=GRAY,va='bottom')
    return fig

def diagram(fig,bounds=(.06,.20,.88,.58),xlim=(0,12),ylim=(0,6)):
    ax=fig.add_axes(bounds); ax.set(xlim=xlim,ylim=ylim); ax.axis('off'); return ax

def chart(fig,bounds,xlabel,ylabel,title=None):
    ax=fig.add_axes(bounds);ax.set(xlabel=xlabel,ylabel=ylabel)
    ax.tick_params(labelsize=11,length=3,pad=6)
    ax.xaxis.labelpad=10;ax.yaxis.labelpad=9
    if title: ax.set_title(title,fontsize=13.5,pad=14,color=INK)
    return ax

def text(ax,x,y,s,color=INK,size=13,ha='left',va='center',**kwargs):
    return ax.text(x,y,s,color=color,fontsize=size,ha=ha,va=va,**kwargs)

def arrow(ax,a,b,color=BLUE,lw=2.2,style='->',ls='-',alpha=1):
    ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle=style,color=color,lw=lw,
        linestyle=ls,alpha=alpha,shrinkA=2,shrinkB=2,mutation_scale=14))

def incoming(ax,start,center,color=CYAN,lw=2.2,radius=.34):
    start=np.asarray(start);center=np.asarray(center)
    end=center+radius*(start-center)/np.linalg.norm(start-center)
    arrow(ax,start,end,color,lw=lw)

def point(ax,p,label,offset=(0,-.33),color=INK):
    ax.plot(*p,'o',ms=6.5,color=color,zorder=5)
    text(ax,p[0]+offset[0],p[1]+offset[1],label,color,14,ha='center')

def card(ax,x,y,w,h,title,body='',color=BLUE,size=13,body_size=12.5):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.04,rounding_size=.10',
                              ec=LINE,fc=LIGHT,lw=1.1))
    ax.plot([x+.14,x+.14],[y+.19,y+h-.19],color=color,lw=3)
    if body:
        text(ax,x+.34,y+h*.72,title,color,size,va='center')
        text(ax,x+.34,y+h*.29,body,INK,body_size,va='center',linespacing=1.4)
    else: text(ax,x+w/2,y+h/2,title,color,size,ha='center')

def formula(fig,s,y=.14,size=19):
    fig.text(.5,y,s,ha='center',va='center',fontsize=size,color=INK,
             bbox=dict(boxstyle='round,pad=.6',fc=LIGHT,ec='none'))

def legend(fig,items,y=.758,x=.5,ncol=None,size=11.5):
    handles=[Line2D([0],[0],color=c,lw=2.5,ls=ls,label=s) for s,c,ls in items]
    fig.legend(handles=handles,loc='center',bbox_to_anchor=(x,y),ncol=ncol or len(items),
               frameon=False,fontsize=size,handlelength=2.2,columnspacing=1.5)

def save(fig,name):
    fig.canvas.draw(); renderer=fig.canvas.get_renderer()
    labels=[]; outside=[]; collisions=[]
    for artist in fig.findobj(Text):
        if not artist.get_visible() or not artist.get_text().strip(): continue
        box=artist.get_window_extent(renderer)
        if box.width<=0 or box.height<=0: continue
        labels.append((artist,box))
        if box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.width+1 or box.y1 > fig.bbox.height+1:
            outside.append(artist.get_text())
    for i,(a,ba) in enumerate(labels):
        for b,bb in labels[i+1:]:
            dx=min(ba.x1,bb.x1)-max(ba.x0,bb.x0)
            dy=min(ba.y1,bb.y1)-max(ba.y0,bb.y0)
            if dx>2 and dy>2: collisions.append([a.get_text(),b.get_text(),round(dx,1),round(dy,1)])
    audit.append(dict(figure=name,text_count=len(labels),overlaps=collisions,outside_canvas=outside))
    fig.savefig(OUT/(name+'.svg'))
    fig.savefig(OUT/(name+'.png'),dpi=210)
    plt.close(fig)

