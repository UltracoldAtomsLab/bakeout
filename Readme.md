# Bakeout

Collection of software for our bakeout system.

Infrastructure

## Loggers

The data collection scripts

## Webmonitor

Webmonitor: web interface for the real-time and long term data

Using nginx for load balancing between a couple of instances, so either of them can be down for maintenance and still have a working interface.

## Database

MongoDB replica set running on 2+ computers in the lab for higher level of data resilience. Just make sure to do clean shutdown to avoid data loss (which still does happen, darn.
