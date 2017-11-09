from migen import *

class Mux3(Module):
  def __init__( self, nbits ):
    self.sel = Signal(nbits)
    self.in0 = Signal(nbits)
    self.in1 = Signal(nbits)
    self.in2 = Signal(nbits)
    self.out = Signal(nbits)

    self.comb += [
      Case( self.sel, {
        0: self.out.eq( self.in0 ),
        1: self.out.eq( self.in1 ),
        "default": self.out.eq( self.in2 ),
      })
    ]

class Mux2(Module):
  def __init__( self, nbits ):
    self.sel = Signal(nbits)
    self.in0 = Signal(nbits)
    self.in1 = Signal(nbits)
    self.out = Signal(nbits)

    self.comb += [
      Case( self.sel, {
        0: self.out.eq( self.in0 ),
        "default": self.out.eq( self.in1 ),
      })
    ]

class Subtractor(Module):
  def __init__( self, nbits ):
    self.in0 = Signal(nbits)
    self.in1 = Signal(nbits)
    self.out = Signal(nbits)

    self.comb += [
      self.out.eq( self.in0 - self.in1 )
    ]

class LeftLogicalShifter(Module):
  def __init__( self, nbits, shamt ):
    self.in_ = Signal(nbits)
    self.out = Signal(nbits)

    self.comb += [
      self.out.eq( self.in_ << shamt )
    ]

class RightLogicalShifter(Module):
  def __init__( self, nbits, shamt ):
    self.in_ = Signal(nbits)
    self.out = Signal(nbits)

    self.comb += [
      self.out.eq( self.in_ >> shamt )
    ]

class Reg(Module):
  def __init__( self, nbits ):
    self.in_ = Signal(nbits)
    self.out = Signal(nbits)

    self.sync += [
      self.out.eq(self.in_),
    ]

class RegEn(Module):
  def __init__( self, nbits ):
    self.in_ = Signal(nbits)
    self.en  = Signal()
    self.out = Signal(nbits)

    self.sync += [
      If( self.en, self.out.eq(self.in_) )
    ]

@ResetInserter()
class RegRst(Module):
  def __init__( self, nbits ):
    self.in_ = Signal(nbits)
    self.out = Signal(nbits)

    self.sync += [
      self.out.eq(self.in_),
    ]

Q_MUX_SEL_0   = 0
Q_MUX_SEL_LSH = 1

R_MUX_SEL_IN    = 0
R_MUX_SEL_SUB1  = 1
R_MUX_SEL_SUB2  = 2

D_MUX_SEL_IN  = 0
D_MUX_SEL_RSH = 1

