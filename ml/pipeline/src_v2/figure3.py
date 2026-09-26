"""Parity plots and metrics calculated directly from saved holdout predictions."""
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score,mean_absolute_error
from plot_style import *
d=pd.read_csv(O/'figure3.csv');fig,axs=plt.subplots(2,2,figsize=(8.5,6.5),layout='constrained')
prots=['notebook_fixed','composition_random','composition_grouped','composition_grouped_refit'];names=['Notebook\nrandom','Composition\nrandom','Grouped\nfixed','Grouped\nrefit']
for k,(target,unit) in enumerate([('Curie(TC) (K)',r'$T_C$ (K)'),('Coercivity (Oe)',r'$\log_{10}[H_c/(1\ \mathrm{Oe})]$')]):
 g=d[(d.target==target)&(d.protocol=='composition_grouped_refit')];ax=axs[0,k];ax.scatter(g.observed,g.predicted,s=15,c=COLORS[k],alpha=.65,edgecolors='none',rasterized=True);lo=min(g.observed.min(),g.predicted.min());hi=max(g.observed.max(),g.predicted.max());ax.plot([lo,hi],[lo,hi],color='#555555',linestyle='--',lw=1);ax.set(xlabel='Observed '+unit,ylabel='Predicted '+unit);ax.text(.04,.94,f'Composition-grouped refit\n$R^2$ = {r2_score(g.observed,g.predicted):.3f}\nMAE = {mean_absolute_error(g.observed,g.predicted):.1f}' if k==0 else f'Composition-grouped refit\n$R^2$ = {r2_score(g.observed,g.predicted):.3f}\nMAE = {mean_absolute_error(g.observed,g.predicted):.3f}',va='top',transform=ax.transAxes,fontsize=9)
 scores=[r2_score((q:=d[(d.target==target)&(d.protocol==p)]).observed,q.predicted) for p in prots];ax=axs[1,k];ax.bar(np.arange(4),scores,color=[COLORS[6],COLORS[k],COLORS[3],COLORS[2]],width=.62);ax.set(xticks=np.arange(4),xticklabels=names,ylabel=r'Test $R^2$',ylim=(0,.88));ax.tick_params(axis='x',labelsize=8)
 for i,s in enumerate(scores):ax.text(i,s+.025,f'{s:.3f}',ha='center',fontsize=9)
for ax,l in zip(axs.flat,'abcd'):panel(ax,l)
save(fig,3)

