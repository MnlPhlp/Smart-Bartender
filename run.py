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

from menu import MenuItem, Menu, Back, MenuContext, MenuDelegate

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
bartender = Bartender(
    args.server, args.username, args.password)
drink_list, drink_options = bartender.loadDrinks()
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
