"""Dataset distributions and variation at repeated encoded compositions."""
import pandas as pd
import numpy as np
from plot_style import *
d=pd.read_csv(O/'figure2.csv');fig,axs=plt.subplots(2,2,figsize=(8.5,6.2),layout='constrained')
axs[0,0].hist(d['Curie(TC) (K)'],bins=35,color=COLORS[0],edgecolor='white',linewidth=.4);axs[0,0].set(xlabel=r'$T_C$ (K)',ylabel='Records')
axs[0,1].hist(d.log10_Hc_Oe,bins=35,color=COLORS[1],edgecolor='white',linewidth=.4);axs[0,1].set(xlabel=r'$\log_{10}[H_c/(1\ \mathrm{Oe})]$',ylabel='Records')
sc=axs[1,0].scatter(d.VEC,d['Curie(TC) (K)'],c=d.log10_Hc_Oe,s=10,alpha=.65,cmap='viridis',rasterized=True);axs[1,0].set(xlabel='Valence electron concentration',ylabel=r'$T_C$ (K)');fig.colorbar(sc,ax=axs[1,0],label=r'$\log_{10}[H_c/(1\ \mathrm{Oe})]$',shrink=.8)
g=d.groupby('composition_group').agg(n=('log10_Hc_Oe','size'),lo=('log10_Hc_Oe','min'),hi=('log10_Hc_Oe','max'));g=g[g.n>1]
axs[1,1].hist(g.hi-g.lo,bins=25,color=COLORS[2],edgecolor='white',linewidth=.4);axs[1,1].set(xlabel=r'Within-composition $\log_{10} H_c$ range',ylabel='Repeated compositions');axs[1,1].text(.97,.92,f'{len(g)} repeated groups',ha='right',transform=axs[1,1].transAxes,fontsize=9)
for ax,l in zip(axs.flat,'abcd'):panel(ax,l)
save(fig,2)