@ResetInserter()
class IntDivRem4Ctrl(Module):

  def __init__(self, nbits):

    self.req_val  = Signal()
    self.req_rdy  = Signal()
    self.resp_val = Signal()
    self.resp_rdy = Signal()
    self.sub_negative1 = Signal()
    self.sub_negative2 = Signal()
    self.quotient_mux_sel  = Signal()
    self.quotient_reg_en   = Signal()
    self.remainder_mux_sel = Signal(2)
    self.remainder_reg_en  = Signal()
    self.divisor_mux_sel   = Signal()

    import math
    state_nbits = 1+int( math.ceil( math.log( nbits, 2 ) ) )

    STATE_IDLE = 0
    STATE_DONE = 1
    STATE_CALC = 1+nbits/2

    self.counter = Reg(nbits)
    myfsm = FSM(reset_state="STATE_IDLE")

    self.submodules += myfsm, self.counter

    myfsm.act( "STATE_IDLE",

      # State transition

      If(self.req_val & self.req_rdy,
        NextState("STATE_CALC")
      ),

      # State outputs

      If(self.req_val & self.req_rdy,
        self.counter.in_.eq( (nbits>>1)-1 ),
      ),
      self.req_rdy.eq(1),
      self.resp_val.eq(0),
      self.remainder_mux_sel.eq(R_MUX_SEL_IN),
      self.remainder_reg_en.eq(1),
      self.quotient_mux_sel.eq(Q_MUX_SEL_0),
      self.quotient_reg_en.eq(1),
      self.divisor_mux_sel.eq(D_MUX_SEL_IN),
    )

    myfsm.act( "STATE_DONE",

      # State transition

      If(self.resp_val & self.resp_rdy,
        NextState("STATE_IDLE"),
      ),

      # State outputs

      self.req_rdy.eq(0),
      self.resp_val.eq(1),
      self.remainder_mux_sel.eq(R_MUX_SEL_IN),
      self.remainder_reg_en.eq(0),
      self.quotient_mux_sel.eq(Q_MUX_SEL_0),
      self.quotient_reg_en.eq(0),
      self.divisor_mux_sel.eq(D_MUX_SEL_IN),
    )

    myfsm.act( "STATE_CALC",

      # State transition

      If(self.counter.out == 0,
        NextState("STATE_DONE"),
      ),

      # State outputs

      self.counter.in_.eq( self.counter.out-1 ),

      self.req_rdy.eq(0),
      self.resp_val.eq(0),
      If(self.sub_negative2,
        self.remainder_mux_sel.eq(R_MUX_SEL_SUB1),
      ).Else(
        self.remainder_mux_sel.eq(R_MUX_SEL_SUB2),
      ),
      self.remainder_reg_en.eq( ~(self.sub_negative1 & self.sub_negative2) ),
      self.quotient_mux_sel.eq(Q_MUX_SEL_LSH),
      self.quotient_reg_en.eq(1),
      self.divisor_mux_sel.eq(D_MUX_SEL_RSH),
    )

class IntDivRem4Dpath(Module):

  def __init__(self, nbits):
    self.req_msg  = Signal(nbits*2)
    self.resp_msg = Signal(nbits*2)

    self.sub_negative1 = Signal()
    self.sub_negative2 = Signal()
    self.quotient_mux_sel  = Signal()
    self.quotient_reg_en   = Signal()
    self.remainder_mux_sel = Signal(2)
    self.remainder_reg_en  = Signal()
    self.divisor_mux_sel   = Signal()

    self.remainder_mux     = Mux3(nbits*2)
    self.remainder_reg     = RegEn(nbits*2)
    self.divisor_mux       = Mux2(nbits*2)
    self.divisor_reg       = Reg(nbits*2)
    self.quotient_mux      = Mux2(nbits)
    self.quotient_reg      = RegEn(nbits)
    self.quotient_lsh      = LeftLogicalShifter(nbits, 2)
    self.sub1              = Subtractor(nbits*2)
    self.divisor_rsh1      = RightLogicalShifter(nbits*2, 1)
    self.remainder_mid_mux = Mux2(nbits*2)
    self.sub2              = Subtractor(nbits*2)
    self.divisor_rsh2      = RightLogicalShifter(nbits*2, 1)

    self.submodules += self.remainder_mux, self.remainder_reg, \
                       self.divisor_mux, self.divisor_reg, \
                       self.quotient_mux, self.quotient_reg, self.quotient_lsh, \
                       self.sub1, self.divisor_rsh1, self.remainder_mid_mux, \
                       self.sub2, self.divisor_rsh2

    self.comb += [

      # remainder_mux
      self.remainder_mux.sel.eq( self.remainder_mux_sel ),
      self.remainder_mux.in0.eq( self.req_msg[:nbits] ),
      self.remainder_mux.in1.eq( self.sub1.out ),
      self.remainder_mux.in2.eq( self.sub2.out ),

      # remainder_reg
      self.remainder_reg.in_.eq( self.remainder_mux.out ),
      self.remainder_reg.en.eq ( self.remainder_reg_en ),

      # divisor_mux
      self.divisor_mux.sel.eq( self.divisor_mux_sel ),
      self.divisor_mux.in0.eq( Cat(Constant(0, (nbits-1, False) ), self.req_msg[nbits:]) ),
      self.divisor_mux.in1.eq( self.divisor_rsh2.out ),

      # divisor_reg
      self.divisor_reg.in_.eq( self.divisor_mux.out ),

      # quotient_mux
      self.quotient_mux.sel.eq( self.quotient_mux_sel ),
      self.quotient_mux.in0.eq( 0 ),
      self.quotient_mux.in1.eq( self.quotient_lsh.out +
                            Cat(~self.sub_negative2,
                                ~self.sub_negative1) ),

      # quotient_reg
      self.quotient_reg.in_.eq( self.quotient_mux.out ),
      self.quotient_reg.en.eq(  self.quotient_reg_en ),

      # quotient_lsh
      self.quotient_lsh.in_.eq( self.quotient_reg.out ),

      # sub1
      self.sub1.in0.eq( self.remainder_reg.out ),
      self.sub1.in1.eq( self.divisor_reg.out ),
      self.sub_negative1.eq( self.sub1.out[nbits*2-1] ),

      # divisor_rsh1
      self.divisor_rsh1.in_.eq( self.divisor_reg.out ),

      # remainder_mid_mux
      self.remainder_mid_mux.sel.eq( self.sub_negative1 ),
      self.remainder_mid_mux.in0.eq( self.sub1.out ),
      self.remainder_mid_mux.in1.eq( self.remainder_reg.out ),

      # sub2
      self.sub2.in0.eq( self.remainder_mid_mux.out ),
      self.sub2.in1.eq( self.divisor_rsh1.out ),
      self.sub_negative2.eq( self.sub2.out[nbits*2-1] ),

      # divisor_rsh2
      self.divisor_rsh2.in_.eq( self.divisor_rsh1.out ),

      # resp_msg
      self.resp_msg.eq( Cat( self.remainder_reg.out[:nbits], self.quotient_reg.out ) ),
    ]

