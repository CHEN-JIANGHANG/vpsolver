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

from .... import *

class CmdLoadVBP:
    def __init__(self):
        self.defs = ""
        self.data = ""

    def __getitem__(self, name):
        return lambda *args: self.evalcmd(name, args)

    def evalcmd(self, name, args):
        assert 1 <= len(args) <= 3
        fname = args[0]
        i0 = args[1] if len(args) > 1 else 1
        d0 = args[2] if len(args) > 2 else 1
        instance = VBP.fromFile(fname, verbose=False)

        self.defs += "#BEGIN_DEFS: %s\n" % name
        self.defs += "param %s_m := %d;\n" % (name, instance.m)
        self.defs += "param %s_n := %d;\n" % (name, sum(instance.b))
        self.defs += "param %s_p := %d;\n" % (name, instance.ndims)
        self.defs += "set %s_I := %d..%s_m;\n" % (name, i0, name)
        self.defs += "set %s_D := %d..%s_p;\n" % (name, d0, name)
        self.defs += "param %s_W{%s_D};\n" % (name, name)
        self.defs += "param %s_b{%s_I};\n" % (name, name)
        self.defs += "param %s_w{%s_I,%s_D};\n" % (name, name, name)
        self.defs += "#END_DEFS: %s\n" % name

        self.data += "#BEGIN_DATA: %s\n" % name
        self.data += "param %s_W default 0 := " % name
        for i in xrange(instance.ndims):
            if instance.W[i] != 0:
                self.data += "[%d]%d" % (i0+i, instance.W[i])
        self.data += ";\n"
        self.data += "param %s_b default 0 := " % name
        for i in xrange(instance.m):
            if instance.b[i] != 0:
                self.data += "[%d]%d" % (i0+i, instance.b[i])
        self.data += ";\n"
        self.data += "param %s_w default 0 := " % name
        for i in xrange(instance.m):
            for d in xrange(instance.ndims):
                if instance.w[i][d] != 0:
                    self.data += "[%d,%d]%d" % (i0+i, d0+d, instance.w[i][d])
        self.data += ";\n"
        self.data += "#END_DATA: %s\n" % name

        return instance
