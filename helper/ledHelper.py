from threading import Thread
from neopixel import NeoPixel
import time

SLEEP_TIME = 0.05
COLOR_STEPS = 10


class Led:
    pixel: NeoPixel
    cycleRunning: bool
    cycleThread: Thread
    baseColor: "tuple[int, int, int]"

    def __init__(self, leds: NeoPixel, baseColor) -> None:
        self.pixel = leds
        self.cycleRunning = False
        self.baseColor = baseColor

    def base(self):
        self.pixel.fill(self.baseColor)

    def clear(self):
        self.pixel.fill((0, 0, 0))

    def shutdownSequence(self):
        for i in range(0, len(self.pixel)):
            # turn lights off
            self.pixel[i] = self.baseColor
            time.sleep(SLEEP_TIME)

    def powerUpSequence(self):
        for i in range(0, len(self.pixel)):
            # make lights green
            self.pixel[i] = wheel((255//len(self.pixel))*i)
            time.sleep(SLEEP_TIME)

    def startCycle(self):
        if self.cycleRunning:
            return
        self.cycleRunning = True
        self.cycleThread = Thread(target=self.cycleFunc)
        self.cycleThread.start()

    def stopCycle(self):
        if not self.cycleRunning:
            return
        self.cycleRunning = False
        self.cycleThread.join()

    def cycleFunc(self):
        i = 0
        color = 0
        while self.cycleRunning:
            self.pixel[i] = wheel(color)
            color = (color+COLOR_STEPS) % 255
            i = (i+1) % len(self.pixel)
            time.sleep(SLEEP_TIME)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
