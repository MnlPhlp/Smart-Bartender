from flask_ask import Ask, session, question, statement
from flask import request


def defineAlexaSkill(app, drinkCallback):
    ask = Ask(app, "/")

    @ask.launch
    def launch():
        speech_text = "welcome to the smart bartender"
        print(speech_text)
        return question(speech_text).reprompt(speech_text).simple_card(speech_text)

    @ask.intent('DrinkIntent')
    def drink_intent():
        content = request.get_json()
        drink = ""
        try:
            drink = content['request']['intent']['slots']['drink'][
                'resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        except KeyError:
            return "der angegebene Drink ist nicht verfügbar"
        print("drink intent called with drink: "+drink)
        message = drinkCallback(drink)
        return statement(message)

    @ask.intent('AMAZON.HelpIntent')
    def help():
        speech_text = 'You can say hello to me!'
        return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

    @ask.session_ended
    def session_ended():
        return "{}", 200

    app.config['ASK_VERIFY_REQUESTS'] = False
