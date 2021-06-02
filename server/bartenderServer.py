from threading import Thread
from flask import app
from flask import request, jsonify
from server.alexaSkill import defineAlexaSkill
from flask import Flask
from config.drinks import drink_list
import matplotlib.pyplot as plt


def html(message):
    return f"""
        <html>
            <head>
                <link rel="stylesheet" href="style.css">
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
    serverThread: Thread

    def __init__(self, bartender):
        self.bartender = bartender
        self.loadValidDrinks()
        self.app.add_url_rule("/makeDrink", "makeDrink", self.drinkEndpoint)
        self.app.add_url_rule("/stop", "stop", self.stopEndpoint)
        self.app.add_url_rule("/", "index", self.indexHandler)
        self.app.add_url_rule("/style.css", "css", self.cssHandler)
        self.app.add_url_rule("/favicon.ico", "favicon", self.favicon)
        self.app.add_url_rule("/stats.json", "stats", self.statsJson)
        self.app.add_url_rule("/stats", "stats graph", self.statsGraph)

    def start(self):
        defineAlexaSkill(self.app, self)
        self.serverThread = Thread(
            target=lambda: self.app.run(host="0.0.0.0", port=8080))
        self.serverThread.start()

    def cssHandler(self):
        with open("static/style.css", "rt") as f:
            return f.read()

    def favicon(self):
        with open("static/favicon.ico", "rb") as f:
            return f.read()

    def indexHandler(self):
        body = '<div class="row">'
        for drink in self.validDrinks:
            body += f'<a href="makeDrink?drink={drink}"> <button class="column">{drink}</button> </a>'
        body += "</div>"
        return html(body)

    def stopEndpoint(self):
        Thread(target=self.bartender.stop).start()
        message = '<span class="message">stopping current drink</span>'
        message += '<a href="/"><button>back</button></a>'
        return html(message)

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
        message = f'<span class="message">{html(self.makeDrink(drink))}</span>'
        message += '<br><a href="/stop"><button>stop</button></a>'
        message += '<br><a href="/"><button>back</button></a>'
        return message

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
            t = Thread(
                target=lambda: self.bartender.makeDrink(name, ingredients))
            t.start()
            return f"starte {name}"

    def statsJson(self):
        return jsonify(self.bartender.stats)

    def statsGraph(self):
        dates = [date for date in self.bartender.stats.keys() if date !=
                 "total"]
        plt.xticks(range(len(dates)), dates)
        plt.locator_params(axis="x", nbins=5)
        for drink in [drink["name"] for drink in drink_list]:
            # skip drink if there are no stats
            if not drink in self.bartender.stats[list(dates)[0]]:
                continue
            data = []
            for date in dates:
                # skip drink if there are no stats
                if not drink in self.bartender.stats[date]:
                    data.append(0)
                else:
                    data.append(self.bartender.stats[date][drink])
            print(drink+": "+str(data))
            plt.plot(data, ".-", label=drink)
        plt.legend()
        plt.savefig("graph.svg")
        with open("graph.svg", "rb") as f:
            return f.read()

    def stop(self):
        # find a way to stop the app server
        pass
