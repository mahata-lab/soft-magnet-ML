import csv
from pathlib import Path
import re


def find_folder_by_prefix(base_path, prefix):
    """Finds a directory matching a given prefix (e.g., 'Run_47_')."""
    base = Path(base_path)
    matches = [
        d for d in base.iterdir() if d.is_dir() and d.name.startswith(prefix)
    ]
    if matches:
        return matches[0]
    return None


def get_final_energy(folder_path):
    """Parses OSZICAR or vasprun.xml, with fallback checking for OUTCAR."""
    folder = Path(folder_path)

    # 1. Check OSZICAR
    oszicar = folder / "OSZICAR"
    if oszicar.exists():
        with open(oszicar, "r", errors="ignore") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if "E0=" in line or "F=" in line:
                    match = re.search(r"E0=\s*([-\d\.]+)", line)
                    if match:
                        return float(match.group(1))

    # 2. Check vasprun.xml
    vasprun = folder / "vasprun.xml"
    if vasprun.exists():
        with open(vasprun, "r", errors="ignore") as f:
            for line in reversed(f.readlines()):
                if "e_0_energy" in line:
                    match = re.search(r">([-\d\.]+)<", line)
                    if match:
                        return float(match.group(1))

    # 3. Check OUTCAR
    outcar = folder / "OUTCAR"
    if outcar.exists():
        with open(outcar, "r", errors="ignore") as f:
            for line in reversed(f.readlines()):
                if "energy  without entropy=" in line or "energy(sigma->0)" in line:
                    match = re.search(r"=\s*([-\d\.]+)", line)
                    if match:
                        return float(match.group(1))

    print(f"Warning: Could not extract energy from {folder.name}")
    return None


def extract_candidate_energies(base_path, num_atoms_per_cell=16):
    base = Path(base_path)

    candidate_pairs = [
        {
            "Candidate": "Cand 1 (Fe46Co34)",
            "BCC_prefix": "Run_45_",
            "FCC_prefix": "Run_46_",
        },
        {
            "Candidate": "Cand 2 (Fe38Co40)",
            "BCC_prefix": "Run_47_",
            "FCC_prefix": "Run_48_",
        },
        {
            "Candidate": "Cand 3 (Fe26Co45)",
            "BCC_prefix": "Run_49_",
            "FCC_prefix": "Run_50_",
        },
    ]

    results = []

    for pair in candidate_pairs:
        bcc_folder = find_folder_by_prefix(base, pair["BCC_prefix"])
        fcc_folder = find_folder_by_prefix(base, pair["FCC_prefix"])

        if not bcc_folder:
            print(f"Directory starting with '{pair['BCC_prefix']}' NOT FOUND.")
            continue
        if not fcc_folder:
            print(f"Directory starting with '{pair['FCC_prefix']}' NOT FOUND.")
            continue

        e_bcc = get_final_energy(bcc_folder)
        e_fcc = get_final_energy(fcc_folder)

        if e_bcc is not None and e_fcc is not None:
            delta_e_total = e_fcc - e_bcc
            delta_e_mev_atom = (delta_e_total / num_atoms_per_cell) * 1000.0

            results.append(
                {
                    "Candidate": pair["Candidate"],
                    "E_BCC (eV)": f"{e_bcc:.6f}",
                    "E_FCC (eV)": f"{e_fcc:.6f}",
                    "Delta_E (meV/atom)": f"{delta_e_mev_atom:.2f}",
                    "Ground State": "BCC" if delta_e_mev_atom > 0 else "FCC",
                }
            )

    if results:
        print("\n" + "=" * 67)
        print(
            f"{'Candidate':<20} | {'E_BCC (eV)':<12} | {'E_FCC (eV)':<12} | {'dE (meV/atom)':<14} | {'Ground State'}"
        )
        print("-" * 67)
        for r in results:
            cand = r["Candidate"]
            e_b = r["E_BCC (eV)"]
            e_f = r["E_FCC (eV)"]
            de = r["Delta_E (meV/atom)"]
            gs = r["Ground State"]
            print(f"{cand:<20} | {e_b:<12} | {e_f:<12} | {de:<14} | {gs}")
        print("=" * 67 + "\n")

        # Save to CSV
        csv_file = base / "candidate_phase_stabilities.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"Results saved to {csv_file}")


if __name__ == "__main__":
    dft_directory = "/home/student3/Desktop/soft-magnets/dft_runs"
    extract_candidate_energies(dft_directory, num_atoms_per_cell=16)
