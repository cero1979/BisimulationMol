"""Scientific four-panel figure generated from verified R3 results."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]


def main():
    w=json.loads((ROOT/'results/death_receptor_branching_witness.json').read_text())
    s=json.loads((ROOT/'results/death_receptor_execution_summary.json').read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(7.5,6.8))
    fig.subplots_adjust(left=.03,right=.98,top=.97,bottom=.03,hspace=.15,wspace=.12)
    teal,red,ink='#007f78','#b83d4c','#23272d'
    def text(ax,x,y,t,**kw):
        ax.text(x,y,t,ha='center',va='center',color=ink,**kw)
    def arrow(ax,a,b,color='#65717b',style='-',rad=0):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,lw=1.4,
                                     color=color,linestyle=style,connectionstyle=f'arc3,rad={rad}'))
    for ax in axes.flat:
        ax.set(xlim=(0,1),ylim=(0,1)); ax.axis('off')
    a,b,c,d=axes.flat
    for ax,title in zip(axes.flat,['A  Published mechanistic contrast','B  Sustained TNF: same stable fates',
                                  'C  Shared state, fixed observations','D  Withdraw TNF from that state']):
        ax.text(0,1,title,ha='left',va='top',fontweight='bold',fontsize=10)
    text(a,.48,.84,'TNF / death receptor',fontweight='bold')
    for x,y,label in [(.16,.48,'NFkB'),(.50,.60,'CASP8'),(.83,.48,'MPT'),(.50,.26,'CASP3')]:
        a.text(x,y,label,ha='center',va='center',fontsize=11,
               bbox=dict(boxstyle='round,pad=0.32',facecolor='#f2f5f6',edgecolor='#a5b0b7'))
    arrow(a,(.43,.79),(.18,.55),style='--')
    arrow(a,(.50,.79),(.50,.68),style='--')
    arrow(a,(.58,.79),(.81,.55),style='--')
    arrow(a,(.48,.53),(.48,.33),style='--')
    arrow(a,(.58,.30),(.60,.56),color=teal,rad=.55)
    a.text(.71,.30,'feedback\nFB+ only',ha='center',va='center',color=teal,fontsize=9)
    text(a,.16,.38,'survival',fontsize=9)
    text(a,.83,.38,'necrosis',fontsize=9)
    text(a,.50,.16,'apoptotic marker',fontsize=9)
    text(a,.49,.04,'Dashed: multistep pathway context',fontsize=8.5)
    for x,label,color in [(.60,'FB+',teal),(.84,'FB-',red)]:
        b.text(x,.81,label,ha='center',fontweight='bold',color=color)
    for y,fate in zip((.67,.51,.35),('survival','apoptosis','necrosis')):
        b.text(.03,y,fate.title(),ha='left',va='center')
        for x,model,color in [(.60,'DR-FB+',teal),(.84,'DR-FB-',red)]:
            assert fate in s['models'][model]['sustained']['initial_reachable_terminal_fates']
            b.plot(x,y,'o',color=color,markersize=8)
    text(b,.48,.16,'Exact terminal-fate agreement',fontsize=9)
    text(b,.48,.06,'Global sustained traces differ (verified word)',fontsize=8.5)
    text(c,.5,.83,f"{w['common_raw_history']['raw_depth']} shared raw updates",fontweight='bold')
    text(c,.5,.67,'TNFR > DISC_TNF > CASP8 > BAX\n> MOMP > Cyt_c > apoptosome > CASP3',fontsize=8.8,linespacing=1.7)
    arrow(c,(.5,.56),(.5,.45))
    text(c,.5,.37,'NFkB = 0   CASP3 = 1   MPT = 0',fontweight='bold',fontsize=9)
    text(c,.5,.24,'Visible history: CASP3_up',fontsize=9)
    text(c,.5,.10,'Continued TNF from this state:\nidentical exact language {epsilon}',fontsize=9,linespacing=1.5)
    text(d,.5,.83,'Same action: withdraw_TNF',fontweight='bold')
    for x,label,color in [(.24,'FB+',teal),(.76,'FB-',red)]:
        arrow(d,(.5,.76),(x,.66),color=color)
        d.text(x,.60,label,ha='center',fontweight='bold',color=color,fontsize=11)
    text(d,.24,.46,'CASP3 persists',fontsize=9)
    text(d,.76,.46,'CASP3 can turn off',fontsize=9)
    text(d,.24,.32,'Apoptosis only',fontweight='bold',fontsize=9)
    text(d,.76,.32,'Naive signature only',fontweight='bold',fontsize=9)
    text(d,.5,.15,'FB+ is simulated by FB-; reverse fails',fontsize=9)
    text(d,.5,.05,'State-specific result; not cellular recovery',fontsize=8.5)
    fig.savefig(ROOT/'revision_R3/R3_Fig1.pdf',bbox_inches='tight',metadata={'CreationDate':None})
    fig.savefig(ROOT/'revision_R3/R3_Fig1.png',dpi=180,bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__':
    main()
