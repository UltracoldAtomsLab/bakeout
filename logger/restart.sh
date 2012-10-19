
# do correct things
rmmod -w cdc_acm && modprobe cdc_acm && echo "EMI - restarted" | mail -s 'Bakeout' imrehg@gmail.com && ./thermologger.py thermologger.conf > thermolog4000.csv &
