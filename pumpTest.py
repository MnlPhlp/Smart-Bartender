import time
import gpio
import board


pumps = []
for pin in [board.D0, board.D5, board.D6, board.D13, board.D19, board.D26]:
    pump = digitalio.DigitalInOut(pin)
    pump.direction = digitalio.Direction.OUTPUT
    pump.value = True
    pumps.append(pump)


def pour(pump, ml):
    pump.value = False
    time.sleep(ml/27.5)
    pump.value = True


for i in range(0, 5):
    pour(pumps[i], 50)
