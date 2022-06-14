from helper.ledHelper import Led
from helper.displayHelper import Display, mockDisplay
from bartenderBase import BartenderBase
import time
import json
import threading
import board
import neopixel
import adafruit_ssd1306
from adafruit_debouncer import Debouncer
import digitalio
from adafruit_blinka.microcontroller.bcm283x.pin import Pin
import logging

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

LEFT_BTN_PIN = board.D14
LEFT_PIN_BOUNCE = 500

RIGHT_BTN_PIN = board.D15
RIGHT_PIN_BOUNCE = 500

NUMBER_NEOPIXELS = 12
NEOPIXEL_PIN = board.D18
NEOPIXEL_BRIGHTNESS = 0.5
BASE_COLOR = (50, 0, 0)


class Bartender(BartenderBase):
    leds: Led
    server: BartenderServer
    stats: dict
    running: bool
    stopEvent: threading.Event

    def __init__(self):
        super(Bartender, self).__init__()

        # setup led strip:
        self.leds = Led(neopixel.NeoPixel(
            NEOPIXEL_PIN, NUMBER_NEOPIXELS, brightness=NEOPIXEL_BRIGHTNESS), BASE_COLOR)
        self.leds.clear()
        self.leds.powerUpSequence()
        self.leds.startCycle()

        # setup buttons
        pin1 = digitalio.DigitalInOut(LEFT_BTN_PIN)
        pin1.direction = digitalio.Direction.INPUT
        pin1.pull = digitalio.Pull.UP
        self.btn1 = Debouncer(pin1, interval=0.2)

        pin2 = digitalio.DigitalInOut(RIGHT_BTN_PIN)
        pin2.direction = digitalio.Direction.INPUT
        pin2.pull = digitalio.Pull.UP
        self.btn2 = Debouncer(pin2, interval=0.2)

        # configure screen
        try:
            dsp = adafruit_ssd1306.SSD1306_I2C(
                SCREEN_WIDTH, SCREEN_HEIGHT, board.I2C(), addr=0x3C)
        except:
            logging.warn("no display found. Using mock display")
            dsp = mockDisplay()
        self.display = Display(dsp)
        # Clear display.
        self.display.setup()
        self.display.show()

        # load the pump configuration from file
        self.pump_configuration = Bartender.readPumpConfiguration()

        self.leds.stopCycle()
        self.leds.shutdownSequence()
        logging.info("Done initializing")

    @staticmethod
    def readPumpConfiguration():
        config = json.load(open('config/pump_config.json'))
        for pump in config.keys():
            pinId = config[pump]["pin"]
            pin = digitalio.DigitalInOut(Pin(pinId))
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = True
            config[pump]["pin"] = pin
        return config

    def writePumpConfiguration(self):
        jsonData = {}
        # create a deep copy to change the pins from objects back to ints
        for pump in self.pump_configuration.keys():
            jsonData[pump] = {
                "value": self.pump_configuration[pump]["value"],
                "name": self.pump_configuration[pump]["name"],
                "pin": self.pump_configuration[pump]["pin"]._pin.id,
                "rate": self.pump_configuration[pump]["rate"]

            }
        with open("config/pump_config.json", "w") as jsonFile:
            json.dump(jsonData, jsonFile)

    def clean(self):
        waitTime = 20
        pumpThreads = []

        # cancel any button presses while the drink is being made
        self.running = True

        for pump in self.pump_configuration.keys():
            pump_t = threading.Thread(target=self.pour, args=(
                self.pump_configuration[pump]["pin"], waitTime))
            pumpThreads.append(pump_t)

        # start the pump threads
        for thread in pumpThreads:
            thread.start()

        # start the progress bar
        self.progressBar(waitTime)

        # wait for threads to finish
        for thread in pumpThreads:
            thread.join()

        # show the main menu
        self.menuContext.showMenu()

        # sleep for a couple seconds to make sure the interrupts don't get triggered
        time.sleep(2)

        # reenable interrupts
        self.running = False

    def displayMenuItem(self, menuItem):
        logging.info(f"current menu: {menuItem.name}")
        self.display.clear()
        self.display.displayText(menuItem.name)
        self.display.show()

    def pour(self, pin, waitTime):
        pin.value = False
        logging.info(f"pump on pin {pin._pin} started")
        self.stopEvent.wait(waitTime)
        pin.value = True
        logging.info(f"pump on pin {pin._pin} stoped")

    def progressBar(self, waitTime):
        stepTime = 0.05
        start = time.time()
        percent = 0
        while percent < 100 and not self.stopEvent.is_set():
            loopStart = time.time()
            # update the progress bar
            self.display.drawProgressBar(percent)
            self.display.show()
            # wait the remaining time to limit refreshes
            loopElapsed = time.time()-loopStart
            if loopElapsed < stepTime:
                time.sleep(stepTime-loopElapsed)
            # update the percentage
            percent = ((time.time()-start)/waitTime*100)

        self.display.drawProgressBar(100)

    def makeDrink(self, drink, ingredients):
        # cancel any button presses while the drink is being made
        self.running = True
        self.addStats(drink, ingredients)

        # display the drink in the making
        self.display.clear()
        self.display.displayText(drink)

        # launch a thread to control lighting
        self.leds.startCycle()

        # Parse the drink ingredients and spawn threads for pumps
        maxTime = 0
        pumpThreads = []
        pumps = self.pump_configuration
        for pump in [pumps[key] for key in pumps if pumps[key]["value"] in ingredients]:
            waitTime = ingredients[pump["value"]]/pump["rate"]
            if (waitTime > maxTime):
                maxTime = waitTime
            pump_t = threading.Thread(
                target=self.pour, args=(pump["pin"], waitTime))
            pumpThreads.append(pump_t)

        # start the pump threads
        for thread in pumpThreads:
            thread.start()

        # start the progress bar
        self.progressBar(maxTime)

        # wait for threads to finish
        for thread in pumpThreads:
            thread.join()

        # show the main menu
        self.menuContext.showMenu()

        # stop the light thread
        self.leds.stopCycle()
        self.leds.shutdownSequence()

        # reenable interrupts
        self.running = False

    def handleInput(self):
        self.btn1.update()
        self.btn2.update()
        if self.btn1.fell:
            self.left_btn()
        if self.btn2.fell:
            self.right_btn()

    def stop(self):
        logging.info("stopping current drink")
        self.stopEvent.set()
        # wait for everything to finish
        while self.running:
            time.sleep(0.5)
        self.stopEvent.clear()
        logging.info("drink is stoped")

    def shutdown(self):
        self.stop()
        logging.info("clearing screen")
        self.display.clear()
        self.display.show()
        logging.info("turning off leds")
        self.leds.stopCycle()
        self.leds.clear()
