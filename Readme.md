# Setup
```
pip install flask flask_bower flask-socketio flask_restful flask_caching
git submodule update --recursive --init
cd openmct-tutorial
npm install
cd ..
python run.py
```

### Openmct setup
cd sources/openmct
```
pip install nvm  spacy scikit-learn 
# Maybe need this ???
# pip spacey
nvm install 

```


# Overview
This is a basic translator of CCSDS binary packets into python CTypes and then to JSON packets and transmitted via a socket.io server.

CCSDS packet definitions are described in CTypes.

# Running 
python app.py --ProjectDir proj_example

# Customization
Users are expected to copy the proj_example folder for their own project.

Look at the proj_example/driver.py

## Telemetry database

The driver class is expected to have a tlms object, or property getter that contains ctype structures objects of the packets that will be returned from GetPackets.

The main app will use inspection to scan through all of the telemetry packets, and build a json database of the telemetry packets to send to openmct.  This can be done by calling app.py with the --regen_tlmdb, or if proj_example/tlm_db/tlm.json does not exist.

Once created tlm.json can be further modified for polynomials, and limits.
More to come later... (units, descriptions)

It will eventually also generate the logging routines for each packet to log incoming packets for the openmct frontend to have historical data to plot with..

## GetPackets

A seperate thread will be created repeatably calls drivers GetPackets class function.
It is expected that GetPackets will repetably yield a dictionary describing the packet. 
