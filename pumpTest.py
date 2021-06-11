import time
import digitalio
import board
import sys

pumps = []
for pin in [board.D0, board.D5, board.D6, board.D13, board.D19, board.D26]:
    pump = digitalio.DigitalInOut(pin)
    pump.direction = digitalio.Direction.OUTPUT
    pump.value = True
    pumps.append(pump)


def pour(pump, ml,rate):
    pump.value = False
    time.sleep(ml/rate)
    pump.value = True


pour(pumps[int(sys.argv[1])], 200,int(sys.argv[2]))
