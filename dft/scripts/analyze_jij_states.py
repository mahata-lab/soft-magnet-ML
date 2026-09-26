import matplotlib.pyplot as plt
from pathlib import Path

def parse_oszicar(oszicar_path):
    """Extracts final energy (E0) and total magnetization from OSZICAR."""
    if not oszicar_path.is_file():
        return None, None
    
    last_e0, last_mag = None, 0.0
    
    with open(oszicar_path, 'r') as f:
        for line in f:
            if "E0=" in line:
                parts = line.split()
                try:
                    for i, p in enumerate(parts):
                        if "E0=" in p:
                            val_str = parts[i+1] if p == "E0=" else p.split("=")[1]
                            last_e0 = float(val_str)
                        elif "mag=" in p:
                            val_str = parts[i+1] if p == "mag=" else p.split("=")[1]
                            last_mag = float(val_str)
                except (IndexError, ValueError):
                    continue
                        
    return last_e0, last_mag

def parse_site_magnetization(outcar_path):
    """Extracts final atom-resolved magnetic moments from OUTCAR."""
    if not outcar_path.is_file():
        return {}
    
    site_mags = {}
    recording = False
    
    with open(outcar_path, 'r') as f:
        for line in f:
            if "magnetization (x)" in line or ("tot" in line and "ion" in line):
                recording = True
                site_mags = {}
                continue
            if recording and "----------------------------------------------------" in line:
                continue
            if recording and "tot" in line and not "ion" in line:
                recording = False
                continue
            if recording and line.strip():
                parts = line.split()
                if len(parts) >= 5 and parts[0].isdigit():
                    site_mags[int(parts[0])] = float(parts[-1])
                    
    return site_mags

def main():
    parent_dir = Path(".")
    state_dirs = sorted([d for d in parent_dir.iterdir() if d.is_dir() and d.name.startswith("state")])
    
    if not state_dirs:
        print("No 'state*' directories found in the current directory.")
        return

    summary_data = {}
    
    print("=" * 60)
    print(f"{'State Directory':<20}{'Final E0 (eV)':<20}{'Total Mag (uB)':<20}")
    print("=" * 60)

    for state_dir in state_dirs:
        oszicar = state_dir / "OSZICAR"
        outcar = state_dir / "OUTCAR"
        
        e0, total_mag = parse_oszicar(oszicar)
        site_mags = parse_site_magnetization(outcar)
        
        summary_data[state_dir.name] = {
            "e0": e0,
            "total_mag": total_mag,
            "site_mags": site_mags
        }
        
        e0_str = f"{e0:.6f}" if e0 is not None else "Not Found"
        mag_str = f"{total_mag:.4f}" if total_mag is not None else "Not Found"
        print(f"{state_dir.name:<20}{e0_str:<20}{mag_str:<20}")

    print("\n" + "=" * 60)
    print("SITE-RESOLVED MAGNETIZATION COMPARISON")
    print("=" * 60)
    
    all_atoms = sorted(list({atom for data in summary_data.values() for atom in data["site_mags"].keys()}))
    
    if all_atoms:
        header = f"{'Atom ID':<10}" + "".join([f"{s:<15}" for s in summary_data.keys()])
        print(header)
        print("-" * len(header))
        
        for atom in all_atoms:
            row = f"{atom:<10}"
            for state_name in summary_data.keys():
                val = summary_data[state_name]["site_mags"].get(atom, "N/A")
                val_str = f"{val:.3f}" if isinstance(val, float) else val
                row += f"{val_str:<15}"
            print(row)

    states_with_e0 = [s for s, data in summary_data.items() if data["e0"] is not None]
    energies = [summary_data[s]["e0"] for s in states_with_e0]

    if energies:
        plt.figure(figsize=(8, 5))
        plt.bar(states_with_e0, energies, color='skyblue', edgecolor='black')
        plt.ylabel(r'Energy $E_0$ (eV)')
        plt.title(r'Four-State $J_{ij}$ Energy Comparison')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig("jij_4states_energy_comparison.png", dpi=300)
        print("\nMulti-state energy plot saved as 'jij_4states_energy_comparison.png'")
        plt.show()

if __name__ == "__main__":
    main()
