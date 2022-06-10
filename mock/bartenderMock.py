import logging
import json
import threading
from time import sleep
from bartender.bartenderBase import BartenderBase


class Bartender(BartenderBase):
    def __init__(self):
        super(Bartender, self).__init__()
        # load the pump configuration from file
        self.pump_configuration = json.load(open('config/pump_config.json'))

    def handleInput(self):
        pass

    def shutdown(self):
        logging.info("EMPTY MOCK: shutdown")

    def makeDrink(self, drink, ingredients):
        # cancel any button presses while the drink is being made
        self.running = True
        self.addStats(drink, ingredients)
        logging.info(f"MOCK: makeDrink starting {drink}")
        i = 0
        while i < 20 and not self.stopEvent.is_set():
            sleep(0.1)
            i += 1
        logging.info("MOCK: makeDrink done")
        # reenable interrupts
        self.running = False

    def displayMenuItem(self, menuItem):
        logging.info(f"current menu: {menuItem.name}")
