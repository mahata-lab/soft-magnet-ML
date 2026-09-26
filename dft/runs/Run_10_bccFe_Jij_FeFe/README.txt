Run: Run_10_bccFe_Jij_FeFe
System: bcc Fe, 2x2x2 conventional supercell, 16 Fe atoms
Purpose: Four-state mapping for nearest-neighbor Fe-Fe exchange J1.
         Map ID in plan: Row 2.

Flipped pair: Fe atom 0 at (0, 0, 0) and Fe atom 1 at (1/4, 1/4, 1/4).
These are nearest neighbors at distance a*sqrt(3)/2 ~ 2.48 A.

For each state subfolder, copy POSCAR and use the MAGMOM line below
in your INCAR. All other atoms (14 of them) take +2.20 as a reference.

After running all four states:
    J_FeFe = (E_pp + E_mm - E_pm - E_mp) / 4

Suggested INCAR (same for all 4 states except MAGMOM):
    ISTART = 0
    ICHARG = 2
    ENCUT  = 500
    EDIFF  = 1E-6
    ISMEAR = 1
    SIGMA  = 0.1
    ISPIN  = 2
    LORBIT = 11
    NELM   = 100

Suggested KPOINTS: Monkhorst-Pack 8 x 8 x 8 (scaled from 16x16x16
for unit cell because the supercell is 2x larger in each direction).

