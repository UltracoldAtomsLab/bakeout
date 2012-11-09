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

import bottle

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

    def query(self, cmd, **kwargs):
        self.write(cmd)
        return self.readline(kwargs)
                

rga = RGA('ttyS0')
print "#", rga.query("ID?").strip()
rga.write("MI1")
rga.write("MF100")
rga.query("FL1.0")
rga.query("NF4")
n = int(rga.query("HP?"))
rga.write("HS1")
vals = []
print "# Startscan"
for i in range(n):
    x = rga.read(bytes=4)
    # print i+1, [hex(ord(v)) for v in x]
    r = ord(x[0]) + ord(x[1])*(2**8) + ord(x[2])*(2**8)**2 + ord(x[3])*(2**8)**3
    print "%d, %d" %(i+1, r)
    # r = ord(x[3]) + ord(x[2])*256 + ord(x[1])*256**2 + ord(x[0])*256**3
    # print "%d: %d" %(i, r)
p = rga.readline()
# print "Pressure:", p, len(p)
# print rga.query("HS1")


# print rga.readline()
# print rga.readline()
# print rga.readline()


print "# Filament:", rga.query("FL0")
print rga.readline()

# ### Exit code
# def signal_handler(signal, frame):
#     pump.cleanup()
#     sys.exit(0)

# signal.signal(signal.SIGTERM, signal_handler)
# ### Exit code end

# connection = pymongo.Connection(mongos)
# db = connection[database]
# coll = db[collection]

# tdelay = 1

# def senddata(date, dbid, value):
#     """ Sending data to the server
#     """
#     document = {"type": "pressure",
#                 "id": "%s" %(dbid),
#                 "date": date,
#                 "reading": {"value": value,
#                             "unit": "torr"},
#                 "err": None,
#                 }
#     coll.insert(document)

# # Start recording
# nexttime = time.time() + tdelay
# while True:
#     try:
#         while time.time() < nexttime:
#             time.sleep(0.0001)
#         date = datetime.datetime.utcnow()
#         value = pump.getPressure()
#         if value > 1e-11:  # 1e-11 means High Voltage off, <0 means error (in this driver's language)
#             nexttime += tdelay
#             senddata(date, dbid, value)
#             print "%.2f,%g" %(time.time(), value)
#             sys.stdout.flush()  # enables following it real-time with cat
#     except pymongo.errors.AutoReconnect:
#         print "# Trying AutoReconnect"
#         continue
#     except KeyboardInterrupt:
#         pump.cleanup()
#         break
#     except:
#         pump.cleanup()
#         raise
