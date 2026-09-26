#!/usr/bin/env python3
from pathlib import Path
import re

# Set spin quantum numbers (e.g., S = 2.0 for Fe, S = 1.5 for Co, or 0.5 for spin-1/2 mapping)
S_I = 1.0
S_J = 1.0


def get_energy(folder_path: Path) -> float:
    """Extracts final energy (TOTEN) from OSZICAR or OUTCAR."""
    oszicar = folder_path / "OSZICAR"
    outcar = folder_path / "OUTCAR"

    if oszicar.is_file():
        lines = oszicar.read_text(errors="ignore").splitlines()
        for line in reversed(lines):
            if "F=" in line:
                match = re.search(r"F=\s*([\d\.\-\+E]+)", line)
                if match:
                    return float(match.group(1))

    if outcar.is_file():
        lines = outcar.read_text(errors="ignore").splitlines()
        for line in reversed(lines):
            if "free energy  TOTEN" in line:
                return float(line.split()[-2])

    raise FileNotFoundError(f"Missing valid OSZICAR or OUTCAR in {folder_path}")


def process_jij_run(jij_dir: Path):
    """Processes a single Jij folder containing state1_pp, state2_pm, state3_mp, state4_mm."""
    # Mapping state keys to exact folder naming
    state_map = {
        "pp": "state1_pp",
        "pm": "state2_pm",
        "mp": "state3_mp",
        "mm": "state4_mm",
    }
    energies = {}

    for state_key, folder_name in state_map.items():
        state_dir = jij_dir / folder_name

        if not state_dir.is_dir():
            print(f"  [SKIP] Subfolder '{folder_name}' missing in {jij_dir.name}")
            return

        try:
            energies[state_key] = get_energy(state_dir)
        except Exception as e:
            print(f"  [FAIL] {jij_dir.name}/{folder_name}: {e}")
            return

    # Extract energies
    E_pp = energies["pp"]
    E_pm = energies["pm"]
    E_mp = energies["mp"]
    E_mm = energies["mm"]

    # Calculate Jij
    delta_E = (E_pm + E_mp) - (E_pp + E_mm)
    J_eV = delta_E / (4.0 * S_I * S_J)
    J_meV = J_eV * 1000.0
    nature = "FM" if J_meV > 0 else "AFM"

    print(f"\nFolder: {jij_dir.name}")
    print(f"  E_pp = {E_pp:14.6f} eV | E_pm = {E_pm:14.6f} eV")
    print(f"  E_mp = {E_mp:14.6f} eV | E_mm = {E_mm:14.6f} eV")
    print(f"  --> Delta E : {delta_E:10.6f} eV")
    print(f"  --> Jij     : {J_meV:10.4f} meV ({nature})")


def main():
    root = Path(".").resolve()
    # Find all top-level directories containing 'Jij' in their name
    jij_folders = sorted(
        [d for d in root.iterdir() if d.is_dir() and "Jij" in d.name]
    )

    if not jij_folders:
        print("No folders containing 'Jij' were found.")
        return

    print(f"Found {len(jij_folders)} Jij calculation folders.")
    print("=" * 60)

    for jij_dir in jij_folders:
        process_jij_run(jij_dir)

    print("=" * 60)


if __name__ == "__main__":
    main()
