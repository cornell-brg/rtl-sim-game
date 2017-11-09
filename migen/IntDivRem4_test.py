import random
random.seed(0xdeadbeef)

from migen import *
from IntDivRem4   import IntDivRem4

def TestHarness( idiv, src_msgs, sink_msgs ):
  for i in range(1000):
    yield idiv.req_val.eq( src_msgs != None )
    if src_msgs:
      yield idiv.req_msg.eq( src_msgs[0] )
    yield idiv.resp_rdy.eq(1)

    yield # cycle

    req_rdy  = (yield idiv.req_rdy)
    resp_val = (yield idiv.resp_val)
    resp_msg = (yield idiv.resp_msg)

    if (req_rdy):
      src_msgs.pop(0)

    print( " REM:", hex((yield idiv.dpath.remainder_reg.out)),
           " DIV:", hex((yield idiv.dpath.divisor_reg.out)),
           " QUO:", hex((yield idiv.dpath.quotient_reg.out)) )

    if ((yield idiv.resp_val)):
      assert (yield idiv.resp_msg) == sink_msgs.pop(0)
      if not sink_msgs:
        return

def gen_msgs( nbits ):
  src_msgs  = []
  sink_msgs = []

  for i in range(10):
    x = random.randint(2, 2**nbits-1)
    y = random.randint(1, min(x, 2**(nbits//3*2)))
    src_msgs.append( (y << nbits) | x )
    sink_msgs.append( ((x // y) << nbits) | (x % y) )

  return src_msgs, sink_msgs

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_4():
  src_msgs, sink_msgs = gen_msgs( 4 )

  idiv = IntDivRem4(4)
  run_simulation( idiv, TestHarness( idiv, src_msgs, sink_msgs ) )

def test_64():
  src_msgs, sink_msgs = gen_msgs( 64 )

  idiv = IntDivRem4(64)
  run_simulation( idiv, TestHarness( idiv, src_msgs, sink_msgs ) )

def test_128():
  src_msgs, sink_msgs = gen_msgs( 128 )

  idiv = IntDivRem4(128)
  run_simulation( idiv, TestHarness( idiv, src_msgs, sink_msgs ) )
