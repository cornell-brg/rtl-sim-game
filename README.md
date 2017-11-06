An RTL Simulation mini-game
===========================
This repo keeps the implementations of an RTL radix-four iterative divider
in various RTL frameworks/languages (PyMTL, PyRTL, MyHDL, (Migen), Chisel,
Verilog) and sets up the simulation in different simulators (SimJIT-RTL of
PyMTL, fast/compiled sim for PyRTL, iverilog/VCS/Verilator for verilog).

The goal of this mini-game is to compare the simulation performance across
different frameworks/simulators using the same design implemented to the
same detail. To our knowledge, this is the first open-source mini-game.

Here are step-by-step instructions to run each simulator.

First, you need to clone all frameworks to sibling folders you cloned the
repo, and install all dependencies for each framework.

```text
  <at this repo's root directory>
  $ cd ..
  $ git clone https://github.com/cornell-brg/pymtl.git
  $ git clone https://github.com/myhdl/myhdl.git
  $ git clone https://github.com/UCSBarchlab/PyRTL.git
  $ git clone https://github.com/cornell-brg/pymtl-v3.git <FIXME>
```

Install these verilog simulators and Chisel's prerequisite. This repo
requires you to add the executable to PATH so that the scripts can
directly call "vcs", "verilator", and "iverilog".

```text
  - iverilog:  git clone git://github.com/steveicarus/iverilog.git
  - verilator: https://www.veripool.org/ftp/verilator-3.876.tgz
  - vcs:       (Commercial!) https://www.synopsys.com/verification/simulation/vcs.html
```


