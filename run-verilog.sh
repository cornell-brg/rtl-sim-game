#!/bin/bash

echo "------------------- Verilog sims -------------------"
module load synopsys-vcs-vcsi-2016.6

# run iverilog

cd iverilog

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

