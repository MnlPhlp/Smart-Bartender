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
pip install https://github.com/MnlPhlp/flask-ask/archive/refs/tags/v0.9.0.zip

echo "activate venv and start server:"
echo ". ./venv/bin/activate"
echo "python run.py"