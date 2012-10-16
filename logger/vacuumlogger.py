#!/usr/bin/env python2

import serial
import time
import sys
import pymongo
import datetime

## Settings
baud = 38400
mongoserver = "brown.local"
mongoport = 27017
database = "baking"

# Check which port to log on
serialnum = 0 if len(sys.argv) < 2 else int(sys.argv[1])
dev = serial.Serial('/dev/ttyS%d' %(serialnum), baud, timeout=2)

connection = pymongo.Connection(mongoserver, mongoport)
db = connection.baking
coll = db.readings

def senddata(date, idnum, value):
    document = {"type": "pressure",
                "id": "vc%d" %(idnum),
                "date": date,
                "reading": {"value": value,
                            "unit": "C"},
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
    except KeyboardInterrupt:
        break
