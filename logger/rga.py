#!/usr/bin/env python2
"""
Stanford Research Systems RGA-200 controllers
"""
import serial
import time
import sys
import pymongo
import datetime
import ConfigParser
import os
import signal
from bitstring import BitArray

config = ConfigParser.SafeConfigParser({'baud': 28800,
                                        'hosts': 'localhost:27017',
                                        })
if len(sys.argv) < 2:
    print("usage: %s configfile" %(sys.argv[0]))
    sys.exit(1)
else:
    configfile = sys.argv[1]
    try:
        config.read(configfile)
    except:
        raise

## Settings
mongos = config.get('Database', 'hosts').split(',')
database = config.get('Database', 'database')
collection = config.get('Database', 'collection')
dbid = config.get('Database', 'dbid')

class RGA:

    cmdterm = '\n\r'
    teststring = 'SRSRGA200VER0.24SN14067'  # The reply to "ID?\r"

    def __init__(self, com=None):
        found = False
        self.dev = None
        if com:
            try:
                self.dev = serial.Serial("/dev/%s" %(com),
                                         baudrate=28800,
                                         bytesize=serial.EIGHTBITS,
                                         stopbits=serial.STOPBITS_ONE,
                                         parity=serial.PARITY_NONE,
                                         timeout=5,
                                         rtscts=True,
                                         xonxoff=None,
                                         dsrdtr=None,
                                         )
                found = True
            except serial.SerialException:
                errormsg = "Can't connect to %s" %(com)
        else:
            for port in range(0, 10):
                try:
                    portname = "/dev/ttyUSB%d" %(port)
                    self.lockfile = portname.split('/')[-1] + '.lock'
                    if os.path.exists(self.lockfile):
                        continue
                    else:
                        open(self.lockfile, 'w').close()
                    self.dev = serial.Serial(portname,
                                             baudrate=28800,
                                             bytesize=serial.EIGHTBITS,
                                             stopbits=serial.STOPBITS_ONE,
                                             parity=serial.PARITY_NONE,
                                             timeout=5,
                                             rtscts=True,
                                             xonxoff=None,
                                             dsrdtr=None,
                                             )
                    q = self.query("ID?").strip()
                    if q == self.teststring:
                        print "# RGA on %s" %(portname)
                        found = True
                        break
                    if os.path.exists(self.lockfile):
                        os.remove(self.lockfile)
                except serial.SerialException:
                    if os.path.exists(self.lockfile):
                        os.remove(self.lockfile)
                    self.lockfile = None
                    continue
            if not found:
                errormsg = "Can't find correct USB"
        if not found:
            raise IOError(errormsg)

    def write(self, cmd):
        q = "%s%s" %(cmd, self.cmdterm)
        self.dev.write(q)
            
    def read(self, bytes=1):
        return self.dev.read(bytes)

    def readline(self, eol='\r', maxchars=None, timeout=5, binary=False):
        """Readline with variable end of line character, since Serial does
        not do that anymore (?)

        eol: end of line char
        maxchars: number of max characters to read, or None for no such limit

        return: read line
        """
        out = []
        until = time.time()+timeout
        while (time.time() < until ) and ((maxchars is None) or (len(out) < maxchars)):
            char = self.read(1)
            out += [char]
            if (not binary) and (char == eol):
                break
        return "".join(out)

    def query(self, cmd):
        self.write(cmd)
        return self.readline()

def bintonum(x):
    """ x is an array of bytes, return 2's complements interpetation """
    temp = ["{0:08b}".format(ord(part)) for part in x]
    temp.reverse() # it is little endian
    binstr = "".join(temp)
    val = BitArray(bin=binstr)
    return val.int

connection = pymongo.Connection(mongos)
db = connection[database]
coll = db[collection]

rga = RGA('ttyS0')
print "#", rga.query("ID?").strip()

def senddata(date, dbid, scan):
    """ Sending data to the server
    """
    document = {"type": "rga",
                "id": "%s" %(dbid),
                "date": date,
                "reading": {"scan": scan,
                            "unit": "1e-16 A"},
                "err": None,
                }
    coll.insert(document)

def dorun(sens=4):
    rga.write("MI1")
    rga.write("MF200")
    rga.query("FL1.0")
    rga.query("NF%d" %sens)
    n = int(rga.query("HP?"))
    rga.write("HS1")
    date = datetime.datetime.utcnow()
    vals = []
    print "# Startscan"
    for i in range(n):
        x = rga.read(bytes=4)
        r = bintonum(x)
        print "%d, %d" %(i+1, r)
        vals += [{'amu': i+1, 'value': r}]
    p = rga.read(bytes=4)  # Get pressure reading
    err = rga.query("ER?")
    print "# Error byte: %X" %(int(err))
    print "# Filament:", rga.query("FL0")
    senddata(date, dbid, vals)

### Exit code
def signal_handler(signal, frame):
    print "# Filament:", rga.query("FL0")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
### Exit code end

try:
    dorun(sens=2)
except pymongo.errors.AutoReconnect:
    pass
except KeyboardInterrupt:
    print "# Filament:", rga.query("FL0")
except:
    print "# Filament:", rga.query("FL0")
    raise
