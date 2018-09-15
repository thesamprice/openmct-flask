
from tlm_dictonary import CType_FlatNames,GetTlmPackets
import sqlite3
tdict = {int: "INT",
        'str': "TEXT",
        long:"BIGINT",
        float: "FLOAT"}
def CNameToSQLName(name):
    name = name.split('.')
    name = '.'.join(name[1:])
    name = name.replace('[','_')
    name = name.replace(']','_')
    name = name.replace('.','_')
    if name == 'rcv_time':
        name = "_rcv_time"
    return name
def _BuildTblFromStruct(struct, drop=True):
    name = type(struct).__name__
    txt = ""
    if drop:
        txt += "DROP TABLE IF EXISTS {name};\n".format(name=name)
    txt = "CREATE TABLE IF NOT EXISTS {name} (\n".format(name=name)
    rows = [ "  rcv_time LONG NOT NULL"]
    for x in CType_FlatNames(struct):
        cname = x[0]
        cname = CNameToSQLName(cname)
        ttype = x[1]
        ctype = tdict[ttype]
        rowtxt = "  {cname} {data_type} NOT NULL".format(cname=cname, data_type=ctype)
        rows.append(rowtxt)
    rowtxt = ',\n'.join(rows)
    txt += rowtxt
    txt += "\n);"
    return txt
def  _BuildTblInsertFromStruct(struct):
    name = type(struct).__name__

    txt  = 'def SQLiteInsert_{name}({name},rcv_time,cur):\n'.format(name=name)
    txt += '    query = """Insert into {name}'.format(name=name)
    cnames = ["rcv_time"]
    qs = ["?"]
    names = ["rcv_time"]
    for x in CType_FlatNames(struct):
        names.append(x[0])
        cname = x[0]
        cname = CNameToSQLName(cname)
        cnames.append(cname)
        qs.append('?')
    txt += '\n(\n        ' + ',\n        '.join(cnames) + '\n)\n'
    txt += '\nvalues(\n  ' + ',\n        '.join(qs) 

    txt += '\n);"""\n'

    txt += '    return cur.execute(query, (' + ',\n        '.join(names) +') )\n\n'
    return txt




def _BuildDatabaseTxtFromModule(module):
    packets = GetTlmPackets(module)
    txt = ""
    for pkt in packets:
        txt += _BuildTblFromStruct(pkt[1])
        txt += "\n\n\n"
        # fname = 'Log_' + pkt[0]
        # funcs[ pkt[0]] = ns[fname]
    return txt

def GetOpenMCTTlmLoggers(module):
    packets = GetTlmPackets(module)
    pkt = packets[0]
    logger = """import sqlite3
"""
    for pkt in packets:
        logger +=  _BuildTblInsertFromStruct(pkt[1])

    #Now we have a bunch of txt of our functions we want
    code = compile(logger,'SQLLoggerModule','exec')
    #Compile our logging options into namespace
    ns = {}    
    exec(code) in ns
    #Just grab our functions
    funcs = {}
    for pkt in packets:
        fname = 'SQLiteInsert_' + pkt[0]
        funcs[ pkt[0]] = ns[fname]
    
    return funcs
def CreateDatabase(name,module):
    conn = sqlite3.connect(name,check_same_thread=False)
    c = conn.cursor()
    query = _BuildDatabaseTxtFromModule(module)
    c.executescript(query)
    conn.commit()
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conn.row_factory = dict_factory
    return conn
if __name__ == "__main__":

    #CType_FlatNames
    import proj_example.rdl.messages as msg
    tlms = type('tlms',(),{})
    tlms.Example_M = msg.Example_M()
    tlms.SPS_M = msg.SPS_M()

    print _BuildTblInsertFromStruct(tlms.Example_M)
    print GetOpenMCTTlmLoggers(tlms)
    CreateDatabase('test.db', tlms)
    
