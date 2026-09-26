Run: Run_46_SQS_cand1_Fe46Co34Ni10Mn4Al2Si5_FCC
        System: 3x3x3 conventional FCC SQS, 108 atoms
        Candidate: cand1_Fe46Co34Ni10Mn4Al2Si5
        ML predictions: Tc = 1108 K, Hc = 33 Oe

        Composition (target vs realised in this SQS cell):
            Fe  target 45.63%  ->  49/108  = 45.37% realised
            Co  target 33.70%  ->  36/108  = 33.33% realised
            Ni  target 10.32%  ->  11/108  = 10.19% realised
            Mn  target  3.46%  ->   4/108  =  3.70% realised
            Al  target  1.84%  ->   2/108  =  1.85% realised
            Si  target  5.06%  ->   6/108  =  5.56% realised

        Lattice constant used for cell generation: a = 3.550 A
            Same caveat as the BCC sibling: relax or scan in VASP.

        Suggested INCAR keys (collinear FM SCF):
            ISTART = 0
            ICHARG = 2
            ENCUT  = 500
            EDIFF  = 1E-5
            ISMEAR = 1
            SIGMA  = 0.1
            ISPIN  = 2
            MAGMOM = 49*+2.50 36*+1.70 11*+0.60 4*+2.00 2*+0.00 6*+0.00
            LORBIT = 11
            NELM   = 200
            LREAL  = Auto

        Suggested KPOINTS: Monkhorst-Pack 5 x 5 x 5

        Notes:
          108 atoms with SOC will be heavy. If the BCC sibling wins on
          total energy (likely for VEC < 8), you can skip the FCC MAE
          calculation and only do the SCF for phase comparison.

          For phase comparison the meaningful quantity is energy per atom,
          not per cell, since BCC and FCC supercells have different sizes.
        
