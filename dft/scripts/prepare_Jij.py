#!/usr/bin/env python3
import re
import shutil
import subprocess
from pathlib import Path

# Conservative core count to keep CPU temps and power draw safe
CORES_TO_USE = 8
VASP_NCL_CMD = f"mpirun -np {CORES_TO_USE} vasp_ncl"

TARGET_PAIRS = {
    "Run_10_bccFe_Jij_FeFe": (1, 2),
    "Run_20_B2FeCo_Jij_FeFe": (1, 2),
    "Run_21_B2FeCo_Jij_FeCo": (1, 9),
    "Run_22_B2FeCo_Jij_CoCo": (9, 10),
    "Run_32_L12Fe3Co_Jij_FeFe": (1, 2),
    "Run_33_L12Fe3Co_Jij_FeCo": (1, 25),
    "Run_43_L12FeCo3_Jij_FeCo": (1, 9),
    "Run_44_L12FeCo3_Jij_CoCo": (9, 10),
}


def get_rwigs_from_potcar(potcar_path: Path) -> str:
    """Extracts RWIGS values directly from the POTCAR file."""
    if not potcar_path.is_file():
        return None
    rwigs_list = []
    for line in potcar_path.read_text(errors="ignore").splitlines():
        if "RWIGS" in line and "=" in line:
            match = re.search(r"RWIGS\s*=\s*([0-9.]+)", line)
            if match:
                rwigs_list.append(match.group(1))
    return " ".join(rwigs_list) if rwigs_list else None


def get_atom_count(poscar_path: Path) -> int:
    """Parses POSCAR to count total atoms."""
    lines = poscar_path.read_text().splitlines()
    for line in lines[5:7]:
        parts = line.split()
        if all(p.isdigit() for p in parts) and parts:
            return sum(int(p) for p in parts)
    return 0


def build_m_constr(num_atoms: int, atom_i: int, atom_j: int, state: str) -> str:
    """Builds the M_CONSTR directional constraint string."""
    idx_i, idx_j = atom_i - 1, atom_j - 1
    vectors = []
    for a in range(num_atoms):
        z_dir = 1
        if state == "pm" and a == idx_j:
            z_dir = -1
        elif state == "mp" and a == idx_i:
            z_dir = -1
        elif state == "mm" and (a == idx_i or a == idx_j):
            z_dir = -1
        vectors.append(f"0 0 {z_dir}")
    return "  ".join(vectors)


def configure_incar(
    state_dir: Path,
    num_atoms: int,
    atom_i: int,
    atom_j: int,
    state: str,
    rwigs_str: str,
    use_wavecar: bool = False,
):
    """Applies stable electronic mixing and constraint settings to INCAR."""
    incar_path = state_dir / "INCAR"
    if not incar_path.is_file():
        return

    lines = incar_path.read_text().splitlines()
    new_lines = []

    # Strip tags that conflict with our non-collinear setup
    remove_keys = {
        "ISPIN",
        "NUPDOWN",
        "MAGMOM",
        "LNONCOLLINEAR",
        "I_CONSTRAINED_M",
        "LAMBDA",
        "M_CONSTR",
        "ICHARG",
        "RWIGS",
        "ISTART",
        "LREAL",
        "NPAR",
        "NSIM",
        "LWAVE",
        "ALGO",
        "AMIX",
        "BMIX",
        "MAXMIX",
    }

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("!") or stripped.startswith("#"):
            new_lines.append(line)
            continue
        key = line.split("=")[0].strip().upper()
        if key not in remove_keys:
            new_lines.append(line)

    m_constr_str = build_m_constr(num_atoms, atom_i, atom_j, state)
    istart_val = "1" if use_wavecar else "0"

    stable_block = [
        "",
        "! --- Stabilized Non-Collinear Constraints ---",
        "LNONCOLLINEAR = .TRUE.",
        "I_CONSTRAINED_M = 1",
        "LAMBDA = 10",  # Restored to 10 to prevent runaway energy
        f"ISTART = {istart_val}",
        "ALGO = Fast",  # Davidson + RMM fallback (prevents divergence)
        "AMIX = 0.2",  # Dampened charge density mixing
        "BMIX = 0.0001",  # Low magnetization density mixing
        "MAXMIX = 40",
        "LREAL = Auto",
        "NPAR = 2",
        "NSIM = 4",
        "LWAVE = .TRUE.",
        f"M_CONSTR = {m_constr_str}",
    ]

    if rwigs_str:
        stable_block.append(f"RWIGS = {rwigs_str}")

    new_lines.extend(stable_block)
    incar_path.write_text("\n".join(new_lines) + "\n")


