"""MSVS V3 / Nordic Slate publication figure artwork for RBF manuscript.
Produces vector PDF + editable SVG from source manuscript evidence only.
Data panels use exact archived per-seed percentages from v2 CSV records.
"""
from __future__ import annotations
import json, math, pathlib, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle, Polygon
from matplotlib.lines import Line2D
from matplotlib import rcParams
from matplotlib import font_manager
from prepare_fonts import FONT_FAMILY, prepare_fonts

# Matplotlib's type-42 PDF backend requires actual TrueType outlines. Register
# the portable metric-preserving Nimbus derivatives instead of system CFF OTFs.
for _font_path in prepare_fonts():
    font_manager.fontManager.addfont(str(_font_path))

OUT=pathlib.Path(__file__).resolve().parents[1]/'figures';OUT.mkdir(parents=True,exist_ok=True)
from build_exact_data import build_exact_data
DATA=build_exact_data()
(pathlib.Path(__file__).resolve().parent/'exact_plot_data.json').write_text(json.dumps(DATA,indent=2))
MM=1/25.4
C={'navy':'#1E293B','ink':'#0F172A','sky':'#0EA5E9','azure':'#0284C7','coral':'#F43F5E','white':'#FFFFFF','pale':'#F8FAFC','grid':'#E2E8F0','slate':'#64748B','border':'#CBD5E1','softblue':'#E0F2FE','lightnavy':'#F1F5F9'}
rcParams.update({
    'font.family':FONT_FAMILY,'font.size':9.6,'text.color':C['ink'],
    'axes.labelcolor':C['navy'],'axes.edgecolor':C['border'],'xtick.color':C['slate'], 'ytick.color':C['slate'],
    'svg.fonttype':'none','pdf.fonttype':42,'ps.fonttype':42,
    'savefig.facecolor':'white','figure.facecolor':'white','figure.dpi':160,
    'path.simplify':False
})

def export(fig,slug):
    fig.savefig(OUT/(slug+'.pdf'),format='pdf',dpi=350,facecolor='white',bbox_inches=None,transparent=False)
    fig.savefig(OUT/(slug+'.svg'),format='svg',dpi=350,facecolor='white',bbox_inches=None,transparent=False)
    fig.savefig(OUT/(slug+'_preview.png'),format='png',dpi=180,facecolor='white',bbox_inches=None,transparent=False)
    plt.close(fig)

def diagram_figure(width,height):
    f=plt.figure(figsize=(width*MM,height*MM));ax=f.add_axes((0,0,1,1))
    ax.set_xlim(0,width);ax.set_ylim(0,height);ax.set_aspect('equal',adjustable='box');ax.axis('off')
    return f,ax

def box(ax,xy,w,h,top,bottom=None,fs=9,fill='pale',stroke='border',title_color='ink',bottom_color='navy',weight='bold',radius=3):
    x,y=xy
    fs=max(fs,9.6)
    pat=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={radius}',linewidth=.9,edgecolor=C[stroke],facecolor=C[fill],zorder=2)
    ax.add_patch(pat)
    if bottom is None:
        ax.text(x+w/2,y+h/2,top,ha='center',va='center',fontsize=fs,color=C[title_color],weight=weight,zorder=3)
    else:
        ax.text(x+w/2,y+h*.67,top,ha='center',va='center',fontsize=fs,color=C[title_color],weight=weight,zorder=3)
        ax.text(x+w/2,y+h*.32,bottom,ha='center',va='center',fontsize=max(9.6,fs-0.6),color=C[bottom_color],zorder=3)

def patharrow(ax,vertices, color='navy',lw=1.3,ms=8,style='-|>',dash=False):
    for a,b in zip(vertices[:-2],vertices[1:-1]):
        ax.plot([a[0],b[0]],[a[1],b[1]],color=C[color],lw=lw,zorder=1,ls='--' if dash else '-')
    a,b=vertices[-2:]
    arr=FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=ms,linewidth=lw,color=C[color],zorder=3,linestyle='--' if dash else '-')
    ax.add_patch(arr)

