"""Pooled held-out predictions across the twenty composition-grouped repeats.

For every repeat the descriptor set and learner already chosen by the nested
protocol are refitted on that repeat's training partition and applied to its
held-out compositions.  No new selection is performed here, so the pooled
parity plot shows exactly the models whose scores are summarised in Table 2.
"""
from pathlib import Path

import numpy as np
import pandas as pd

import features_v3
from refit_v3 import TARGETS, grouped_split, make_model, target_vector

HERE = Path(__file__).resolve().parent


def main():
    d = pd.read_csv(HERE / "src_v2" / "ml_clean_data.csv").set_index("source_row")
    groups = d["composition_group"]
    sets = features_v3.build(d)
    nested = pd.read_csv(HERE / "v3_nested_metrics.csv")
    rep = nested[nested.split != "v2_reference_split"]

    rows = []
    for _, r in rep.iterrows():
        train, test = grouped_split(d.index, groups, seed=int(r.seed))
        X = sets[r.selected_feature_set]
        y = target_vector(d, r.target)
        m = make_model(r.selected_model)
        m.fit(X.loc[train], y.loc[train])
        pred = m.predict(X.loc[test])
        for row, p in zip(test, pred):
            rows.append(dict(repeat=r.split, seed=int(r.seed), target=r.target,
                             source_row=row, composition_group=groups.loc[row],
                             observed=y.loc[row], predicted=p,
                             conformal_halfwidth=r.conformal_halfwidth,
                             feature_set=r.selected_feature_set, model=r.selected_model))
        print(r.split, r.target, "done", flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(HERE / "v3_pooled_predictions.csv", index=False)
    for t in TARGETS:
        g = out[out.target == t]
        from sklearn.metrics import r2_score, mean_absolute_error
        print(t, "pooled R2", round(r2_score(g.observed, g.predicted), 4),
              "MAE", round(mean_absolute_error(g.observed, g.predicted), 4),
              "n", len(g))


if __name__ == "__main__":
    main()
