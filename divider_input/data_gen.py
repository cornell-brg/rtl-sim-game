import random
random.seed(0xdeadbeef)

ninputs = 10009

inp = [ (random.randint(0,3*2**62) | ((107 << random.randint(0,57))<<64)) for _ in xrange(ninputs) ]
oup = [ ((((x & ((1<<64)-1))/(x>>64))<<64) | ((x & ((1<<64)-1))%(x>>64))) for x in inp ]

# Verify
for i in xrange(len(inp)):
  x = inp[i] & ((1<<64)-1)
  y = inp[i] >> 64
  div = x / y
  rem = x % y
  assert div == (oup[i] >> 64)
  assert rem == (oup[i] & ((1<<64)-1))

# dump to python file
with open( "python_input.py", "w") as f:
  f.write("inp = ")
  f.write(str(inp))
  f.write("\n")
  f.write("oup = ")
  f.write(str(oup))
  f.write("\n")

# dump to Verilog file
with open( "verilog_input.v", "w") as f:
  f.write("num_inputs = %d;\n" % len(inp))
  for i in xrange(ninputs):
    f.write( "init( %d, 128'h%s, 128'h%s );\n" % (i, hex(inp[i])[2:], hex(oup[i])[2:]) );

# dump to C++ file
with open( "cpp_input.dat", "w") as f:
  f.write("int num_inputs = %d;\n" % len(inp))

  f.write("int inp[][4] = {\n")
  for i in xrange(ninputs):
    f.write( "{%d,%d,%d,%d}" % ( int( inp[i] & ((1<<32)-1)),
                                 int( (inp[i]>>32) & ((1<<32)-1)),
                                 int( (inp[i]>>64) & ((1<<32)-1)),
                                 int( (inp[i]>>96) & ((1<<32)-1)),
                                 )  )
    if i < ninputs-1:
      f.write( "," )
    f.write("\n")
  f.write("};\n")

  f.write("int oup[][4] = {\n")
  for i in xrange(ninputs):
    f.write( "{%d,%d,%d,%d}" % ( int( oup[i] & ((1<<32)-1)),
                                 int( (oup[i]>>32) & ((1<<32)-1)),
                                 int( (oup[i]>>64) & ((1<<32)-1)),
                                 int( (oup[i]>>96) & ((1<<32)-1)),
                                 )  )
    if i < ninputs-1:
      f.write( "," )
    f.write("\n")
  f.write("};\n")
