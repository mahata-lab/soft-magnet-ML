# DFT calculations

A curated subset of the run set, not the whole thing. Every directory here was
checked before copying: the electronic loop reached EDIFF, VASP terminated
cleanly (`General timing and accounting` present), and no `VERY BAD NEWS`,
`internal error`, `ZBRENT: fatal` or `Error EDDDAV` string appears in OUTCAR.
`included_runs_audit.csv` records that check per run, together with atom count,
ENCUT, EDIFF, final energy and total moment.

Runs that failed the check were deliberately left out. In particular the
four-state exchange sets `Run_20_B2FeCo_Jij_FeFe`, `Run_22_B2FeCo_Jij_CoCo`,
`Run_32`, `Run_33`, `Run_43` and `Run_44` have states that hit the NELM limit
without reaching EDIFF, or never produced an OUTCAR at all. Only the two
complete, fully converged exchange sets are shipped.

## What is here

| Run | Cell | Calculation |
|---|---|---|
| `Run_04_bccFe_vol_a2.866` | bcc Fe | collinear, equilibrium volume |
| `Run_14_B2FeCo_vol_a2.857` | B2 FeCo | collinear, equilibrium volume |
| `Run_25_L12Fe3Co_vol_a3.580` | L1₂ Fe₃Co | collinear, equilibrium volume |
| `Run_37_L12FeCo3_vol_a3.580` | L1₂ FeCo₃ | collinear, equilibrium volume |
| `Run_08_bccFe_MAE_001` | bcc Fe | noncollinear + SOC, M ∥ [001] |
| `Run_09_bccFe_MAE_111` | bcc Fe | noncollinear + SOC, M ∥ [111] |
| `Run_10_bccFe_Jij_FeFe/state{1..4}` | bcc Fe, 16 atoms | four-state exchange mapping |
| `Run_21_B2FeCo_Jij_FeCo/state{1..4}` | B2 FeCo, 16 atoms | four-state exchange mapping |
| `Run_45`–`Run_50` | SQS Fe-Co-Ni-Mn-Al-Si | BCC/FCC pairs for the three ML candidates |

The SQS runs are the BCC and FCC cells for each of the three top ML candidates —
they are what `candidate_phase_stabilities.csv` is computed from, so the phase
comparison can be checked end to end.

`INDEX_all_planned_runs.txt` lists all 50 planned runs for context, including the
ones not shipped here.

## Files inside each run

Kept: `INCAR`, `KPOINTS`, `POSCAR`, `CONTCAR`, `OSZICAR`, `OUTCAR`, `vasp.log`,
`README.txt` where one existed, and `INCAR_MAGMOM.txt` for the exchange states.

Dropped: `WAVECAR`, `CHGCAR`, `CHG`, `DOSCAR`, `EIGENVAL`, `PROCAR`,
`vasprun.xml`, `XDATCAR`, `PCDAT`, `IBZKPT`, `REPORT` — all regenerable, and
together they were around 11 GB for the exchange sets alone.

**`POTCAR` is never included** — it is VASP-licensed and cannot be redistributed.
Each directory has `POTCAR_INFO.txt` with the `TITEL` lines identifying the exact
PAW datasets and the VASP build, so you can concatenate an identical POTCAR from
your own distribution in the order listed.

OUTCAR files above 2 MB are stored gzipped as `OUTCAR.gz` (the MAE runs compress
21 MB → ~0.6 MB). The parsers in `scripts/` read the plain file, so:

```bash
gunzip -k path/to/OUTCAR.gz
```

## Settings

Collinear and SQS runs: ENCUT 520 eV, PREC Accurate, EDIFF 1e-6, LASPH, LMAXMIX 4,
ADDGRID, `ISMEAR = 1`, `SIGMA = 0.05`. The MAE runs add `LNONCOLLINEAR`,
`LSORBIT`, `ISYM = 0`, `ICHARG = 11` and a fixed `SAXIS`. The four-state exchange
cells use ENCUT 440 eV on 16-atom supercells. VASP 6.5.1.

## Scripts

| Script | Purpose |
|---|---|
| `generate-incar.py` | writes INCAR/KPOINTS/POSCAR for the planned runs |
| `run_vasp_queue.py` | serial queue runner with per-run status files |
| `diagnose_vasp_queue.py` | post-hoc check of queue state and failures |
| `get_properties.py` | pulls energy, moment and volume from OUTCAR |
| `get_MAE.py`, `get_MAE2.py` | magnetocrystalline anisotropy from the SOC pair |
| `prepare_Jij.py`, `get_Jij.py` | set up and reduce the four-state exchange runs |
| `analyze_jij_states.py` | energy comparison across the four states |
| `candidates.py` | builds the SQS candidate cells from the ML output |
