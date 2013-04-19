#!/usr/bin/env python2

import serial
import time
import sys
import pymongo
import datetime
import ConfigParser
import os
import signal

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
baud = config.getint('Device', 'baud')
combase = config.get('Device', 'combase')

class WeatherStation:
    """ Thermologger device """

    teststring= 'H,'  # every string received has to start with that

    def __init__(self, com=None, baud=115200):
        found = False
        self.dev = None
        if com:
            try:
                self.dev = serial.Serial("%s" %(com),
                                         baud,
                                         timeout=1,
                                         )
                found = True
            except serial.SerialException:
                errormsg = "Can't connect to %s" %(com)
        else:
            for port in range(0, 20):
                try:
                    portname = "%s%d" %(combase, port)
                    self.lockfile = portname.split('/')[-1] + '.lock'
                    if os.path.exists(self.lockfile):
                        continue
                    else:
                        if os.name <> 'nt':
                            open(self.lockfile, 'w').close()
                    self.dev = serial.Serial(portname,
                                             baud,
                                             timeout=1,
                                             )
                    # Need to do read-delay for Arduino Mega ADK, otherwise
                    # we get a lot of previous junk
                    delay = 0.2
                    finish = time.time() + delay
                    while time.time() < finish:
                        self.dev.readline()
                    # Have to test substring, since the reply is checksummed
                    # and change according to the given instrument ID
                    r = self.dev.readline()
                    if len(r) > 2 and r[0:len(self.teststring)] == self.teststring:
                        print "# Weatherstation on %s" %(portname)
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

    def readline(self):
        return self.dev.readline()

    def cleanup(self, debug=True):
        if self.lockfile and os.path.exists(self.lockfile):
            if debug:
                print "# Removing lockfile"
            os.remove(self.lockfile)
        else:
            if debug:
                print "# No lockfile to clean up"

dev = WeatherStation()

connection = pymongo.Connection(mongos)
db = connection[database]
coll = db.readings

### Exit code
def signal_handler(signal, frame):
    dev.cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
### Exit code end

# Keep reading until Ctrl-C
print "#Date,Humidity(%),Resistance(kOhm),Temperature(C)"
while True:
    try:
        reading = dev.readline().strip()
        if len(reading) > 0:
            date = datetime.datetime.utcnow()
            try:
                id, humidity, resistance, temperature = reading.strip().split(",")
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
        dev.cleanup()
        break
    except:
        dev.cleanup()
        raise
