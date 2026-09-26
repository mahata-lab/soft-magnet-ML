import os

def parse_vasp_magnetic_summary(folder_path):
    outcar_path = os.path.join(folder_path, "OUTCAR")
    oszicar_path = os.path.join(folder_path, "OSZICAR")
    
    is_spin_polarized = "No"
    total_mag = "N/A"
    e_fermi = "N/A"
    
    # 1. Check Spin Polarization and Fermi Energy from OUTCAR
    if os.path.exists(outcar_path):
        try:
            with open(outcar_path, 'r') as f:
                for line in f:
                    if "ISPIN" in line:
                        is_spin_polarized = "Yes (ISPIN=2)" if "2" in line.split() else "No (ISPIN=1)"
                    if "E-fermi" in line:
                        e_fermi = line.split()[2] + " eV"
        except Exception:
            pass

    # 2. Extract Total Magnetic Moment from OSZICAR
    if os.path.exists(oszicar_path):
        try:
            with open(oszicar_path, 'r') as f:
                for line in reversed(f.readlines()):
                    if "mag=" in line:
                        total_mag = line.split("mag=")[1].split()[0] + " \u03bcB"
                        break
        except Exception:
            pass
            
    return is_spin_polarized, total_mag, e_fermi

def scan_all_runs(root_dir="."):
    print(f"{'Folder Name':<35} | {'Spin Pol?':<13} | {'Total Mag':<12} | {'E-Fermi':<10}")
    print("-" * 80)
    
    for folder in sorted(os.listdir(root_dir)):
        folder_path = os.path.join(root_dir, folder)
        if os.path.isdir(folder_path) and folder.startswith("Run_"):
            is_spin, mag, fermi = parse_vasp_magnetic_summary(folder_path)
            print(f"{folder:<35} | {is_spin:<13} | {mag:<12} | {fermi:<10}")

if __name__ == "__main__":
    scan_all_runs()
