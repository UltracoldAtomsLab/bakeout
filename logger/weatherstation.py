#!/usr/bin/env python2

import serial
import time
import sys
import pymongo
import datetime
import ConfigParser

config = ConfigParser.SafeConfigParser({'baud': 115200,
                                        'hosts': 'localhost:27017',
                                        'comid': 'ACM0',
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
comid = config.get('Gauge', 'comid')
dev = serial.Serial('/dev/tty%s' %(comid), baud, timeout=2)

connection = pymongo.Connection(mongos)
db = connection[database]
coll = db.readings

# Keep reading until Ctrl-C
print "#Date,Humidity(%),Resistance(kOhm),Temperature(C)"
while True:
    try:
        reading = dev.readline().strip()
        if len(reading) > 0:
            date = datetime.datetime.utcnow()
            try:
                humidity, resistance, temperature = reading.strip().split(",")
                humidity, resistance, temperature = float(humidity), float(resistance), float(temperature) 
                document = {"humidity": humidity,
                            "temperature": temperature,
                            "date": date,
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
