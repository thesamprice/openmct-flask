from flask import Flask, render_template,send_from_directory
from flask.ext.socketio import SocketIO, emit
#from flask_socketio import SocketIO, emit
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from flask_bower import Bower

from threading import Thread
from flask_caching import Cache
from flask import request
from flask import jsonify
import argparse 

import json
import os
import sys
import glob
import base64
import datetime
import time
from time import sleep

arg_parser = argparse.ArgumentParser(description='python based telemetry and command streamer.')
arg_parser.add_argument('--ProjectDir',  default='proj_example',type=str, help='Project folder to pull configuration data from')
arg_parser.add_argument('--NoTlmOut',  action="store_true", help='Disables output telemetry')
args = arg_parser.parse_args()

app = Flask(__name__)
app._static_folder = '/Users/sprice5/src/websites/openmct-tutorial'
app._static_folder = os.path.dirname(sys.argv[0]) + './openmct-tutorial'
app._static_folder = os.path.abspath(app._static_folder)
app.config.update(user_dir=args.ProjectDir)
#app.config.from_object('config')
app.config['SECRET_KEY'] = 'secret, but not that secret!'

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
Bower(app)
CORS(app)
api = Api(app)
socketio = SocketIO(app,logger=True,engineio_logger=True) #async_mode=async_mode,

@app.route('/<path:path>')
def static_file(path):
    print path, "Static request" , app._static_folder 
    return app.send_static_file(path)

@app.route('/')
def index():
    print "Static request" , app._static_folder + '/index.html'
    return app.send_static_file('index.html')

@app.route('/db_telemetry')
@cache.cached(timeout=50)
def db_telemetry():
    global protocol_rcv, args
    """Requests the current telemetry database"""
    with open(app.config['user_dir'] + '/tlm_db/tlm.json','r') as fid:
        out = json.loads(fid.read())
    print "DB requested"
    return jsonify(out)

@app.route('/saveData', methods=['POST'])
def saveData():
    print request
    data = request.json
    print data
    with open(app.config['user_dir'] + '/data/test.json','w') as fp:
        json.dump(data,fp)
    return 'Success'


@app.route('/getData')
def getData():
    with open(app.config['user_dir'] + '/data/test.json','r') as fp:
        data = json.load(fp)
    return jsonify(data)


async_mode = None
if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()


import importlib

sys.path.insert(0,app.config['user_dir'])
Driver = importlib.import_module('driver', 'driver')
driver = Driver.Driver()
driver.loadMessages()

# Generate the telemetry database for OpenMCT if no database exists
import tlm_dictonary
json_tlm_file = app.config['user_dir'] + '/tlm_db/tlm.json'
if 1: ##not os.path.exists(json_tlm_file):
    with open(app.config['user_dir'] + '/tlm_db/tlm.json','w') as fp:
        tlm_db = tlm_dictonary.GetOpenMCTTlmDict(driver.tlms)
        json.dump(tlm_db,fp)
    print "Tlm DB created from python rdls"

running = False
from tlm_dictonary import CTypeToDict

def background_thread():
    global running
    if running:
       return
    
    running = True
    """Example of how to send server generated events to clients."""
    count = 0

    print 'Grabbing packets'
    while running:
        for z in driver.GetPacket():
            print 'Got packet'
            if z== None:
                print "packet None"
                continue
    
            count += 1
            #Convert the python CType object into json for streaming.
            obj = CTypeToDict(z['obj']) 
            out = {'count': count,
                    'name':z['name'],
                    'time':z['time'],
                    'obj':obj}

            print count, out['name']
            socketio.emit( 'TLM', #'stream',
                            out,
                        namespace='/' , #+ out['name'],
                        broadcast=True)



if args.NoTlmOut == False:
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()    
if __name__ == "__main__":
    print '*'*20 + "Started thread"
    app.run(debug=True,threaded=True)
