"""Rare-earth-free soft-magnet recipe generator.

The generator enumerates Fe-Co-Ni-Mn-Al-Si compositions, predicts Curie
temperature and coercivity with the descriptor-set and model selected in
refit_v3.py, and returns a ranked recipe list in which every entry carries

  * a split-conformal prediction interval calibrated on held-out compositions,
  * an explicit interpolation / extrapolation label derived from the L1 distance
    to the nearest training composition, and
  * a distinction between a point-prediction pass and an interval-robust pass.

Calibration compositions are disjoint from fitting compositions, so the reported
coverage is an out-of-composition coverage rather than an in-sample one.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import r2_score, mean_absolute_error

import features_v3
from refit_v3 import make_model, target_vector, TARGETS, CONFORMAL_LEVEL

HERE = Path(__file__).resolve().parent
SRC = HERE / "src_v2"
ELEMENTS = ["Fe", "Co", "Ni", "Mn", "Al", "Si"]
TC_THRESHOLD = 1000.0          # K
HC_THRESHOLD = 100.0           # Oe
N_CANDIDATES = 20000
DIRICHLET_ALPHA = (5, 2, 1.5, 1, 0.5, 0.5)   # the original design concentration


def design(n, seed=42):
    """Reproduce the original Dirichlet design generator at arbitrary size."""
    rs = np.random.RandomState(seed)
    x = rs.dirichlet(DIRICHLET_ALPHA, n)
    x = np.round(x, 3)
    x = x / x.sum(axis=1, keepdims=True)
    return pd.DataFrame(x, columns=ELEMENTS)


def main():
    d = pd.read_csv(SRC / "ml_clean_data.csv").set_index("source_row")
    groups = d["composition_group"]
    chosen = json.loads((HERE / "v3_production_choice.json").read_text())
    per_target_fs = chosen["per_target_feature_set"]
    sets = features_v3.build(d)

    # Grouped fit / calibration partition: no composition is in both.
    fit_idx, cal_idx = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=7)
                            .split(d, groups=groups))
    fit_rows, cal_rows = d.index[fit_idx], d.index[cal_idx]
    assert not set(groups.loc[fit_rows]) & set(groups.loc[cal_rows])

    models, calib, cal_report = {}, {}, []
    for target in TARGETS:
        X = sets[per_target_fs[target]]
        y = target_vector(d, target)
        m = make_model(chosen["models"][target])
        m.fit(X.loc[fit_rows], y.loc[fit_rows])
        res = np.abs(y.loc[cal_rows].to_numpy() - m.predict(X.loc[cal_rows]))
        n = len(res)
        q = float(np.quantile(res, min(1.0, np.ceil((n + 1) * CONFORMAL_LEVEL) / n)))
        models[target], calib[target] = m, q
        pred = m.predict(X.loc[cal_rows])
        cal_report.append(dict(target=target, model=chosen["models"][target],
                               feature_set=per_target_fs[target],
                               n_fit=len(fit_rows), n_calibration=n,
                               calibration_r2=r2_score(y.loc[cal_rows], pred),
                               calibration_mae=mean_absolute_error(y.loc[cal_rows], pred),
                               conformal_halfwidth=q,
                               empirical_coverage=float(np.mean(res <= q)),
                               level=CONFORMAL_LEVEL))
    pd.DataFrame(cal_report).to_csv(HERE / "v3_recipe_calibration.csv", index=False)
    print(pd.DataFrame(cal_report).to_string(index=False))

    # ---- candidate enumeration -------------------------------------------------
    cand = design(N_CANDIDATES)
    full = pd.DataFrame(0.0, index=cand.index,
                        columns=[c[2:] for c in d.columns if c.startswith("x_")])
    for e in ELEMENTS:
        full[e] = cand[e].to_numpy()
    phys = features_v3.physics_features(full)
    fracs = full.copy()
    fracs.columns = ["x_" + c for c in fracs.columns]
    vec_w = features_v3.load_table().loc[[c[2:] for c in fracs.columns], "nvalence"].to_numpy()
    rho_w = features_v3.load_table().loc[[c[2:] for c in fracs.columns], "density"].to_numpy()
    fracs["VEC"] = fracs.iloc[:, :len(vec_w)].to_numpy() @ vec_w
    fracs["rho_theoretical (g/cm^3)"] = full.to_numpy() @ rho_w
    frames = {"fractions": fracs, "physics": phys,
              "combined": pd.concat([fracs, phys], axis=1)}
    tc = models[TARGETS[0]].predict(
        frames[per_target_fs[TARGETS[0]]][sets[per_target_fs[TARGETS[0]]].columns])
    lhc = models[TARGETS[1]].predict(
        frames[per_target_fs[TARGETS[1]]][sets[per_target_fs[TARGETS[1]]].columns])
    q_tc, q_lhc = calib[TARGETS[0]], calib[TARGETS[1]]

    # ---- novelty gate ----------------------------------------------------------
    xcols = [c for c in d.columns if c.startswith("x_")]
    train_comp = d.loc[fit_rows, xcols].to_numpy()
    cand_comp = fracs[xcols].to_numpy()
    d1 = np.empty(len(cand_comp))
    for i in range(0, len(cand_comp), 512):
        blk = cand_comp[i:i + 512]
        d1[i:i + 512] = np.abs(blk[:, None, :] - train_comp[None, :, :]).sum(axis=2).min(axis=1)

    # Reference scale: how far the held-out calibration compositions sit from the
    # fitting compositions.  Candidates closer than the calibration median are
    # inside the regime where the measured coverage was obtained.
    cal_comp = d.loc[cal_rows, xcols].to_numpy()
    dcal = np.empty(len(cal_comp))
    for i in range(0, len(cal_comp), 512):
        blk = cal_comp[i:i + 512]
        dcal[i:i + 512] = np.abs(blk[:, None, :] - train_comp[None, :, :]).sum(axis=2).min(axis=1)
    d50, d90 = float(np.quantile(dcal, 0.5)), float(np.quantile(dcal, 0.9))
    pd.DataFrame(dict(source_row=cal_rows, distance=dcal)).to_csv(
        HERE / "v3_calibration_distances.csv", index=False)

    r = cand.copy()
    r["VEC"] = fracs["VEC"].to_numpy()
    r["predicted_Tc_K"] = tc
    r["Tc_lower_K"] = tc - q_tc
    r["Tc_upper_K"] = tc + q_tc
    r["predicted_log10_Hc"] = lhc
    r["predicted_Hc_Oe"] = 10 ** lhc
    r["Hc_lower_Oe"] = 10 ** (lhc - q_lhc)
    r["Hc_upper_Oe"] = 10 ** (lhc + q_lhc)
    r["L1_to_nearest_training"] = d1
    r["novelty"] = np.where(d1 <= d50, "interpolation",
                    np.where(d1 <= d90, "near-extrapolation", "far-extrapolation"))
    r["point_pass"] = (r.predicted_Tc_K > TC_THRESHOLD) & (r.predicted_Hc_Oe < HC_THRESHOLD)
    r["interval_pass"] = (r.Tc_lower_K > TC_THRESHOLD) & (r.Hc_upper_Oe < HC_THRESHOLD)
    r["supported_recipe"] = r.interval_pass & (r.novelty != "far-extrapolation")
    # Ranking score: margin above the Tc threshold and below the Hc threshold,
    # both measured on the conservative interval edge, in units of the interval.
    r["tc_margin"] = (r.predicted_Tc_K - TC_THRESHOLD) / q_tc
    r["hc_margin"] = (np.log10(HC_THRESHOLD) - r.predicted_log10_Hc) / q_lhc
    r["recipe_score"] = np.minimum(r.tc_margin, r.hc_margin)
    r = r.sort_values("recipe_score", ascending=False).reset_index(drop=True)
    r.to_csv(HERE / "v3_recipes_all.csv", index=False)

    summary = dict(n_candidates=int(len(r)),
                   n_point_pass=int(r.point_pass.sum()),
                   n_interval_pass=int(r.interval_pass.sum()),
                   n_supported=int(r.supported_recipe.sum()),
                   conformal_halfwidth_Tc_K=q_tc,
                   conformal_halfwidth_log10Hc=q_lhc,
                   Hc_interval_factor=float(10 ** q_lhc),
                   calibration_distance_median=d50,
                   calibration_distance_p90=d90,
                   feature_set=per_target_fs, models=chosen["models"])
    (HERE / "v3_recipe_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

    top = r[r.supported_recipe].head(12) if r.supported_recipe.any() else r.head(12)
    cols = ELEMENTS + ["VEC", "predicted_Tc_K", "Tc_lower_K", "predicted_Hc_Oe",
                       "Hc_upper_Oe", "L1_to_nearest_training", "novelty",
                       "point_pass", "interval_pass", "recipe_score"]
    top[cols].to_csv(HERE / "v3_recipes_top.csv", index=False)
    print(top[cols].to_string(index=False))

    # Continuity: the original 1,000-point design scored with the same models.
    orig = pd.read_csv(SRC / "virtual_screening.csv")
    of = pd.DataFrame(0.0, index=orig.index, columns=[c[2:] for c in xcols])
    for e in ELEMENTS:
        of[e] = orig[e].to_numpy()
    op = features_v3.physics_features(of)
    ofr = of.copy(); ofr.columns = xcols
    ofr["VEC"] = of.to_numpy() @ vec_w
    ofr["rho_theoretical (g/cm^3)"] = of.to_numpy() @ rho_w
    oframes = {"fractions": ofr, "physics": op, "combined": pd.concat([ofr, op], axis=1)}
    orig["predicted_Tc_K"] = models[TARGETS[0]].predict(
        oframes[per_target_fs[TARGETS[0]]][sets[per_target_fs[TARGETS[0]]].columns])
    orig["predicted_log10_Hc"] = models[TARGETS[1]].predict(
        oframes[per_target_fs[TARGETS[1]]][sets[per_target_fs[TARGETS[1]]].columns])
    orig["predicted_Hc_Oe"] = 10 ** orig.predicted_log10_Hc
    orig["Tc_lower_K"] = orig.predicted_Tc_K - q_tc
    orig["Hc_upper_Oe"] = 10 ** (orig.predicted_log10_Hc + q_lhc)
    orig["point_pass"] = (orig.predicted_Tc_K > TC_THRESHOLD) & (orig.predicted_Hc_Oe < HC_THRESHOLD)
    orig["interval_pass"] = (orig.Tc_lower_K > TC_THRESHOLD) & (orig.Hc_upper_Oe < HC_THRESHOLD)
    orig.to_csv(HERE / "v3_original_design_rescored.csv", index=False)
    print("original 1000-point design: point pass", int(orig.point_pass.sum()),
          " interval pass", int(orig.interval_pass.sum()))


if __name__ == "__main__":
    main()
