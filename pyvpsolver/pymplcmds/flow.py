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

import re
from .base import CmdBase
from ..vpsolver import VPSolver, VBP, AFG
from ..model import Model
from ..modelutils import writemod
from .. import pymplutils


class CmdFlow(CmdBase):
    """Command for creating arc-flow models."""

    def __init__(self, *args, **kwargs):
        CmdBase.__init__(self, *args, **kwargs)
        self._zvars = []
        self._graphs = []
        self._prefixes = []

    def _evalcmd(self, zvar, W, w, b, bounds=None):
        """Evalutates CMD[zvar](*args)."""
        match = pymplutils.parse_symbname(zvar, allow_index="[]")
        assert match is not None
        zvar = match

        if isinstance(W, dict):
            W = [W[k] for k in sorted(W)]
        if isinstance(w, dict):
            i0 = min(i for i, d in w)
            d0 = min(d for i, d in w)
            m = max(i for i, d in w)-i0+1
            p = max(d for i, d in w)-d0+1
            ww = [
                [w[i0+i, d0+d] for d in xrange(p)] for i in xrange(m)
            ]
            w = ww
        if isinstance(b, dict):
            b = [b[k] for k in sorted(b)]
        if isinstance(bounds, dict):
            bounds = [bounds[k] for k in sorted(bounds)]

        prefix = "_{0}_".format(zvar.lstrip("^"))
        prefix = prefix.replace("[", "_").replace("]", "_")

        graph, model, declared_vars = self._generate_model(
            zvar, W, w, b, bounds, prefix
        )

        self._zvars.append(zvar)
        self._graphs.append(graph)
        self._prefixes.append(prefix)

        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)

    def _generate_model(self, zvar, W, w, b, bounds=None, prefix=""):
        """Generates a arc-flow model."""
        m = len(w)
        bb = [0]*m
        bvars = []
        for i in xrange(m):
            if isinstance(b[i], str):
                bb[i] = min(
                    W[d]/w[i][d] for d in xrange(len(w[i])) if w[i][d] != 0
                )
                if bounds is not None:
                    bb[i] = min(bb[i], bounds[i])
                bvars.append(b[i])
            else:
                bb[i] = b[i]

        instance = VBP(W, w, bb, verbose=False)
        graph = AFG(instance, verbose=False).graph()
        feedback = (graph.T, graph.S, "Z")
        graph.A.append(feedback)

        vnames = {}
        vnames[feedback] = zvar
        ub = {}
        varl, cons = graph.get_flow_cons(vnames)
        assocs = graph.get_assocs(vnames)
        graph.names = vnames

        labels = {
            (u, v, i): ["i={0}".format(i+1)]
            for (u, v, i) in graph.A
            if isinstance(i, int) and i < m
        }
        graph.set_labels(labels)

        for i in xrange(m):
            if bounds is not None:
                for var in assocs[i]:
                    ub[var] = bounds[i]
            if isinstance(b[i], str):
                varl.append(b[i])
                cons.append((assocs[i], "=", b[i]))
            else:
                if b[i] > 1:
                    cons.append((assocs[i], ">=", b[i]))
                else:
                    cons.append((assocs[i], "=", b[i]))

        model = Model()
        for var in varl:
            model.add_var(name=var, lb=0, ub=ub.get(var, None), vtype="I")
        for lincomb, sign, rhs in cons:
            model.add_con(lincomb, sign, rhs)

        declared_vars = set(bvars)

        def var_name(name):
            if name == zvar:
                return name
            elif name in declared_vars:
                return name
            else:
                return prefix+name

        def con_name(name):
            return prefix+name

        model.rename_vars(var_name)
        model.rename_cons(con_name)

        return graph, model, declared_vars

    def extract(self, varvalues, verbose=False):
        """Extracts an arc-flow solution."""
        lst_sol = []
        newvv = varvalues.copy()
        for zvar, graph, prefix in zip(
                self._zvars, self._graphs, self._prefixes):
            vv = {
                k.replace(prefix, "", 1): v
                for k, v in varvalues.items() if k.startswith(prefix)
            }
            for k in vv:
                del newvv[prefix+k]
            graph.set_flow(vv)
            sol = graph.extract_solution(graph.S, "<-", graph.T)
            lst_sol.append((zvar, varvalues.get(zvar, 0), sol))
            VPSolver.log("Graph: {0} (flow={1:d})\n\t{2}".format(
                    zvar, varvalues.get(zvar, 0), sol
                ),
                verbose=verbose
            )
        return lst_sol, newvv
