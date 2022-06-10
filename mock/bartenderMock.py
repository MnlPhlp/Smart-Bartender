import logging
import json

class Bartender:
    def __init__(self):
        # load the pump configuration from file
        self.pump_configuration = json.load(open('config/pump_config.json'))

    def buildMenu(self, drink_list, drink_options):
        logging.info("EMPTY MOCK: build menu")

    def handleInput(self):
        pass

    def shutdown(self):
        logging.info("EMPTY MOCK: shutdown")

