"""Interpretability of the held-out-composition models.

SHAP values and permutation importances are evaluated on the composition-grouped
test partition of the reference split, using the descriptor set and learner the
nested protocol selected most often.  The attributions therefore describe the
model's behaviour on compositions it was not fitted to.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
import shap
from sklearn.inspection import permutation_importance

import features_v3
from refit_v3 import TARGETS, grouped_split, make_model, target_vector, REFERENCE_SEED

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures_v3"
N_SHAP_FEATURES = 40


def main():
    d = pd.read_csv(HERE / "src_v2" / "ml_clean_data.csv").set_index("source_row")
    groups = d["composition_group"]
    choice = json.loads((HERE / "v3_production_choice.json").read_text())
    sets = features_v3.build(d)
    train, test = grouped_split(d.index, groups, seed=REFERENCE_SEED)

    shap_rows, imp_rows = {}, []
    for target in TARGETS:
        fs = choice["per_target_feature_set"][target]
        X = sets[fs]
        y = target_vector(d, target)
        m = make_model(choice["models"][target])
        m.fit(X.loc[train], y.loc[train])

        expl = shap.TreeExplainer(m)
        sv = expl.shap_values(X.loc[test], check_additivity=False)
        sv = np.asarray(sv)
        order = np.argsort(-np.abs(sv).mean(axis=0))[:N_SHAP_FEATURES]
        cols = X.columns[order]
        rows = []
        for j, c in zip(order, cols):
            rows.append(pd.DataFrame(dict(feature=c, shap=sv[:, j],
                                          value=X.loc[test, c].to_numpy())))
        shap_rows[target] = pd.concat(rows, ignore_index=True)

        pi = permutation_importance(m, X.loc[test], y.loc[test], n_repeats=15,
                                    random_state=42, n_jobs=2, scoring="r2")
        top = np.argsort(-pi.importances_mean)[:20]
        for j in top:
            imp_rows.append(dict(target=target, feature=X.columns[j],
                                 importance_mean=pi.importances_mean[j],
                                 importance_sd=pi.importances_std[j],
                                 feature_set=fs, model=choice["models"][target]))
        print(target, fs, choice["models"][target], "top:",
              list(X.columns[top[:6]]), flush=True)

    shap_rows[TARGETS[0]].to_csv(OUT / "figure5_shap_tc.csv", index=False)
    shap_rows[TARGETS[1]].to_csv(OUT / "figure5_shap_hc.csv", index=False)
    pd.DataFrame(imp_rows).to_csv(OUT / "figure5_importance.csv", index=False)
    print("interpretability tables written")


if __name__ == "__main__":
    main()
