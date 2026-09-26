Run: Run_09_bccFe_MAE_111
System: bcc Fe (2-atom conventional cell)
Purpose: Non-collinear SOC SCF with M || [111]. Pair with Run_08.
         MAE = E[111] - E[001]. Expected ~ 1.4 ueV/atom, easy [001].
         Map ID in plan: Row 4.

Same INCAR as Run_08, except:
    SAXIS  = 1 1 1
    MAGMOM = 1.27 1.27 1.27  1.27 1.27 1.27   ! ~2.20 / sqrt(3) per axis

