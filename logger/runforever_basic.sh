#!/bin/bash

CMD="./dummy.py > test.csv &"

trap ctrl_c INT
function ctrl_c() {
    kill ${PID}
    echo "Finished with " ${PID}
    exit
}

function run_cmd() {
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