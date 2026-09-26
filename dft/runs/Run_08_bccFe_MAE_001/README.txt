Run: Run_08_bccFe_MAE_001
System: bcc Fe (2-atom conventional cell)
Lattice constant: a = 2.866 A  (replace with fitted a0 if it differs)
Purpose: Non-collinear SOC SCF with M || [001]. Reference for MAE.
         Map ID in plan: Row 3.

Workflow:
  1. Run a collinear ISPIN=2 SCF first to converge the charge density.
     Save CHGCAR.
  2. Restart this run with the saved CHGCAR.

Suggested INCAR keys:
    ISTART  = 1
    ICHARG  = 11
    ENCUT   = 500
    EDIFF   = 1E-7
    ISMEAR  = -5            ! tetrahedron for MAE
    ISPIN   = 2
    LNONCOLLINEAR = .TRUE.
    LSORBIT = .TRUE.
    SAXIS   = 0 0 1
    MAGMOM  = 0 0 2.20  0 0 2.20    ! 3 numbers per atom in noncoll
    LMAXMIX = 4
    NELM    = 200
    GGA_COMPAT = .FALSE.

Suggested KPOINTS: Monkhorst-Pack 24 x 24 x 24 (or denser)

Pair this with Run_09 (M || [111]) for bcc Fe MAE.

