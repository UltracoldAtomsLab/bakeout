# BOMon2

Bakeout Monitor server, rewritten in Python. This routes the temperature and pressure measurement from the database to the front end.

## Installing

Should be all set by cloning the git repo. Needs Python2 (tested with 2.7.4),
and [PyMongo](http://api.mongodb.org/python/current/) and [json](http://docs.python.org/2/library/json.html).

## Running

Update the configuration into `monitor.json` (with the database and sensor information), then run with `python server.py`.

The server is currently run on port 5000.
