# Loggers

This directory has all the hardware interfacing code. Most of it is hacked together, and one evolved into the other. The correct way would be making more complete drivers and separate the driver code from the logging. Another day

## Files

* **vacuumlogger.py**: Using the Pfeiffer Vacuum's SingleGauge [TPG261][tpg261] (over RS232C interface with serial cable)
* **iongauge01.py**: Ion Gauge measurement for Agilent [XGS-600][xgs600] controller (over RS232 interface, with USB-Serial)
* **thermologger.py**: temperature logging with Arduino Mega ADK, over USB CDC
* **relog.sh/restart.sh**: helper scripts for restarting thermologger when it craps out (as it usually does).

All the scripts run with appropriate config files as their first argument, and they output on the console the data they receive (so can pipe into a file as well).

[tpg261]: http://www.pfeiffer-vacuum.com/products/measurement/activeline/controllers/onlinecatalog.action?detailPdoId=3523 "Pfeiffer site for TPG261"
[xgs600]: http://www.chem.agilent.com/en-US/products-services/Instruments-Systems/Vacuum-Technologies/Vacuum-Measurement/XGS-600-Controller/Pages/default.aspx "Product website"
