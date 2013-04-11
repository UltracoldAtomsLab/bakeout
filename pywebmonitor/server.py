"""
Python remake of the bakeout monitoring web interface

MIT License 2013 Gergely Imreh <imrehg@gmail.com>
"""
import sys
import bottle
from bottle import route, view, static_file, post, get, request, run
import json
from pymongo import MongoClient
import socket
import dateutil.parser as parser
from bson.json_util import dumps
import datetime

version = 'v20130411-2218py'
hostname = socket.gethostname()

if len(sys.argv) < 2:
    print("Usage: server.py configfile.json")
    sys.exit(1)

# Setting up configuration
configfilename = sys.argv[1]
configfile = open(configfilename)
settings = json.load(configfile)

mongos = settings['mongos'].split(',')
replicaset = settings['replicaset']
databasename = settings['database']
sensorsin = settings['sensors']

# Parse sensor names and database IDs
sensorname = dict([(s['dbid'], s['name'])for s in sensorsin])
# Only load enabled sensors
sensors = [s for s in sensorsin if s['enabled']]

# Connect to database
collection = MongoClient(mongos, replicaset=replicaset, slave_okay=True)
db = collection[databasename]
readings = db.readings;

@route('/static/<path:path>')
def staticAssets(path):
    """ Load static assets """
    return static_file(path,  root='./public/')
@route('/favicon.ico')
def favicon():
    """ Load favicon """
    return static_file('favicon.ico',  root='./public/')

@route('/')
@view('index')
def index():
    """ Show the interface """
    params = {'sensors': sensors, 'version': version, 'hostname': hostname}
    return params

@get('/readings')
def sendReadings():
    """ Send reading data back to the interface """
    # Get parameters

    # Time example: 2013-04-11T20:46:54.892+08:00
    try:
        sincedate = parser.parse(request.query.get('sincedate'))
    except ValueError:
        sincedate = None

    try:
        tilldate = parser.parse(request.query.get('tilldate'))
    except ValueError:
        tilldate = None

    try:
        limit = int(request.query.get('limit'))
    except ValueError:
        limit = None
    if limit is None:
        limit = 10000

    # Get results and format to match native JSON
    results = readings.find({"date": {"$gt": sincedate, "$lte": tilldate}}).sort([("date", 1)]).limit(limit)
    outresult = json.loads(dumps(results))
    for i in range(len(outresult)):
        outresult[i]['date'] = datetime.datetime.utcfromtimestamp(float(outresult[i]['date']['$date']/1000.0)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        outresult[i]['_id'] = outresult[i]['_id']['$oid']

    return {"result": "OK", "readings": outresult}

@route('/export')
@view('export')
def export():
    """ Export data interface """
    params = {'sensorlist': sensorname, 'version': version, 'hostname': hostname}
    return params

# @route('/rga')
# @route('/rgadata')
# @route('/rgadatas')

run(host='0.0.0.0', port=5000)

