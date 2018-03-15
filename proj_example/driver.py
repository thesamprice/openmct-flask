import inspect
from time import sleep,time
import random
import ctypes
import rdl.messages as module

def AddArgs(arg_parser):
    arg_parser.add_argument('--tlm_delay',  default=.1,type=float, help='Seconds delay between each ')
    return arg_parser

class Driver(object):
    
    running = 1
    def __init__(self,args):
        self._tlms =  type('tlmdb', (object,), {})
        self.messages = []
        self.loadMessages()
        self.args = args
    def loadMessages(self):

        # Use the inspect module to find all of the structures in this module
        # That are tagged with _tlm_
        members = inspect.getmembers(module)
        packets = []
        for member in members:
            obj = member[1]
            if hasattr(obj, '_tlm_'):
                tlm_buff = bytearray(ctypes.sizeof(obj))
                tlm_obj = obj.from_buffer(tlm_buff)

                setattr(self._tlms, member[0], tlm_obj)
                self.messages.append({'name':member[0],
                                      'type':member[1],
                                      'buffer':tlm_buff,
                                      'obj':tlm_obj})

    @property
    def tlms(self):
        return self._tlms

    def GetPacket(self):
        """Gets one packet, decodes it into a python ctype object and returns it.
           In reality you would grab the header off the serial port / tcp,
           CHeck the apid,
           copy the header into the tlm buffer matching the apid
           grab the rest of the packet into the tlm buffer.
        """
        tlms = self.tlms
        while(self.running):
            tlms.SPS_M.x += random.random() -.5
            tlms.SPS_M.y += random.random() -.5
            tlms.SPS_M.z += random.random() -.5

            yield {'time':time(),'name':'SPS_M', 'obj':tlms.SPS_M}
            sleep(.2)

            tlms.Example_M.temp_a += int( random.random() * 10) -5
            tlms.Example_M.temp_b += int(random.random() *10 ) -5
            tlms.Example_M.temp_c[0] += int(random.random() *10 ) -5
            yield {'time':time(),'name':'Example_M', 'obj':tlms.Example_M}
            sleep(.2)