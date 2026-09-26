"""Raw SOC orientation differences. EDIFF is a target scale, not an error bar."""
import numpy as np
import pandas as pd
from plot_style import *
d=pd.read_csv(O/'figure9.csv');fig,ax=plt.subplots(figsize=(8.1,3.7));x=np.arange(len(d))
for off,col,label,color in [(-.18,'delta_e0_microeV_atom',r'$E_{\sigma\to0}$',COLORS[0]),(0,'delta_free_microeV_atom','Free energy',COLORS[1]),(.18,'delta_band_microeV_atom','Band energy',COLORS[2])]:ax.bar(x+off,d[col],width=.17,label=label,color=color)
ax.scatter(x,d.EDIFF_microeV_atom,marker='_',s=600,color='#555555',label='EDIFF / atom (target scale)');ax.axhline(0,color='#555555',lw=.7);ax.set(xticks=x,xticklabels=[LABELS[m]+'\n'+('[001] → [111]' if i<2 else '[001] → [100]') for i,m in enumerate(d.material)],ylabel=r'Raw energy difference ($\mu$eV/atom)',ylim=(-.08,.87));ax.legend(ncol=2,loc='upper right',frameon=False,fontsize=9);ax.text(.01,.93,'Unconverged as anisotropy constants',transform=ax.transAxes,fontsize=10)
save(fig,9)