def lane_label(ax,x,y,k,t):
    ax.text(x,y,k,color=C['navy'],weight='bold',fontsize=10.0,ha='left',va='baseline')
    ax.text(x+9,y,t,color=C['slate'],fontsize=9.6,ha='left',va='baseline')

# Fig 1: decision paths
fig,ax=diagram_figure(190,104)
ax.add_patch(FancyBboxPatch((4,53),182,43,boxstyle='round,pad=0,rounding_size=3',facecolor=C['white'],edgecolor=C['grid'],lw=.8))
ax.add_patch(FancyBboxPatch((4,7),182,43,boxstyle='round,pad=0,rounding_size=3',facecolor=C['pale'],edgecolor=C['grid'],lw=.8))
lane_label(ax,9,91,'A','NEAREST-PROTOTYPE REFERENCE')
lane_label(ax,9,45,'B','GAUSSIAN RBF CLASSIFIER')
xstart=[9,54,99,144];w=36
box(ax,(xstart[0],61),w,23,'Query image',r'$x$; prototypes $c_j$',fs=8.8,fill='pale')
box(ax,(xstart[1],61),w,23,'Compare distances',r'$\|x-c_j\|_2^2$',fs=8.5,fill='pale')
box(ax,(xstart[2],61),w,23,'Select nearest',r'$j_0=\arg\min_j d_j^2$',fs=8.8,fill='pale')
box(ax,(xstart[3],61),w,23,'Reference class',r'$a=\operatorname{label}(c_{j_0})$',fs=8.8,fill='softblue',stroke='azure')
for a,b in zip(xstart[:-1],xstart[1:]):patharrow(ax,[(a+w,72.5),(b-2,72.5)],lw=1.45)
box(ax,(xstart[0],15),w,23,'Query & data',r'$x,\ (X,Y),\ \{c_j\}$',fs=8.7,fill='pale')
box(ax,(xstart[1],15),w,23,'Gaussian features',r'$H_{\sigma},\ h_{\sigma}(x)$',fs=8.7,fill='pale')
box(ax,(xstart[2],15),w,23,'Ridge readout',r'$W_{\sigma,\lambda}$ from all $Y$',fs=8.7,fill='pale')
box(ax,(xstart[3],15),w,23,'Fitted class',r'$\hat y_{\sigma,\lambda}$',fs=8.7,fill='softblue',stroke='azure')
for a,b in zip(xstart[:-1],xstart[1:]):patharrow(ax,[(a+w,26.5),(b-2,26.5)],lw=1.45)
# Preserve the approved UPDATED vector geometry. The supplied plotting script
# predates its manual question-mark/connector-spacing correction, so source the
# exact PDF-space coordinates from that approved vector asset (points -> mm).
_pt_to_mm=25.4/72
_pdf_y=lambda y:104-y*_pt_to_mm
_connector_x=514.4879760742188*_pt_to_mm
ax.plot([_connector_x,_connector_x],[_pdf_y(218.27000427246094),_pdf_y(165.5)],lw=1.3,color=C['azure'],ls=(0,(3,2)))
ax.plot([_connector_x,_connector_x],[_pdf_y(134.5),_pdf_y(87.875)],lw=1.3,color=C['azure'],ls=(0,(3,2)))
ax.plot([178.6,181.5],[73,73],lw=1.1,color=C['azure'])
ax.plot([178.6,181.5],[27,27],lw=1.1,color=C['azure'])
ax.add_patch(Rectangle((507.10198974609375*_pt_to_mm,_pdf_y(159.19900512695312)),
                       (521.8989868164062-507.10198974609375)*_pt_to_mm,
                       (159.19900512695312-139.0)*_pt_to_mm,
                       facecolor='white',edgecolor='none',zorder=3))
