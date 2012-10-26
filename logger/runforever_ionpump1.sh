#!/bin/bash

CMD="./ionpump01.py ionpump1.conf >> ionpump1.csv &"
TEXT="External Ion Pump restarted"
EMAIL=imrehg@gmail.com

trap ctrl_c INT
function ctrl_c() {
    kill ${PID}
    echo "Finished with " ${PID}
    exit
}

function run_cmd() {
    echo "${TEXT}" | mail -s 'Bakeout' ${EMAIL}
    echo ${CMD}
    eval ${CMD}
    PID=$!
    echo ${PID}
}

run_cmd
while true; do
    while kill -0 "$PID"; do
	sleep 0.5
    done
    echo "Killed!"
    run_cmd
done
