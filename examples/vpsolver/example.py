#!/usr/bin/env python
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
import sys
sdir = os.path.dirname(__file__)
if sdir != "":
    os.chdir(sdir)

INSTALLED = False
if not INSTALLED:
    project_dir = "../../"
    sys.path.insert(0, project_dir)
    os.environ["PATH"] = "{0}/scripts:{0}/bin:{1}".format(
        project_dir, os.environ["PATH"]
    )

from pyvpsolver import VPSolver, VBP, AFG, MPS, LP, solvers


def main():
    """Examples: how to use VBP, AFG, MPS, LP and VPSolver"""

    # Create instanceA:
    instanceA = VBP([5180], [1120, 1250, 520, 1066, 1000, 1150],
                            [9, 5, 91, 18, 11, 64], verbose=False)

    # Create instanceB from a .vbp file
    instanceB = VBP.fromFile("instance.vbp", verbose=False)

    # Create an arc-flow graph for instanceA
    afg = AFG(instanceA, verbose=False)

    # Create .mps and .lp models for instanceA
    mps_model = MPS(afg, verbose=False)
    lp_model = LP(afg, verbose=False)

    # Draw the arc-flow graph for instanceA (requires pygraphviz)
    afg.graph().draw("tmp/graph.svg")

    # Solve instanceA using bin/vpsolver (requires Gurobi)
    out, sol = VPSolver.vpsolver(instanceA, verbose=True)

    # Solve instanceA using any vpsolver script (i.e., any MIP solver):
    #   The scripts accept models with and without the underlying graphs.
    #   However, the graphs are required to extract the solution.
    out, sol = VPSolver.script("vpsolver_glpk.sh", lp_model, afg, verbose=True)
    out, sol = VPSolver.script("vpsolver_gurobi.sh", mps_model, verbose=True)

    # Solve an instance directly without creating AFG, MPS or LP objects:
    out, sol = VPSolver.script("vpsolver_glpk.sh", instanceB, verbose=True)

    # Print the solution:
    obj, patterns = sol
    print "Objective:", obj
    print "Solution:", patterns

    # Pretty-print the solution:
    solvers.vbp.print_solution(obj, patterns)


if __name__ == "__main__":
    main()
