# BOMon

Bakeout Monitor server. This routes the temperature and pressure measurement from the database to the front end.

## Installing

Should be all set by cloning the git repo, then `npm install` to update all node dependencies

## Running

Have to install the **supervisor** script for node: `npm instal -g supervisor`, then run: `supervisor server`. This enables crash recovery, which is more important than crash debugging at the moment.

The server is currently run on port 5000.
