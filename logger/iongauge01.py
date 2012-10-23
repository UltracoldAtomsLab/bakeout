#!/usr/bin/env python2

import serial
import time
import sys
import pymongo
import datetime
import ConfigParser

config = ConfigParser.SafeConfigParser({'baud': 38400,
                                        'hosts': 'localhost:27017',
                                        'com': 0,
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

# Check which port to log on
baud = config.getint('Gauge', 'baud')
serialconn = config.get('Gauge', 'com')
dev = serial.Serial('/dev/tty%s' %(serialconn), baud, parity=serial.PARITY_NONE, timeout=2)
dbid = config.get('Gauge', 'dbid')
gaugeid = config.get('Gauge', 'gaugeid')

def query(cmd, bytes=None):
    dev.write("#00"+cmd+"\r")
    return dev.readline(bytes)

def getPressure(gaugeid):
    reading = query("02U%s" %(gaugeid), 11)
    value = float(reading[1:-1])  # input format ">x.xxxE-xx\r"
    return value

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
        value = getPressure(gaugeid)
        nexttime += tdelay
        senddata(date, dbid, value)
        print "%.2f,%g" %(time.time(), value)
        sys.stdout.flush()  # enables following it real-time with cat
    except pymongo.errors.AutoReconnect:
	continue
    except KeyboardInterrupt:
        break
