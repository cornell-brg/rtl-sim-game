#=======================================================================
# MeshRouterRTL.py
#=======================================================================

from pymtl            import *
from pclib.rtl        import Crossbar, RoundRobinArbiterEn, NormalQueue
from pclib.ifcs       import InValRdyBundle, OutValRdyBundle

#=======================================================================
# CtrlDpathIfc
#=======================================================================
class CtrlDpathIfc( PortBundle ):
  def __init__( s, side ):

    # Control signals (ctrl -> dpath)
    s.in_dest  = InPort ( clog2(side)*2 )
    s.in_val   = InPort ( 1 )
    s.in_rdy   = OutPort( 1 )
    s.xbar_sel = OutPort( 3 )
    s.out_val  = OutPort( 1 )
    s.out_rdy  = InPort ( 1 )

CtrlIfc, DpathIfc = create_PortBundles( CtrlDpathIfc )

#=======================================================================
# MeshRouterRTL
#=======================================================================
class MeshRouter( Model ):

  def __init__( s, side, nmessages, payload_nbits ):
    # Assume the mesh network is side*side where side is 2^k

    assert side > 0 and not (side & (side - 1))
    xy_nbits   = clog2(side)
    dest_nbits = clog2(side) * 2

    msg_nbits = dest_nbits * 2 + clog2(nmessages) + payload_nbits

    #-------------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------------

    s.router_id = InPort( dest_nbits )

    s.id_x = Wire( xy_nbits )
    s.id_y = Wire( xy_nbits )
    s.connect( s.id_x, s.router_id[0:xy_nbits] )
    s.connect( s.id_y, s.router_id[xy_nbits:dest_nbits] )

    s.in_ = [ InValRdyBundle( msg_nbits ) for x in xrange(5) ]
    s.out = [ OutValRdyBundle( msg_nbits ) for x in xrange(5) ]

    s.dpath = MeshRouterDpath( side, nmessages, payload_nbits )
    s.ctrl  = MeshRouterCtrl ( side )

    s.connect( s.dpath.id_x, s.id_x )
    s.connect( s.dpath.id_y, s.id_y )
    s.connect( s.ctrl.id_x, s.id_x )
    s.connect( s.ctrl.id_y, s.id_y )

    for i in xrange( 5 ):
      s.connect( s.in_[i],      s.dpath.in_[i] )
      s.connect( s.out[i],      s.dpath.out[i] )
      s.connect( s.ctrl.c2d[i], s.dpath.c2d[i] )

  def line_trace( s ):
    return '|'.join( ['{},{}'.format( s.in_[ i ].to_str( s.in_[i].msg ),
                                      s.out[ i ].to_str( s.out[i].msg ) )
                      for i in xrange(5) ] )

#-----------------------------------------------------------------------
# MeshRouterRTLDpath
#-----------------------------------------------------------------------
class MeshRouterDpath( Model ):

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

    s.id_x = InPort( xy_nbits )
    s.id_y = InPort( xy_nbits )

    s.in_ = [ InValRdyBundle( msg_nbits ) for x in xrange(5) ]
    s.out = [ OutValRdyBundle( msg_nbits ) for x in xrange(5) ]
    s.c2d = [ DpathIfc( side ) for x in xrange(5) ]

    # Input Queues
    # 5 ports --> 4 additional entries
    s.q_in = [ NormalQueue( 4, msg_nbits ) for x in range( 5 ) ]

    # Crossbar
    s.xbar = Crossbar( 5, msg_nbits )

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
class MeshRouterCtrl( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, side ):
    MASK_NORTH = 0b00001
    MASK_EAST  = 0b00010
    MASK_SOUTH = 0b00100
    MASK_WEST  = 0b01000
    MASK_TERM  = 0b10000

    NORTH = 0
    EAST  = 1
    SOUTH = 2
    WEST  = 3
    TERM  = 4

    xy_nbits   = clog2( side )
    dest_nbits = xy_nbits * 2

    s.c2d = [ CtrlIfc( side ) for x in xrange(5) ]

    s.id_x = InPort( xy_nbits )
    s.id_y = InPort( xy_nbits )

    s.arbiters = [ RoundRobinArbiterEn( 5 ) for x in xrange(5) ]

    for i in xrange( 5 ):
      s.connect( s.arbiters[i].en, s.c2d[i].out_rdy )

    @s.combinational
    def arbiter_req():

      s.arbiters[ NORTH ].reqs.value = 0
      s.arbiters[ SOUTH ].reqs.value = 0
      s.arbiters[ EAST  ].reqs.value = 0
      s.arbiters[ WEST  ].reqs.value = 0
      s.arbiters[ TERM  ].reqs.value = 0

      # enumerate the input ports
      for i in xrange( 5 ):
        dest_x = s.c2d[i].in_dest[0:xy_nbits]
        dest_y = s.c2d[i].in_dest[xy_nbits:dest_nbits]

        # XY routing

        if   dest_x < s.id_x: s.arbiters[ WEST  ].reqs[i].value = s.c2d[i].in_val
        elif dest_x > s.id_x: s.arbiters[ EAST  ].reqs[i].value = s.c2d[i].in_val
        elif dest_y < s.id_y: s.arbiters[ SOUTH ].reqs[i].value = s.c2d[i].in_val
        elif dest_y > s.id_y: s.arbiters[ NORTH ].reqs[i].value = s.c2d[i].in_val
        else:                 s.arbiters[ TERM  ].reqs[i].value = s.c2d[i].in_val

    @s.combinational
    def set_ctrl_signals():

      for i in range( 5 ):
        s.c2d[i].out_val.value = s.arbiters[i].grants != 0

        s.c2d[i].in_rdy.value = any(
           ( s.arbiters[0].grants[i] & s.c2d[0].out_rdy,
             s.arbiters[1].grants[i] & s.c2d[1].out_rdy,
             s.arbiters[2].grants[i] & s.c2d[2].out_rdy,
             s.arbiters[3].grants[i] & s.c2d[3].out_rdy,
             s.arbiters[4].grants[i] & s.c2d[4].out_rdy )
        )

        # Set xbar select

        if   s.arbiters[i].grants == MASK_NORTH: s.c2d[i].xbar_sel.value = NORTH
        elif s.arbiters[i].grants == MASK_EAST : s.c2d[i].xbar_sel.value = EAST
        elif s.arbiters[i].grants == MASK_SOUTH: s.c2d[i].xbar_sel.value = SOUTH
        elif s.arbiters[i].grants == MASK_WEST : s.c2d[i].xbar_sel.value = WEST
        elif s.arbiters[i].grants == MASK_TERM : s.c2d[i].xbar_sel.value = TERM
        else                                   : s.c2d[i].xbar_sel.value = 0
