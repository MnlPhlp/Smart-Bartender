from threading import Thread
import threading
from flask import app
from flask.globals import request
from server.alexaSkill import defineAlexaSkill
from flask import Flask
from config.drinks import drink_list


def html(message):
    return f"""
        <html>
            <head>
                <title>Smart Barkeeper</title>
            <head>
            <body>
                {message}
            </body>
        </html>
        """


class BartenderServer():
    app = Flask(__name__)
    validDrinks: "dict[str,dict]" = {}
    invalidDrinks: "dict[str,dict]" = {}

    def __init__(self, bartender):
        self.bartender = bartender
        self.loadValidDrinks()
        self.app.add_url_rule("/makeDrink", "makeDrink", self.drinkEndpoint)
        self.app.add_url_rule("/stop", "stop", self.stopEndpoint)
        self.app.add_url_rule("/", "index", self.indexHandler)

    def start(self):
        defineAlexaSkill(self.app, self.makeDrink)
        self.app.run(host="0.0.0.0", port=8080)

    def indexHandler(self):
        body = ""
        for drink in self.validDrinks:
            body += f'<a href="makeDrink?drink={drink}"> <button> {drink} </button> </a>'
        return html(body)

    def stopEndpoint(self):
        self.bartender.stop()
        return html("stopping current drink")

    def loadValidDrinks(self):
        for drink in drink_list:
            ingredients = drink["ingredients"]
            presentIng = []
            # check if all ingredients are configured in the pump config
            for ing in ingredients.keys():
                for p in self.bartender.pump_configuration.keys():
                    if (ing == self.bartender.pump_configuration[p]["value"]):
                        presentIng.append(ing)
            if (len(presentIng) == len(ingredients.keys())):
                self.validDrinks[drink["key"]] = drink
            else:
                # store the missing ingredients for a helpful message
                drink["ingredients"] = [
                    i for i in ingredients if i not in presentIng]
                self.invalidDrinks[drink["key"]] = drink

    def drinkEndpoint(self):
        """make a drink
        """
        if request.args.get("drink") == None:
            return html('kein Getränk angegeben')

        drink = str(request.args.get("drink"))
        return html(self.makeDrink(drink))

    def makeDrink(self, drink):
        # check if drink is valid
        name = drink
        if not drink in self.validDrinks:
            missingIngredients = ""
            if drink in self.invalidDrinks:
                name = self.invalidDrinks[drink]["name"]
                # if the drink is in the list show missing ingredients
                missingIngredients = " Fehlende Zutaten sind: " + \
                    str(self.invalidDrinks[drink]["ingredients"])
            return f'das Getränk {name} ist nicht verfügbar.'+missingIngredients
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
