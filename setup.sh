#!/bin/bash
echo cloning repository
git clone https://github.com/MnlPhlp/Smart-Bartender.git
cd Smart-Bartender
echo creating venv
python3 -m venv .
source ./bin/activate
echo installing libraries
pip install -r requirements.txt