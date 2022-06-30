from multiprocessing import Process
from helper.ledHelper import Led
from server.bartenderServer import BartenderServer
import os
if os.uname().machine == "x86_64":
    from mock.bartenderMock import Bartender
else:
    from bartender.bartender import Bartender
from datetime import datetime
import time
import json
import threading
import logging
from logging.handlers import RotatingFileHandler
from sys import stdout
import argparse
import requests

from menu import MenuItem, Menu, Back, MenuContext, MenuDelegate
from config.drinks import drink_list as drink_list_import, drink_options as drink_options_import


def loadDrinks(server, username, password):
    try:
        resp = requests.get(f"{server}/v1/cocktail/fav",
                            headers={
                                "Content-Type": "application/json",
                                "username": username,
                                "password": password,
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


    # setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# log to cli
clihandler = logging.StreamHandler(stdout)
clihandler.setLevel(logging.INFO)
logger.addHandler(clihandler)
# log to file
fileHandler = RotatingFileHandler("log.log", mode='a', maxBytes=5*1024*1024,
                                  backupCount=2, encoding='utf-8', delay=False)
fileHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)


p = argparse.ArgumentParser()
p.add_argument("-u", "--user", dest="username", type=str, default="")
p.add_argument("-p", "--pass", dest="password", type=str, default="")
p.add_argument("-a", "--alexaUser", dest="alexaUser",
               type=str, default="")
p.add_argument("-s", "--server", dest="server",
               type=str, default="http://localhost:1234")

args = p.parse_args()
drink_list, drink_options = loadDrinks(
    args.server, args.username, args.password)
bartender = Bartender()
bartender.buildMenu(drink_list, drink_options)
server = BartenderServer(
    bartender, drink_list, args.username, args.password, args.alexaUser)
logging.info("starting server")
server.start()
logging.info("starting button handling")
# main loop
try:
    while True:
        bartender.handleInput()
        time.sleep(0.1)
except KeyboardInterrupt:
    logging.info("stopped by user")
finally:
    logging.info("shutting down")
    logging.info("stopping running threads")
    bartender.shutdown()
    logging.info("stopping server")
    server.stop()
