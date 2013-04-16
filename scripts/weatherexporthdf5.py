#!/usr/bin/env python2
"""
Weatherstation export

usage: python weatherexporthdf5.py servers database collection outputfile

servers: single, or comma delimited list of servers in replica set localhost:27017 or localhost27017,otherhost:27017
database: database name
collection: collection name
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

if len(sys.argv) < 5:
    print("usage: %s servers database collection outputfile" %(sys.argv[0]))
    sys.exit(1)
else:
    servers = sys.argv[1]
    database = sys.argv[2]
    collection = sys.argv[3]
    outputfile = sys.argv[4]

## Settings
mongos = servers.split(',')

## Connect to database
connection = pymongo.Connection(mongos)
db = connection[database]
coll = db[collection]

#Define reading class
class Weather(IsDescription):
    id = StringCol(24)  # 24 char MongoDB record ID
    date = StringCol(29)  # Date string
    temperature = FloatCol()  # Temperature reading, double precision
    humidity = FloatCol()  # Humidity reading, double precision

## Retrieve data

def export(filename):
    """ export data into file

    filename: output filename, should end in "h5"
    """
    recs = coll.find({}, sort=[('date', 1)])
    h5file = openFile(filename, mode = "w", title = "Weatherstation")
    group = h5file.createGroup("/", 'weather', 'Weather log')
    table = h5file.createTable(group, 'reading', Weather, "Weather readings")
    reading = table.row
    for r in recs:
        reading['id'] = r['_id']
        reading['date'] = getDate(r['date'])
        reading['temperature'] = r['temperature']
        reading['humidity'] = r['humidity']
        # Insert new record
        reading.append()
    # Close (and flush) the file
    h5file.close()

print "Exporting weather data"
export(outputfile)

print "Done"
