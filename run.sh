#!/bin/bash

echo "------------------- Using CPython -------------------"
source /work/global/brg/install/venv-pkgs/x86_64-centos7/python2.7.13/bin/activate

# run pymtl
cd pymtl

echo
./idiv-sim --sim python --cycle 1000000
./idiv-sim --sim python --cycle 1000000
./idiv-sim --sim python --cycle 1000000

echo
./idiv-sim --sim simjit --cycle 1000000
./idiv-sim --sim simjit --cycle 1000000
./idiv-sim --sim simjit --cycle 1000000

# run mamba

cd ../mamba

echo
./idiv-sim --cycle 1000000
./idiv-sim --cycle 1000000
./idiv-sim --cycle 1000000

# run myhdl

cd ../myhdl

echo 
./idiv-sim --cycle 1000000
./idiv-sim --cycle 1000000
./idiv-sim --cycle 1000000

# run pyrtl

cd ../pyrtl

echo
./idiv-sim --sim normal --cycle 1000000
./idiv-sim --sim normal --cycle 1000000
./idiv-sim --sim normal --cycle 1000000

echo
./idiv-sim --sim fast --cycle 1000000
./idiv-sim --sim fast --cycle 1000000
./idiv-sim --sim fast --cycle 1000000

echo
./idiv-sim --sim compiled --cycle 1000000
./idiv-sim --sim compiled --cycle 1000000
./idiv-sim --sim compiled --cycle 1000000

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
./idiv-sim --sim normal --cycle 10000000
./idiv-sim --sim normal --cycle 10000000
./idiv-sim --sim normal --cycle 10000000

echo
./idiv-sim --sim fast --cycle 10000000
./idiv-sim --sim fast --cycle 10000000
./idiv-sim --sim fast --cycle 10000000

echo
./idiv-sim --sim compiled --cycle 10000000
./idiv-sim --sim compiled --cycle 10000000
./idiv-sim --sim compiled --cycle 10000000


echo "------------------- Verilog sims -------------------"
module load synopsys-vcs-vcsi-2016.6

# run iverilog

cd ../iverilog

echo
./idiv-sim --vsrc chisel --cycle 10000000
./idiv-sim --vsrc chisel --cycle 10000000
./idiv-sim --vsrc chisel --cycle 10000000

echo
./idiv-sim --vsrc verilog --cycle 10000000
./idiv-sim --vsrc verilog --cycle 10000000
./idiv-sim --vsrc verilog --cycle 10000000

# run vcs

cd ../vcs

echo
./idiv-sim --vsrc chisel --cycle 10000000
./idiv-sim --vsrc chisel --cycle 10000000
./idiv-sim --vsrc chisel --cycle 10000000

echo
./idiv-sim --vsrc verilog --cycle 10000000
./idiv-sim --vsrc verilog --cycle 10000000
./idiv-sim --vsrc verilog --cycle 10000000

