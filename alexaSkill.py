from flask import Flask
from flask_ask import Ask, request, session, question, statement

app = Flask(__name__)
ask = Ask(app, "/")


@ask.launch
def launch():
    speech_text = "welcome to the smart bartender"
    print(speech_text)
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)


@ask.intent('DrinkIntent', mapping={'drink': 'drink'})
def drink_intent(drink, room):
    print(drink)
    return statement(f"making a {drink}")


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)


@ask.session_ended
def session_ended():
    return "{}", 200


app.config['ASK_VERIFY_REQUESTS'] = False
app.run(port=8080)
