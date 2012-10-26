#!/usr/bin/env python2

import serial
import time
import sys
import pymongo
import datetime
import ConfigParser

config = ConfigParser.SafeConfigParser({'baud': 9600,
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
dbid = config.get('Gauge', 'dbid')

# Check which port to log on
baud = config.getint('Gauge', 'baud')

class DualGauge:

    teststring = '>005 uC ver. 1.6.6  \r'  # microcontroller version string

    def __init__(self, com=None, baud=9600):
        found = False
        self.dev = None
        if com:
            try:
                self.dev = serial.Serial("/dev/%s" %(com),
                                         baud,
                                         bytesize=serial.EIGHTBITS,
                                         stopbits=serial.STOPBITS_ONE,
                                         parity=serial.PARITY_NONE,
                                         timeout=1,
                                         )
                found = True
            except serial.SerialException:
                errormsg = "Can't connect to %s" %(usb)
        else:
            for port in range(0, 10):
                try:
                    self.dev = serial.Serial("/dev/ttyUSB%d" %(port),
                                             baud,
                                             bytesize=serial.EIGHTBITS,
                                             stopbits=serial.STOPBITS_ONE,
                                             parity=serial.PARITY_NONE,
                                             timeout=1,
                                             )
                    q = self.query("005?")
                    if q == self.teststring:
                        print "# IonGauge on ttyUSB%d" %(port)
                        found = True
                        break
                except serial.SerialException:
                    continue
            if not found:
                errormsg = "Can't find correct USB"
        if not found:
            raise IOError(errormsg)

    def write(self, cmd):
        self.dev.write("#"+cmd+"\r")

    def read(self, bytes=1):
        return self.dev.read(bytes)

    def readline(self, eol='\r', maxchars=None, timeout=1):
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
            if char == eol:
                break
        return "".join(out)

    def query(self, cmd):
        self.write(cmd)
        return self.readline()

    def getPressure(self, channel=1):
        q = "%d02?" %(channel)
        res = self.query(q)
        try:
            value = float(res[4:-1])
        except:
            raise
            value = -1
        return value

gauge = DualGauge()

connection = pymongo.Connection(mongos)
db = connection[database]
coll = db[collection]

tdelay = 1

def senddata(date, dbid, value):
    """ Sending data to the server
    """
    document = {"type": "pressure",
                "id": "%s" %(dbid),
                "date": date,
                "reading": {"value": value,
                            "unit": "torr"},
                "err": None,
                }
    coll.insert(document)

# Start recording
nexttime = time.time() + tdelay
while True:
    try:
        while time.time() < nexttime:
            time.sleep(0.0001)
        date = datetime.datetime.utcnow()
        value = gauge.getPressure()
        if value > 0:
            nexttime += tdelay
            # senddata(date, dbid, value)
            print "%.2f,%g" %(time.time(), value)
            sys.stdout.flush()  # enables following it real-time with cat
    except pymongo.errors.AutoReconnect:
	continue
    except KeyboardInterrupt:
        break
