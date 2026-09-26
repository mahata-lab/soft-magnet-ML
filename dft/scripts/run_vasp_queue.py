#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

# --- Configuration ---
VASP_CMD = "mpirun -np 16 vasp_ncl"


def natural_key(path: Path):
    """Sorts folders naturally (e.g., Run_2 before Run_10)."""
    parts = re.split(r"(\d+)", path.as_posix())
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def find_vasp_folders(root: Path) -> list[Path]:
    """Finds all directories containing a POSCAR file."""
    return sorted({p.parent for p in root.rglob("POSCAR")}, key=natural_key)


def is_already_done(run_dir: Path) -> bool:
    """Checks if OUTCAR exists and finished successfully."""
    outcar = run_dir / "OUTCAR"
    if not outcar.is_file():
        return False

    try:
        text = outcar.read_text(errors="ignore").lower()
        return "general timing and accounting information" in text
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Run VASP folders sequentially.")
    parser.add_argument(
        "root", 
        nargs="?", 
        default=".", 
        help="Root directory containing VASP run folders (default: current directory)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip folders that have already completed successfully according to OUTCAR.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    folders = find_vasp_folders(root)

    if not folders:
        print(f"No folders with a POSCAR file were found in {root}.")
        return

    print(f"Root Directory : {root}")
    print(f"Command        : {VASP_CMD}")
    print(f"Resume Mode    : {'ENABLED' if args.resume else 'DISABLED'}")
    print(f"Folders Found  : {len(folders)}\n" + "-" * 50)

    for idx, folder in enumerate(folders, start=1):
        # Skip finished runs if --resume is passed
        if args.resume and is_already_done(folder):
            print(f"[{idx}/{len(folders)}] [SKIP] Already completed: {folder.name}")
            continue

        print(f"[{idx}/{len(folders)}] [RUNNING] {folder.name}...")

        log_file = folder / "vasp.log"
        with log_file.open("w") as f:
            res = subprocess.run(
                VASP_CMD,
                cwd=folder,
                stdout=f,
                stderr=subprocess.STDOUT,
                shell=True,
                executable="/bin/bash",
            )

        if res.returncode == 0 and is_already_done(folder):
            print(f"[{idx}/{len(folders)}] [DONE] Successfully finished: {folder.name}")
        else:
            print(f"[{idx}/{len(folders)}] [FAILED] Error in: {folder.name} (Check vasp.log)")

    print("-" * 50 + "\nAll queue tasks processed.")


if __name__ == "__main__":
    main()
