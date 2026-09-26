import csv
from pathlib import Path
import re


def find_folder_by_prefix(base_path, prefix):
    """Finds a directory matching a given prefix."""
    base = Path(base_path)
    matches = [
        d for d in base.iterdir() if d.is_dir() and d.name.startswith(prefix)
    ]
    if matches:
        return matches[0]
    return None


def get_final_energy(folder_path):
    """Extracts ground state total energy from VASP run."""
    if not folder_path:
        return None

    folder = Path(folder_path)

    # 1. OSZICAR
    oszicar = folder / "OSZICAR"
    if oszicar.exists():
        with open(oszicar, "r", errors="ignore") as f:
            for line in reversed(f.readlines()):
                if "E0=" in line or "F=" in line:
                    match = re.search(r"E0=\s*([-\d\.]+)", line)
                    if match:
                        return float(match.group(1))

    # 2. OUTCAR (Fallback for SOC calculations)
    outcar = folder / "OUTCAR"
    if outcar.exists():
        with open(outcar, "r", errors="ignore") as f:
            for line in reversed(f.readlines()):
                if "energy  without entropy=" in line or "energy(sigma->0)" in line:
                    match = re.search(r"=\s*([-\d\.]+)", line)
                    if match:
                        return float(match.group(1))

    return None


def extract_mae(base_path, num_atoms=16):
    base = Path(base_path)

    # Add any systems you ran MAE on (e.g., B2FeCo, L12Fe3Co, L12FeCo3, or candidates)
    mae_systems = [
        {
            "System": "B2 FeCo",
            "axis_100_prefix": "Run_18_B2FeCo_MAE_001",
            "axis_111_prefix": "Run_19_B2FeCo_MAE_100",
        },
        {
            "System": "L12 Fe3Co",
            "axis_100_prefix": "Run_30_L12Fe3Co_MAE_001",
            "axis_111_prefix": "Run_31_L12Fe3Co_MAE_100",
        },
        {
            "System": "L12 FeCo3",
            "axis_100_prefix": "Run_41_L12FeCo3_MAE_001",
            "axis_111_prefix": "Run_42_L12FeCo3_MAE_100",
        },
    ]

    results = []

    for s in mae_systems:
        folder_100 = find_folder_by_prefix(base, s["axis_100_prefix"])
        folder_111 = find_folder_by_prefix(base, s["axis_111_prefix"])

        e_100 = get_final_energy(folder_100)
        e_111 = get_final_energy(folder_111)

        if e_100 is not None and e_111 is not None:
            # Energy diff in eV
            delta_e_eV = e_111 - e_100
            # Convert eV to micro-eV (uEV) per atom
            mae_uev_atom = (delta_e_eV / num_atoms) * 1e6

            results.append(
                {
                    "System": s["System"],
                    "E_[100] (eV)": f"{e_100:.6f}",
                    "E_[111] (eV)": f"{e_111:.6f}",
                    "MAE (uEV/atom)": f"{mae_uev_atom:.2f}",
                    "Easy Axis": "[100]" if mae_uev_atom > 0 else "[111]",
                }
            )

    if results:
        print("\n" + "=" * 65)
        print(
            f"{'System':<15} | {'E_[100] (eV)':<12} | {'E_[111] (eV)':<12} | {'MAE (uEV/atom)':<14} | Easy Axis"
        )
        print("-" * 65)
        for r in results:
            print(
                f"{r['System']:<15} | {r['E_[100] (eV)']:<12} | {r['E_[111] (eV)']:<12} | {r['MAE (uEV/atom)']:<14} | {r['Easy Axis']}"
            )
        print("=" * 65 + "\n")


if __name__ == "__main__":
    dft_directory = "/home/student3/Desktop/soft-magnets/dft_runs"
    extract_mae(dft_directory, num_atoms=16)
