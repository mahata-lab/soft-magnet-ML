"""Inference on the original Dirichlet composition grid; no model fitting."""
import pandas as pd
import numpy as np
from plot_style import *
d=pd.read_csv(O/'figure4.csv');p=d.passes_point_thresholds;fig,axs=plt.subplots(1,2,figsize=(9,3.6),layout='constrained')
sc=axs[0].scatter(d.VEC,d.predicted_Tc_K,c=d.predicted_log10_Hc_Oe,s=14,cmap='viridis',alpha=.65,rasterized=True);axs[0].scatter(d.loc[p,'VEC'],d.loc[p,'predicted_Tc_K'],s=30,facecolors='none',edgecolors=COLORS[1],lw=.8,label=f'{p.sum()} threshold hits');axs[0].axhline(1000,color='#555555',ls='--',lw=1);axs[0].set(xlabel='Valence electron concentration',ylabel=r'Predicted $T_C$ (K)');axs[0].legend(loc='lower right');fig.colorbar(sc,ax=axs[0],label=r'Predicted $\log_{10} H_c$',shrink=.8)
axs[1].scatter(d.loc[~p,'nearest_training_composition_L1'],d.loc[~p,'predicted_Tc_K'],s=14,color='#BBBBBB',alpha=.6,label='Other points');axs[1].scatter(d.loc[p,'nearest_training_composition_L1'],d.loc[p,'predicted_Tc_K'],s=20,color=COLORS[1],label='Threshold hits');axs[1].axhline(1000,color='#555555',ls='--',lw=1);axs[1].set(xlabel='Nearest training composition distance (L1)',ylabel=r'Predicted $T_C$ (K)');axs[1].legend(loc='lower right')
for ax,l in zip(axs,'ab'):panel(ax,l)
save(fig,4)