def run_vasp_job(folder: Path) -> bool:
    """Executes VASP and checks OUTCAR for successful execution."""
    log_path = folder / "vasp.log"
    print(f"    --> Executing VASP in {folder.name}...")
    with log_path.open("w") as log_file:
        subprocess.run(
            VASP_NCL_CMD,
            cwd=folder,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            shell=True,
            executable="/bin/bash",
        )

    outcar = folder / "OUTCAR"
    if outcar.is_file():
        text = outcar.read_text(errors="ignore").lower()
        if "general timing and accounting information" in text:
            return True
    return False


def get_e0_energy(folder: Path) -> float:
    """Extracts penalty-free energy E0 (energy without entropy) from OUTCAR."""
    outcar = folder / "OUTCAR"
    if not outcar.is_file():
        return None
    e0_values = []
    for line in outcar.read_text(errors="ignore").splitlines():
        if "energy  without entropy" in line:
            parts = line.split()
            try:
                e0_values.append(float(parts[-1]))
            except ValueError:
                pass
    return e0_values[-1] if e0_values else None


def main():
    root = Path(".").resolve()
    print("=" * 60)
    print(
        f"Starting Stabilized Sequential Non-Collinear Workflow ({CORES_TO_USE} cores)"
    )
    print("=" * 60)

    for folder_pattern, (atom_i, atom_j) in TARGET_PAIRS.items():
        jij_dir = root / folder_pattern
        if not jij_dir.is_dir():
            continue

        print(f"\n[System] {jij_dir.name}")

        pp_dir = jij_dir / "state1_pp"
        pm_dir = jij_dir / "state2_pm"
        mp_dir = jij_dir / "state3_mp"
        mm_dir = jij_dir / "state4_mm"

        # Step 1: Run state1_pp base calculation
        poscar = pp_dir / "POSCAR"
        potcar = pp_dir / "POTCAR"
        num_atoms = get_atom_count(poscar)
        rwigs_str = get_rwigs_from_potcar(potcar)

        for f in ["WAVECAR", "CHGCAR", "OUTCAR", "OSZICAR", "vasp.log"]:
            (pp_dir / f).unlink(missing_ok=True)

        configure_incar(
            pp_dir,
            num_atoms,
            atom_i,
            atom_j,
            "pp",
            rwigs_str,
            use_wavecar=False,
        )
        print("  --> Running state1_pp (Ground State Base)...")
        if not run_vasp_job(pp_dir):
            print("  [ERROR] Ground state pp failed. Skipping system.")
            continue

        src_wavecar = pp_dir / "WAVECAR"
        if not src_wavecar.is_file():
            print("  [ERROR] WAVECAR missing. Skipping system.")
            continue

        # Step 2: Run remaining states sequentially using WAVECAR
        other_states = {"pm": pm_dir, "mp": mp_dir, "mm": mm_dir}
        for state_key, s_dir in other_states.items():
            for f in ["WAVECAR", "CHGCAR", "OUTCAR", "OSZICAR", "vasp.log"]:
                (s_dir / f).unlink(missing_ok=True)

            shutil.copy2(src_wavecar, s_dir / "WAVECAR")
            configure_incar(
                s_dir,
                num_atoms,
                atom_i,
                atom_j,
                state_key,
                rwigs_str,
                use_wavecar=True,
            )

            print(f"  --> Running {state_key} state with initial guess...")
            run_vasp_job(s_dir)

        # Step 3: Extract E0 & Compute Jij
        energies = {
            "pp": get_e0_energy(pp_dir),
            "pm": get_e0_energy(pm_dir),
            "mp": get_e0_energy(mp_dir),
            "mm": get_e0_energy(mm_dir),
        }

        E_pp, E_pm, E_mp, E_mm = (
            energies["pp"],
            energies["pm"],
            energies["mp"],
            energies["mm"],
        )
        if None not in (E_pp, E_pm, E_mp, E_mm):
            delta_e = (E_pp + E_mm) - (E_pm + E_mp)
            jij_mev = (delta_e / 4.0) * 1000.0
            coupling = "FM" if jij_mev > 0 else "AFM"
            print(f"\n  RESULTS (Penalty-Free E0):")
            print(f"    E_pp = {E_pp:.6f} eV | E_pm = {E_pm:.6f} eV")
            print(f"    E_mp = {E_mp:.6f} eV | E_mm = {E_mm:.6f} eV")
            print(f"    --> Delta E : {delta_e:10.6f} eV")
            print(f"    --> Jij     : {jij_mev:10.4f} meV ({coupling})")
        else:
            print(
                "\n  [ERROR] Could not compute Jij due to incomplete states."
            )

        print("-" * 60)


if __name__ == "__main__":
    main()
