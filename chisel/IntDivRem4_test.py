import random
random.seed(0xdeadbeef)

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink
from IntDivRem4   import IntDivRem4

class TestHarness (Model):

  def __init__( s, nbits, src_msgs, sink_msgs,
                src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src  = TestSource ( Bits(nbits*2), src_msgs,  src_delay  )
    s.idiv = IntDivRem4()
    s.sink = TestSink   ( Bits(nbits*2), sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.idiv.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.idiv = TranslationTool( s.idiv )

    # Connect

    s.connect( s.src.out,  s.idiv.req  )
    s.connect( s.idiv.resp, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.sink.line_trace()

def gen_msgs( nbits ):
  src_msgs  = []
  sink_msgs = []

  for i in xrange(10):
    x = random.randint(2, 2**nbits-1)
    y = random.randint(1, min(x, 2**(nbits/3*2)))
    z = Bits(nbits*2,0)
    z[0:nbits]  = x
    z[nbits:nbits*2] = y
    src_msgs.append( z )
    sink_msgs.append( Bits(nbits*2, ((x / y) << nbits) | (x % y) ) )

  return src_msgs, sink_msgs

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_64_delay( dump_vcd, test_verilog ):
  src_msgs, sink_msgs = gen_msgs( 64 )
  run_sim( TestHarness( 64,
                        src_msgs, sink_msgs, 3, 14,
                        dump_vcd, test_verilog ) )
