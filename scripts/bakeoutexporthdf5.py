#!/usr/bin/env python2
"""
Bakeout exporting file

usage: python bakeoutexporthdf5.py servers database collection readingtype outputfile

servers: single, or comma delimited list of servers in replica set localhost:27017 or localhost27017,otherhost:27017
database: database name
collection: collection name
readingtype: reading type to export
outputfile: filename to store output, should end in .h5
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
from tables import *

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

if len(sys.argv) < 6:
    print("usage: %s servers database collection readingtype outputfile" %(sys.argv[0]))
    sys.exit(1)
else:
    servers = sys.argv[1]
    database = sys.argv[2]
    collection = sys.argv[3]
    readingtype = sys.argv[4]
    outputfile = sys.argv[5]

## Settings
mongos = servers.split(',')

## Connect to database
connection = pymongo.Connection(mongos)
db = connection[database]
coll = db[collection]

#Define reading class
class Measurement(IsDescription):
    id = StringCol(24)  # 24 char MongoDB record ID
    err = StringCol(3)  # Error code
    date = StringCol(29)  # Date string
    unit = StringCol(10)  # Reading unit 
    value = FloatCol()  # Reading value, double precision
    readingtype = StringCol(24)  # Reading type
    deviceid = StringCol(10)  # Device ID

## Retrieve data

def findType(measuretype, filename):
    """ find given measurement type in database and record it into file

    measuretype: text of type, eg. "pressure", "temperature"
    filename: output filename (should end in "h5"
    """
    recs = coll.find({"type": measuretype}, sort=[('date', 1)])
    h5file = openFile(filename, mode = "w", title = "Readings-%s" %(measuretype))
    group = h5file.createGroup("/", 'bakeout', 'Bakeout recording of %s' %(measuretype))
    table = h5file.createTable(group, 'reading', Measurement, "Measurement readings")
    reading = table.row
    for r in recs:
        reading['id'] = r['_id']
        reading['err'] = r['err']
        reading['date'] = getDate(r['date'])
        reading['unit'] = r['reading']['unit']
        reading['value'] = r['reading']['value']
        reading['readingtype'] = measuretype
        reading['deviceid'] = r['id']
        # Insert new record
        reading.append()
    # Close (and flush) the file
    h5file.close()

print "Type: %s" %(readingtype)
findType(readingtype, outputfile)

# def findRGA(filename):
#     recs = coll.find({"type": "rga"}, sort=[('date', 1)])
#     f = open(filename, "w")
#     header = "Date,units"
#     for i in range(1,201):
#         header += ",AMU%d" %(i)
#     f.write(header+"\n")
#     for r in recs:
#         out = "%s,%s" %(getDate(r['date']), r['reading']['unit'])
#         vals = {}
#         for element in r['reading']['scan']:
#             vals[element['amu']] = element['value']
#         for i in range(1, 201):
#             out += ",%g" %(vals[i])
#         f.write(out+"\n")
#     f.close()

# print "RGA"
# findRGA("bakeout_rga.csv")

print "Done"
