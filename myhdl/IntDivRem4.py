from myhdl import *

#-------------------------------------------------------------------------
# Components
#-------------------------------------------------------------------------

def Subtractor( out, in0, in1 ):
  @always_comb
  def comb_logic():
    out.next = in0 - in1
  return instances()

def LeftLogicalShifter( out, in0, in1 ):
  @always_comb
  def comb_logic():
    out.next = in0 << in1
  return instances()

def RightLogicalShifter( out, in0, in1 ):
  @always_comb
  def comb_logic():
    out.next = in0 >> in1
  return instances()

def Reg( clk, out, in_ ):
  @always(clk.posedge)
  def seq_logic():
    out.next = in_
  return instances()

def RegEn( clk, out, in_, en ):
  @always(clk.posedge)
  def seq_logic():
    if en:
      out.next = in_
  return instances()

def RegRst( clk, rst, out, in_, reset_value=0 ):
  @always(clk.posedge)
  def seq_logic():
    if rst:
      out.next = reset_value
    else:
      out.next = in_
  return instances()

def Mux2( out, in0, in1, sel ):
  @always_comb
  def comb_logic():
    if sel == 0:
      out.next = in0
    else:
      out.next = in1
  return instances()

def Mux3( out, in0, in1, in2, sel ):
  @always_comb
  def comb_logic():
    if sel == 0:
      out.next = in0
    elif sel == 1:
      out.next = in1
    else:
      out.next = in2
  return instances()

class IntDivRem4CS:

  def __init__(self):
    self.sub_negative1     = Signal(False)
    self.sub_negative2     = Signal(False)
    self.quotient_mux_sel  = Signal(False)
    self.quotient_reg_en   = Signal(False)
    self.remainder_mux_sel = Signal(modbv(0)[2:])
    self.remainder_reg_en  = Signal(False)
    self.divisor_mux_sel   = Signal(False)

Q_MUX_SEL_0   = 0
Q_MUX_SEL_LSH = 1

R_MUX_SEL_IN    = 0
R_MUX_SEL_SUB1  = 1
R_MUX_SEL_SUB2  = 2

D_MUX_SEL_IN  = 0
D_MUX_SEL_RSH = 1

def IntDivRem4Ctrl( clk, rst, req_val, req_rdy, resp_val, resp_rdy, cs,
                    nbits=64 ):

  import math
  state_nbits = 1+int( math.ceil( math.log( nbits, 2 ) ) )
  state_in_ = Signal( modbv(0)[state_nbits:] )
  state_out = Signal( modbv(0)[state_nbits:] )

  state = RegRst( clk, rst, state_out, state_in_, 0 )

  STATE_IDLE = 0
  STATE_DONE = 1
  STATE_CALC = 1+nbits/2

  @always_comb
  def state_transitions():

    if   state_out == STATE_IDLE:
      if req_val and req_rdy:
        state_in_.next = STATE_CALC

    elif state_out == STATE_DONE:
      if resp_val and resp_rdy:
        state_in_.next = STATE_IDLE

    else:
      state_in_.next = state_out - 1

  @always_comb
  def state_outputs():

    if   state_out == STATE_IDLE:
      req_rdy.next = 1
      resp_val.next = 0

      cs.remainder_mux_sel.next = R_MUX_SEL_IN
      cs.remainder_reg_en.next  = 1

      cs.quotient_mux_sel.next = Q_MUX_SEL_0
      cs.quotient_reg_en.next  = 1

      cs.divisor_mux_sel.next  = D_MUX_SEL_IN

    elif state_out == STATE_DONE:
      req_rdy.next  = 0
      resp_val.next = 1

      cs.quotient_mux_sel.next = Q_MUX_SEL_0
      cs.quotient_reg_en.next  = 0

      cs.remainder_mux_sel.next = R_MUX_SEL_IN
      cs.remainder_reg_en.next  = 0

      cs.divisor_mux_sel.next   = D_MUX_SEL_IN

    else: # calculating
      req_rdy.next     = 0
      resp_val.next    = 0

      cs.remainder_reg_en.next = not (cs.sub_negative1 & cs.sub_negative2)
      if cs.sub_negative2:
        cs.remainder_mux_sel.next = R_MUX_SEL_SUB1
      else:
        cs.remainder_mux_sel.next = R_MUX_SEL_SUB2

      cs.quotient_reg_en.next   = 1
      cs.quotient_mux_sel.next  = Q_MUX_SEL_LSH

      cs.divisor_mux_sel.next   = D_MUX_SEL_RSH

  return instances()

