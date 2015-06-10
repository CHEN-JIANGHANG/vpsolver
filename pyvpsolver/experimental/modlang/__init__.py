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

from .. import *
from cmd import *
import os
import re

def glpk_mod2lp(fname_mod, fname_lp):
    os.system("glpsol --math " + fname_mod + " --check --wlp " + fname_lp + "| grep -v Generating")

def glpk_mod2mps(fname_mod, fname_mps):
    os.system("glpsol --math " + fname_mod + " --check --wmps " + fname_mps + "| grep -v Generating")

class ParseAMPL:
    def __init__(self, mod_in, mod_out = None, pyvars={}):
        FLOW = CmdFlow()
        LOAD_VBP = CmdLoadVBP()
        pyvars['FLOW'] = FLOW
        pyvars['LOAD_VBP'] = LOAD_VBP
        self.FLOW = FLOW
        self.LOAD_VBP = LOAD_VBP
        f = open(mod_in, "r")
        text = f.read()
        rgx = re.compile("(#|/\*\s*)?\$([^\s{\[]+)(\[[^\]]*\])?{(.+?(?=}\s*;))}\s*;(\s*\*/)?", re.DOTALL)
        result = text[:]
        for match in rgx.finditer(text):
            comment, call, args1, args2 = match.groups()[:-1]
            assert call in ['LOAD_VBP', 'FLOW', 'PY']
            strmatch = text[match.start():match.end()]
            if comment != None:
                result = result.replace(strmatch, '/*IGNORED:'+strmatch.strip('/**/')+'*/')
                continue
            if call == 'PY':
                if args1 != None:
                    varname = args1.strip("[]")
                    exec(varname + ' = ""', globals(), pyvars)
                    exec(args2, globals(), pyvars)
                    output = pyvars[varname]
                else:
                    exec(args2, globals(), pyvars)
                    output = ""
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/'+output)
            elif call == 'LOAD_VBP':
                assert args1 != None
                varname = args1.strip("[]'\"")
                call = 'LOAD_VBP[\''+varname+'\']('+args2+')'
                exec(varname + ' = ' + call, globals(), pyvars)
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/')
            elif call == 'FLOW':
                assert args1 != None
                zvar = args1.strip("[]'\"")
                call = 'FLOW[\''+zvar+'\']('+args2+')'
                res = eval(call)
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/'+res)
            else:
                print "Invalid syntax:", strmatch
                assert False

        defs, data = LOAD_VBP.defs, LOAD_VBP.data
        self.result = defs + result
        data_stmt = re.search("data\s*;", self.result, re.DOTALL)
        end_stmt = re.search("end\s*;", self.result, re.DOTALL)
        if data_stmt != None:
            match = data_stmt.group(0)
            self.result = self.result.replace(match, match+'\n'+data)
        else:
            if end_stmt == None:
                self.result += "data;\n"+data
            else:
                match = end_stmt.group(0)
                self.result = self.result.replace(match, "data;\n"+data+"\nend;")
        if end_stmt == None:
            self.result += "end;\n"

        if mod_out != None:
            self.mod_out = mod_out
        else:
            self.mod_out = VPSolver.new_tmp_file(".mod")

        self.writeMOD(self.mod_out)

    def writeMOD(self, fname_mod):
        f = open(fname_mod, "w")
        print >>f, self.result
        f.close()

    def model(self):
        return self.result

    def model_file(self):
        return self.mod_out
