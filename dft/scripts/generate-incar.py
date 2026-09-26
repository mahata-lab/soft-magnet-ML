#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_MAGMOM_BY_ELEMENT = {
    "Nd": 3.0, "Pr": 3.0, "Sm": 5.0, "Tb": 6.0, "Dy": 5.0, "Ho": 4.0, "Er": 3.0, "Tm": 2.0,
    "Fe": 2.2, "Co": 1.7, "Ni": 0.6, "Mn": 3.0, "Cr": 2.0, "V": 2.0,
    "B": 0.0, "C": 0.0, "N": 0.0, "O": 0.0, "F": 0.0, "Si": 0.0, "P": 0.0, "Al": 0.0, "Ga": 0.0, "Ge": 0.0,
}

DEFAULT_LDAU_BY_ELEMENT = {
    "Nd": (3, 6.0, 0.0), "Pr": (3, 6.0, 0.0), "Sm": (3, 6.0, 0.0), "Tb": (3, 6.0, 0.0),
    "Dy": (3, 6.0, 0.0), "Ho": (3, 6.0, 0.0), "Er": (3, 6.0, 0.0), "Tm": (3, 6.0, 0.0),
}

BASE_INCAR = """SYSTEM = Publication-style SCF
ENCUT  = 520
PREC   = Accurate
EDIFF  = 1E-6
NELM   = 120
ALGO   = Normal
ISMEAR = 1
SIGMA  = 0.20
LASPH  = .TRUE.
ADDGRID = .TRUE.
LREAL  = Auto
ISYM   = 2
IBRION = -1
NSW    = 0
LWAVE  = .FALSE.
LCHARG = .FALSE.
ISPIN  = 2
LORBIT = 11
LMAXMIX = 4
"""

def parse_poscar(poscar: Path):
    lines = poscar.read_text(encoding="utf-8", errors="ignore").splitlines()
    if len(lines) < 8:
        raise RuntimeError(f"POSCAR too short: {poscar}")
    species = lines[5].split()
    counts = [int(x) for x in lines[6].split()]
    if len(species) != len(counts):
        raise RuntimeError(f"Species/count mismatch in {poscar}: {species} vs {counts}")
    return species, counts

def magmom_line(species, counts):
    return "MAGMOM = " + " ".join(f"{n}*{DEFAULT_MAGMOM_BY_ELEMENT.get(el, 0.0):.1f}" for el, n in zip(species, counts))

def ldau_lines(species):
    l, u, j = [], [], []
    use = False
    for el in species:
        if el in DEFAULT_LDAU_BY_ELEMENT:
            li, ui, ji = DEFAULT_LDAU_BY_ELEMENT[el]
            l.append(str(li)); u.append(f"{ui:.1f}"); j.append(f"{ji:.1f}")
            use = True
        else:
            l.append("-1"); u.append("0.0"); j.append("0.0")
    return use, " ".join(l), " ".join(u), " ".join(j)

def write_incar(poscar: Path, incar: Path, overwrite: bool):
    if incar.exists() and not overwrite:
        return
    species, counts = parse_poscar(poscar)
    use_ldau, l, u, j = ldau_lines(species)

    lines = [BASE_INCAR.rstrip(), "", magmom_line(species, counts)]
    if use_ldau:
        lines += [
            "LDAU    = .TRUE.",
            "LDAUTYPE = 2",
            f"LDAUL   = {l}",
            f"LDAUU   = {u}",
            f"LDAUJ   = {j}",
        ]
        if any(DEFAULT_LDAU_BY_ELEMENT.get(el, (-1, 0.0, 0.0))[0] == 3 for el in species):
            lines.append("LMAXMIX = 6")
    else:
        lines.append("LDAU    = .FALSE.")

    incar.write_text("".join(lines).rstrip() + "", encoding="utf-8")

def find_dirs(root: Path):
    return sorted({p.parent for p in root.rglob("POSCAR")}, key=lambda p: p.as_posix())

def main():
    ap = argparse.ArgumentParser(description="Write publication-style INCARs from POSCARs.")
    ap.add_argument("root", nargs="?", default=".", help="Root directory to scan")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing INCARs")
    ap.add_argument("--dry-run", action="store_true", help="Print actions only")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    dirs = find_dirs(root)
    print(f"Root: {root}")
    print(f"Found {len(dirs)} POSCAR folders\n")

    for d in dirs:
        poscar = d / "POSCAR"
        incar = d / "INCAR"
        try:
            species, counts = parse_poscar(poscar)
            print(f"[SCAN] {d}")
            print(f"       species = {species}")
            print(f"       counts  = {counts}")
            print(f"       MAGMOM  = {magmom_line(species, counts).split('=',1)[1].strip()}")
            if args.dry_run:
                print("       dry-run only")
            else:
                write_incar(poscar, incar, args.overwrite)
                print(f"       wrote   = {incar}")
            print()
        except Exception as e:
            print(f"[FAIL] {d}: {e}\n")

if __name__ == "__main__":
    main()

