#!/usr/bin/python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2015, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
sdir = os.path.dirname(__file__)
if sdir != "":
    os.chdir(sdir)
import sys
sys.path.insert(0, "../../../")

from pyvpsolver.modlang import AMPLParser, glpk_mod2lp
from pyvpsolver import VPSolver


def main():
    """Parses 'instance.mod'"""

    mod_in = "instance.mod"
    mod_out = "tmp/instance.out.mod"
    parser = AMPLParser()
    parser.parse(mod_in, mod_out)

    lp_out = "tmp/instance.lp"
    glpk_mod2lp(mod_out, lp_out, True)
    out, varvalues = VPSolver.script_wsol(
        "vpsolver_gurobi.sh", lp_out, verbose=True
    )
    sol, varvalues = parser["FLOW"].extract(varvalues, verbose=True)

    print
    print "sol:", sol
    print "varvalues:", [(k, v) for k, v in sorted(varvalues.items())]
    print

    os.system("glpsol --math " + mod_out + "| grep -v Generating")

if __name__ == "__main__":
    main()