@ResetInserter()
class IntDivRem4(Module):

  def __init__( self, nbits=64 ):

    self.req_val = Signal()
    self.req_rdy = Signal()
    self.req_msg = Signal(nbits*2)

    self.resp_val = Signal()
    self.resp_rdy = Signal()
    self.resp_msg = Signal(nbits*2)

    self.ctrl  = IntDivRem4Ctrl( nbits )
    self.dpath = IntDivRem4Dpath( nbits )

    self.submodules += self.ctrl, self.dpath
    self.ios = {
      self.req_val, self.req_rdy, self.req_msg,
      self.resp_val, self.resp_rdy, self.resp_msg,
    }

    self.comb += [
      self.ctrl.req_val .eq( self.req_val ),
      self.req_rdy .eq( self.ctrl.req_rdy ),
      self.resp_val.eq( self.ctrl.resp_val ),
      self.ctrl.resp_rdy.eq( self.resp_rdy ),

      self.dpath.req_msg.eq( self.req_msg ),
      self.resp_msg.eq( self.dpath.resp_msg ),

      self.ctrl.sub_negative1.eq( self.dpath.sub_negative1 ),
      self.ctrl.sub_negative2.eq( self.dpath.sub_negative2 ),

      self.dpath.quotient_mux_sel .eq( self.ctrl.quotient_mux_sel  ),
      self.dpath.quotient_reg_en  .eq( self.ctrl.quotient_reg_en   ),
      self.dpath.remainder_mux_sel.eq( self.ctrl.remainder_mux_sel ),
      self.dpath.remainder_reg_en .eq( self.ctrl.remainder_reg_en  ),
      self.dpath.divisor_mux_sel  .eq( self.ctrl.divisor_mux_sel   ),
    ]


if __name__ == "__main__":
  idiv = IntDivRem4(64)
  run_simulation( idiv, tb(idiv) )
