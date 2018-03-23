import random
random.seed(0xdeadbeee)

from pymtl import *
from pclib.test import TestSource, TestNetSink, run_sim
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from MeshRouter import MeshRouter

class TestHarness( Model ):

  def __init__( s, cls, side, nmessages, payload_nbits, src_msgs, sink_msgs ):
    msg_nbits = clog2(side) * 4 + clog2(nmessages) + payload_nbits

    s.srcs  = [ TestSource( msg_nbits, src_msgs[i] ) for i in xrange(5) ]
    s.sinks = [ TestNetSink( msg_nbits, sink_msgs[i] ) for i in xrange(5) ]

    s.router = cls( side, nmessages, payload_nbits )

    s.connect( s.router.router_id, side/2*side+side/2 )

    for i in xrange(5):
      s.connect( s.srcs[i].out, s.router.in_[i] )
      s.connect( s.sinks[i].in_, s.router.out[i] )

  def done( s ):
    return all( [ x.done for x in s.srcs ] ) and all( [ x.done for x in s.sinks ] )

  def line_trace( s ):
    return s.router.line_trace()

NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3
TERM  = 4
direction_str = ["NORTH","EAST","SOUTH","WEST","TERM"]

def gen_msgs( side, nmessages, payload_nbits ):
  xy_nbits   = clog2( side )
  dest_nbits = xy_nbits * 2
  msg_nbits  = dest_nbits * 2 + clog2(nmessages) + payload_nbits

  src_msgs  = [ [], [], [], [], [] ]
  sink_msgs = [ [], [], [], [], [] ]

  id_x = side/2
  id_y = side/2

  for i in xrange(10):
    payload = random.randint(2, 2**payload_nbits-1)

    dest_x = random.randint( 0, side-1 )
    dest_y = random.randint( 0, side-1 )

    if   dest_x < id_x:
      src_y = id_y
      src_x = random.randint( id_x, side-1 )

      inport  = TERM if src_x == id_x else EAST
      outport = WEST

    elif dest_x > id_x:
      src_y = id_y
      src_x = random.randint( 0, id_x )

      inport  = TERM if src_x == id_x else WEST
      outport = EAST

    else: # dest_x == id_x
      src_x = random.randint( 0, side-1 )

      if dest_y < id_y:
        src_y = random.randint( id_y, side-1 )

        outport = SOUTH
        if src_y == id_y:
          if   src_x < id_x: inport = WEST
          elif src_x > id_x: inport = EAST
        else:
          inport = NORTH

      elif dest_y > id_y:
        src_y = random.randint( 0, id_y )

        outport = NORTH
        if src_y == id_y:
          if   src_x < id_x: inport = WEST
          elif src_x > id_x: inport = EAST
        else:
          inport = SOUTH

      else: # dest_y == id_y
        src_y = random.randint( id_y, side-1 )

        if   src_y < id_y:  inport = SOUTH
        elif src_y > id_y:  inport = NORTH
        else:               inport = TERM

        outport = TERM

    z = Bits(msg_nbits,0)
    z[0:xy_nbits]          = dest_x
    z[xy_nbits:dest_nbits] = dest_y

    z[dest_nbits:dest_nbits+xy_nbits]   = src_x
    z[dest_nbits+xy_nbits:dest_nbits*2] = src_y

    z[dest_nbits*2:dest_nbits*2+clog2(nmessages)] = i
    z[msg_nbits-payload_nbits:msg_nbits] = payload

    # print "{}: {},{} -> {},{} pass by current ({},{}), direction in:{} out:{} ".format(
           # z, src_x, src_y, dest_x, dest_y, id_x, id_y, direction_str[inport],direction_str[outport])

    src_msgs [inport].append( z )
    sink_msgs[outport].append( z )

  return src_msgs, sink_msgs

def test_4x4():
  src_msgs, sink_msgs = gen_msgs( 4, 256, 2 )
  run_sim( TestHarness( MeshRouter, 4, 256, 2,
                         src_msgs, sink_msgs ) )

def test_8x8():
  src_msgs, sink_msgs = gen_msgs( 8, 256, 77 )
  run_sim( TestHarness( MeshRouter, 8, 256, 77,
                         src_msgs, sink_msgs ) )
def test_16x16():
  src_msgs, sink_msgs = gen_msgs( 16, 256, 77 )
  run_sim( TestHarness( MeshRouter, 16, 256, 77,
                         src_msgs, sink_msgs ) )

