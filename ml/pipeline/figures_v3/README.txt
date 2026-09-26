figures_v3 — source data, code and graphics for soft-magnet-paper-v3.docx
=========================================================================

No DFT, VAMPIRE or other simulation was run for v3.  All first-principles and
atomistic content is the audited reanalysis of the existing runs carried over
from v2.  The machine-learning results were refitted from the existing cleaned
dataset only.

Pipeline (run in this order)
----------------------------
  elemental_table.py      -> elemental_properties.csv
                             elemental reference data for the weighted
                             descriptors, taken from mendeleev 1.3.0

  features_v3.py          library; builds the three descriptor sets
                             'fractions' (79), 'physics' (146), 'combined' (225)

  refit_v3.py             descriptor-set comparison on identical grouped splits
                          -> v3_repeat_metrics.csv, v3_summary.csv,
                             v3_selection.csv, v3_protocol.json

  refit_v3_nested.py      headline protocol: 20 composition-grouped repeats with
                          nested selection of descriptor set AND learner
                          -> v3_nested_metrics.csv, v3_nested_summary.csv,
                             v3_nested_selection.csv, v3_production_choice.json

  pooled_predictions.py   refits each repeat's selected configuration to pool all
                          held-out predictions
                          -> v3_pooled_predictions.csv

  recipe_generator.py     conformal calibration on held-out compositions, then
                          20,000-point Fe-Co-Ni-Mn-Al-Si generation
                          -> v3_recipe_calibration.csv, v3_recipes_all.csv,
                             v3_recipes_top.csv, v3_recipe_summary.json,
                             v3_calibration_distances.csv,
                             v3_original_design_rescored.csv

  interpret_v3.py         SHAP and permutation importance on held-out compositions
                          -> figure5_shap_tc.csv, figure5_shap_hc.csv,
                             figure5_importance.csv

  prepare_figures_v3.py   assembles every figure source table
                          -> figure3_*.csv, figure4_*.csv, figure6_*.csv,
                             v3_resolution_summary.json

  figure1.py ... figure10.py
                          one script per figure; each reads only the shipped
                          figureN*.csv tables and writes figureN.png (600 dpi),
                          figureN.pdf and figureN.svg

  build_manuscript_v3.py  builds soft-magnet-paper-v3.docx from manuscript_v3.txt,
                          copying the 30 Zotero citation fields and the cached
                          bibliography of "Summer Paper.docx" as intact XML
                          -> ../soft-magnet-paper-v3.docx,
                             ../document_verification_v3.json

Figures
-------
  figure1   workflow schematic
  figure2   dataset characteristics
  figure3   evaluation protocol and partition sensitivity
  figure4   pooled held-out parity, descriptor sets, interval calibration
  figure5   SHAP and permutation importance on held-out compositions
  figure6   recipe generator, novelty gate and resolvable design envelope
  figure7   static DFT volume scans           (v2 figure5, unchanged data)
  figure8   candidate cell comparison         (v2 figure6, unchanged data)
  figure9   spin-orbit orientation energies   (v2 figure7, unchanged data)
  figure10  VAMPIRE magnetization curves      (v2 figure8, unchanged data)

Carried-over audit tables (produced in v2, unchanged)
-----------------------------------------------------
  dft_run_audit.csv, exchange_audit.csv, mae_raw_outputs.csv,
  vampire_all_curves.csv, vampire_summary.csv, vampire_parameters.csv,
  composition_label_variation.csv, ml_clean_data.csv, ml_audit.json,
  ml_metrics.csv, virtual_screening.csv

Key results
-----------
  Composition-grouped, 20 repeats, nested selection:
      Curie temperature   R2 = 0.601 +/- 0.080   MAE = 114.0 +/- 13.2 K
      log10 coercivity    R2 = 0.589 +/- 0.069   MAE = 0.591 +/- 0.051
  Pooled over 6,936 held-out records: 0.602 and 0.593.
  Random partitions of the same data give 0.739 and 0.671 with 172 of 348
  test records sharing a composition with training.

  Split-conformal coverage at the 0.90 level: 0.910 +/- 0.028 and 0.908 +/- 0.039.
  Prediction +/- 2 tree standard deviations, read as 95%: 0.916 and 0.891.

  Recipe generator, 20,000 candidates:
      31 point-prediction hits at Tc > 1000 K and Hc < 100 Oe
       0 survive the interval-robust criterion at that target
     147 supported recipes at Tc > 600 K and Hc < 100 Oe
         (see supported_recipes_600K_100Oe.csv, Table 3 of the manuscript)

Software
--------
  Python 3.11, scikit-learn 1.7.2, XGBoost 3.2.0, SHAP 0.51.0,
  mendeleev 1.3.0, matplotlib, pandas, numpy, python-docx, lxml.
  Random seeds are fixed in every script.
