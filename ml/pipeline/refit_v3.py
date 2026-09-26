"""v3 evaluation: descriptor-set comparison under repeated composition-grouped
splitting, with nested model selection and split-conformal prediction intervals.

Nothing in this script touches an outer test partition before that partition is
scored.  Model choice and interval width are fixed inside each outer training
partition using a further grouped split.

Outputs (all written next to this file):
  v3_repeat_metrics.csv     per repeat / descriptor set / target outer-test scores
  v3_summary.csv            mean +/- sd over the ten random repeats
  v3_selection.csv          inner-validation scores that drove model selection
  v3_predictions.csv        outer-test predictions for the reference split
  v3_protocol.json          split membership and software versions
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from xgboost import XGBRegressor

import features_v3

HERE = Path(__file__).resolve().parent
SRC = HERE / "src_v2"
TARGETS = ["Curie(TC) (K)", "Coercivity (Oe)"]
FEATURE_SETS = ["fractions", "physics", "combined"]
MODELS = ["RF", "ExtraTrees", "XGB"]
N_REPEATS = 10
REFERENCE_SEED = 42          # the split used in v2, kept for continuity
CONFORMAL_LEVEL = 0.90


def make_model(name, seed=42):
    if name == "RF":
        return RandomForestRegressor(n_estimators=300, min_samples_leaf=2,
                                     max_features=0.5, random_state=seed, n_jobs=2)
    if name == "ExtraTrees":
        return ExtraTreesRegressor(n_estimators=300, min_samples_leaf=1,
                                   max_features=0.7, random_state=seed, n_jobs=2)
    return XGBRegressor(n_estimators=600, max_depth=4, learning_rate=0.03,
                        min_child_weight=4, reg_lambda=5.0, subsample=0.85,
                        colsample_bytree=0.6, random_state=seed, n_jobs=2,
                        tree_method="hist")


def target_vector(d, target):
    """Curie temperature is modelled directly; coercivity on a base-10 log scale."""
    return d[target].astype(float) if target.startswith("Curie") else np.log10(d[target].astype(float))


def grouped_split(index, groups, seed, test_size=0.2):
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=test_size,
                                    random_state=seed).split(index, groups=groups))
    return np.asarray(index)[tr], np.asarray(index)[te]


def evaluate(X, y, groups, train, test, seed, records, tag):
    """Select a model on an inner grouped split, refit, score the untouched test."""
    inner_tr, inner_va = grouped_split(train, groups.loc[train], seed=1000 + seed)
    assert not set(groups.loc[inner_tr]) & set(groups.loc[inner_va])
    assert not set(groups.loc[train]) & set(groups.loc[test])

    trials = []
    for name in MODELS:
        m = make_model(name)
        m.fit(X.loc[inner_tr], y.loc[inner_tr])
        p = m.predict(X.loc[inner_va])
        trials.append(dict(model=name,
                           inner_r2=r2_score(y.loc[inner_va], p),
                           inner_mae=mean_absolute_error(y.loc[inner_va], p),
                           residuals=np.abs(y.loc[inner_va].to_numpy() - p)))
    for t in trials:
        records.append({**tag, "model": t["model"], "inner_r2": t["inner_r2"],
                        "inner_mae": t["inner_mae"]})

    best = max(trials, key=lambda t: t["inner_r2"])
    # Split-conformal half-width from the inner validation residuals only.
    n = len(best["residuals"])
    q = np.quantile(best["residuals"], min(1.0, np.ceil((n + 1) * CONFORMAL_LEVEL) / n))

    model = make_model(best["model"])
    model.fit(X.loc[train], y.loc[train])
    pred = model.predict(X.loc[test])
    obs = y.loc[test].to_numpy()
    base = np.full(len(test), y.loc[train].mean())
    return dict(model=best["model"],
                inner_r2=best["inner_r2"],
                n_train=len(train), n_test=len(test),
                r2=r2_score(obs, pred),
                mae=mean_absolute_error(obs, pred),
                rmse=mean_squared_error(obs, pred) ** 0.5,
                baseline_r2=r2_score(obs, base),
                baseline_mae=mean_absolute_error(obs, base),
                conformal_halfwidth=q,
                conformal_coverage=float(np.mean(np.abs(obs - pred) <= q)),
                ), pred, obs, model


def main():
    d = pd.read_csv(SRC / "ml_clean_data.csv").set_index("source_row")
    groups = d["composition_group"]
    sets = features_v3.build(d)
    rows, selection, preds = [], [], []

    seeds = [REFERENCE_SEED] + list(range(N_REPEATS))
    for seed in seeds:
        label = "reference" if seed == REFERENCE_SEED else f"repeat_{seed}"
        train, test = grouped_split(d.index, groups, seed=seed)
        for fs in FEATURE_SETS:
            X = sets[fs]
            for target in TARGETS:
                y = target_vector(d, target)
                tag = dict(split=label, seed=seed, feature_set=fs, target=target)
                res, pred, obs, model = evaluate(X, y, groups, train, test, seed, selection, tag)
                rows.append({**tag, **res})
                print(f"{label:12s} {fs:10s} {target[:12]:12s} "
                      f"{res['model']:11s} R2={res['r2']:.3f} MAE={res['mae']:.3f} "
                      f"cov={res['conformal_coverage']:.3f}", flush=True)
                if label == "reference":
                    for r, p, o in zip(test, pred, obs):
                        preds.append(dict(feature_set=fs, target=target, source_row=r,
                                          composition_group=groups.loc[r],
                                          observed=o, predicted=p,
                                          conformal_halfwidth=res["conformal_halfwidth"]))

    m = pd.DataFrame(rows)
    m.to_csv(HERE / "v3_repeat_metrics.csv", index=False)
    pd.DataFrame(selection).to_csv(HERE / "v3_selection.csv", index=False)
    pd.DataFrame(preds).to_csv(HERE / "v3_predictions.csv", index=False)

    rep = m[m.split != "reference"]
    summary = (rep.groupby(["feature_set", "target"])
                  .agg(r2_mean=("r2", "mean"), r2_sd=("r2", "std"),
                       r2_min=("r2", "min"), r2_max=("r2", "max"),
                       mae_mean=("mae", "mean"), mae_sd=("mae", "std"),
                       rmse_mean=("rmse", "mean"),
                       coverage_mean=("conformal_coverage", "mean"),
                       halfwidth_mean=("conformal_halfwidth", "mean"),
                       baseline_r2_mean=("baseline_r2", "mean"),
                       n_repeats=("r2", "size"))
                  .reset_index())
    ref = m[m.split == "reference"][["feature_set", "target", "model", "r2", "mae", "rmse",
                                     "conformal_coverage", "conformal_halfwidth"]]
    ref = ref.rename(columns={c: "reference_" + c for c in
                              ["model", "r2", "mae", "rmse", "conformal_coverage",
                               "conformal_halfwidth"]})
    summary = summary.merge(ref, on=["feature_set", "target"])
    summary.to_csv(HERE / "v3_summary.csv", index=False)
    print("\n", summary.to_string(index=False))

    import sklearn, xgboost
    (HERE / "v3_protocol.json").write_text(json.dumps(dict(
        n_records=int(len(d)), n_groups=int(groups.nunique()),
        seeds=seeds, reference_seed=REFERENCE_SEED,
        conformal_level=CONFORMAL_LEVEL,
        feature_counts={k: int(v.shape[1]) for k, v in sets.items()},
        models=MODELS,
        selection="highest inner grouped-validation R2; outer test never used",
        python=sys.version.split()[0], sklearn=sklearn.__version__,
        xgboost=xgboost.__version__), indent=2))


if __name__ == "__main__":
    main()
