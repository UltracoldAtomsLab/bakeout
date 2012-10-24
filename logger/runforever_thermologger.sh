#!/bin/bash

CMD="rmmod -w cdc_acm && modprobe cdc_acm && ./thermologger.py thermologger.conf > thermolog4000.csv &"
TEXT="Thermologger restarted"
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
