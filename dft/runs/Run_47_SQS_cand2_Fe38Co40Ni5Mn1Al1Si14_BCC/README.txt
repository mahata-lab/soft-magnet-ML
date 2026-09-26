Run: Run_47_SQS_cand2_Fe38Co40Ni5Mn1Al1Si14_BCC
        System: 3x3x3 conventional BCC SQS, 54 atoms
        Candidate: cand2_Fe38Co40Ni5Mn1Al1Si14
        ML predictions: Tc = 1090 K, Hc = 16 Oe

        Composition (target vs realised in this SQS cell):
            Fe  target 38.26%  ->  21/54  = 38.89% realised
            Co  target 40.42%  ->  22/54  = 40.74% realised
            Ni  target  5.16%  ->   3/54  =  5.56% realised
            Mn  target  1.40%  ->   1/54  =  1.85% realised
            Al  target  1.08%  ->   0/54  =  0.00% realised
            Si  target 13.69%  ->   7/54  = 12.96% realised

        Lattice constant used for cell generation: a = 2.860 A
            Run a volume scan (5-7 points around a = 2.860 A) before
            taking properties seriously. SQS lattice constants are estimates;
            the actual a0 comes from VASP relaxation or EOS fit.

        Suggested INCAR keys (collinear FM SCF):
            ISTART = 0
            ICHARG = 2
            ENCUT  = 500
            EDIFF  = 1E-5     ! slightly looser than ordered cells; 54 atoms
            ISMEAR = 1
            SIGMA  = 0.1
            ISPIN  = 2
            MAGMOM = 21*+2.50 22*+1.70 3*+0.60 1*+2.00 7*+0.00
            LORBIT = 11
            NELM   = 200
            LREAL  = Auto     ! .FALSE. preferred but slow for 54 atoms

        Suggested KPOINTS: Monkhorst-Pack 5 x 5 x 5  (compatible with
            16x16x16 used for 2-atom unit cells, since 3x3x3 supercell is
            ~3x larger in each direction).

        Workflow:
          1. Collinear FM SCF at the lattice constant above.
          2. Compare total energy to the FCC SQS of the same composition
             (Run_xx with the FCC suffix) to decide which phase is stable.
          3. For the winning phase, run a volume scan (optional) and a
             non-collinear SOC pair (M||[001], M||[100]) for MAE.
          4. Extract site-resolved magnetic moments from OUTCAR (LORBIT=11)
             and compare element-by-element with the ML surrogate's
             predicted Ms.
        
