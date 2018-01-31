# Setup
pip install flask flask_bower flask-socketio flask_restful flask_caching
git submodule update --recursive --init

# Overview
This is a basic translater of CCSDS binary packets into python CTypes and then to JSON packets and transmitted via a socket.io server.

CCSDS packet definitions are described in CTypes.

# Running 
python run.py --ProjectDir proj_example

# Customization
Users are expected to create their own project example.

