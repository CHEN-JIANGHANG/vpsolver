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
from copy import deepcopy

RGX_SYMBNAME = "\\^?[a-zA-Z_][a-zA-Z0-9_]*"
RGX_INDEX1 = "(?:\\s*\\[[^\\]]*\\])?" # [] index
RGX_INDEX2 = "(?:\\s*{[^}]*})?" # {} index
RGX_SYMBNAME_INDEX1 = RGX_SYMBNAME + RGX_INDEX1
RGX_SYMBNAME_INDEX2 = RGX_SYMBNAME + RGX_INDEX2


def parse_symbname(expr, allow_index=""):
    """Matches and returns a symbolic name."""
    assert allow_index in ("", "[]", "{}")
    if allow_index == "[]":
        rgx_symb = RGX_SYMBNAME_INDEX1
    elif allow_index == "{}":
        rgx_symb = RGX_SYMBNAME_INDEX2
    else:
        rgx_symb = RGX_SYMBNAME
    match = re.match("\\s*("+rgx_symb+")\\s*$", expr)
    if match is None:
        return None
    name = match.groups()[0]
    return name


def parse_symblist(expr, allow_index=""):
    """Matches and returns a list of symbolic names."""
    assert allow_index in ("", "[]", "{}")
    if allow_index == "[]":
        rgx_symb = RGX_SYMBNAME_INDEX1
    elif allow_index == "{}":
        rgx_symb = RGX_SYMBNAME_INDEX2
    else:
        rgx_symb = RGX_SYMBNAME
    match = re.match(
        "\\s*(\\s*"+rgx_symb+"\\s*(?:,\\s*"+rgx_symb+"\\s*)*)\\s*$", expr
    )
    if match is None:
        return None
    lst = match.groups()[0].split(",")
    lst = [x.strip() for x in lst]
    return lst


def parse_indexed(expr, index_type):
    """Matches and returns an indexed symbolic name (i.e., name{index})."""
    assert index_type in ("[]", "{}")
    if index_type == "[]":
        match = re.match(
            "\\s*("+RGX_SYMBNAME+")\\s*"
            "(\\[\\s*"+RGX_SYMBNAME+"\\s*(?:,"
            "\\s*"+RGX_SYMBNAME+"\\s*)*\\])?\\s*$",
            expr
        )
    elif index_type == "{}":
        match = re.match(
            "\\s*("+RGX_SYMBNAME+")\\s*"
            "({\\s*"+RGX_SYMBNAME+"\\s*(?:,\\s*"+RGX_SYMBNAME+"\\s*)*})?\\s*$",
            expr
        )
    if match is None:
        return None
    name, index = match.groups()
    if index is not None:
        index = index.strip(index_type+" ")
        index = index.split(",")
        index = [x.strip() for x in index]
    return name, index


def list2dict(lst, i0=0):
    """Converts a list to a dictionary."""
    dic = {}

    def conv_rec(key, lst):
        for i in xrange(len(lst)):
            if not isinstance(lst[i], list):
                if key == []:
                    dic[i0+i] = lst[i]
                else:
                    dic[tuple(key+[i0+i])] = lst[i]
            else:
                conv_rec(key+[i0+i], lst[i])

    conv_rec([], lst)
    return dic


def tuple2str(tuple_):
    """Converts a tuple to a AMPL tuple."""

    def format_entry(e):
        if not isinstance(e, str):
            return str(e)
        else:
            return "'{0}'".format(e)

    return ",".join(format_entry(e) for e in tuple_)


def ampl_set(name, values, sets, params):
    """Generates the definition for an AMPL set."""
    assert name not in sets
    assert name not in params
    sets[name] = deepcopy(values)
    if name.startswith("^"):
        return "", ""

    def format_entry(e):
        if isinstance(e, str):
            return "'{0}'".format(e)
        elif isinstance(e, (tuple, list)):
            return "({0})".format(tuple2str(e))
        else:
            return str(e)

    defs = "set {0} := {{{1}}};\n".format(
        name, ",".join(format_entry(e) for e in values)
    )
    return defs, ""


def ampl_param(name, index, value, sets, params):
    """Generates the definition for an AMPL parameter."""
    assert name not in sets
    assert name not in params
    params[name] = deepcopy(value)
    if name.startswith("^"):
        return "", ""

    if isinstance(value, dict):
        defs = "param {0}{{{1}}};\n".format(name, index)

        def format_entry(k, v):
            if isinstance(k, str):
                k = "'{0}'".format(k)
            elif isinstance(k, tuple):
                k = tuple2str(k)
            else:
                k = str(k)
            if isinstance(v, str):
                v = "'{0}'".format(v)
            else:
                v = str(v)
            return "[{0}]{1}".format(k, v)

        data = "param {0} := {1};\n".format(
            name, "".join(format_entry(k, v) for k, v in value.items())
        )
        return defs, data
    else:
        assert index is None
        assert isinstance(value, (str, float, int))
        if isinstance(value, str):
            value = "'{0}'".format(value)
        defs = "param {0} := {1};\n".format(name, str(value))
        return defs, ""


def lincomb2str(lincomb):
    """Returns the linear combination as a string."""

    def format_entry(var, coef):
        var = var.lstrip("^")
        if abs(coef) != 1:
            if coef >= 0:
                return "+{0:g}*{1}".format(coef, var)
            else:
                return "-{0:g}*{1}".format(abs(coef), var)
        else:
            if coef >= 0:
                return "+{0}".format(var)
            else:
                return "-{0}".format(var)

    return "".join(format_entry(var, coef) for var, coef in lincomb)


def ampl_var(name, typ="", lb=None, ub=None):
    """Generates the definition for an AMPL variable."""
    if name.startswith("^"):
        return ""
    defs = "var {0}".format(name)
    if typ == "I":
        typ = "integer"
    elif typ == "B":
        typ = "binary"
    if typ != "":
        defs += ", {0}".format(typ)
    if lb is not None:
        defs += ", >= {0:g}".format(lb)
    if ub is not None:
        defs += ", <= {0:g}".format(ub)
    defs += ";"
    return defs


def ampl_con(name, lincomb, sign, rhs):
    """Generates the definition for an AMPL constraint."""
    if name.startswith("^"):
        return ""
    if sign in (">", "<"):
        sign += "="
    defs = "s.t. {name}: {lin} {sign} {rhs};".format(
        name=name,
        lin=lincomb2str(lincomb),
        sign=sign,
        rhs=rhs
    )
    return defs
