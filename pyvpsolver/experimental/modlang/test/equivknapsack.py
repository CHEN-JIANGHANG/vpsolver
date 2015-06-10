#!/usr/bin/python
import sys
sys.path.insert(0, "../../../../")

from pyvpsolver.experimental.modlang import *

ampl = ParseAMPL("equivknapsack.mod")
ampl.writeMOD("equivknapsack.out.mod")
glpk_mod2lp(ampl.model_file(), "equivknapsack.lp")
out, varvalues = VPSolver.script_wsol("vpsolver_gurobi.sh", "equivknapsack.lp", verbose=True)
sol, varvalues = ampl.FLOW.extract(varvalues, verbose=True)
print
print 'varvalues:', [(k,v) for k,v in sorted(varvalues.items())]
print

os.system("glpsol --math " + ampl.model_file() + " --nomip")
