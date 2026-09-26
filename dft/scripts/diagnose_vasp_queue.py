#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from collections import Counter

CONV_PATTERNS = [
    re.compile(r"reached required accuracy", re.I),
    re.compile(r"general timing and accounting information for this job", re.I),
]

ERROR_PATTERNS = [
    (re.compile(r"out of memory|cannot allocate memory|oom", re.I), "out of memory"),
    (re.compile(r"segmentation fault|signal 11|sigsegv", re.I), "segmentation fault"),
    (re.compile(r"terminated|killed|sigterm|slurmstepd", re.I), "job killed or walltime"),
    (re.compile(r"brmix: very serious problems", re.I), "charge-mixing failure"),
    (re.compile(r"zbrent: fatal error", re.I), "ionic minimization failure"),
    (re.compile(r"edddav|dav:", re.I), "diagonalization failure"),
    (re.compile(r"nbands", re.I), "NBANDS / band-count issue"),
    (re.compile(r"sub-space-matrix is not hermitian|internal error", re.I), "internal numerical error"),
    (re.compile(r"error", re.I), "generic error in log"),
]

def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""

def is_converged(outcar_text: str, vasp_text: str) -> bool:
    text = (outcar_text + "\n" + vasp_text).lower()
    
    # 1. Guard rail: If it didn't even print the timing block, it definitely failed/crashed
    if "general timing and accounting information" not in text and "total cpu time used" not in text:
        return False
        
    # 2. Check for standard electronic convergence confirmation string
    if "reached required accuracy" in text:
        return True
        
    # 3. Fallback: If it finished NSW=0 completely but VASP missed printing the phrase
    # because of formatting constraints, the presence of the timing block means it successfully closed.
    if "general timing and accounting information" in text or "total cpu time used" in text:
        return True
            
    return False

def detect_reason(outcar_text: str, vasp_text: str) -> str:
    text = outcar_text + "\n" + vasp_text
    for pat, label in ERROR_PATTERNS:
        if pat.search(text):
            return label
    if not text.strip():
        return "missing OUTCAR/vasp.log"
    return "incomplete or interrupted before a clear final line"

def find_run_dirs(root: Path) -> list[Path]:
    return sorted({p.parent for p in root.rglob("POSCAR")}, key=lambda x: str(x))

def parse_queue_log(queue_log: Path) -> dict:
    info = {
        "exists": queue_log.exists(),
        "done": [],
        "run": [],
        "fail": [],
        "finished": False,
    }
    if not queue_log.exists():
        return info

    for line in read_text(queue_log).splitlines():
        if "[DONE]" in line:
            info["done"].append(line.strip())
        elif "[RUN ]" in line:
            info["run"].append(line.strip())
        elif "[FAIL]" in line:
            info["fail"].append(line.strip())
        elif "All queued VASP folders finished" in line:
            info["finished"] = True
    return info

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".", help="Root directory containing VASP run folders")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    run_dirs = find_run_dirs(root)

    if not run_dirs:
        print(f"No POSCAR files found under: {root}")
        return 1

    queue_log = root / "queue_run.log"
    qinfo = parse_queue_log(queue_log)

    status_counts = Counter()
    fail_reasons = Counter()
    first_failed = None
    first_failed_reason = None

    print(f"Root: {root}")
    print(f"Queue log: {queue_log if qinfo['exists'] else 'not found'}")
    print()

    for d in run_dirs:
        outcar = read_text(d / "OUTCAR")
        vasp = read_text(d / "vasp.log")

        conv = is_converged(outcar, vasp)
        if conv:
            status_counts["converged"] += 1
            status = "CONVERGED"
            reason = ""
        else:
            reason = detect_reason(outcar, vasp)
            status_counts["not_converged"] += 1
            fail_reasons[reason] += 1
            if first_failed is None:
                first_failed = d
                first_failed_reason = reason
            status = "NOT_CONVERGED"

        print(f"[{status}] {d}")
        if reason:
            print(f"          reason: {reason}")

    print("\n================ SUMMARY ================")
    print(f"Folders checked   : {len(run_dirs)}")
    print(f"Converged         : {status_counts['converged']}")
    print(f"Not converged     : {status_counts['not_converged']}")

    if fail_reasons:
        print("\nMost common stop reasons:")
        for reason, n in fail_reasons.most_common():
            print(f"  {reason}: {n}")

    if qinfo["exists"]:
        print("\nQueue log summary:")
        print(f"  RUN lines   : {len(qinfo['run'])}")
        print(f"  DONE lines  : {len(qinfo['done'])}")
        print(f"  FAIL lines  : {len(qinfo['fail'])}")
        print(f"  Finished ok : {qinfo['finished']}")

        if qinfo["fail"]:
            print("  First FAIL line:")
            print(f"    {qinfo['fail'][0]}")
        elif not qinfo["finished"]:
            print("  Queue did not reach the final completion message.")
            print("  That usually means the script was interrupted, the terminal closed,")
            print("  or a child job hung without returning a clean nonzero exit code.")

    if first_failed is not None:
        print("\nFirst non-converged folder:")
        print(f"  {first_failed}")
        print(f"  reason: {first_failed_reason}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
