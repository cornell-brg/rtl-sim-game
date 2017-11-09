import random
random.seed(0xdeadbeef)

from IntDivRem4  import IntDivRem4
from myhdl import *

def TestHarness( nbits, src_msgs, sink_msgs ):
  clk = Signal(False)
  rst = Signal(False)

  req_val = Signal(True)
  req_rdy = Signal(False)
  req_msg = Signal( modbv(src_msgs.pop(0))[nbits*2:0] )
  resp_val = Signal(False)
  resp_rdy = Signal(True)
  resp_msg = Signal( modbv(0)[nbits*2:0] )

  idiv = IntDivRem4(clk, rst, req_val, req_rdy, req_msg,
                              resp_val, resp_rdy, resp_msg, nbits )
  tmp = Signal(modbv(0)[nbits:0])

  @always(delay(1))
  def clkgen():
    clk.next = not clk

  @always(clk.posedge)
  def src():
    if req_val and req_rdy:
      if src_msgs:
        req_msg.next = src_msgs.pop(0)
      else:
        req_val.next = 0

  @always_comb
  def sink():
    if sink_msgs:
      if resp_rdy and resp_val:
        sink_msg = sink_msgs.pop(0)
        if resp_msg != sink_msg:
          raise StopSimulation("Test Failed! [ {} != {} ]".format(resp_msg, sink_msg))
    else:
      raise StopSimulation("Test Passed!")

  return instances()

def gen_msgs( nbits ):
  src_msgs  = []
  sink_msgs = []

  for i in xrange(10):
    x = random.randint(2, 2**nbits-1)
    y = random.randint(1, min(x, 2**(nbits/3*2)))
    src_msgs.append( (y << nbits) | x )
    sink_msgs.append( ((x / y) << nbits) | (x % y) )

  return src_msgs, sink_msgs

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_14():
  src_msgs, sink_msgs = gen_msgs( 14 )
  sim = Simulation( TestHarness( 14,
                                 src_msgs, sink_msgs ) )
  sim.run(5000)

def test_64_delay():
  src_msgs, sink_msgs = gen_msgs( 64 )
  sim = Simulation( TestHarness( 64,
                                 src_msgs, sink_msgs ) )
  sim.run(5000)

def test_128():
  src_msgs, sink_msgs = gen_msgs( 128 )
  sim = Simulation( TestHarness( 128,
                                 src_msgs, sink_msgs ) )
  sim.run(5000)
