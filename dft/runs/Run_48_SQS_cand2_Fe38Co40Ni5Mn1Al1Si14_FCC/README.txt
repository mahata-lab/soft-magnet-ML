Run: Run_48_SQS_cand2_Fe38Co40Ni5Mn1Al1Si14_FCC
        System: 3x3x3 conventional FCC SQS, 108 atoms
        Candidate: cand2_Fe38Co40Ni5Mn1Al1Si14
        ML predictions: Tc = 1090 K, Hc = 16 Oe

        Composition (target vs realised in this SQS cell):
            Fe  target 38.26%  ->  41/108  = 37.96% realised
            Co  target 40.42%  ->  44/108  = 40.74% realised
            Ni  target  5.16%  ->   6/108  =  5.56% realised
            Mn  target  1.40%  ->   1/108  =  0.93% realised
            Al  target  1.08%  ->   1/108  =  0.93% realised
            Si  target 13.69%  ->  15/108  = 13.89% realised

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
            MAGMOM = 41*+2.50 44*+1.70 6*+0.60 1*+2.00 1*+0.00 15*+0.00
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
        
