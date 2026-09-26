"""Composition -> descriptor construction for the v3 analysis.

Three descriptor sets are compared on identical composition-grouped splits:

  FS-A  'fractions'  : the 77 raw elemental fractions plus the two supplied
                       aggregate columns (VEC, arithmetic density).  This is the
                       representation used in the notebook and in v2.
  FS-B  'physics'    : composition-weighted statistics of tabulated elemental
                       properties (Ward et al. 2016 style) plus global
                       chemistry descriptors.  No raw fractions.
  FS-C  'combined'   : FS-A + FS-B.

For a record with atomic fractions x_i and an elemental property p_i the
weighted statistics are

    mean   = sum_i x_i p_i
    absdev = sum_i x_i |p_i - mean|
    max    = max_{i: x_i>0} p_i
    min    = min_{i: x_i>0} p_i
    range  = max - min
    mode   = p_j  with  j = argmax_i x_i

Global descriptors: effective number of components, ideal mixing entropy,
atomic-size mismatch delta, electronegativity mismatch, and the summed
fractions of chemically meaningful element families.
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent

PROPS = [
    "Z", "mass", "radius", "covalent_radius", "electronegativity",
    "melting_point", "boiling_point", "density", "molar_volume",
    "ionization_energy", "electron_affinity", "thermal_conductivity",
    "heat_of_formation", "nvalence", "n_s", "n_p", "n_d", "n_f",
    "group", "period", "mendeleev_number", "gs_magmom",
]

FAMILIES = {
    "f_3d": ["Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"],
    "f_4d5d": ["Y", "Zr", "Nb", "Mo", "Ru", "Rh", "Pd", "Ag", "Cd", "Hf",
               "Ta", "W", "Re", "Os", "Ir", "Pt", "Au"],
    "f_rare_earth": ["La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb", "Dy",
                     "Ho", "Er", "Tm", "Lu"],
    "f_actinide": ["Am", "Pa", "Pu", "U"],
    "f_metalloid": ["B", "C", "Si", "P", "Ge", "As", "Sb", "Te"],
    "f_chalcogen_halogen": ["O", "S", "Se", "F", "Cl", "I"],
    "f_light_metal": ["Li", "Be", "Na", "Mg", "Al", "K", "Ca", "Rb", "Sr", "Ba"],
    "f_ferromagnetic_host": ["Fe", "Co", "Ni"],
}


def load_table():
    return pd.read_csv(HERE / "elemental_properties.csv", index_col=0)


def physics_features(frac: pd.DataFrame, table: pd.DataFrame | None = None) -> pd.DataFrame:
    """frac: DataFrame of atomic fractions, columns = element symbols, rows sum to 1."""
    if table is None:
        table = load_table()
    syms = [s for s in frac.columns if s in table.index]
    X = frac[syms].to_numpy(dtype=float)
    X = X / np.clip(X.sum(axis=1, keepdims=True), 1e-12, None)
    present = X > 0
    out = {}

    for p in PROPS:
        v = table.loc[syms, p].to_numpy(dtype=float)
        mean = X @ v
        absdev = (X * np.abs(v[None, :] - mean[:, None])).sum(axis=1)
        big = np.where(present, v[None, :], -np.inf)
        small = np.where(present, v[None, :], np.inf)
        vmax = big.max(axis=1)
        vmin = small.min(axis=1)
        mode = v[X.argmax(axis=1)]
        out[f"{p}_mean"] = mean
        out[f"{p}_absdev"] = absdev
        out[f"{p}_max"] = vmax
        out[f"{p}_min"] = vmin
        out[f"{p}_range"] = vmax - vmin
        out[f"{p}_mode"] = mode

    # Global / mixing descriptors.
    with np.errstate(divide="ignore", invalid="ignore"):
        lnx = np.where(X > 0, np.log(np.clip(X, 1e-12, None)), 0.0)
    out["n_components"] = present.sum(axis=1).astype(float)
    out["mixing_entropy"] = -(X * lnx).sum(axis=1)           # S_ideal / R
    out["n_effective"] = np.exp(out["mixing_entropy"])
    out["x_max"] = X.max(axis=1)

    r = table.loc[syms, "radius"].to_numpy(dtype=float)
    rbar = X @ r
    out["size_mismatch_delta"] = np.sqrt(
        (X * (1.0 - r[None, :] / np.clip(rbar[:, None], 1e-12, None)) ** 2).sum(axis=1))
    chi = table.loc[syms, "electronegativity"].to_numpy(dtype=float)
    chibar = X @ chi
    out["electronegativity_mismatch"] = np.sqrt(
        (X * (chi[None, :] - chibar[:, None]) ** 2).sum(axis=1))

    for name, members in FAMILIES.items():
        cols = [s for s in members if s in syms]
        out[name] = X[:, [syms.index(s) for s in cols]].sum(axis=1) if cols else np.zeros(len(X))

    return pd.DataFrame(out, index=frac.index)


def build(df: pd.DataFrame):
    """Return (fraction_frame, physics_frame, combined_frame) for a clean data table."""
    xcols = [c for c in df.columns if c.startswith("x_")]
    frac = df[xcols].copy()
    frac.columns = [c[2:] for c in xcols]
    phys = physics_features(frac)
    fsA = pd.concat([df[xcols], df[["VEC", "rho_theoretical (g/cm^3)"]]], axis=1)
    fsB = phys
    fsC = pd.concat([fsA, fsB], axis=1)
    return {"fractions": fsA.astype(float),
            "physics": fsB.astype(float),
            "combined": fsC.astype(float)}


if __name__ == "__main__":
    d = pd.read_csv(HERE / "src_v2" / "ml_clean_data.csv").set_index("source_row")
    sets = build(d)
    for k, v in sets.items():
        print(f"{k:10s} {v.shape[1]:4d} features  finite={np.isfinite(v.to_numpy()).all()}")
