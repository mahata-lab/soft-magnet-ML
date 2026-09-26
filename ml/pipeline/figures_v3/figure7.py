"""Static DFT energy and moment scans, normalized by actual atom count."""
import pandas as pd
from plot_style import *
d=pd.read_csv(O/'figure7.csv');fig,axs=plt.subplots(2,2,figsize=(8.7,6.1),layout='constrained')
for ax,(mat,g),col,l in zip(axs.flat,d.groupby('material',sort=False),COLORS,'abcd'):
 g=g[g.include_energy_curve].sort_values('a_A');ax.plot(g.a_A,g.relative_energy_meV_atom,'o-',color=col,lw=1.4,ms=4);ax.set(xlabel=r'Lattice parameter ($\AA$)',ylabel=r'$E-E_{\min}$ (meV/atom)',title=LABELS[mat]);ax2=ax.twinx();ax2.plot(g.a_A,g.moment_muB_atom,'s--',color='#555555',lw=1,ms=3);ax2.set_ylabel(r'Moment ($\mu_B$/atom)',color='#555555');ax2.spines['right'].set_visible(True);panel(ax,l)
save(fig,7)
