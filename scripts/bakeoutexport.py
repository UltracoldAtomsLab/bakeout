#!/usr/bin/env python2
"""
RGA long term logging output
"""
import time
import sys
import pymongo
import datetime
import ConfigParser
import numpy as np
import pylab as pl
import pytz
import matplotlib.dates as mdates

# Current timezone info, a tuple of a pytz timezone and
# a string of correct offset for printing ISO 8601 timezone offset
tzinfo = (pytz.timezone('Asia/Taipei'), "+08:00")
def getDate(indate):
    """Turning MongoDB date object into ISO8601 date format
    by adding time zone information, and adjusting for Taiwan

    input: date object
    output: date string
    """
    t1 = indate.replace(tzinfo=pytz.timezone('UTC'))
    t2 = t1.astimezone(tzinfo[0])
    isotime = t2.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + tzinfo[1]  # microseconds included and time zone too
    return isotime


config = ConfigParser.SafeConfigParser({'hosts': 'localhost:27017'})

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

## Connect to database
connection = pymongo.Connection(mongos)
db = connection[database]
coll = db[collection]

## Retrieve data
# recs = coll.find({"type": "rga"}, sort=[('date', 1)])

def findType(measuretype, filename):
    recs = coll.find({"type": measuretype}, sort=[('date', 1)])
    f = open(filename, "w")
    header = "#Date, sensor ID, value, unit, error code"
    f.write(header+"\n")
    for r in recs:
        out = "%s,%s,%g,%s,%s" %(getDate(r['date']), r['id'], r['reading']['value'],r['reading']['unit'], r['err'])
        f.write(out+"\n")
    f.close()

print "temperatures"
findType("temperature", "bakeout_temperature.csv")
print "pressures"
findType("pressure", "bakeout_pressure.csv")

def findRGA(filename):
    recs = coll.find({"type": "rga"}, sort=[('date', 1)])
    f = open(filename, "w")
    header = "Date,units"
    for i in range(1,201):
        header += ",AMU%d" %(i)
    f.write(header+"\n")
    for r in recs:
        out = "%s,%s" %(getDate(r['date']), r['reading']['unit'])
        vals = {}
        for element in r['reading']['scan']:
            vals[element['amu']] = element['value']
        for i in range(1, 201):
            out += ",%g" %(vals[i])
        f.write(out+"\n")
    f.close()

print "RGA"
findRGA("bakeout_rga.csv")

print "Done"
