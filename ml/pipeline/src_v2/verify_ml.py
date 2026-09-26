"""Six small fixed-parameter refits; no search, DFT, or spin simulations.
Run in the existing WSL Python environment. All outputs stay beside this file.
"""
from pathlib import Path
import json,platform
import numpy as np
import pandas as pd
import sklearn,xgboost
from sklearn.model_selection import train_test_split,GroupShuffleSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
from xgboost import XGBRegressor
O=Path(__file__).resolve().parent;R=O.parents[1]
raw=pd.read_csv(R/'ML-data/magneticMaterials_finalDataset_encoded.csv')
x=[c for c in raw if c.startswith('x_')];targets=['Curie(TC) (K)','Coercivity (Oe)']
clean=raw.drop_duplicates();clean=clean[clean['rho_theoretical (g/cm^3)']>0].copy()
metrics=[];predictions=[];groupmodels={};manifest={}
def groups(d):return pd.factorize(d[x].round(8).apply(tuple,axis=1))[0]
for protocol,d in [('notebook_fixed',raw),('composition_random',clean),('composition_grouped',clean)]:
 g=groups(d)
 if protocol=='composition_grouped':tr,te=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42).split(d,groups=g))
 else:tr,te=train_test_split(np.arange(len(d)),test_size=.2,random_state=42)
 features=[c for c in d if c not in targets] if protocol=='notebook_fixed' else x+['VEC','rho_theoretical (g/cm^3)']
 X=d[features].astype(float)
 overlap=np.isin(g[te],g[tr])
 manifest[protocol]=dict(n_train=len(tr),n_test=len(te),n_features=len(features),n_groups=len(set(g)),test_rows_composition_seen=int(overlap.sum()),train_source_rows=d.index[tr].tolist(),test_source_rows=d.index[te].tolist())
 for target in targets:
  y=d[target].to_numpy(); is_tc=target.startswith('Curie');y=y if is_tc else np.log10(y)
  model=XGBRegressor(n_estimators=200,max_depth=7,learning_rate=.1,random_state=42,n_jobs=2,tree_method='hist') if is_tc else RandomForestRegressor(n_estimators=200,min_samples_leaf=1,max_features=1.,random_state=42,n_jobs=2)
  model.fit(X.iloc[tr],y[tr]);p=model.predict(X.iloc[te]);base=np.full(len(te),np.mean(y[tr]))
  m=dict(protocol=protocol,target=target,n_train=len(tr),n_test=len(te),r2=r2_score(y[te],p),mae=mean_absolute_error(y[te],p),rmse=mean_squared_error(y[te],p)**.5,baseline_r2=r2_score(y[te],base),baseline_mae=mean_absolute_error(y[te],base),test_composition_overlap=int(overlap.sum()))
  spread=np.full(len(te),np.nan)
  if not is_tc:
   spread=np.std([tree.predict(X.iloc[te].values) for tree in model.estimators_],axis=0)
   m['coverage_within_2_tree_sd']=float(np.mean(np.abs(y[te]-p)<=2*spread))
  metrics.append(m)
  for k,ix in enumerate(te):predictions.append(dict(protocol=protocol,target=target,source_row=int(d.index[ix]),composition_group=int(g[ix]),composition_seen=bool(overlap[k]),observed=y[ix],predicted=float(p[k]),tree_sd=spread[k]))
  if protocol=='composition_grouped':groupmodels[target]=(model,features)
  print(m,flush=True)
pd.DataFrame(metrics).to_csv(O/'ml_metrics.csv',index=False);pd.DataFrame(predictions).to_csv(O/'ml_predictions.csv',index=False)
clean.assign(source_row=clean.index,composition_group=groups(clean)).to_csv(O/'ml_clean_data.csv',index=False)
# Inference only on the original notebook's random composition design.
rng=np.random.RandomState(42);comp=np.round(rng.dirichlet([5,2,1.5,1,.5,.5],1000),3);comp/=comp.sum(axis=1,keepdims=True)
elements=['Fe','Co','Ni','Mn','Al','Si'];v=pd.DataFrame(0.,index=np.arange(1000),columns=x)
for i,e in enumerate(elements):v['x_'+e]=comp[:,i]
v['VEC']=comp@np.array([8,9,10,7,3,4]);v['rho_theoretical (g/cm^3)']=comp@np.array([7.874,8.90,8.908,7.21,2.70,2.33])
res=pd.DataFrame(comp,columns=elements);res.insert(0,'virtual_id',np.arange(1000));res['VEC']=v.VEC
for target,(model,features) in groupmodels.items():
 pr=model.predict(v[features]);res['predicted_Tc_K' if target.startswith('Curie') else 'predicted_log10_Hc_Oe']=pr
res['predicted_Hc_Oe']=10**res.predicted_log10_Hc_Oe;res['passes_point_thresholds']=(res.predicted_Tc_K>1000)&(res.predicted_Hc_Oe<100)
trainrows=manifest['composition_grouped']['train_source_rows'];cx=raw.loc[trainrows,x].to_numpy();vx=v[x].to_numpy()
res['nearest_training_composition_L1']=[np.abs(cx-row).sum(axis=1).min() for row in vx]
res.to_csv(O/'virtual_screening.csv',index=False)
audit=dict(raw_rows=len(raw),duplicates=int(raw.duplicated().sum()),zero_density_after_dedup=int((raw.drop_duplicates()['rho_theoretical (g/cm^3)']<=0).sum()),clean_rows=len(clean),active_elements=int((raw[x].sum()>0).sum()),raw_unique_compositions=len(set(groups(raw))),clean_unique_compositions=len(set(groups(clean))),clean_VEC_Tc_pearson=float(clean.VEC.corr(clean[targets[0]])),virtual_pass_count=int(res.passes_point_thresholds.sum()),python=platform.python_version(),sklearn=sklearn.__version__,xgboost=xgboost.__version__,protocols=manifest)
(O/'ml_audit.json').write_text(json.dumps(audit,indent=2));print('virtual passes',audit['virtual_pass_count'],flush=True)
# Distribution of label variation at identical encoded compositions.
g=clean.assign(group=groups(clean),logHc=np.log10(clean['Coercivity (Oe)'])).groupby('group')
dup=g.agg(n=('logHc','size'),Tc_min=(targets[0],'min'),Tc_max=(targets[0],'max'),logHc_min=('logHc','min'),logHc_max=('logHc','max'))
dup['Tc_range_K']=dup.Tc_max-dup.Tc_min;dup['logHc_range']=dup.logHc_max-dup.logHc_min;dup.to_csv(O/'composition_label_variation.csv')
