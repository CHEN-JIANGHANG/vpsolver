#!/bin/sh
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
#
# Copyright (C) 2013, Filipe Brandao
# Faculdade de Ciencias, Universidade do Porto
# Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

set -e
echo "Copyright (C) 2013, Filipe Brandao"
echo "Usage: vpsolver_lpsolve.sh instance.vbp"

tmpdir=tmp/
if [ "$#" -eq 1 ]; then
    fname=$1
    echo "\nvbp2afg..."
    bin/vbp2afg $fname $tmpdir/$fname.afg -2 

    echo "\nafg2mps..."
    bin/afg2mps $tmpdir/$fname.afg $tmpdir/$fname.mps

    echo "\nsolving the MIP model using lp_solve..."
    lp_solve -mps $tmpdir/$fname.mps > $tmpdir/$fname.out    
    sed -e '1,/variables:/d' $tmpdir/$fname.out > $tmpdir/$fname.sol

    echo "\nvbpsol..."
    bin/vbpsol $tmpdir/$fname.afg $tmpdir/$fname.sol | sed -e '/Instance:/,$d' | sed '/^$/d'
fi
