Run: Run_25_L12Fe3Co_vol_a3.580
System: L1_2 Fe3Co (4-atom cell: 3 Fe on faces + 1 Co at corner)
Lattice constant: a = 3.580 A
Purpose: Volume scan for EOS fit.
         Map ID in plan: Row 18, point 3 of 7.

Suggested INCAR keys:
    ISTART = 0
    ENCUT  = 500
    EDIFF  = 1E-6
    ISMEAR = 1
    SIGMA  = 0.1
    ISPIN  = 2
    MAGMOM = +2.50 +2.50 +2.50  +1.70    ! 3 Fe, then 1 Co
    LORBIT = 11

Suggested KPOINTS: Monkhorst-Pack 16 x 16 x 16

Note: L1_2 Fe3Co is metastable. The broad scan brackets the true
equilibrium more conservatively than B2 FeCo.

