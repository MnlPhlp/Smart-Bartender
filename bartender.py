from ledHelper import Led
from api.bartenderServer import BartenderServer
from displayHelper import Display
import time
import json
import threading
import board
import neopixel
import adafruit_ssd1306
from adafruit_debouncer import Debouncer
import digitalio

from menu import MenuItem, Menu, Back, MenuContext, MenuDelegate
from drinks import drink_list, drink_options

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

LEFT_BTN_PIN = board.D20
LEFT_PIN_BOUNCE = 500

RIGHT_BTN_PIN = board.D21
RIGHT_PIN_BOUNCE = 500

NUMBER_NEOPIXELS = 12
NEOPIXEL_PIN = board.D18
NEOPIXEL_BRIGHTNESS = 0.1

FLOW_RATE = 10/100.0


class Bartender(MenuDelegate):
    leds: Led

    def __init__(self):
        self.running = False

        # setup led strip:
        self.leds = Led(neopixel.NeoPixel(
            NEOPIXEL_PIN, NUMBER_NEOPIXELS, brightness=NEOPIXEL_BRIGHTNESS))
        self.leds.clear()
        self.leds.powerUpSequence()
        self.leds.startCycle()

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
        self.display = Display(adafruit_ssd1306.SSD1306_I2C(
            SCREEN_WIDTH, SCREEN_HEIGHT, board.I2C(), addr=0x3C))
        # Clear display.
        self.display.setup()
        self.display.show()

        # load the pump configuration from file
        self.pump_configuration = Bartender.readPumpConfiguration()
        for pump in self.pump_configuration.keys():
            GPIO.setup(
                self.pump_configuration[pump]["pin"], GPIO.OUT, initial=GPIO.HIGH)

        self.leds.stopCycle()
        self.leds.shutdownSequence()
        print(" Done initializing")

    @staticmethod
    def readPumpConfiguration():
        return json.load(open('pump_config.json'))

    @staticmethod
    def writePumpConfiguration(configuration):
        with open("pump_config.json", "w") as jsonFile:
            json.dump(configuration, jsonFile)

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
            self.makeDrink(menuItem.name, menuItem.attributes["ingredients"])
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
        print(menuItem.name)
        self.display.clear()
        self.display.displayText(menuItem.name)
        self.display.show()

    def pour(self, pin, waitTime):
        GPIO.setmode(GPIO.BCM)
        GPIO.output(pin, GPIO.LOW)
        print(f"pump on pin {pin} started")
        time.sleep(waitTime)
        GPIO.output(pin, GPIO.HIGH)
        print(f"pump on pin {pin} stoped")

    def progressBar(self, waitTime):
        stepTime = 0.05
        start = time.time()
        percent = 0
        while percent < 100:
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
        for ing in ingredients.keys():
            for pump in self.pump_configuration.keys():
                if ing == self.pump_configuration[pump]["value"]:
                    waitTime = ingredients[ing] * FLOW_RATE
                    if (waitTime > maxTime):
                        maxTime = waitTime
                    pump_t = threading.Thread(target=self.pour, args=(
                        self.pump_configuration[pump]["pin"], waitTime))
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

        # sleep for a couple seconds to make sure the interrupts don't get triggered
        time.sleep(2)

        # reenable interrupts
        self.running = False

    def left_btn(self, ctx):
        if not self.running:
            self.menuContext.advance()

    def right_btn(self, ctx):
        if not self.running:
            self.menuContext.select()

    def handleInput(self):
        self.btn1.update()
        self.btn2.update()
        if self.btn1.fell:
            self.left_btn()
        if self.btn2.fell:
            self.right_btn()

    def run(self):
        # main loop
        try:
            while True:
                time.sleep(0.1)
                self.handleInput()

        except KeyboardInterrupt:
            print("shutting down")
        print("clearing screen")
        self.display.clear()
        self.display.show()
        print("turning off leds")
        self.leds.stopCycle()
        self.leds.clear()


bartender = Bartender()
bartender.buildMenu(drink_list, drink_options)
bartnderServer = BartenderServer(bartender)
bartnderServer.start()
bartender.run()
