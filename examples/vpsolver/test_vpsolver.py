#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function


def test_vbpsolver():
    """Test vbpsolver."""
    from pyvpsolver import VPSolver
    from pyvpsolver.solvers import vbpsolver
    W = (5180, 9)
    w = [(1120, 1), (1250, 1), (520, 1), (1066, 1), (1000, 1), (1150, 1)]
    b = [9, 5, 91, 18, 11, 64]

    lp_file = VPSolver.new_tmp_file(".lp")
    mps_file = VPSolver.new_tmp_file(".mps")
    svg_file = VPSolver.new_tmp_file(".svg")

    solution = vbpsolver.solve(W, w, b, script="vpsolver_glpk.sh")
    vbpsolver.print_solution(solution)
    obj, patterns = solution
    assert obj == 33

    solution = vbpsolver.solve(
        W, w, b, lp_file=lp_file, mps_file=mps_file, svg_file=svg_file,
        script="vpsolver_glpk.sh"
    )
    vbpsolver.print_solution(solution)
    obj, patterns = solution
    assert obj == 33


def test_mvpsolvers():
    """Test mvpsolvers."""
    from pyvpsolver import VPSolver
    from pyvpsolver.solvers import mvpsolver2013, mvpsolver2016
    Ws = [(100, 75), (75, 50)]
    Cs = [3, 2]
    Qs = [-1, -1]
    ws = [
        [(75, 50)],
        [(40, 15), (25, 25)]
    ]
    b = [2, 1]

    for mvpsolver in [mvpsolver2013, mvpsolver2016]:
        solution = mvpsolver.solve(
            Ws, Cs, Qs, ws, b, script="vpsolver_glpk.sh"
        )
        mvpsolver.print_solution(solution)
        obj, patterns = solution
        assert obj == 5

        lp_file = VPSolver.new_tmp_file(".lp")
        mps_file = VPSolver.new_tmp_file(".mps")
        svg_file = VPSolver.new_tmp_file(".svg")

        solution = mvpsolver.solve(
            Ws, Cs, Qs, ws, b, lp_file=lp_file, mps_file=mps_file,
            svg_file=svg_file, script="vpsolver_glpk.sh"
        )
        mvpsolver.print_solution(solution)
        obj, patterns = solution
        assert obj == 5


def test_scripts():
    """Test scripts."""
    from pyvpsolver import VPSolver, VBP, AFG, LP, MPS
    W = (5180, 9)
    w = [(1120, 1), (1250, 1), (520, 1), (1066, 1), (1000, 1), (1150, 1)]
    b = [9, 5, 91, 18, 11, 64]
    VPSolver.clear()
    instance = VBP(W, w, b, verbose=True)
    afg = AFG(instance, verbose=True)
    lp = LP(afg, verbose=True)
    mps = MPS(afg, verbose=True)
    VPSolver.set_verbose(False)
    output, solution = VPSolver.script("vpsolver_glpk.sh", instance)
    assert solution[0] == 33
    output, solution = VPSolver.script("vpsolver_glpk.sh", afg)
    assert solution[0] == 33
    output, solution = VPSolver.script("vpsolver_glpk.sh", afg, lp)
    assert solution[0] == 33
    output, solution = VPSolver.script("vpsolver_glpk.sh", afg, mps)
    assert solution[0] == 33
    output, solution = VPSolver.script("vpsolver_glpk.sh", lp)
    assert solution is None
    output, solution = VPSolver.script("vpsolver_glpk.sh", mps)
    assert solution is None
    output, solution = VPSolver.script("vpsolver_glpk.sh", afg.afg_file)
    assert solution[0] == 33
    output, solution = VPSolver.script("vpsolver_glpk.sh", lp.lp_file)
    assert solution is None
    output, solution = VPSolver.script("vpsolver_glpk.sh", mps.mps_file)
    assert solution is None
    VPSolver.clear()


if __name__ == "__main__":
    test_vbpsolver()
    test_mvpsolvers()
    test_scripts()
