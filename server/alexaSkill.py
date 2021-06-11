from flask_ask import Ask, session, question, statement
from flask import request


def defineAlexaSkill(app, bartenderServer, alexaUser):
    ask = Ask(app, "/")

    def checkUserId() -> bool:
        userid=request.get_json()["session"]["user"]["userId"]
        ok = userid == alexaUser
        if not ok:
            print("illegal request from "+userid)
        return ok

    @ask.launch
    def launch():
        if not checkUserId():
            return(statement("ungültige userId"))
        speech_text = "smart barkeeper ist gestartet"
        print(speech_text)
        return question(speech_text).reprompt(speech_text).simple_card(speech_text)

    @ask.intent('DrinkIntent')
    def drink_intent():
        if not checkUserId():
            return(statement("ungültige userId"))
        content = request.get_json()
        drink = ""
        try:
            drink = content['request']['intent']['slots']['drink'][
                'resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        except KeyError:
            return "der angegebene Drink ist nicht verfügbar"
        print("drink intent called with drink: "+drink)
        resp = question(bartenderServer.makeDrink(drink))
        return resp

    @ask.intent('AMAZON.StopIntent')
    def stop():
        if not checkUserId():
            return(statement("ungültige userId"))
        bartenderServer.bartender.stop()
        return statement("stoppe den aktuellen drink")

    @ask.session_ended
    def session_ended():
        return "{}", 200

    app.config['ASK_VERIFY_REQUESTS'] = False
