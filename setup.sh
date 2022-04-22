#!/bin/bash
#echo cloning repository
#git clone https://github.com/MnlPhlp/Smart-Bartender.git
#cd Smart-Bartender
echo creating venv
python3 -m venv venv
source ./venv/bin/activate
echo installing libraries
if ( uname -a | grep x86_64 ); then
    pip install -r requirements_pc.txt
else
    pip install -r requirements.txt
fi
pip install https://github.com/johnwheeler/flask-ask/archive/55960acee3e91c3ae66208b0b020123c860439cd.zip