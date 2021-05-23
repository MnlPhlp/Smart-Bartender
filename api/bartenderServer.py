from threading import Thread
import threading
from flask import app
from flask.globals import request
from api.alexaSkill import defineAlexaSkill
from flask import Flask
from drinks import drink_list


class BartenderServer():
    app = Flask(__name__)
    validDrinks: "dict[str,dict]" = {}

    def __init__(self, bartender):
        self.bartender = bartender
        self.loadValidDrinks()
        self.app.add_url_rule("/makeDrink", "makeDrink", self.drinkEndpoint)

    def start(self):
        defineAlexaSkill(self.app, self.makeDrink)
        self.app.run(host="0.0.0.0", port=8080)

    def loadValidDrinks(self):
        for drink in drink_list:
            ingredients = drink["ingredients"]
            presentIng = 0
            # check if all ingredients are configured in the pump config
            for ing in ingredients.keys():
                for p in self.bartender.pump_configuration.keys():
                    if (ing == self.bartender.pump_configuration[p]["value"]):
                        presentIng += 1
            if (presentIng == len(ingredients.keys())):
                self.validDrinks[drink["key"]] = drink

    def drinkEndpoint(self):
        """make a drink
        """
        if request.args.get("drink") == None:
            return 'kein Getränk angegeben'

        drink = str(request.args.get("drink"))
        return self.makeDrink(drink)

    def makeDrink(self, drink):
        # check if drink is valid
        if not drink in self.validDrinks:
            return f'das Getränk {drink} ist nicht verfügbar'
        # make the drink
        if self.bartender.running:
            return "der barkeeper läuft bereits"
        else:
            # get data
            ingredients = self.validDrinks[drink]["ingredients"]
            name = self.validDrinks[drink]["name"]
            t = threading.Thread(
                target=lambda: self.bartender.makeDrink(name, ingredients))
            t.start()
            return f"starte {name}"
