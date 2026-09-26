"""Assemble the figure source tables for v3 from the evaluation and generator
outputs.  Every figure reads exactly one or more of the CSV files written here,
so each panel can be regenerated from the shipped tables alone.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

import features_v3
from refit_v3 import TARGETS, grouped_split, make_model, target_vector, REFERENCE_SEED

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures_v3"
SRC = HERE / "src_v2"
TC, HC = TARGETS


def main():
    d = pd.read_csv(SRC / "ml_clean_data.csv").set_index("source_row")
    groups = d["composition_group"]
    nested = pd.read_csv(HERE / "v3_nested_metrics.csv")
    nsum = pd.read_csv(HERE / "v3_nested_summary.csv")
    old = pd.read_csv(OUT / "ml_metrics.csv")

    # ---- figure 3 -----------------------------------------------------------
    rep = nested[nested.split != "v2_reference_split"].copy()
    sd, mae_map = {}, {}
    for _, r in nested.iterrows():
        _, te = grouped_split(d.index, groups, seed=int(r.seed))
        sd[(r.split, r.target)] = d.loc[te, r.target].std() if r.target == TC \
            else np.log10(d.loc[te, r.target]).std()
    nested["test_target_sd"] = [sd[(r.split, r.target)] for _, r in nested.iterrows()]
    nested.to_csv(OUT / "figure3_repeats.csv", index=False)

    prot = []
    for t in TARGETS:
        o = old[old.target == t].set_index("protocol")
        n = nsum[nsum.target == t].iloc[0]
        ref = nested[(nested.split == "v2_reference_split") & (nested.target == t)].iloc[0]
        prot += [
            dict(protocol="notebook_random", target=t, r2=o.loc["notebook_fixed", "r2"],
                 r2_sd=np.nan,
                 test_rows_sharing_a_training_composition=o.loc["notebook_fixed",
                                                                "test_composition_overlap"]),
            dict(protocol="composition_random", target=t, r2=o.loc["composition_random", "r2"],
                 r2_sd=np.nan,
                 test_rows_sharing_a_training_composition=o.loc["composition_random",
                                                                "test_composition_overlap"]),
            dict(protocol="grouped_single_v2", target=t, r2=ref.r2, r2_sd=np.nan,
                 test_rows_sharing_a_training_composition=0),
            dict(protocol="grouped_repeated_v3", target=t, r2=n.r2_mean, r2_sd=n.r2_sd,
                 test_rows_sharing_a_training_composition=0),
        ]
    pd.DataFrame(prot).to_csv(OUT / "figure3_protocols.csv", index=False)

    # ---- figure 4 -----------------------------------------------------------
    # Pooled held-out predictions from all twenty repeats (see pooled_predictions.py).
    pd.read_csv(HERE / "v3_pooled_predictions.csv").to_csv(
        OUT / "figure4_parity.csv", index=False)
    des = pd.read_csv(HERE / "v3_summary.csv")[
        ["feature_set", "target", "r2_mean", "r2_sd", "mae_mean", "coverage_mean"]]
    des.to_csv(OUT / "figure4_descriptors.csv", index=False)

    # Coverage as a function of the nominal conformal level, re-derived on the
    # reference split; plus the empirical coverage of a +/-2 tree s.d. interval.
    sets = features_v3.build(d)
    choice = json.loads((HERE / "v3_production_choice.json").read_text())
    train, test = grouped_split(d.index, groups, seed=REFERENCE_SEED)
    inner_tr, inner_va = grouped_split(train, groups.loc[train], seed=1000 + REFERENCE_SEED)
    cov_rows = []
    for t in TARGETS:
        fs = choice["per_target_feature_set"][t]
        X, y = sets[fs], target_vector(d, t)
        m = make_model(choice["models"][t])
        m.fit(X.loc[inner_tr], y.loc[inner_tr])
        res = np.abs(y.loc[inner_va].to_numpy() - m.predict(X.loc[inner_va]))
        m2 = make_model(choice["models"][t])
        m2.fit(X.loc[train], y.loc[train])
        err = np.abs(y.loc[test].to_numpy() - m2.predict(X.loc[test]))
        rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=2,
                                   max_features=0.5, random_state=42, n_jobs=2)
        rf.fit(X.loc[train], y.loc[train])
        tree_pred = np.stack([e.predict(X.loc[test].to_numpy()) for e in rf.estimators_])
        tree_err = np.abs(y.loc[test].to_numpy() - tree_pred.mean(axis=0))
        tree_cov = float(np.mean(tree_err <= 2 * tree_pred.std(axis=0)))
        n = len(res)
        for lvl in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]:
            q = np.quantile(res, min(1.0, np.ceil((n + 1) * lvl) / n))
            cov_rows.append(dict(target=t, nominal=lvl, empirical=float(np.mean(err <= q)),
                                 halfwidth=float(q), tree_coverage_at_2sd=tree_cov))
    pd.DataFrame(cov_rows).to_csv(OUT / "figure4_coverage.csv", index=False)

    # ---- figure 6 -----------------------------------------------------------
    r = pd.read_csv(HERE / "v3_recipes_all.csv")
    keep = ["Fe", "Co", "Ni", "Mn", "Al", "Si", "VEC", "predicted_Tc_K", "Tc_lower_K",
            "Tc_upper_K", "predicted_Hc_Oe", "Hc_lower_Oe", "Hc_upper_Oe",
            "L1_to_nearest_training", "novelty", "point_pass", "interval_pass",
            "supported_recipe", "recipe_score"]
    r[keep].to_csv(OUT / "figure6_candidates.csv", index=False)
    top = r[r.supported_recipe] if r.supported_recipe.any() else r
    top.head(15)[keep].to_csv(OUT / "figure6_top.csv", index=False)

    summ = json.loads((HERE / "v3_recipe_summary.json").read_text())
    dist = pd.concat([
        pd.DataFrame(dict(kind="candidate", distance=r.L1_to_nearest_training)),
        pd.DataFrame(dict(kind="calibration",
                          distance=pd.read_csv(HERE / "v3_calibration_distances.csv").distance)),
    ], ignore_index=True)
    dist["d50"] = summ["calibration_distance_median"]
    dist["d90"] = summ["calibration_distance_p90"]
    dist.to_csv(OUT / "figure6_distance.csv", index=False)

    pd.DataFrame([
        dict(stage="Generated candidates", n=summ["n_candidates"],
             note="Dirichlet design over six elements"),
        dict(stage="Point-prediction pass", n=summ["n_point_pass"],
             note=r"$T_C>1000$ K and $H_c<100$ Oe"),
        dict(stage="Interval-robust pass", n=summ["n_interval_pass"],
             note="90% interval entirely inside the target"),
        dict(stage="Supported recipes", n=summ["n_supported"],
             note="and not far extrapolation"),
    ]).to_csv(OUT / "figure6_funnel.csv", index=False)

    # Which threshold pairs the generator can actually resolve.
    tcs = np.arange(300.0, 1101.0, 25.0)
    hcs = np.logspace(0, 4, 41)
    grid = []
    ok = r.novelty != "far-extrapolation"
    for a in tcs:
        for b in hcs:
            n_int = int(((r.Tc_lower_K > a) & (r.Hc_upper_Oe < b) & ok).sum())
            n_pt = int(((r.predicted_Tc_K > a) & (r.predicted_Hc_Oe < b)).sum())
            grid.append(dict(tc_threshold=a, hc_threshold=b,
                             n_interval_robust=n_int, n_point=n_pt))
    g = pd.DataFrame(grid)
    g.to_csv(OUT / "figure6_resolution.csv", index=False)
    feas = g[g.n_interval_robust >= 10]
    best = feas.loc[feas.tc_threshold.idxmax()] if len(feas) else None
    (HERE / "v3_resolution_summary.json").write_text(json.dumps(dict(
        most_demanding_Tc_with_10_recipes=float(best.tc_threshold) if best is not None else None,
        matching_Hc=float(best.hc_threshold) if best is not None else None,
        n_at_target=int(g[(g.tc_threshold == 1000) &
                          (np.isclose(g.hc_threshold, hcs[np.argmin(abs(hcs - 100))]))
                          ].n_interval_robust.iloc[0])), indent=2))

    print("figure tables written")


if __name__ == "__main__":
    main()
