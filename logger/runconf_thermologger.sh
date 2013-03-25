NAME="Thermologger"
## Can't use this if there is more than one ACM device connected
#CMD="(rmmod -w cdc_acm && modprobe cdc_acm); ./thermologger.py thermologger.conf >> thermologger.csv &"

## Might have to manually run rmmod / modprobe when needed
CMD="./thermologger.py thermologger.conf >> thermologger.csv &"
