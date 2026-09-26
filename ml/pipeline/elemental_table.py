"""Build the elemental property reference table used by the physics-based descriptors.

Values are taken from the `mendeleev` package (v1.3.0), which compiles CRC/NIST
reference data.  Ground-state elemental magnetic moments are supplied separately
because they are not carried by that package; values are the accepted
low-temperature magnetic moments of the elemental ground-state solids
(zero for elements with no ordered moment in the elemental solid).

Run once:  python3 elemental_table.py   ->  elemental_properties.csv
"""
from pathlib import Path
import warnings

import pandas as pd
from mendeleev import element

warnings.filterwarnings("ignore")

OUT = Path(__file__).resolve().parent

# Ground-state magnetic moment of the elemental solid (mu_B/atom).
GS_MAGMOM = {
    "Fe": 2.22, "Co": 1.72, "Ni": 0.61, "Gd": 7.63, "Tb": 9.34, "Dy": 10.33,
    "Ho": 10.34, "Er": 9.1, "Tm": 7.14, "Cr": 0.62, "Mn": 2.10, "Nd": 2.9,
    "Sm": 0.13, "Pr": 2.7, "Ce": 0.6, "Eu": 7.0, "Ho ": 0.0,
}

# Valence-shell occupancies (s, p, d, f) of the neutral ground-state atom.
def valence_spdf(el):
    counts = {"s": 0, "p": 0, "d": 0, "f": 0}
    try:
        for (n, l), occ in el.ec.conf.items():
            counts[l] = counts.get(l, 0) + occ
    except Exception:
        pass
    # Magpie convention: count only the valence (outermost s/p plus open d/f).
    try:
        maxn = max(n for (n, l) in el.ec.conf)
    except Exception:
        return counts
    v = {"s": 0, "p": 0, "d": 0, "f": 0}
    for (n, l), occ in el.ec.conf.items():
        if l in ("s", "p") and n == maxn:
            v[l] += occ
        elif l == "d" and n == maxn - 1 and occ < 10:
            v[l] += occ
        elif l == "d" and n == maxn - 1 and occ == 10 and el.block == "d":
            v[l] += occ
        elif l == "f" and n == maxn - 2 and occ < 14:
            v[l] += occ
    return v


def build(symbols):
    rows = []
    for s in symbols:
        try:
            el = element(s)
        except Exception:
            continue
        v = valence_spdf(el)
        rows.append(dict(
            symbol=s,
            Z=el.atomic_number,
            mass=el.atomic_weight,
            radius=el.metallic_radius or el.atomic_radius or el.covalent_radius_pyykko,
            covalent_radius=el.covalent_radius_pyykko,
            electronegativity=el.en_pauling,
            melting_point=el.melting_point,
            boiling_point=el.boiling_point,
            density=el.density,
            molar_volume=el.atomic_volume,
            ionization_energy=el.ionenergies.get(1),
            electron_affinity=el.electron_affinity,
            thermal_conductivity=el.thermal_conductivity,
            heat_of_formation=el.heat_of_formation,
            nvalence=el.nvalence(),
            n_s=v["s"], n_p=v["p"], n_d=v["d"], n_f=v["f"],
            group=el.group_id, period=el.period,
            mendeleev_number=el.mendeleev_number,
            gs_magmom=GS_MAGMOM.get(s, 0.0),
        ))
    t = pd.DataFrame(rows).set_index("symbol")
    # A small number of reference entries are missing for rare species; fill
    # with the period-wise median so the weighted statistics stay defined.
    for c in t.columns:
        if t[c].isna().any():
            t[c] = t[c].fillna(t[c].median())
    return t


if __name__ == "__main__":
    d = pd.read_csv(OUT / "src_v2" / "ml_clean_data.csv", nrows=1)
    syms = [c[2:] for c in d.columns if c.startswith("x_")]
    t = build(syms)
    t.to_csv(OUT / "elemental_properties.csv")
    print(t.shape, "elements ->", OUT / "elemental_properties.csv")
    print(t.loc[["Fe", "Co", "Ni", "Mn", "Al", "Si"]].T)