# Exact original 15 pt glyph baseline/origin, retaining approved visual center.
ax.text(181.4779833984375,_pdf_y(154.8984375),'?',ha='center',va='baseline',fontsize=15.0,color=C['azure'],weight='bold',zorder=4)
ax.text(95,2,'Theorem 1 certifies equality of the two class labels throughout a parameter region.',ha='center',va='bottom',fontsize=9.6,color=C['slate'])
export(fig,'Figure_01_Two_Decision_Paths')

# Fig 2: certificate + parameter-region geometry
fig,ax=diagram_figure(190,118)
# Subtle panel division
ax.plot([128,128],[7,113],lw=.85,color=C['grid'])
ax.text(4,113,'A',color=C['navy'],fontweight='bold',fontsize=10.0,ha='left',va='top')
ax.text(13,113,'TRAINING-TO-CERTIFICATE CONSTRUCTION',color=C['slate'],fontsize=9.6,ha='left',va='top')
ax.text(132,113,'B',color=C['navy'],fontweight='bold',fontsize=10.0,ha='left',va='top')
ax.text(141,113,'CERTIFIED REGION',color=C['slate'],fontsize=9.6,ha='left',va='top')
# 4 training quantities; each its own role, mathematically correct
starts=[5,36,67,98]
items=[(r'$V_t$','prototype\noverlap'),(r'$P_t$','other labeled\nrows'),(r'$Q_t$','quadratic\noverlap'),(r'$\gamma_t$','spectral\nfloor')]
for x,(symbol,role) in zip(starts,items):
    ax.add_patch(FancyBboxPatch((x,82),26,23,boxstyle='round,pad=0,rounding_size=2.4',facecolor=C['pale'],edgecolor=C['border'],linewidth=.7))
    ax.text(x+13,99,symbol,ha='center',va='center',fontsize=11.0,color=C['navy'])
    ax.text(x+13,89,role,ha='center',va='center',fontsize=9.6,color=C['slate'],linespacing=1.15)
    patharrow(ax,[(x+13,82),(x+13,75)],color='slate',lw=.9,ms=7)
ax.add_patch(FancyBboxPatch((5,51),119,24,boxstyle='round,pad=0,rounding_size=2.6',facecolor=C['softblue'],edgecolor=C['azure'],linewidth=1))
ax.text(64.5,67,r'$D^{\mathrm{sharp}}_{ab}(t,\lambda_0)=\max\!\left\{\|F_{ab}(\lambda_0;t)\|_2,\ \|V_{ab,t}+P_{ab,t}\|_2\right\}$',ha='center',va='center',fontsize=9.6,color=C['ink'])
ax.text(64.5,57,r'training-only bound; $\gamma_t+\lambda_0>0$',ha='center',va='center',fontsize=9.6,color=C['slate'])
box(ax,(5,12),52,27,'Query geometry',r'$L_b(t),\ n_t$',fs=9,fill='pale')
box(ax,(68,12),56,27,'Strict margin test',r'$L_b(t)>n_tD_{ab}^{\mathrm{sharp}}$',fs=9,fill='softblue',stroke='azure')
patharrow(ax,[(64.5,51),(64.5,44),(96,44),(96,40)],color='azure',lw=1.2,ms=8)
patharrow(ax,[(57,25.5),(67,25.5)],color='azure',lw=1.2,ms=8)
ax.text(65,4.5,r'Apply to every competing class $b\ne a$ (Eq. 13).',ha='center',va='bottom',fontsize=9.6,color=C['slate'])
# parameter plane in right panel
x0,y0=143,27
xt,yt=172,49
ax.add_patch(Rectangle((x0+1,yt),xt-x0-1,55,facecolor=C['softblue'],edgecolor='none',zorder=0))
# axes & boundaries
patharrow(ax,[(x0,y0),(x0,109)],color='ink',lw=1.0,ms=8)
patharrow(ax,[(x0,y0),(188,y0)],color='ink',lw=1.0,ms=8)
ax.plot([x0,xt],[yt,yt],color=C['azure'],lw=1.3,zorder=2)
ax.plot([xt,xt],[y0,104],color=C['azure'],lw=1.3,zorder=2)
ax.plot([x0+1,x0+1],[yt,104],color=C['azure'],lw=.8,ls=':',alpha=.9)
ax.plot([x0-2,x0+1],[yt,yt],color=C['ink'],lw=.8)
ax.plot([xt,xt],[y0-2,y0+2],color=C['ink'],lw=.8)
ax.text(x0-4,yt,r'$\lambda_0$',ha='right',va='center',fontsize=9.6,color=C['navy'])
ax.text(xt,y0-5,r'$t$',ha='center',va='top',fontsize=9.6,color=C['navy'])
ax.text(187,y0-5,r'$\sigma$',ha='right',va='top',fontsize=10.0,color=C['navy'])
ax.text(x0-3,108,r'$\lambda$',ha='right',va='center',fontsize=10.0,color=C['navy'])
ax.text(x0+1,106,r'$\uparrow\ \infty$',ha='left',va='center',fontsize=9.6,color=C['azure'])
ax.text((x0+xt)/2,72,'Uniform\nlabel agreement',ha='center',va='center',fontsize=9.6,color=C['navy'],weight='bold',linespacing=1.25)
ax.text((x0+xt)/2,16,r'$0<\sigma\leq t$',ha='center',va='center',fontsize=9.6,color=C['navy'])
ax.text((x0+xt)/2,10,r'$\lambda\geq\lambda_0$',ha='center',va='center',fontsize=9.6,color=C['navy'])
export(fig,'Figure_02_Uniform_Certificate_Mechanism')

