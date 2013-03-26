"""
Simple serial monitoring
"""
import serial
import sys

if (len(sys.argv) < 3):
    print("Usage: python simpleserial.py DEVICE BAUD\n\n")
    sys.exit(1)
com = sys.argv[1]
baud = sys.argv[2]

device = serial.Serial(com, baud, timeout=2)
while True:
    try:
        print(device.readline().strip())
    except (KeyboardInterrupt):
        print("#closed")
        break
