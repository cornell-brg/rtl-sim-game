import random
random.seed(0xdeadbeef)

ninputs = 10009

# generate input msgs

NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3
TERM  = 4
direction_str = ["NORTH","EAST","SOUTH","WEST","TERM"]

side = 8

id_x = id_y   = side/2
xy_nbits      = 3
dest_nbits    = xy_nbits * 2
num_messages  = 256
payload_nbits = 77
msg_nbits     = dest_nbits * 2 + 8 + payload_nbits

src_msgs  = [ [], [], [], [], [] ]
sink_msgs = [ [], [], [], [], [] ]

for i in xrange(100000):
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

  z = 0
  # z[0:xy_nbits]          = dest_x
  # z[xy_nbits:dest_nbits] = dest_y
  # z[dest_nbits:dest_nbits+xy_nbits]   = src_x
  # z[dest_nbits+xy_nbits:dest_nbits*2] = src_y
  # z[dest_nbits*2:dest_nbits*2+clog2(num_messages)] = i % 256
  # z[msg_nbits-payload_nbits:msg_nbits] = payload

  z |= dest_x 
  z |= dest_y << xy_nbits
  z |= src_x << dest_nbits
  z |= src_y << (dest_nbits+xy_nbits)
  z |= (i%256) << (dest_nbits*2)
  z |= payload << (msg_nbits-payload_nbits)

  # print "{}: {},{} -> {},{} pass by current ({},{}), direction in:{} out:{} ".format(
         # z, src_x, src_y, dest_x, dest_y, id_x, id_y, direction_str[inport],direction_str[outport])

  if len(src_msgs[inport]) < 1024:
    src_msgs [inport].append( z )
    sink_msgs[outport].append( z )

for x in src_msgs:
  print len(x)
print "---"
for x in sink_msgs:
  print len(x)


# dump to python file
with open( "python_input.py", "w") as f:
  f.write("side = 8\n")
  f.write("id_x = id_y   = side/2\n")
  f.write("xy_nbits      = 3\n")
  f.write("dest_nbits    = xy_nbits * 2\n")
  f.write("num_messages  = 256\n")
  f.write("payload_nbits = 77\n")
  f.write("msg_nbits     = dest_nbits * 2 + 8 + payload_nbits\n")
  f.write("msgcount      = 1024\n\n")

  f.write("inp = [")
  for i in xrange(5):
    f.write("[")
    for j in src_msgs[i]:
      x = str(j)
      if x[-1] == 'L':
        x = x[:-1]
      f.write(x+",\n")
    f.write("],\n")
  f.write("]\n")
