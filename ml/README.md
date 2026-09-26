# Machine learning pipeline

## Layout matters

The scripts resolve every path from their own location, and they were written to
run from a working directory that holds `src_v2/` (v2 baseline inputs) and
`figures_v3/` (outputs). That tree is reproduced here exactly:

```
pipeline/
  *.py            the pipeline, run from this directory
  src_v2/         ml_clean_data.csv and the rest of the v2 inputs
  figures_v3/     every v3 output, plus figure1-10.py and plot_style.py
```

Run the pipeline scripts from `pipeline/`, and the figure scripts from
`pipeline/figures_v3/`. Nothing needs editing.

## Order

| Step | Script | Produces |
|---|---|---|
| 1 | `elemental_table.py` | `elemental_properties.csv` — 22 elemental properties |
| 2 | `features_v3.py` | 146 Magpie-style weighted elemental statistics |
| 3 | `refit_v3.py` | 20 composition-grouped repeats, `v3_repeat_metrics.csv` |
| 4 | `refit_v3_nested.py` | nested selection, `v3_nested_*.csv` |
| 5 | `pooled_predictions.py` | `v3_pooled_predictions.csv` (6,936 held-out records) |
| 6 | `recipe_generator.py` | split-conformal intervals, `v3_recipes_all.csv`, `supported_recipes_600K_100Oe.csv` |
| 7 | `interpret_v3.py` | SHAP attributions, `figure5_shap_*.csv` |
| 8 | `prepare_figures_v3.py` | every `figure*.csv` the plots consume |
| 9 | `figures_v3/figure{1..10}.py` | the manuscript figures at 600 dpi |

`figures_v3/` already contains a completed run's outputs, so any single step can
be re-run or inspected without redoing the fits.

## Descriptors

Tc: 0.600 (composition fractions) → 0.630 (fractions + elemental statistics),
selected in 13/20 repeats. Hc: 0.587 → 0.565, with plain fractions selected in
12/20 repeats. The asymmetry is the point — coercivity is extrinsic, so
composition-only descriptors cannot reach it, and adding elemental statistics
does not help.

## Data

- `data/magnetic_anisotropy_materials.csv` — raw source records. Still carries
  DOI, Material_Type and Crystal_Structure.
- `data/magneticMaterials_finalDataset_encoded.csv` — encoded dataset used for
  modelling. The DOIs were dropped here, which is why a publication-level holdout
  cannot be rebuilt from it.
- `pipeline/src_v2/ml_clean_data.csv` — the cleaned table the models actually read.

## Notebooks

`notebooks/` holds the exploratory work that preceded the pipeline. They are kept
for provenance; the scripts in `pipeline/` are the version the manuscript reports.
