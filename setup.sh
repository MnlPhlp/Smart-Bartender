#!/bin/bash
echo creating venv
python3 -m venv venv
source ./venv/bin/activate
echo installing libraries
if ( uname -a | grep x86_64 ); then
    pip install -r requirements_pc.txt
else
    pip install -r requirements.txt
fi
pip install https://github.com/MnlPhlp/flask-ask/archive/460bf1ee1593103c2891d512e1dff86d31ece8bb.zip