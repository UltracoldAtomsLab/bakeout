#!/bin/bash

TERM="EMI?"

while true; do
  journalctl -afb -n0 | grep ${TERM} -m1 && ./restart.sh
done
