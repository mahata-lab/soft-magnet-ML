Run: Run_49_SQS_cand3_Fe26Co45Ni11Mn2Al4Si12_BCC
        System: 3x3x3 conventional BCC SQS, 54 atoms
        Candidate: cand3_Fe26Co45Ni11Mn2Al4Si12
        ML predictions: Tc = 1089 K, Hc = 9 Oe

        Composition (target vs realised in this SQS cell):
            Fe  target 25.87%  ->  14/54  = 25.93% realised
            Co  target 45.00%  ->  24/54  = 44.44% realised
            Ni  target 10.79%  ->   6/54  = 11.11% realised
            Mn  target  1.77%  ->   1/54  =  1.85% realised
            Al  target  4.51%  ->   2/54  =  3.70% realised
            Si  target 12.07%  ->   7/54  = 12.96% realised

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
            MAGMOM = 14*+2.50 24*+1.70 6*+0.60 1*+2.00 2*+0.00 7*+0.00
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
        
