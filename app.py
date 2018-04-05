from flask import Flask, render_template,send_from_directory
#from flask.ext.socketio import SocketIO, emit
from flask_socketio import SocketIO, emit
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

import eventlet
eventlet.monkey_patch()


arg_parser = argparse.ArgumentParser(description='python based telemetry and command streamer.',add_help=False)
arg_parser.add_argument('--ProjectDir',  default='proj_example',type=str, help='Project folder to pull configuration data from')
arg_parser.add_argument('--NoTlmOut',  action="store_true", help='Disables output telemetry')
arg_parser.add_argument('-v','--verbose',  action="store_true", help='Disables verbose output')
arg_parser.add_argument('--regen_tlmdb',  action="store_true", help='Regenerates the telemetry database')
#arg_parser.add_argument('--uart',    type=str,help='UART device to pull data from')
#arg_parser.add_argument('-h', '--help',  action="store_true", help='Disables output telemetry')
arg_parser.add_help = False
args = arg_parser.parse_known_args()[0]

app = Flask(__name__)

app._static_folder = os.path.dirname(sys.argv[0]) + './openmct-tutorial'
app._static_folder = os.path.abspath(app._static_folder)
app.config.update(user_dir=args.ProjectDir)
#app.config.from_object('config')
app.config['SECRET_KEY'] = 'secret, but not that secret!'

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
Bower(app)
CORS(app)
api = Api(app)
socketio = SocketIO(app,logger=args.verbose,engineio_logger=args.verbose) #async_mode=async_mode,

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

@app.route('/pages/<path:path>', methods=['POST','PUT'])
def saveData(path):
    print request, path
    data = request.json
    print data
    #TODO Securify path
    full_path = app.config['user_dir'] + '/pages/' + path

    if os.path.isdir(full_path):
        pass

    with open( full_path ,'w') as fp:
        json.dump(data,fp,indent=1)

    return 'Success'


@app.route('/pages/<path:path>')
def getData(path):
        #TODO Securify path
    full_path = app.config['user_dir'] + '/pages/' + path
    print 'Request', full_path
    if os.path.isdir(full_path):
        data = {'type':'dir',
         'name':path.split('/')[-1],
         'children':os.listdir(full_path)}
        return jsonify(data)
    elif os.path.exists(full_path ):
        with open( full_path ,'r') as fp:
            data = json.load(fp)
            return jsonify(data)


@app.route('/pages')
def getPagesRoot():
    return getData('')


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

if hasattr(Driver, 'AddArgs'):
    arg_parser = Driver.AddArgs(arg_parser)

arg_parser.add_help = True

arg_parser.add_argument(
                '-h', '--help',
                action='help', default=argparse.SUPPRESS,
                help=argparse._('show this help message and exit'))

args = arg_parser.parse_args()

driver = Driver.Driver(args)


# Generate the telemetry database for OpenMCT if no database exists
import tlm_dictonary
json_tlm_file = app.config['user_dir'] + '/tlm_db/tlm.json'
if not os.path.exists(json_tlm_file) or args.regen_tlmdb:
    with open(app.config['user_dir'] + '/tlm_db/tlm.json','w') as fp:
        tlm_db = tlm_dictonary.GetOpenMCTTlmDict(driver.tlms)
        json.dump(tlm_db,fp,indent=1)
    print "Tlm DB created from python rdls"

#Generate the file loggers
tlm_loggers = tlm_dictonary.GetOpenMCTTlmLoggers(driver.tlms)

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
    logging_dest = app.config['user_dir'] + '/hist_data/'
    while running:
        for z in driver.GetPacket():
            #print 'Got packet'
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
            
            if args.verbose or 1:
                print count, out['name']

            #Emit out to different channels
            socketio.emit( 'TLM', #'stream',
                            out,
                        namespace='/' , #+ out['name'],
                        broadcast=True)

            #Log out the packet to a make shift database?
            # if z['name'] in tlm_loggers:
            #     tlm_loggers[z['name']](z['obj'], z['time'], logging_dest)




if args.NoTlmOut == False:
#    thread = Thread(target=background_thread)
#    thread.daemon = True
#    thread.start()    
    eventlet.spawn(background_thread)
if __name__ == "__main__":
    print '*'*20 + "Started thread"
    socketio.run(app,host='127.0.0.1')
#    app.run(debug=False,threaded=True)
