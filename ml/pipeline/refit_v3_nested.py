"""Fully nested evaluation: both the descriptor set and the learner are chosen
inside each outer training partition, so the outer composition-grouped test score
is not used for any selection decision.

Twenty outer repeats give a mean and a standard deviation for the quantity the
screening actually depends on: accuracy on encoded compositions the model has
never seen.  The single split used in v2 is scored alongside them for continuity.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import features_v3
from refit_v3 import (CONFORMAL_LEVEL, FEATURE_SETS, MODELS, REFERENCE_SEED,
                      TARGETS, grouped_split, make_model, target_vector)

HERE = Path(__file__).resolve().parent
N_REPEATS = 20


def main():
    d = pd.read_csv(HERE / "src_v2" / "ml_clean_data.csv").set_index("source_row")
    groups = d["composition_group"]
    sets = features_v3.build(d)

    rows, choices, preds = [], [], []
    seeds = [REFERENCE_SEED] + list(range(N_REPEATS))
    for seed in seeds:
        label = "v2_reference_split" if seed == REFERENCE_SEED else f"repeat_{seed:02d}"
        train, test = grouped_split(d.index, groups, seed=seed)
        inner_tr, inner_va = grouped_split(train, groups.loc[train], seed=1000 + seed)
        assert not set(groups.loc[inner_tr]) & set(groups.loc[inner_va])
        assert not set(groups.loc[train]) & set(groups.loc[test])

        for target in TARGETS:
            y = target_vector(d, target)
            trials = []
            for fs in FEATURE_SETS:
                X = sets[fs]
                for name in MODELS:
                    m = make_model(name)
                    m.fit(X.loc[inner_tr], y.loc[inner_tr])
                    p = m.predict(X.loc[inner_va])
                    trials.append(dict(feature_set=fs, model=name,
                                       inner_r2=r2_score(y.loc[inner_va], p),
                                       residuals=np.abs(y.loc[inner_va].to_numpy() - p)))
            best = max(trials, key=lambda t: t["inner_r2"])
            for t in trials:
                choices.append(dict(split=label, target=target, feature_set=t["feature_set"],
                                    model=t["model"], inner_r2=t["inner_r2"],
                                    selected=(t is best)))

            n = len(best["residuals"])
            q = float(np.quantile(best["residuals"],
                                  min(1.0, np.ceil((n + 1) * CONFORMAL_LEVEL) / n)))
            X = sets[best["feature_set"]]
            m = make_model(best["model"])
            m.fit(X.loc[train], y.loc[train])
            pred = m.predict(X.loc[test])
            obs = y.loc[test].to_numpy()
            base = np.full(len(test), y.loc[train].mean())
            rec = dict(split=label, seed=seed, target=target,
                       selected_feature_set=best["feature_set"], selected_model=best["model"],
                       inner_r2=best["inner_r2"], n_train=len(train), n_test=len(test),
                       r2=r2_score(obs, pred), mae=mean_absolute_error(obs, pred),
                       rmse=mean_squared_error(obs, pred) ** 0.5,
                       baseline_r2=r2_score(obs, base),
                       baseline_mae=mean_absolute_error(obs, base),
                       conformal_halfwidth=q,
                       conformal_coverage=float(np.mean(np.abs(obs - pred) <= q)))
            rows.append(rec)
            print(f"{label:20s} {target[:12]:12s} {best['feature_set']:10s} "
                  f"{best['model']:11s} R2={rec['r2']:.3f} MAE={rec['mae']:.3f} "
                  f"cov={rec['conformal_coverage']:.3f}", flush=True)
            if label == "v2_reference_split":
                for r_, p_, o_ in zip(test, pred, obs):
                    preds.append(dict(target=target, source_row=r_,
                                      composition_group=groups.loc[r_],
                                      observed=o_, predicted=p_, conformal_halfwidth=q))

    m_ = pd.DataFrame(rows)
    m_.to_csv(HERE / "v3_nested_metrics.csv", index=False)
    pd.DataFrame(choices).to_csv(HERE / "v3_nested_selection.csv", index=False)
    pd.DataFrame(preds).to_csv(HERE / "v3_nested_reference_predictions.csv", index=False)

    rep = m_[m_.split != "v2_reference_split"]
    summ = (rep.groupby("target")
               .agg(n_repeats=("r2", "size"), r2_mean=("r2", "mean"), r2_sd=("r2", "std"),
                    r2_min=("r2", "min"), r2_max=("r2", "max"),
                    r2_q05=("r2", lambda s: s.quantile(0.05)),
                    r2_q95=("r2", lambda s: s.quantile(0.95)),
                    mae_mean=("mae", "mean"), mae_sd=("mae", "std"),
                    rmse_mean=("rmse", "mean"),
                    coverage_mean=("conformal_coverage", "mean"),
                    coverage_sd=("conformal_coverage", "std"),
                    halfwidth_mean=("conformal_halfwidth", "mean"),
                    baseline_r2_mean=("baseline_r2", "mean"),
                    baseline_mae_mean=("baseline_mae", "mean"))
               .reset_index())
    ref = m_[m_.split == "v2_reference_split"].set_index("target")
    summ["v2_split_r2"] = summ.target.map(ref.r2)
    summ["v2_split_mae"] = summ.target.map(ref.mae)
    summ["r2_sem"] = summ.r2_sd / np.sqrt(summ.n_repeats)
    summ.to_csv(HERE / "v3_nested_summary.csv", index=False)
    print("\n", summ.to_string(index=False))

    # Production configuration = the choice made most often across the repeats.
    prod = {t: rep[rep.target == t].selected_model.value_counts().idxmax() for t in TARGETS}
    pfs = {t: rep[rep.target == t].selected_feature_set.value_counts().idxmax() for t in TARGETS}
    fs_common = max(set(pfs.values()), key=lambda v: list(pfs.values()).count(v))
    import sklearn, xgboost
    (HERE / "v3_production_choice.json").write_text(json.dumps(dict(
        feature_set=fs_common, per_target_feature_set=pfs, models=prod,
        rule="modal inner-validation winner across the 20 repeats",
        python=sys.version.split()[0], sklearn=sklearn.__version__,
        xgboost=xgboost.__version__), indent=2))
    print("\nproduction:", fs_common, prod, pfs)


if __name__ == "__main__":
    main()
