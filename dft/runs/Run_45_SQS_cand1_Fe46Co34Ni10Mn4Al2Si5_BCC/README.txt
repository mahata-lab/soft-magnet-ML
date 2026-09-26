Run: Run_45_SQS_cand1_Fe46Co34Ni10Mn4Al2Si5_BCC
        System: 3x3x3 conventional BCC SQS, 54 atoms
        Candidate: cand1_Fe46Co34Ni10Mn4Al2Si5
        ML predictions: Tc = 1108 K, Hc = 33 Oe

        Composition (target vs realised in this SQS cell):
            Fe  target 45.63%  ->  25/54  = 46.30% realised
            Co  target 33.70%  ->  18/54  = 33.33% realised
            Ni  target 10.32%  ->   5/54  =  9.26% realised
            Mn  target  3.46%  ->   2/54  =  3.70% realised
            Al  target  1.84%  ->   1/54  =  1.85% realised
            Si  target  5.06%  ->   3/54  =  5.56% realised

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
            MAGMOM = 25*+2.50 18*+1.70 5*+0.60 2*+2.00 1*+0.00 3*+0.00
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
        
