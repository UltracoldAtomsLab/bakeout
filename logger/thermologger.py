#!/usr/bin/env python2

import serial
import time
import sys
import pymongo
import datetime

## Settings
baud = 115200
mongoserver = "localhost"
mongoport = 27017
database = "baking"

# Check which port to log on
serialnum = 0 if len(sys.argv) < 2 else int(sys.argv[1])
dev = serial.Serial('/dev/ttyACM%d' %(serialnum), baud, timeout=1)

connection = pymongo.Connection(mongoserver, mongoport)
db = connection.baking
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
            except:
                raise
                pass
            print reading  # show on standard output
            sys.stdout.flush()  # enables following it real-time with cat
    except KeyboardInterrupt:
        break
