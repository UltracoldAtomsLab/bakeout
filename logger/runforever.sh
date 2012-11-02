#!/bin/bash

die () {
    echo >&2 "$@"
    exit 1
}

# If no settings file specified, nothing to do
[ "$#" -eq 1 ] || die "Usage: ${0} settingsfile"

# Load configuration
CONF=$1
source ${CONF}
source commonconf

# Make sure we know what are we starting
read -p ">${NAME}< - Press [y] to start: " -n 1
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Stopping"
    exit 1
fi
echo "OK"

# Capture keyboard interrupt
trap ctrl_c INT
function ctrl_c() {
    kill ${PID}
    echo "Finished with" ${PID}
    exit
}

# Run on the background
function run_cmd() {
    echo "${TEXT}" | mail -s 'Bakeout' ${EMAIL}
    echo ${CMD}
    eval ${CMD}
    PID=$!
    echo ${PID}
    # Give it some time to settle down, 5 seconds should be okay
    # with this, we should notice if the program is consistently not starting
    sleep 5
}

i=0
sleeptime=1
run_cmd
while true; do
    date=`date`
    echo "Time: ${date}, sleep ${sleeptime}s"
    sleep ${sleeptime}
    while kill -0 "$PID"; do
	sleep 0.5
        i=-1
    done
    echo "${PID} was killed!"
    run_cmd
    i=$[$i+1]
    sleeptime=$((2**${i}))
done
