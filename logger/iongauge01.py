#!/usr/bin/env python2
"""
Varian XGS-600 ion gauge controller and logging
"""
import serial
import time
import sys
import pymongo
import datetime
import ConfigParser
import os
import signal

config = ConfigParser.SafeConfigParser({'baud': 38400,
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
gaugeid = config.get('Gauge', 'gaugeid')

# Check which port to log on
baud = config.getint('Gauge', 'baud')

class IonGauge:
    """ IonGauge Controller XGS-600
    """
    teststring = [">0200,0150\r", ">0170,0150\r"]  # this are our current software revision strings, the see if we found our gauge
    lockfile = None

    def __init__(self, gaugeid, baud=19200, usb=None):
        found = False
        self.dev = None
        self.gaugeid = gaugeid
        if usb:
            try:
                self.dev = serial.Serial("/dev/%s" %(usb), baud, parity=serial.PARITY_NONE, timeout=2)
                found = True
            except serial.SerialException:
                errormsg = "Can't connect to %s" %(usb)
        else:
            for port in range(0, 10):
                try:
                    portname = "/dev/ttyUSB%d" %(port)
                    self.lockfile = portname.split('/')[-1] + '.lock'
                    if os.path.exists(self.lockfile):
                        print "# Skipped %s because it appears locked" %(portname)
                        continue
                    else:
                        open(self.lockfile, 'w').close()
                    self.dev = serial.Serial(portname, baud, parity=serial.PARITY_NONE, timeout=2)
                    q = self.query("05", 11)
                    if q in self.teststring:
                        v, r = self.getPressure()
                        if v is not None:
                            print "# IonGauge on ttyUSB%d" %(port)
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

    def query(self, cmd, bytes=None):
        """ Run a query for a given command
        """
        self.dev.write("#00"+cmd+"\r")
        return self.dev.readline(bytes)

    def getPressure(self):
        """ Get pressure reading for a given Gauge ID
        """
        reading = self.query("02U%s" %(self.gaugeid), 11)
        try:
            value = float(reading[1:-1])  # input format ">x.xxxE-xx\r"
        except ValueError:
            value = None
        return value, reading


gauge = IonGauge(gaugeid, baud)

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

### Exit code
def cleanup(dev):
    print "# Exiting"
    if dev.lockfile and os.path.exists(dev.lockfile):
        print "# Removing lockfile"
        os.remove(dev.lockfile)

def signal_handler(signal, frame):
    cleanup(gauge)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
### Exit code end

# Start recording
nexttime = time.time() + tdelay
while True:
    try:
        while time.time() < nexttime:
            time.sleep(0.0001)
        date = datetime.datetime.utcnow()
        value, reading = gauge.getPressure()
        if value == None:
            print "# ValueError: %s" %(reading.strip())
            cleanup(gauge)
            break
        if value > 0:
            nexttime += tdelay
            senddata(date, dbid, value)
            print "%.2f,%g" %(time.time(), value)
            sys.stdout.flush()  # enables following it real-time with cat
    except pymongo.errors.AutoReconnect:
	continue
    except KeyboardInterrupt:
        cleanup(gauge)
        break
    except:
        cleanup(gauge)
        raise
