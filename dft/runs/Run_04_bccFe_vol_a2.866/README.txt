Run: Run_04_bccFe_vol_a2.866
System: bcc Fe (2-atom conventional cell)
Lattice constant: a = 2.866 A
Purpose: Volume scan point for Birch-Murnaghan EOS fit.
         Map ID in plan: Row 1 (volume scan, point 4 of 7).

Suggested INCAR keys:
    ISTART = 0
    ICHARG = 2
    ENCUT  = 500
    EDIFF  = 1E-6
    ISMEAR = 1
    SIGMA  = 0.1
    ISPIN  = 2
    MAGMOM = +2.20 +2.20
    LORBIT = 11
    NELM   = 100
    LREAL  = .FALSE.

Suggested KPOINTS: Monkhorst-Pack 16 x 16 x 16

After all 7 volume points are done:
  fit E(V) to Birch-Murnaghan or Murnaghan EOS
  extract a0, B0
  proceed to MAE runs at the fitted a0 (will become Run_09 setup)

