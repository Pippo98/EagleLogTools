import os
import can
import time

home  = os.path.expanduser("~")
fname = home+'/.odometer'

bustype = 'socketcan_native'
try:
    channel = 'can0'
    bus = can.interface.Bus(channel=channel, bustype=bustype)
except:
    channel = 'vcan0'
    bus = can.interface.Bus(channel=channel, bustype=bustype)

bus.set_filters([
  {"can_id":0xD1, "can_mask":0b11111111101, "extended":False},
])
msg = can.Message(arbitration_id=0x0, data=[], is_extended_id=False)

status = open(fname, 'a+')

runStartTime = None
runEndTime   = None

lastStatus = ""
status.seek(0,0)                    # move to file start
lines = status.readlines()


km = 0
rotations = 0
if len(lines) > 1:

  lastStatus = lines[-1]

  s = lastStatus.split(";")
  runStartTime  = float(s[0])
  runEndTime    = float(s[1])
  rotations     = int(s[2])
  km            = float(s[3])

  print(rotations)
  print(0xFFFFFF)

  msg.arbitration_id = 0xD2
  msg.data = rotations.to_bytes(3, "big")
  msg.dlc = 3
  bus.send(msg)
  
  print("-"*10)
  print("start:\r\n\t{}\nend:\r\n\t{}\nrotations:\r\n\t{}\nKm:\r\n\t{}".format(runStartTime, runEndTime, rotations, km))
  print("-"*10)

prev_rotations = rotations
km = 0
rotations = 0
message = None
while True:
  try:
    message = bus.recv()
  except KeyboardInterrupt:
    break
  print(" "*100, end="\r")

  msg_id = message.arbitration_id
  
  if msg_id == 0xD1:
    if message.dlc < 6:
      continue
    rotations = int.from_bytes(message.data[:3], "big")
    km = int.from_bytes(message.data[3:], "big")
    km = float(km) / 1000

    if rotations < prev_rotations:
      msg.arbitration_id = 0xD2
      msg.data = prev_rotations.to_bytes(3, "big")
      msg.dlc = 3
      bus.send(msg)
      continue
    else:
      print("incrementing", end="\r")

  if msg_id == 0xD3 or runStartTime == None:
    km = 0
    rotations = 0
    print("new run", end="\r")
    runStartTime = time.time()

  line = "{};{};{};{};\n".format(runStartTime,time.time(),rotations,km) 
  
  if msg_id == 0xD3 or len(lines) == 0:
    lines.append(line)
  else:
    lines[-1] = line
  
  status.seek(0,0)
  status.truncate()
  status.write("start;end;rotations;km;\n")
  status.write("".join(lines))
  status.flush()

  prev_rotations = rotations

status.close()
