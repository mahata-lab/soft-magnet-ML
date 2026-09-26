# Soft magnetic alloys — leakage-controlled ML and first-principles bounds

Code, data and a curated set of VASP calculations behind the soft-magnet manuscript
(v3). The repository holds two branches of the work:

1. **A statistical branch.** Composition-grouped models for Curie temperature and
   coercivity, a split-conformal recipe generator, and the audit that shows why a
   random train/test split overstates what composition-only descriptors can do.
2. **A first-principles branch.** VASP calculations on bcc Fe, B2 FeCo, L1<sub>2</sub>
   Fe<sub>3</sub>Co, L1<sub>2</sub> FeCo<sub>3</sub> and SQS Fe-Co-Ni-Mn-Al-Si solid
   solutions, which bound how far the generated recipes may be read physically.

## Headline results

Composition-grouped splits, 20 repeats, nested model selection (no leakage):

| | Curie temperature | log<sub>10</sub> coercivity |
|---|---|---|
| R², 20 grouped repeats | **0.601 ± 0.080** | **0.589 ± 0.069** |
| R², pooled over 6,936 held-out records | 0.602 | 0.593 |
| MAE | 114.0 ± 13.2 K | 0.591 ± 0.051 |
| R², random split (leaky reference) | 0.739 | 0.671 |

Random splits leave 172 of 348 test records sharing a composition with training.
Single grouped splits mislead in **both** directions: across 20 repeats R² for T<sub>c</sub>
spans 0.466–0.738 at nearly constant MAE.

Conformal recipe generator, 20,000 Fe-Co-Ni-Mn-Al-Si candidates:

- 31 point-prediction hits at T<sub>c</sub> > 1000 K, H<sub>c</sub> < 100 Oe
- **0** survive once the calibrated 90% interval must lie inside the target
- **147 supported recipes** at T<sub>c</sub> > 600 K, H<sub>c</sub> < 100 Oe
- Interval coverage 0.910 ± 0.028 (T<sub>c</sub>) and 0.908 ± 0.039 (H<sub>c</sub>) at nominal 0.90

## Layout

```
dft/
  runs/                        20 converged VASP calculations (see dft/README.md)
  scripts/                     INCAR generation, queue runner, OUTCAR parsers
  included_runs_audit.csv      per-run convergence audit of everything shipped here
  INDEX_all_planned_runs.txt   the full 50-run plan, for context
  candidate_phase_stabilities.csv
ml/
  pipeline/                    the analysis pipeline, laid out as the scripts expect
    src_v2/                    v2 baseline inputs the v3 scripts read
    figures_v3/                v3 outputs + the figure scripts that draw them
  data/                        raw and encoded source datasets
  notebooks/                   exploratory notebooks
figures/                       rendered manuscript figures (png / pdf / svg)
tools/                         manuscript assembly script
```

## Reproducing

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cd ml/pipeline
python elemental_table.py        # 146 Magpie-style features from 22 elemental properties
python refit_v3.py               # 20 composition-grouped repeats
python refit_v3_nested.py        # nested model selection
python pooled_predictions.py
python recipe_generator.py       # split-conformal intervals + candidate screen
python interpret_v3.py           # SHAP attributions
python prepare_figures_v3.py     # assembles every figure*.csv

cd figures_v3
for f in figure*.py; do python "$f"; done
```

Scripts resolve paths relative to their own location, so run them from the
directory they live in. `ml/pipeline/figures_v3/` already contains the outputs
of a full run, so the figure scripts can be run without redoing the fits.

## A note on POTCAR files

**No POTCAR is included anywhere in this repository.** VASP pseudopotentials are
distributed under a licence that does not permit redistribution. Each run
directory carries `POTCAR_INFO.txt` listing the exact PAW datasets (the `TITEL`
lines from the run's own OUTCAR) and the VASP version used, so you can rebuild an
identical POTCAR by concatenating them from your own licensed distribution, in the
order given. `.gitignore` blocks `POTCAR` at every path depth so one cannot be
committed by accident.

## Known limitations

- Composition grouping is the strongest holdout the encoded dataset supports.
  Source DOIs were dropped during encoding, so a publication-level holdout cannot
  be rebuilt from `magneticMaterials_finalDataset_encoded.csv`. The raw
  `magnetic_anisotropy_materials.csv` still carries DOI, Material_Type and
  Crystal_Structure — rejoining them is the obvious next step.
- Coercivity is extrinsic: it depends on microstructure and processing that
  composition-only descriptors cannot see. SHAP attributions for H<sub>c</sub> reduce to
  Sm/Nd/P/B, i.e. chemical-family recognition rather than mechanism.
- The resolvable envelope at H<sub>c</sub> < 100 Oe reaches 864 candidates above 500 K and
  147 above 600 K, but only 1 above 650 K and none above 700 K. A 1000 K target is
  roughly 350 K beyond what the calibrated evidence supports.
