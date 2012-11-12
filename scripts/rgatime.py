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

## Atom number settings
amus = {2: "H2",
        # 12: "C",
        18: "H2O",
        28: "N2",
        # 32: "32?",
        44: "CO2",
        }
testamu = amus.keys()
testamu.sort()
styles = {2: "r-",
          12: "g--",
          18: "b:",
          28: "r--",
          32: "g-",
          44: "k-",
          }

## Connect to database
connection = pymongo.Connection(mongos)
db = connection[database]
coll = db[collection]

## Retrieve data
recs = coll.find({"type": "rga"}, sort=[('date', 1)])

## Setting up parameters
change = {}  # to hold the measurement data
for a in testamu:
    change[a] = []
dates = []

## Organizing measurement values
for r in recs:
    scan = r["reading"]["scan"]
    amu = [v['amu'] for v in scan]
    value = [int(abs(v['value']))*1e-16 for v in scan]
    out = dict(zip(amu, value))
    date = r['date'].replace(tzinfo=pytz.timezone('UTC'))
    dates.append(date)
    for a in testamu:
        change[a] += [out[a]]

## Plotting
fig = pl.figure(figsize=(11.27, 8.69))  # Should be A4 size
ax = fig.add_subplot(111)
for a in testamu:
    pl.semilogy(dates, change[a], styles[a], label="%s, AMU=%d" %(amus[a], a), linewidth=3)

pl.legend(loc='best')
pl.xlabel('Date', fontsize=14)
pl.ylabel('Ion Current (A)', fontsize=14)
pl.title('RGA recording', fontsize=16)
days = mdates.DayLocator()
hours   = mdates.HourLocator()
daysFmt = mdates.DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(daysFmt)
ax.xaxis.set_minor_locator(hours)
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
fig.autofmt_xdate()

## Save result
pl.savefig('rga.png')
pl.savefig('rga.pdf')

## Plot on screen
pl.show()
