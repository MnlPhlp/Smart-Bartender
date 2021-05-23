from flask import app
from flask.globals import request
from api.alexaSkill import defineAlexaSkill
import flask
from drinks import drink_list


class BartenderServer():
    app = flask(__name__)
    validDrinks: "dict[str,list[str]]"

    def __init__(self, bartender):
        self.bartender = bartender
        self.loadValidDrinks()

    def start(self):
        defineAlexaSkill(self.app, self.makeDrink)
        self.app.run(port=8080)

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

    @app.route('makeDrink')
    def drinkEndpoint(self):
        """make a drink
        """
        if request.args.get("drink") == None:
            return 'no drink given'

        drink = str(request.args.get("drink"))
        self.makeDrink(drink)

    def makeDrink(self, drink):
        # check if drink is valid
        if self.validDrinks[drink] == None:
            return 'invalid drink'
        # get ingredients
        ingredients = self.validDrinks[drink]
        # make the drink
        self.bartender.makeDrink(drink, ingredients)
        return "started making a "+drink


if __name__ == "__main__":
    b = BartenderServer(None)
    b.start()