def IntDivRem4Dpath( clk, rst, req_msg, resp_msg, cs,
                     nbits=64, line_trace=False ):

  remainder_reg_out = Signal( modbv(0)[nbits*2:] )
  remainder_mux_out = Signal( modbv(0)[nbits*2:] )
  divisor_mux_out   = Signal( modbv(0)[nbits*2:] )
  divisor_reg_out   = Signal( modbv(0)[nbits*2:] )
  quotient_mux_out  = Signal( modbv(0)[nbits:] )

  quotient_reg_out  = Signal( modbv(0)[nbits:] )
  quotient_lsh_out  = Signal( modbv(0)[nbits:] )
  sub1_out          = Signal( modbv(0)[nbits*2:] )
  divisor_rsh1_out  = Signal( modbv(0)[nbits*2:] )
  remainder_mid_mux_out = Signal( modbv(0)[nbits*2:] )
  sub2_out          = Signal( modbv(0)[nbits*2:] )
  divisor_rsh2_out  = Signal( modbv(0)[nbits*2:] )

  remainder_mux_in_in = Signal( modbv(0)[nbits*2:] )

  @always_comb
  def comb_remainder_mux_in_in():
    remainder_mux_in_in.next = req_msg[nbits:0]

  remainder_mux = Mux3( remainder_mux_out,
                        remainder_mux_in_in, # R_MUX_SEL_IN    = 0
                        sub1_out, # R_MUX_SEL_SUB1  = 1
                        sub2_out, # R_MUX_SEL_SUB2  = 2
                        cs.remainder_mux_sel )

  remainder_reg = RegEn( clk,
                         remainder_reg_out,
                         remainder_mux_out,
                         cs.remainder_reg_en )

  divisor_mux_in_in = Signal( modbv(0)[nbits*2:] )
  @always_comb
  def comb_divisor_mux_in_in():
    divisor_mux_in_in.next = concat(req_msg[nbits*2:nbits], modbv(0)[nbits-1:])
    

  divisor_mux = Mux2( divisor_mux_out,
                        divisor_mux_in_in, # D_MUX_SEL_IN = 0
                        divisor_rsh2_out, # D_MUX_SEL_RSH = 1
                        cs.divisor_mux_sel )

  divisor_reg = Reg( clk,
                     divisor_reg_out,
                     divisor_mux_out)

  quotient_mux_in_lsh = Signal( modbv(0)[nbits:] )

  @always_comb
  def comb_quotient_mux_in_lsh():
    quotient_mux_in_lsh.next = quotient_lsh_out + \
      concat( not cs.sub_negative1, not cs.sub_negative2 )

  quotient_mux = Mux2( quotient_mux_out,
                        0, # Q_MUX_SEL_0 = 0
                        quotient_mux_in_lsh, # Q_MUX_SEL_LSH = 1
                        cs.quotient_mux_sel )

  quotient_reg = RegEn( clk,
                        quotient_reg_out,
                        quotient_mux_out,
                        cs.quotient_reg_en )

  quotient_lsh = LeftLogicalShifter( quotient_lsh_out,
                                     quotient_reg_out, 2 )

  sub1 = Subtractor(  sub1_out,
                      remainder_reg_out, divisor_reg_out )

  @always_comb
  def comb_sub_negative1():
    cs.sub_negative1.next = sub1_out[nbits*2-1]

  divisor_rsh1 = RightLogicalShifter( divisor_rsh1_out,
                                      divisor_reg_out, 1 )

  remainder_mid_mux = Mux2( remainder_mid_mux_out,
                            sub1_out, remainder_reg_out,
                            cs.sub_negative1 )

  sub2 = Subtractor(  sub2_out,
                      remainder_mid_mux_out, divisor_rsh1_out )

  @always_comb
  def comb_sub_negative2():
    cs.sub_negative2.next = sub2_out[nbits*2-1]

  divisor_rsh2 = RightLogicalShifter( divisor_rsh2_out,
                                      divisor_rsh1_out, 1 )

  @always_comb
  def comb_resp_msg():
    resp_msg.next = concat( quotient_reg_out, remainder_reg_out[nbits:0] )

  return instances()

def IntDivRem4(clk, rst,
                  req_val, req_rdy, req_msg, resp_val, resp_rdy, resp_msg,
                  nbits=64):

  cs    = IntDivRem4CS()
  ctrl  = IntDivRem4Ctrl( clk, rst, req_val, req_rdy, resp_val, resp_rdy, cs, nbits )
  dpath = IntDivRem4Dpath( clk, rst, req_msg, resp_msg, cs, nbits )

  return instances()
