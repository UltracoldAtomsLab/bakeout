#!/usr/bin/env python2
"""
Gamma Vacuum SPCe controller
"""
import serial
import time
import sys
import pymongo
import datetime
import ConfigParser
import os
import signal

config = ConfigParser.SafeConfigParser({'baud': 11520,
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
devid = config.getint('Gauge', 'devid')

class GVPump:

    # Partial ion pump controller model number q[2:-3]
    # Full is e.g. "07 OK 00 DIGITEL SPCe 4E\r" with channel number (07), and checksum (4E)
    teststring = ' OK 00 DIGITEL SPCe '
    cmdstart = '~'
    cmdterm = '\r'

    def __init__(self, idnum, com=None, baud=115200):
        found = False
        self.dev = None
        self.id = "%0.2X" %(idnum)
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
                                             baud,
                                             bytesize=serial.EIGHTBITS,
                                             stopbits=serial.STOPBITS_ONE,
                                             parity=serial.PARITY_NONE,
                                             timeout=1,
                                             )
                    # Have to test substring, since the reply is checksummed
                    # and change according to the given instrument ID
                    q = self.query("01")[2:-3]
                    if q == self.teststring:
                        print "# IonPump on ttyUSB%d" %(port)
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

    def __checksum(self, content):
        """Calculate command checksum
        Manual page 31 has description:
        'add decimal values of all characters in the packet, excluding start,
        checksum, and terminator. Divide result by 256 and the integer remainder
        converted to two ASCII hex digits is the checksum for the command.'
        E.g. '~ 01 01 XX' + carriage return whre XX is the as of now unknown
        checksum, will give XX=22

        Input:
        ======
        content: the command data excluding the start, checksum, and terminator,
                 eg. for the above one it would be ' 01 01 ' (together with spaces

        Output:
        =======
        2-char checksum value
        """
        return "%0.2X" %(sum([ord(c) for c in content]) % 256)

    def write(self, cmd, data=None):
        cmdstr = ' %s %s ' %(self.id, cmd)
        if data:
            cmdstr += '%s ' %(data)
        chksum = self.__checksum(cmdstr)
        out = self.cmdstart + cmdstr + chksum + self.cmdterm
        self.dev.write(out)

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

    def query(self, cmd, data=None):
        self.write(cmd, data)
        return self.readline()

    def getPressure(self, chksum=True):
        q = "0B"
        res = self.query(q)
        # Result is different in high resolution and normal modes:
        # Normal resolutuion: "9.7E-09"
        # High resolution: "9.71E-09"
        # If 8 characters are taken into account, then it can always be correctly converted
        try:
            value = float(res[9:17])
        except:
            raise
            value = -1
        return value

    def cleanup(self, debug=True):
        if self.lockfile and os.path.exists(self.lockfile):
            if debug:
                print "# Removing lockfile"
            os.remove(self.lockfile)
        else:
            if debug:
                print "# No lockfile to clean up"

pump = GVPump(devid, baud=baud)

### Exit code
def signal_handler(signal, frame):
    pump.cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
### Exit code end

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
        value = pump.getPressure()
        nexttime += tdelay
        if value > 1e-11:  # 1e-11 means High Voltage off, <0 means error (in this driver's language)
            senddata(date, dbid, value)
            print "%.2f,%g" %(time.time(), value)
            sys.stdout.flush()  # enables following it real-time with cat
    except pymongo.errors.AutoReconnect:
        print "# Trying AutoReconnect"
        continue
    except KeyboardInterrupt:
        pump.cleanup()
        break
    except:
        pump.cleanup()
        raise