# Results figures using exact frozen-result CSV summaries
LABELS=['1/16','1/8','1/4','1/2','1','2']

def common_panels():
    f,axs=plt.subplots(2,3,figsize=(190*MM,128*MM),sharex=True,sharey=True)
    f.subplots_adjust(left=.092,right=.986,bottom=.154,top=.838,wspace=.19,hspace=.44)
    for i,ax in enumerate(axs.ravel()):
        ax.set_ylim(-4,103);ax.set_xlim(-.38,5.38)
        ax.set_xticks(range(6),labels=LABELS)
        ax.set_yticks([0,25,50,75,100])
        ax.tick_params(axis='both',which='major',labelsize=9.6, length=2.3, width=.62,pad=2)
        ax.set_axisbelow(True)
        ax.yaxis.grid(True,color=C['grid'],lw=.7)
        ax.axvspan(-.26,.26,color=C['softblue'],zorder=0,alpha=.55)
        ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(C['border']);ax.spines['bottom'].set_color(C['border'])
        ax.spines['left'].set_linewidth(.68);ax.spines['bottom'].set_linewidth(.68)
        ds='MNIST' if i<3 else 'Fashion-MNIST';pen=[0,1,100][i%3]
        ax.set_title(f'{chr(65+i)}   {ds}   |   '+r'$\lambda_0='+str(pen)+'$',fontsize=9.6,color=C['navy'],loc='left',weight='bold',pad=7)
        ax.set_xticklabels(LABELS,fontsize=9.6)
    f.text(.54,.035,r'Upper bandwidth $t/s_C$',ha='center',va='center',fontsize=9.6,color=C['navy'])
    return f,axs

def render_raw(ax,rec,key,color,marker,xshift=0):
    vals=np.asarray(rec[key]['five_seed_percent'])
    # Plot the five exact per-seed outcomes; small x offsets separate repeats.
    for k in range(6):
        xx=k+xshift+np.linspace(-.12,.12,5)
        ax.plot(xx,vals[k],ls='None',marker=marker,markersize=3.8,
                markerfacecolor='white',markeredgecolor=color,alpha=.64,markeredgewidth=.72,zorder=3)

