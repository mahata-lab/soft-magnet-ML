Run: Run_50_SQS_cand3_Fe26Co45Ni11Mn2Al4Si12_FCC
        System: 3x3x3 conventional FCC SQS, 108 atoms
        Candidate: cand3_Fe26Co45Ni11Mn2Al4Si12
        ML predictions: Tc = 1089 K, Hc = 9 Oe

        Composition (target vs realised in this SQS cell):
            Fe  target 25.87%  ->  28/108  = 25.93% realised
            Co  target 45.00%  ->  48/108  = 44.44% realised
            Ni  target 10.79%  ->  12/108  = 11.11% realised
            Mn  target  1.77%  ->   2/108  =  1.85% realised
            Al  target  4.51%  ->   5/108  =  4.63% realised
            Si  target 12.07%  ->  13/108  = 12.04% realised

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
            MAGMOM = 28*+2.50 48*+1.70 12*+0.60 2*+2.00 5*+0.00 13*+0.00
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
        
