"""Extract figure tables from existing audit outputs. No simulations or ML fits."""
from pathlib import Path
import re,json
import numpy as np
import pandas as pd
O=Path(__file__).resolve().parent;R=O.parents[1]
a=pd.read_csv(O/'dft_run_audit.csv');d=pd.read_csv(O/'ml_clean_data.csv')
pd.DataFrame([
 ['Literature data','1,736 encoded records','Deduplicate and check units',0,0],
 ['ML evaluation','1,713 records; 1,058 compositions','Fixed models; composition grouping',1,0],
 ['Screening','1,000 Fe–Co–Ni–Mn–Al–Si points','32 point-threshold hits; hypotheses',2,0],
 ['DFT benchmarks','Existing volume, SOC and spin-state outputs','Check atoms, spin states and convergence',0,1],
 ['Spin benchmarks','Seven existing VAMPIRE curves','Recover inputs and transition proxies',1,1],
 ['Interpretation','Composition priorities and validation limits','No claim of validated coercivity',2,1],
],columns=['stage','data','method','column','row']).to_csv(O/'figure1.csv',index=False)
d['log10_Hc_Oe']=np.log10(d['Coercivity (Oe)']);d.to_csv(O/'figure2.csv',index=False)
pd.concat([pd.read_csv(O/'ml_predictions.csv'),pd.read_csv(O/'refit_predictions.csv')],ignore_index=True).to_csv(O/'figure3.csv',index=False)
pd.read_csv(O/'virtual_screening_refit.csv').to_csv(O/'figure4.csv',index=False)
v=a[(a.archive=='dft_runs')&a.run.str.contains('_vol_')].copy()
v['material']=v.run.str.extract(r'Run_\d+_(.+)_vol_')[0];v['moment_muB_atom']=v.mag_total_muB/v.natoms
v['include_energy_curve']=~v.run.str.startswith('Run_01_')
v['relative_energy_meV_atom']=np.nan
for mat,g in v.groupby('material'):
 ix=g[g.include_energy_curve].index;v.loc[ix,'relative_energy_meV_atom']=1000*(v.loc[ix,'energy_eV_atom']-v.loc[ix,'energy_eV_atom'].min())
v.to_csv(O/'figure5.csv',index=False)
c=a[(a.archive=='dft_runs')&a.run.str.contains('SQS')].copy();c['candidate']=c.run.str.extract(r'cand(\d)')[0].astype(int);c['phase']=c.run.str.extract(r'_(BCC|FCC)$')[0];c['moment_muB_atom']=c.mag_total_muB/c.natoms
c.to_csv(O/'figure6.csv',index=False)
ma=a[(a.archive=='new_runs')&a.run.str.contains('MAE')].copy();ma['material']=ma.run.str.extract(r'Run_\d+_(.+)_MAE')[0]
ma['ebands_eV']=np.nan;ma['fixed_density_magnetization_spinor']=''
for ix,row in ma.iterrows():
 txt=(R/row.path/'OUTCAR').read_text(errors='replace')
 vals=re.findall(r'EBANDS\s*=\s*([-+\d.Ee]+)',txt)
 if vals:ma.loc[ix,'ebands_eV']=float(vals[-1])
 vals=re.findall(r'number of electron\s+[-+\d.Ee]+\s+magnetization\s+([^\n]+)',txt)
 if vals:ma.loc[ix,'fixed_density_magnetization_spinor']=vals[-1].strip()
ma.to_csv(O/'mae_raw_outputs.csv',index=False)
mr=[]
for mat,g in ma.groupby('material',sort=False):
 g=g.sort_values('run');u,w=g.iloc[0],g.iloc[1];mr.append(dict(material=mat,axis1=u.SAXIS,axis2=w.SAXIS,natoms=u.natoms,energy1_eV=u.e0_eV,energy2_eV=w.e0_eV,delta_e0_microeV_atom=(w.e0_eV-u.e0_eV)*1e6/u.natoms,delta_free_microeV_atom=(w.toten_eV-u.toten_eV)*1e6/u.natoms,delta_band_microeV_atom=(w.ebands_eV-u.ebands_eV)*1e6/u.natoms,EDIFF_microeV_atom=float(u.EDIFF)*1e6/u.natoms,source1=u.path,source2=w.path))
pd.DataFrame(mr).to_csv(O/'figure7.csv',index=False)
pd.read_csv(O/'vampire_all_curves.csv').to_csv(O/'figure8.csv',index=False)
# Retain electronic step histories for all archived calculations.
steps=[]
for _,r in a.iterrows():
 p=R/r.path/'OSZICAR'
 if not p.exists():continue
 for line in p.read_text(errors='replace').splitlines():
  m=re.match(r'^\s*(DAV|RMM|CG|DMP):\s*(\d+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)',line)
  if m:steps.append(dict(path=r.path,solver=m[1],step=int(m[2]),energy_eV=float(m[3]),delta_energy_eV=float(m[4])))
pd.DataFrame(steps).to_csv(O/'electronic_convergence.csv',index=False)
print('Figure tables ready; existing electronic steps:',len(steps));print(pd.DataFrame(mr).to_string(index=False))

