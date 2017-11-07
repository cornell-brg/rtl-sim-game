#!/bin/bash

echo "------------------- Using PyPy -------------------"
source /work/global/sj634/Installations/venvs/pypy-bits/bin/activate

# run pymtl
cd pymtl

echo
./idiv-sim --sim python --cycle 10000000
./idiv-sim --sim python --cycle 10000000
./idiv-sim --sim python --cycle 10000000

echo
./idiv-sim --sim simjit --cycle 10000000
./idiv-sim --sim simjit --cycle 10000000
./idiv-sim --sim simjit --cycle 10000000

# run mamba

cd ../mamba

echo
./idiv-sim --cycle 100000000
./idiv-sim --cycle 100000000
./idiv-sim --cycle 100000000

# run myhdl

cd ../myhdl

echo 
./idiv-sim --cycle 10000000
./idiv-sim --cycle 10000000
./idiv-sim --cycle 10000000

# run pyrtl

cd ../pyrtl

echo
./idiv-sim --sim normal --cycle 1000000
./idiv-sim --sim normal --cycle 1000000
./idiv-sim --sim normal --cycle 1000000

echo
./idiv-sim --sim fast --cycle 10000000
./idiv-sim --sim fast --cycle 10000000
./idiv-sim --sim fast --cycle 10000000

echo
./idiv-sim --sim compiled --cycle 10000000
./idiv-sim --sim compiled --cycle 10000000
./idiv-sim --sim compiled --cycle 10000000

