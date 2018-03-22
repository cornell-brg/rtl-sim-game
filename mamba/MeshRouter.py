#=======================================================================
# MeshRouterRTL.py
#=======================================================================

from pymtl            import *
from pclib.rtl        import Crossbar, RoundRobinArbiterEn, NormalQueueRTL
from pclib.ifcs       import InValRdyIfc, OutValRdyIfc

#=======================================================================
# CtrlDpathIfc
#=======================================================================
class CtrlDpathIfc( Interface ):
  def __init__( s, side ):

    # Control signals (ctrl -> dpath)
    s.in_dest  = InVPort ( mk_bits( clog2(side)*2 ) )
    s.in_val   = InVPort ( Bits1 )
    s.in_rdy   = OutVPort( Bits1 )
    s.xbar_sel = OutVPort( Bits3 )
    s.out_val  = OutVPort( Bits1 )
    s.out_rdy  = InVPort ( Bits1 )

#=======================================================================
# MeshRouterRTL
#=======================================================================
class MeshRouter( RTLComponent ):

  def __init__( s, side, nmessages, payload_nbits ):
    # Assume the mesh network is side*side where side is 2^k

    assert side > 0 and not (side & (side - 1))
    xy_nbits   = clog2(side)
    dest_nbits = clog2(side) * 2

    msg_nbits = dest_nbits * 2 + clog2(nmessages) + payload_nbits

    #-------------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------------

    s.router_id = InVPort( mk_bits(dest_nbits) )

    s.id_x = Wire( mk_bits(xy_nbits) )
    s.id_y = Wire( mk_bits(xy_nbits) )
    s.connect( s.id_x, s.router_id[0:xy_nbits] )
    s.connect( s.id_y, s.router_id[xy_nbits:dest_nbits] )

    s.in_ = [ InValRdyIfc( mk_bits(msg_nbits) ) for x in xrange(5) ]
    s.out = [ OutValRdyIfc( mk_bits(msg_nbits) ) for x in xrange(5) ]

    s.dpath = MeshRouterDpath( side, nmessages, payload_nbits )(
      id_x = s.id_x,
      id_y = s.id_y,
    )
    s.ctrl  = MeshRouterCtrl ( side )(
      id_x = s.id_x,
      id_y = s.id_y,
    )

    for i in xrange( 5 ):
      s.connect( s.in_[i],      s.dpath.in_[i] )
      s.connect( s.out[i],      s.dpath.out[i] )
      s.connect( s.ctrl.c2d[i], s.dpath.c2d[i] )

  def line_trace( s ):
    return '|'.join( ['{},{}'.format( s.in_[ i ].line_trace(),
                                      s.out[ i ].line_trace() )
                      for i in xrange(5) ] )

#-----------------------------------------------------------------------
# MeshRouterRTLDpath
#-----------------------------------------------------------------------
class MeshRouterDpath( RTLComponent ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, side, nmessages, payload_nbits ):
    xy_nbits   = clog2(side)
    dest_nbits = clog2(side) * 2
    msg_nbits  = dest_nbits * 2 + clog2(nmessages) + payload_nbits

    #-------------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------------

    s.id_x = InVPort( mk_bits(xy_nbits) )
    s.id_y = InVPort( mk_bits(xy_nbits) )

    s.in_ = [ InValRdyIfc( mk_bits(msg_nbits) ) for x in xrange(5) ]
    s.out = [ OutValRdyIfc( mk_bits(msg_nbits) ) for x in xrange(5) ]
    s.c2d = [ CtrlDpathIfc( side ).inverse() for x in xrange(5) ]

    # Input Queues
    # 5 ports --> 4 additional entries
    s.q_in = [ NormalQueueRTL( 4, mk_bits(msg_nbits) ) for x in range( 5 ) ]

    # Crossbar
    s.xbar = Crossbar( 5, mk_bits(msg_nbits) )

    for i in xrange( 5 ):
      s.connect( s.q_in[i].enq,      s.in_[i]            )

      s.connect( s.q_in[i].deq.msg[0:dest_nbits], s.c2d[i].in_dest  )
      s.connect( s.q_in[i].deq.val,  s.c2d[i].in_val  )
      s.connect( s.q_in[i].deq.rdy,  s.c2d[i].in_rdy  )

      s.connect( s.q_in[i].deq.msg,  s.xbar.in_[i]       )
      s.connect( s.c2d [i].xbar_sel, s.xbar.sel[i]       )

      s.connect( s.xbar.out[i],      s.out[i].msg        )
      s.connect( s.c2d[i].out_val,   s.out[i].val        )
      s.connect( s.c2d[i].out_rdy,   s.out[i].rdy        )

