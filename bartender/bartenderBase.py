import string
from menu import MenuItem, Menu, Back, MenuContext, MenuDelegate
import json
from datetime import datetime
import threading
import logging
from time import sleep
from config.drinks import drink_list as drink_list_import, drink_options as drink_options_import
import requests


class BartenderBase(MenuDelegate):
    stats: dict
    running: bool
    stopEvent: threading.Event
    server: string
    username: string
    password: string

    def __init__(self,server, username, password):
        self.running = False
        self.stopEvent = threading.Event()
        self.server = server
        self.username = username
        self.password = password

        self.stats = self.loadStats()

    def addStats(self, drink, ingredients):
        time = datetime.now().strftime("%d.%m.%y-%H:%M")
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
                selected = "*" if opt == self.pump_configuration[p]["value"] else ""
                config.addOption(MenuItem('pump_selection', opt, {
                                 "key": p, "value": opt, "name": opt}))
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
        # add reload drinks option to reload drinks from the server
        configuration_menu.addOption(MenuItem("reload_drinks", "Reload drinks"))
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
            self.writePumpConfiguration()
            return True
        elif(menuItem.type == "clean"):
            self.clean()
            return True
        elif(menuItem.type == "reload_drinks"):
            drink_list, drink_options = self.loadDrinks()
            self.buildMenu(drink_list, drink_options)
        return False

    def stop(self):
        if not self.running:
            return
        logging.info("stopping current drink")
        self.stopEvent.set()
        # wait for everything to finish
        while self.running:
            sleep(0.5)
        self.stopEvent.clear()
        logging.info("drink is stoped")

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

    def loadDrinks(self):
        try:
            resp = requests.get(f"{self.server}/v1/cocktail/fav",
                                headers={
                                    "Content-Type": "application/json",
                                    "username": self.username,
                                    "password": self.password,
                                })
        except Exception as err:
            logging.warning(
                f"no cocktails loaded from server. Error during request: {err}")
            # return imported values
            return drink_list_import, drink_options_import
        if resp.status_code != 200:
            logging.warning(
                f"no cocktails loaded from server. Request failed: {resp.content}")
            # return imported values
            return drink_list_import, drink_options_import
        resp = json.loads(resp.content)
        drink_list = []
        drink_options = set()
        cocktail = {}
        for cocktailJson in resp["Data"]:
            cocktail["name"] = cocktailJson["Name"]
            cocktail["ingredients"] = {}
            for ing in cocktailJson["Ingredients"]:
                drink_options.add(ing["Name"])
                cocktail["ingredients"][ing["Name"]] = ing["Amount"]
            print(cocktail)
            drink_list.append(cocktail)
        drink_options.add("Nothing")
        drink_options = list(drink_options)
        return drink_list, drink_options
