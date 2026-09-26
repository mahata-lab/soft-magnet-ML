from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent
COLORS=['#1965B0','#D55E00','#009E73','#8E6BBE','#DFAF22','#4C98A8','#777777']
LABELS={'bccFe':'bcc Fe','B2FeCo':'B2 FeCo','L12Fe3Co':r'L1$_2$ Fe$_3$Co','L12FeCo3':r'L1$_2$ FeCo$_3$','fccCo':'fcc Co','fccNi':'fcc Ni','fccMn':'fcc Mn'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':11,'axes.titlesize':11,'legend.fontsize':9,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.8,'xtick.direction':'out','ytick.direction':'out','pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
def panel(ax,label):ax.text(-.13,1.06,label,transform=ax.transAxes,fontweight='bold',fontsize=13)
def save(fig,n):
 for ext in ['png','pdf','svg']:fig.savefig(O/f'figure{n}.{ext}',dpi=600,bbox_inches='tight')
 plt.close(fig)
