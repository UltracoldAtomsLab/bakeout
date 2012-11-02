NAME="Thermologger"
CMD="rmmod -w cdc_acm | modprobe cdc_acm | ./thermologger.py thermologger.conf >> thermologger.csv &"
