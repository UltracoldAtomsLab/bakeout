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

# Check which port to log on
baud = config.getint('Gauge', 'baud')
serialnum = config.getint('Gauge', 'com')
dev = serial.Serial('/dev/ttyS%d' %(serialnum), baud, timeout=2)

connection = pymongo.Connection(mongos)
db = connection[database]
coll = db.readings

def senddata(date, idnum, value):
    document = {"type": "pressure",
                "id": "vc%d" %(idnum),
                "date": date,
                "reading": {"value": value,
                            "unit": "torr"},
                "err": None,
                }
    coll.insert(document)

while True:
    try:
        line = dev.readline().strip()
        date = datetime.datetime.utcnow()

        vals = line.split(",")
        s1 = int(vals[0])
        if s1 == 0:
            r1 = float(vals[1])
            senddata(date, 0, r1)
        s2 = int(vals[2])
        if s2 == 0:
            r2 = float(vals[3])
            senddata(date, 1, r2)
        print time.time(), ",", line
        sys.stdout.flush()  # enables following it real-time with cat
    except pymongo.errors.AutoReconnect:
	continue
    except KeyboardInterrupt:
        break
