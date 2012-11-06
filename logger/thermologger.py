#!/usr/bin/env python2

import serial
import time
import sys
import pymongo
import datetime
import ConfigParser

config = ConfigParser.SafeConfigParser({'baud': 115200,
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
dev = serial.Serial('/dev/ttyACM%d' %(serialnum), baud, timeout=1)

connection = pymongo.Connection(mongos)
db = connection[database]
coll = db.readings

# Need to do read-delay for Arduino Mega ADK, otherwise
# we get a lot of previous junk
delay = 0.05
finish = time.time() + delay
while time.time() < finish:
    dev.readline()


# Keep reading until Ctrl-C
print "#HotJunction(C),ColdJunction(C)"
while True:
    try:
        reading = dev.readline().strip()
        if len(reading) > 0:
            date = datetime.datetime.utcnow()
            try:
                idnum, tc, cc, ctime, err = reading.strip().split(",")
                idnum, tc, cc = int(idnum), float(tc), float(cc)
                document = {"type": "temperature",
                            "id": "tc%d" %(idnum),
                            "date": date,
                            "reading": {"value": tc,
                                        "unit": "C"},
                            "err": err,
                            }
                coll.insert(document)

                if idnum == 0:
                    document = {"type": "temperature",
                                "id": "coldpoint",
                                "date": date,
                                "reading": {"value": cc,
                                            "unit": "C"},
                                "err": None,
                                }
                    coll.insert(document)
            except ValueError:
                raise # Make sure we crash
            print reading  # show on standard output
            sys.stdout.flush()  # enables following it real-time with cat
    except pymongo.errors.AutoReconnect:
        print "# Trying AutoReconnect"
        continue
    except KeyboardInterrupt:
        break
