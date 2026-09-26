import os
import re

def get_final_energy(oszicar_path):
    """Extracts the final E0 energy from an OSZICAR file."""
    if not os.path.exists(oszicar_path):
        return None
    try:
        with open(oszicar_path, 'r') as f:
            for line in reversed(f.readlines()):
                if "E0=" in line:
                    return float(line.split("E0=")[1].split()[0])
    except Exception:
        return None
    return None

def scan_and_calculate_mae(root_dir="."):
    mae_groups = {}
    
    # Matches: Run_XX_MaterialName_MAE_Direction
    # Group 1 = MaterialName, Group 2 = Direction
    pattern = re.compile(r"^Run_\d+_(.*)_MAE_(\d+)")

    print("--- Debugging Scan ---")
    for folder in sorted(os.listdir(root_dir)):
        folder_path = os.path.join(root_dir, folder)
        if os.path.isdir(folder_path):
            match = pattern.match(folder)
            if match:
                material_name = match.group(1)
                direction = match.group(2)
                
                oszicar_file = os.path.join(folder_path, "OSZICAR")
                energy = get_final_energy(oszicar_file)
                
                print(f"Folder: {folder} -> Matched As: {material_name}, Axis: {direction}, Energy: {energy}")
                
                if energy is not None:
                    if material_name not in mae_groups:
                        mae_groups[material_name] = {}
                    mae_groups[material_name][direction] = energy
    
    print("-" * 60 + "\n")

    # Print Final Report
    print(f"{'Material System':<25} | {'Axis 1':<6} | {'Axis 2':<6} | {'MAE (meV)':<12}")
    print("-" * 60)
    
    for system, data in sorted(mae_groups.items()):
        # Check for 001 vs 100 pairing
        if "001" in data and "100" in data:
            mae_ev = data["100"] - data["001"]
            mae_mev = mae_ev * 1000
            print(f"{system:<25} | {'001':<6} | {'100':<6} | {mae_mev:>10.4f} meV")
            
        # Check for 001 vs 111 pairing
        if "001" in data and "111" in data:
            mae_ev = data["111"] - data["001"]
            mae_mev = mae_ev * 1000
            print(f"{system:<25} | {'001':<6} | {'111':<6} | {mae_mev:>10.4f} meV")

if __name__ == "__main__":
    scan_and_calculate_mae()
