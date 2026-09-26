"""Candidate energy comparison and composition mismatch; no phase-stability claim."""
import numpy as np
import pandas as pd
from plot_style import *
d=pd.read_csv(O/'figure6.csv');fig,axs=plt.subplots(1,2,figsize=(8.8,3.6),layout='constrained');els=['Fe','Co','Ni','Mn','Al','Si'];delta=[];mismatch=[]
for c,g in d.groupby('candidate'):
 b=g[g.phase=='BCC'].iloc[0];f=g[g.phase=='FCC'].iloc[0];delta.append((f.energy_eV_atom-b.energy_eV_atom)*1000);mismatch.append([(0 if pd.isna(f.get('x_'+e,0)) else f['x_'+e])*100-(0 if pd.isna(b.get('x_'+e,0)) else b['x_'+e])*100 for e in els])
axs[0].bar([1,2,3],delta,color=[COLORS[0],COLORS[0],COLORS[1]],width=.6);axs[0].axhline(0,color='#555555',lw=.8);axs[0].set(xticks=[1,2,3],xticklabels=['C1','C2','C3'],ylabel=r'$E_{\mathrm{FCC}}/N_{\mathrm{FCC}}-E_{\mathrm{BCC}}/N_{\mathrm{BCC}}$'+'\n(meV/atom)',ylim=(-18,80));axs[0].text(.04,.95,'Different compositions\nNo stability assignment',va='top',transform=axs[0].transAxes,fontsize=9)
for i,v in enumerate(delta):axs[0].text(i+1,v+2 if v>=0 else v-2,f'{v:+.2f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
im=axs[1].imshow(mismatch,cmap='RdBu_r',vmin=-1,vmax=1,aspect='auto');axs[1].set(xticks=range(6),xticklabels=els,yticks=range(3),yticklabels=['C1','C2','C3']);fig.colorbar(im,ax=axs[1],label='FCC − BCC composition (at.%)',shrink=.85)
for i in range(3):
 for j in range(6):axs[1].text(j,i,f'{mismatch[i][j]:+.2f}',ha='center',va='center',fontsize=8,color='white' if abs(mismatch[i][j])>.6 else 'black')
for ax,l in zip(axs,'ab'):panel(ax,l)
save(fig,6)
