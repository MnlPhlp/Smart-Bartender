from flask import app
from flask.globals import request
from api.alexaSkill import defineAlexaSkill
from flask import Flask
from drinks import drink_list


class BartenderServer():
    app = Flask(__name__)
    validDrinks: "dict[str,list[str]]" = {}

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
                self.validDrinks[drink["name"]] = ingredients.keys()

    def drinkEndpoint(self):
        """make a drink
        """
        if request.args.get("drink") == None:
            return 'no drink given'

        drink = str(request.args.get("drink"))
        return self.makeDrink(drink)

    def makeDrink(self, drink):
        # check if drink is valid
        if not drink in self.validDrinks:
            return f'invalid drink {drink}. Valid options are: {self.validDrinks}'
        # get ingredients
        ingredients = self.validDrinks[drink]
        # make the drink
        self.bartender.makeDrink(drink, ingredients)
        return "started making a "+drink
