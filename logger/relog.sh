#!/bin/bash

TERM="EMI?"

echo ">> Started"
while true; do
  journalctl -afb -n0 | grep ${TERM} -m1 && echo "found" && ./restart.sh
done
