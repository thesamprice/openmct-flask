import inspect
def GetTlmPackets(module):
    members = inspect.getmembers(module)
    packets = []
    for member in members:
        obj = member[1]
        if hasattr(obj, '_tlm_'):
            packets.append(member)
    return packets


def GetOpenMCTTlmLoggers(module):
    def GetLogger(pkt):
        fmt = """
def Log_{PktName}({PktName},time,dest='./'):
    with open(dest + '/{PktName}', 'ab+' ) as fid:
        data = pack('d', time)
        fid.write(data)    
""".format(PktName=pkt[0])
        typ_dict = {long:'l',
        int:'i',
        float:'d',
        'str':'string'}
        #TODO this takes up more space than is needed ie int8 is same as int32 ...
        for f in CType_FlatNames(pkt[1]):
            if 'string' == typ_dict[f[1]]: #TODO Deal with strings ...
                #Open file, get position, write text
                #Open position file and write position 
                continue
            
            fmt += """
    with open(dest + '/{fname}' , 'ab+') as fid:
        data = pack('{type}', {fname})
        fid.write(data)""".format(type=typ_dict[f[1]],fname=f[0])

        return fmt
    packets = GetTlmPackets(module)
    pkt = packets[0]
    logger = """from struct import pack
"""
    for pkt in packets:
        logger +=  GetLogger(pkt)

    #Now we have a bunch of txt of our functions we want
    code = compile(logger,'LoggerModule','exec')
    #Compile our logging options into namespace
    ns = {}    
    exec(code) in ns
    #Just grab our functions
    funcs = {}
    for pkt in packets:
        fname = 'Log_' + pkt[0]
        funcs[ pkt[0]] = ns[fname]
    
    return funcs
def GetOpenMCTTlmDict(module):
    
    top_folder = 'TLM_db'
    output = {'name':top_folder, 
              'key':top_folder}
    typ_dict = {long:'integer',
                int:'integer',
                float:'float',
                'str':'string'}
    packets = GetTlmPackets(module)
    pkt = packets[0]
    meas = []
    for pkt in packets:
        location = 'example.taxonomy:spacecraft' + '.' + pkt[0]

        loc =   {'key':pkt[0],
                 'name': pkt[0],
                 'type': 'folder',
                 'location': top_folder,
                 'children':[],
                };      

        meas.append(loc)
        for f in CType_FlatNames(pkt[1]):
            print f
            m = {'key':f[0],
                 'name':f[0],
                 'location':pkt[0],
                 'type':'example.telemetry',
                 'children':[],
                 'properites':{
                     'scale':1
                 },
                 'values':[
                    {
                        'key':'value',
                        'name':'Value',
                        'units':'None',
                        # 'min':-1000,
                        # 'max':1000,
                        'format':typ_dict[f[1]],
                        "hints": {
                            "range": 1
                        }
                    },
                    {
                        "key": "utc",
                        "source": "timestamp",
                        "name": "Timestamp",
                        "format": "utc",
                        "hints": {
                            "domain": 1
                        }
                    }
                 ]}
            loc['children'].append(m)
#            meas.append(m)
    output['children'] = meas
    return output
def CType_FlatNames(struct,started=False,name=""):

    if started:
        pass
#        name += '.'
    else:
        name += struct.__class__.__name__

    def get_value(name, value):
         if (type(value) not in [int, long, float, bool,str]) and not bool(value):
             # it's a null pointer
             yield (name, 'pointer',)
         elif hasattr(value, "_length_") and hasattr(value, "_type_"):
             # Probably an array
             #print value
             for f in get_array(name,value):
                 yield f
         elif hasattr(value, "_fields_"):
             # Probably another struct
             for f in CType_FlatNames(value,started=True,name=name):
                 yield f
         elif (type(value) == str):
             yield (name, 'str',)
         else:
             yield (name,type(value),)

    def get_array(name, array):
        aname = name
        cnt = 0
        for value in array:
            aname = name + '[' + str(cnt) + ']'
            for f in get_value(aname,value):
                yield f
            cnt += 1

    for f in struct._fields_:
        field = f[0]
        fname = name + '.' + f[0]
        value = getattr(struct, field)
        # if the type is not a primitive and it evaluates to False ...

        for x in get_value(fname,value):
            yield x


def CTypeToDict(struct):
    result = {}
    #print struct
    def get_value(value):
         if (type(value) not in [int, long, float, bool]) and not bool(value):
             # it's a null pointer
             value = None
         elif hasattr(value, "_length_") and hasattr(value, "_type_"):
             # Probably an array
             #print value

             value = get_array(value)
         elif hasattr(value, "_fields_"):
             # Probably another struct
             value = CTypeToDict(value)
         return value
    def get_array(array):
        ar = []
        for value in array:
            value = get_value(value)
            ar.append(value)
        return ar
    for f  in struct._fields_:
         field = f[0]
         value = getattr(struct, field)
         # if the type is not a primitive and it evaluates to False ...
         value = get_value(value)
         result[field] = value
    return result



def DictToCType(dictonary,dest):
    """Converts a dictionary to a CType"""
    #print struct
    def set_value(src,dest):
        value = src
        if (type(dest) not in [int, long, float, bool,str]) and not bool(dest):
            # it's a null pointer
            value = None
        elif hasattr(dest, "_length_") and hasattr(dest, "_type_"):
            # Probably an array
            #print value
            value = set_array(src,dest)

        elif hasattr(dest, "_fields_"):
            # Probably another struct
            value = DictToCType(src,dest)
        return value
    def set_array(array,dest):
        ind = 0
        for value in array:
            value = set_value(value,dest[ind])
            dest[ind] = value
            ind += 1
        return dest
    for name in dictonary:
         value = dictonary[name]

         try:
             out = getattr(dest, name)
             # if the type is not a primitive and it evaluates to False ...
             v_out = set_value(value,out)

             setattr(dest,name,v_out)
         except AttributeError:
             print "Missing",name
         except TypeError:
             k = type(getattr(dest,name))
             setattr(dest,name,k(value))
         except :
             print  name, value, type(value)
    return dest




if __name__ == "__main__":

    #CType_FlatNames
    import proj_example.rdl.messages as msg
    tlms = type('tlms',(),{})
    tlms.Example_M = msg.Example_M()
    tlms.SPS_M = msg.SPS_M()

    print GetOpenMCTTlmLoggers(tlms)
        
