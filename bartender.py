from multiprocessing import Process
from helper.ledHelper import Led
from server.bartenderServer import BartenderServer
from helper.displayHelper import Display, mockDisplay
from datetime import datetime
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
from logging.handlers import RotatingFileHandler
from sys import stdout

from menu import MenuItem, Menu, Back, MenuContext, MenuDelegate
from config.drinks import drink_list, drink_options

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

FLOW_RATE = 10/100.0

# setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# log to cli
clihandler = logging.StreamHandler(stdout)
clihandler.setLevel(logging.INFO)
logger.addHandler(clihandler)
# log to file
fileHandler = RotatingFileHandler("log.log", mode='a', maxBytes=5*1024*1024,
                                  backupCount=2, encoding='utf-8', delay=False)
fileHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)


class Bartender(MenuDelegate):
    leds: Led
    server: BartenderServer
    stats: dict

    def __init__(self):
        self.running = False
        self.stopEvent = threading.Event()

        # setup led strip:
        self.leds = Led(neopixel.NeoPixel(
            NEOPIXEL_PIN, NUMBER_NEOPIXELS, brightness=NEOPIXEL_BRIGHTNESS), BASE_COLOR)
        self.leds.clear()
        self.leds.powerUpSequence()
        self.leds.startCycle()

        self.stats = self.loadStats()

        # setup buttons
        pin1 = digitalio.DigitalInOut(LEFT_BTN_PIN)
        pin1.direction = digitalio.Direction.INPUT
        pin1.pull = digitalio.Pull.UP
        self.btn1 = Debouncer(pin1)

        pin2 = digitalio.DigitalInOut(RIGHT_BTN_PIN)
        pin2.direction = digitalio.Direction.INPUT
        pin2.pull = digitalio.Pull.UP
        self.btn2 = Debouncer(pin2)

        # configure screen
        # adafruit_ssd1306.SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, board.I2C(), addr=0x3C))
        self.display = Display(mockDisplay())
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

    @staticmethod
    def writePumpConfiguration(configuration):
        jsonData = {}
        # create a deep copy to change the pins from objects back to ints
        for pump in configuration.keys():
            jsonData[pump] = {
                "value": configuration[pump]["value"],
                "name": configuration[pump]["name"],
                "pin": configuration[pump]["pin"]._pin.id
            }
        with open("config/pump_config.json", "w") as jsonFile:
            json.dump(jsonData, jsonFile)

    def buildMenu(self, drink_list, drink_options):
        # create a new main menu
        m = Menu("Main Menu")

        # add drink options
        drink_opts = []
        for d in drink_list:
            drink_opts.append(MenuItem('drink', d["name"], {
                              "ingredients": d["ingredients"]}))

        configuration_menu = Menu("Configure")

        # add pump configuration options
        pump_opts = []
        for p in sorted(self.pump_configuration.keys()):
            config = Menu(self.pump_configuration[p]["name"])
            # add fluid options for each pump
            for opt in drink_options:
                # star the selected option
                selected = "*" if opt["value"] == self.pump_configuration[p]["value"] else ""
                config.addOption(MenuItem('pump_selection', opt["name"], {
                                 "key": p, "value": opt["value"], "name": opt["name"]}))
            # add a back button so the user can return without modifying
            config.addOption(Back("Back"))
            config.setParent(configuration_menu)
            pump_opts.append(config)

        # add pump menus to the configuration menu
        configuration_menu.addOptions(pump_opts)
        # add a back button to the configuration menu
        configuration_menu.addOption(Back("Back"))
        # adds an option that cleans all pumps to the configuration menu
        configuration_menu.addOption(MenuItem('clean', 'Clean'))
        configuration_menu.setParent(m)

        m.addOptions(drink_opts)
        m.addOption(configuration_menu)
        # create a menu context
        self.menuContext = MenuContext(m, self)

    def filterDrinks(self, menu):
        """
        Removes any drinks that can't be handled by the pump configuration
        """
        for i in menu.options:
            if (i.type == "drink"):
                i.visible = False
                ingredients = i.attributes["ingredients"]
                presentIng = 0
                for ing in ingredients.keys():
                    for p in self.pump_configuration.keys():
                        if (ing == self.pump_configuration[p]["value"]):
                            presentIng += 1
                if (presentIng == len(ingredients.keys())):
                    i.visible = True
            elif (i.type == "menu"):
                self.filterDrinks(i)

    def selectConfigurations(self, menu):
        """
        Adds a selection star to the pump configuration option
        """
        for i in menu.options:
            if (i.type == "pump_selection"):
                key = i.attributes["key"]
                if (self.pump_configuration[key]["value"] == i.attributes["value"]):
                    i.name = "%s %s" % (i.attributes["name"], "*")
                else:
                    i.name = i.attributes["name"]
            elif (i.type == "menu"):
                self.selectConfigurations(i)

    def prepareForRender(self, menu):
        self.filterDrinks(menu)
        self.selectConfigurations(menu)
        return True

    def menuItemClicked(self, menuItem):
        if (menuItem.type == "drink"):
            def func(): return self.makeDrink(
                menuItem.name, menuItem.attributes["ingredients"])
            t = threading.Thread(target=func)
            t.start()
            return True
        elif(menuItem.type == "pump_selection"):
            self.pump_configuration[menuItem.attributes["key"]
                                    ]["value"] = menuItem.attributes["value"]
            Bartender.writePumpConfiguration(self.pump_configuration)
            return True
        elif(menuItem.type == "clean"):
            self.clean()
            return True
        return False

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
            waitTime = ingredients[pump["value"]] * FLOW_RATE
            self.addStats(drink, ingredients)
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

    def addStats(self, drink, ingredients):
        time = datetime.now().strftime("%d.%m-%H")
        # create entries if they don't exist
        if not time in self.stats:
            self.stats[time] = {}
        stats = self.stats[time]
        total = self.stats["total"]
        if not drink in stats:
            stats[drink] = 0
        if not drink in total:
            total[drink] = 0
        # add the volume to the entries
        total[drink] += 1
        stats[drink] = total[drink]
        self.saveStats()

    def loadStats(self):
        try:
            with open("stats.json", "rt") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"total": {}}

    def saveStats(self):
        with open("stats.json", "wt") as f:
            return json.dump(self.stats, f)

    def left_btn(self):
        logging.info("left button pressed")
        if not self.running:
            logging.info("menu advance")
            self.menuContext.advance()

    def right_btn(self):
        logging.info("right button pressed")
        if not self.running:
            logging.info("menu select")
            self.menuContext.select()
        else:
            logging.info("stop")
            self.stop()

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

    def run(self):
        # main loop
        try:
            while True:
                self.handleInput()
                time.sleep(0.1)
        except KeyboardInterrupt:
            logging.info("shutting down")
        logging.info("stopping running threads")
        self.stop()
        self.server.stop()
        logging.info("clearing screen")
        self.display.clear()
        self.display.show()
        logging.info("turning off leds")
        self.leds.stopCycle()
        self.leds.clear()


bartender = Bartender()
bartender.buildMenu(drink_list, drink_options)
bartender.server = BartenderServer(bartender)
logging.info("starting server")
bartender.server.start()
logging.info("starting button handling")
bartender.run()