#-----------------------------------------------------------------------
# MeshRouterCtrl
#-----------------------------------------------------------------------
class MeshRouterCtrl( RTLComponent ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, side ):
    MASK_NORTH = Bits5( 0b00001 )
    MASK_EAST  = Bits5( 0b00010 )
    MASK_SOUTH = Bits5( 0b00100 )
    MASK_WEST  = Bits5( 0b01000 )
    MASK_TERM  = Bits5( 0b10000 )

    NORTH = Bits3( 0 )
    EAST  = Bits3( 1 )
    SOUTH = Bits3( 2 )
    WEST  = Bits3( 3 )
    TERM  = Bits3( 4 )

    xy_nbits   = clog2( side )
    dest_nbits = xy_nbits * 2

    s.c2d = [ CtrlDpathIfc( side ) for x in xrange(5) ]

    s.id_x = InVPort( mk_bits(xy_nbits) )
    s.id_y = InVPort( mk_bits(xy_nbits) )

    s.arbiters = [ RoundRobinArbiterEn( 5 ) for x in xrange(5) ]

    for i in xrange( 5 ):
      s.connect( s.arbiters[i].en, s.c2d[i].out_rdy )

    @s.update
    def arbiter_req():

      s.arbiters[ NORTH ].reqs = Bits5( 0 )
      s.arbiters[ SOUTH ].reqs = Bits5( 0 )
      s.arbiters[ EAST  ].reqs = Bits5( 0 )
      s.arbiters[ WEST  ].reqs = Bits5( 0 )
      s.arbiters[ TERM  ].reqs = Bits5( 0 )

      # enumerate the input ports
      for i in xrange( 5 ):
        dest_x = s.c2d[i].in_dest[0:xy_nbits]
        dest_y = s.c2d[i].in_dest[xy_nbits:dest_nbits]

        # XY routing

        if   dest_x < s.id_x: s.arbiters[ WEST  ].reqs[i] = s.c2d[i].in_val
        elif dest_x > s.id_x: s.arbiters[ EAST  ].reqs[i] = s.c2d[i].in_val
        elif dest_y < s.id_y: s.arbiters[ SOUTH ].reqs[i] = s.c2d[i].in_val
        elif dest_y > s.id_y: s.arbiters[ NORTH ].reqs[i] = s.c2d[i].in_val
        else:                 s.arbiters[ TERM  ].reqs[i] = s.c2d[i].in_val

    @s.update
    def set_ctrl_signals():

      for i in range( 5 ):
        s.c2d[i].out_val = s.arbiters[i].grants != 0

        s.c2d[i].in_rdy = any(
           ( s.arbiters[0].grants[i] & s.c2d[0].out_rdy,
             s.arbiters[1].grants[i] & s.c2d[1].out_rdy,
             s.arbiters[2].grants[i] & s.c2d[2].out_rdy,
             s.arbiters[3].grants[i] & s.c2d[3].out_rdy,
             s.arbiters[4].grants[i] & s.c2d[4].out_rdy )
        )

        # Set xbar select

        if   s.arbiters[i].grants == MASK_NORTH: s.c2d[i].xbar_sel = Bits3( NORTH )
        elif s.arbiters[i].grants == MASK_EAST : s.c2d[i].xbar_sel = Bits3( EAST  )
        elif s.arbiters[i].grants == MASK_SOUTH: s.c2d[i].xbar_sel = Bits3( SOUTH )
        elif s.arbiters[i].grants == MASK_WEST : s.c2d[i].xbar_sel = Bits3( WEST  )
        elif s.arbiters[i].grants == MASK_TERM : s.c2d[i].xbar_sel = Bits3( TERM  )
        else                                   : s.c2d[i].xbar_sel = Bits3( 0 )
