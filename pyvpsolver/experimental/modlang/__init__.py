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

def glpk_mod2lp(fname_mod, fname_lp, verbose = False):
    if verbose:
        os.system("glpsol --math " + fname_mod + " --check --wlp " + fname_lp + "| grep -v Generating")
    else:
        os.system("glpsol --math " + fname_mod + " --check --wlp " + fname_lp + ">> /dev/null")

def glpk_mod2mps(fname_mod, fname_mps, verbose = False):
    if verbose:
        os.system("glpsol --math " + fname_mod + " --check --wmps " + fname_mps + "| grep -v Generating")
    else:
        os.system("glpsol --math " + fname_mod + " --check --wmps " + fname_mps + ">> /dev/null")

class ParseAMPL:
    def __init__(self, mod_in, mod_out = None, pyvars={}):
        _globals, _locals = {}, pyvars
        SET = CmdSet()
        PARAM = CmdParam()
        FLOW = CmdFlow("I")
        FLOW_LP = CmdFlow("C")
        LOAD_VBP = CmdLoadVBP(pyvars)
        GRAPH = CmdGraph()
        pyvars['SET'] = SET
        pyvars['PARAM'] = PARAM
        pyvars['FLOW'] = FLOW
        pyvars['FLOW_LP'] = FLOW_LP
        pyvars['GRAPH'] = GRAPH
        pyvars['LOAD_VBP'] = LOAD_VBP
        self.FLOW = FLOW
        self.LOAD_VBP = LOAD_VBP
        f = open(mod_in, "r")
        text = f.read()
        rgx = re.compile("(#|/\*\s*)?\$([^\s{\[]+)(\[[^\]]*\])?{(.+?(?=}\s*;))}\s*;(\s*\*/)?", re.DOTALL)
        result = text[:]
        for match in rgx.finditer(text):
            comment, call, args1, args2 = match.groups()[:-1]
            assert call in ['SET', 'PARAM', 'LOAD_VBP', 'FLOW', 'FLOW_LP', 'GRAPH', 'PY']
            strmatch = text[match.start():match.end()]
            if comment != None:
                result = result.replace(strmatch, '/*IGNORED:'+strmatch.strip('/**/')+'*/')
                continue
            if call == 'PY':
                if args1 != None:
                    varname = args1.strip("[]")
                    exec(varname + ' = ""', _globals, _locals)
                    exec(args2, _globals, _locals)
                    output = _locals[varname]
                else:
                    exec(args2, _globals, _locals)
                    output = ""
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/'+output)
            elif call == 'LOAD_VBP':
                assert args1 != None
                varname = args1.strip("[]'\"")
                call = 'LOAD_VBP[\''+varname+'\']('+args2+')'
                exec(call, _globals, _locals)
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/')
            elif call == 'SET':
                assert args1 != None
                name = args1.strip("[]'\"")
                call = 'SET[\''+name+'\']('+args2+')'
                exec(call, _globals, _locals)
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/')
            elif call == 'PARAM':
                assert args1 != None
                name = args1.strip("[]'\"")
                call = 'PARAM[\''+name+'\']('+args2+')'
                exec(call, _globals, _locals)
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/')
            elif call == 'FLOW':
                assert args1 != None
                zvar = args1.strip("[]'\"")
                call = 'FLOW[\''+zvar+'\']('+args2+')'
                res = eval(call, _globals, _locals)
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/'+res)
            elif call == 'FLOW_LP':
                assert args1 != None
                zvar = args1.strip("[]'\"")
                call = 'FLOW_LP[\''+zvar+'\']('+args2+')'
                res = eval(call, _globals, _locals)
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/'+res)
            elif call == 'GRAPH':
                assert args1 != None
                set_names = args1.strip("[]'\"")
                call = 'GRAPH[\''+set_names+'\']('+args2+')'
                exec(call, _globals, _locals)
                result = result.replace(strmatch, '/*EVALUATED:'+strmatch+'*/')
            else:
                print "Invalid syntax:", strmatch
                assert False

        defs = "#BEGIN_DEFS\n"
        defs += LOAD_VBP.defs + SET.defs + PARAM.defs + GRAPH.defs
        defs += "#END_DEFS\n"
        data = "#BEGIN_DATA\n"
        data += LOAD_VBP.data + PARAM.data
        data += "#END_DATA\n"
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
