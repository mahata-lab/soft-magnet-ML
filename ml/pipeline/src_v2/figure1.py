"""Workflow schematic. Input: figure1.csv. Output: PNG 600 dpi, PDF and SVG."""
import pandas as pd
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from plot_style import *
d=pd.read_csv(O/'figure1.csv');fig,ax=plt.subplots(figsize=(10,4.6));ax.set(xlim=(-.15,9.8),ylim=(-.4,4.25));ax.axis('off')
for i,r in d.iterrows():
 x=r['column']*3.3;y=2.45-r['row']*2.15
 ax.add_patch(FancyBboxPatch((x,y),3.,1.35,boxstyle='round,pad=0.07,rounding_size=0.06',facecolor='#F0F5FA' if i<3 else '#F4F2EE',edgecolor=COLORS[0] if i<3 else '#777777',linewidth=1.1))
 ax.text(x+.15,y+1.07,r.stage,weight='bold',fontsize=11)
 data={'Literature data':'1,736 encoded records','ML evaluation':'1,713 records\n1,058 compositions','Screening':'1,000 six-element points\n32 point-threshold hits','DFT benchmarks':'Volume, SOC and\nspin-state outputs','Spin benchmarks':'Seven VAMPIRE curves\nand parameter files','Interpretation':'Composition priorities\nand validation limits'}
 ax.text(x+.15,y+.62,data[r.stage],fontsize=10,va='center')
 methods=['Deduplicate; inspect provenance','Fixed models; grouped holdout','Treat hits as hypotheses','Atoms, spin states, convergence','Inputs and transition proxies','No validated coercivity claim']
 ax.text(x+.15,y+.15,methods[i],fontsize=8.6,color='#454545')
for y in [3.12,.97]:
 for x in [3.04,6.34]:ax.add_patch(FancyArrowPatch((x,y),(x+.22,y),arrowstyle='-|>',mutation_scale=13,color='#333333'))
ax.add_patch(FancyArrowPatch((8.1,2.37),(8.1,1.73),arrowstyle='-|>',mutation_scale=13,color='#333333'))
ax.text(4.8,2.08,'Existing calculations provide separate physical benchmarks',ha='center',fontsize=9,color='#555555')
save(fig,1)

