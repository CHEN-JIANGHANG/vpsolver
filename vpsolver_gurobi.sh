#!/bin/bash
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
echo "Usage 1: vpsolver_gurobi.sh instance.vbp"
echo "Usage 2: vpsolver_gurobi.sh graph.afg model.mps/.lp"

BASEDIR=`dirname $0`
BIN_DIR=$BASEDIR/bin/
TMP_DIR=`mktemp -d -t XXXXXXXXXX`

solve(){
    local model_file=$1
    GRB_PARAMS=Threads=1 Presolve=1 Method=2 MIPFocus=1 Heuristics=1 MIPGap=0 MIPGapAbs=1-10^5
    echo -e "\n>>> solving the MIP model using Gurobi..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    gurobi_cl $GRB_PARAMS ResultFile=$TMP_DIR/vars.sol $model_file
    sed '/#/d' < $TMP_DIR/vars.sol > $TMP_DIR/vars.sol2
    mv $TMP_DIR/vars.sol2 $TMP_DIR/vars.sol
}

if [ "$#" -gt 2 ]; then
    exit
fi

if [ "$#" -eq 1 ]; then
    instance=$1
    afg_file=$TMP_DIR/graph.afg
    model_file=$TMP_DIR/model.mps
    
    echo -e "\n>>> vbp2afg..."
    $BIN_DIR/vbp2afg $instance $afg_file -2 

    echo -e "\n>>> afg2mps..."
    $BIN_DIR/afg2mps $afg_file $model_file
fi

if [ "$#" -eq 2 ]; then 
    afg_file=$1
    model_file=$2    
fi

solve $model_file;

echo -e "\n>>> vbpsol..."
$BIN_DIR/vbpsol $afg_file $TMP_DIR/vars.sol

rm -rf $TMP_DIR

