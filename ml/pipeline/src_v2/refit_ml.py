"""Bounded refit: three prespecified models per target, one internal grouped
validation split, then one selected-model refit per target. No parameter search.
The existing outer composition-held-out test rows are never used in selection.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
from xgboost import XGBRegressor
O=Path(__file__).resolve().parent
d=pd.read_csv(O/'ml_clean_data.csv').set_index('source_row');a=json.loads((O/'ml_audit.json').read_text());m=a['protocols']['composition_grouped'];tr=np.array(m['train_source_rows']);te=np.array(m['test_source_rows'])
features=[c for c in d if c.startswith('x_')]+['VEC','rho_theoretical (g/cm^3)'];X=d[features].astype(float)
inner_train,inner_val=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=17).split(X.loc[tr],groups=d.loc[tr,'composition_group']))
it=tr[inner_train];iv=tr[inner_val]
assert not set(d.loc[it,'composition_group'])&set(d.loc[iv,'composition_group'])
assert not set(d.loc[tr,'composition_group'])&set(d.loc[te,'composition_group'])
def model(name):
 if name=='RF_regularized':return RandomForestRegressor(n_estimators=300,min_samples_leaf=2,max_features=.7,random_state=42,n_jobs=2)
 if name=='ExtraTrees_regularized':return ExtraTreesRegressor(n_estimators=300,min_samples_leaf=2,max_features=1.,random_state=42,n_jobs=2)
 return XGBRegressor(n_estimators=300,max_depth=3,learning_rate=.04,min_child_weight=5,reg_lambda=10,subsample=.9,colsample_bytree=.9,random_state=42,n_jobs=2,tree_method='hist')
scores=[];preds=[];metrics=[];selected={}
for target in ['Curie(TC) (K)','Coercivity (Oe)']:
 y=d[target] if target.startswith('Curie') else np.log10(d[target]); trials=[]
 for name in ['RF_regularized','ExtraTrees_regularized','XGB_regularized']:
  mod=model(name);mod.fit(X.loc[it],y.loc[it]);pr=mod.predict(X.loc[iv]);s=dict(target=target,model=name,validation_r2=r2_score(y.loc[iv],pr),validation_mae=mean_absolute_error(y.loc[iv],pr),n_inner_train=len(it),n_validation=len(iv));scores.append(s);trials.append(s);print(s,flush=True)
 best=max(trials,key=lambda q:q['validation_r2'])['model'];mod=model(best);mod.fit(X.loc[tr],y.loc[tr]);pr=mod.predict(X.loc[te]);base=np.full(len(te),y.loc[tr].mean())
 me=dict(protocol='composition_grouped_refit',target=target,model=best,n_train=len(tr),n_test=len(te),r2=r2_score(y.loc[te],pr),mae=mean_absolute_error(y.loc[te],pr),rmse=mean_squared_error(y.loc[te],pr)**.5,baseline_r2=r2_score(y.loc[te],base),baseline_mae=mean_absolute_error(y.loc[te],base),test_composition_overlap=0);metrics.append(me);print('OUTER TEST',me,flush=True)
 for row,p in zip(te,pr):preds.append(dict(protocol='composition_grouped_refit',target=target,source_row=row,composition_group=d.loc[row,'composition_group'],composition_seen=False,observed=y.loc[row],predicted=p,tree_sd=np.nan))
 selected[target]=(mod,best)
pd.DataFrame(scores).to_csv(O/'refit_validation.csv',index=False);pd.DataFrame(metrics).to_csv(O/'refit_metrics.csv',index=False);pd.DataFrame(preds).to_csv(O/'refit_predictions.csv',index=False)
(O/'refit_protocol.json').write_text(json.dumps(dict(inner_train=it.tolist(),inner_validation=iv.tolist(),outer_train=tr.tolist(),outer_test=te.tolist(),selection='Highest internal grouped-validation R2 from three prespecified models per target; outer test not used to choose model'),indent=2))
# Inference on unchanged original virtual grid; no full-data retraining.
v=pd.read_csv(O/'virtual_screening.csv');vx=pd.DataFrame(0.,index=v.index,columns=features)
for e in ['Fe','Co','Ni','Mn','Al','Si']:vx['x_'+e]=v[e]
vx['VEC']=v.VEC;vx['rho_theoretical (g/cm^3)']=v[['Fe','Co','Ni','Mn','Al','Si']].values@np.array([7.874,8.9,8.908,7.21,2.7,2.33])
for target,(mod,name) in selected.items():v['predicted_Tc_K' if target.startswith('Curie') else 'predicted_log10_Hc_Oe']=mod.predict(vx)
v['predicted_Hc_Oe']=10**v.predicted_log10_Hc_Oe;v['passes_point_thresholds']=(v.predicted_Tc_K>1000)&(v.predicted_Hc_Oe<100);v.to_csv(O/'virtual_screening_refit.csv',index=False);print('Refit virtual passes',v.passes_point_thresholds.sum())