def render_mean(ax,rec,key,color,marker,ls='-',lw=1.55,xshift=0):
    xs=np.arange(6,dtype=float)+xshift
    ys=rec[key]['mean_percent']
    ax.plot(xs,ys,ls=ls,marker=marker,markersize=4.1,markerfacecolor=color,markeredgecolor='white',markeredgewidth=.4,
            color=color,lw=lw,solid_capstyle='round',zorder=4)

# Fig3 coverage
fig,axs=common_panels()
for i,(ax,r) in enumerate(zip(axs.ravel(),DATA['coverage'])):
    render_raw(ax,r,'sharp_basic',C['navy'],'o',xshift=-.06)
    render_raw(ax,r,'frobenius',C['azure'],'s',xshift=.06)
    render_mean(ax,r,'sharp_basic',C['navy'],'o',xshift=-.06)
    render_mean(ax,r,'frobenius',C['azure'],'s',ls=(0,(4.2,2.8)),xshift=.06)
fig.text(.016,.50,'Certified evaluation queries (%)',fontsize=9.6,rotation=90,ha='center',va='center',color=C['navy'])
leg=[
 Line2D([0],[0],color=C['navy'],lw=1.55,marker='o',markersize=4.2,label='Sharp / basic mean'),
 Line2D([0],[0],color=C['azure'],lw=1.55,ls='--',marker='s',markersize=4,label='Frobenius mean'),
 Line2D([0],[0],ls='None',marker='o',markersize=4,markerfacecolor='white',markeredgecolor=C['slate'],label='Individual seed')
]
# Preserve the approved PDF-space legend baseline after CFF -> TrueType
# conversion changes FreeType's legend box height by 0.265625 pt.
fig.legend(handles=leg,loc='upper center',ncol=3,frameon=False,fontsize=9.6,bbox_to_anchor=(.52,.962-.265625/(128*MM*72)),handlelength=2.3,columnspacing=1.8)
fig.text(.51,.085,'Shaded band: narrowest scaled endpoint; other scaled endpoints have zero coverage.',ha='center',va='center',fontsize=9.6,color=C['slate'])
export(fig,'Figure_03_Certificate_Coverage')

# Fig4 agreement vs accuracy
fig,axs=common_panels()
for i,(ax,r) in enumerate(zip(axs.ravel(),DATA['agreement_accuracy'])):
    render_raw(ax,r,'agreement',C['navy'],'o',xshift=-.045)
    render_raw(ax,r,'readout_accuracy',C['azure'],'s',xshift=.045)
    baseline=r['nearest_prototype_accuracy']['mean_percent']
    ax.plot(range(6),baseline,color=C['slate'],ls=(0,(1.5,2.3)),lw=1.6,zorder=2)
    render_mean(ax,r,'agreement',C['navy'],'o',xshift=-.045)
    render_mean(ax,r,'readout_accuracy',C['azure'],'s',xshift=.045)
fig.text(.016,.50,'Evaluation queries (%)',fontsize=9.6,rotation=90,ha='center',va='center',color=C['navy'])
leg=[
 Line2D([0],[0],color=C['navy'],lw=1.55,marker='o',markersize=4,label='Nearest-label agreement'),
 Line2D([0],[0],color=C['azure'],lw=1.55,marker='s',markersize=4,label='Readout accuracy'),
 Line2D([0],[0],color=C['slate'],lw=1.6,ls=':',label='Nearest-prototype accuracy')]
# Equivalent 0.25 pt font-box compensation for this legend's text.
fig.legend(handles=leg,loc='upper center',ncol=3,frameon=False,fontsize=9.6,bbox_to_anchor=(.52,.962-.25/(128*MM*72)),handlelength=2.2,columnspacing=1.55)
fig.text(.51,.085,r'Each fitted-point observation uses $(\sigma,\lambda)=(t,\lambda_0)$; marker outlines show individual seeds.',ha='center',va='center',fontsize=9.6,color=C['slate'])
export(fig,'Figure_04_Agreement_Accuracy')

print('Created four figure pairs PDF/SVG and previews in',OUT)
