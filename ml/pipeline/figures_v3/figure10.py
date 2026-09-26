"""All existing VAMPIRE curves; show ferromagnetic and Mn responses separately."""
import pandas as pd
from plot_style import *
d=pd.read_csv(O/'figure10.csv');fig,axs=plt.subplots(1,2,figsize=(9,3.7),layout='constrained')
for mat,color in zip(['bccFe','B2FeCo','L12Fe3Co','L12FeCo3','fccCo','fccNi'],COLORS):
 g=d[d.material==mat];axs[0].plot(g.temperature_K,g.last_output_column,lw=1.35,color=color,label=LABELS[mat])
axs[0].axhline(.1,color='#555555',ls=':',lw=1);axs[0].set(xlabel='Temperature (K)',ylabel='Normalized magnetization magnitude',xlim=(0,1800),ylim=(0,1.03));axs[0].legend(frameon=False,ncol=2,fontsize=8)
g=d[d.material=='fccMn'];axs[1].plot(g.temperature_K,g.last_output_column,lw=1.2,color=COLORS[3]);axs[1].set(xlabel='Temperature (K)',ylabel='Normalized net magnetization magnitude',xlim=(0,500));axs[1].text(.05,.92,'fcc Mn\nNet magnetization does not locate $T_N$',va='top',transform=axs[1].transAxes,fontsize=9)
for ax,l in zip(axs,'ab'):panel(ax,l)
save(fig,10)
