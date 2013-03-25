# Loggers

This directory has all the hardware interfacing code. Most of it is hacked together, and one evolved into the other. The correct way would be making more complete drivers and separate the driver code from the logging. Another day

## Files

### Executable
* **runforever.sh**: keeping things running, this is the script to use for every equipment

### Configuration files
* **commonconf**: common configuration settings
* **runconf_fullrange.sh**: Using the Pfeiffer Vacuum's SingleGauge [TPG261][tpg261] (over RS232C interface with serial cable)
* **runconf_iongaugefront.sh**: Ion Gauge measurement for Agilent [XGS-600][xgs600] controller (over RS232 interface, with USB-Serial)
* **runconf_iongaugeback.sh**: Ion Gauge measurement for Agilent [XGS-600][xgs600] controller (over RS232 interface, with USB-Serial)
* **runconf_ionpump_internal_front.sh**: GammaVacuum controller for internal ion pump
* **runconf_ionpump_internal_back.sh**: GammaVacuum controller for internal ion pump
* **runconf_thermologger.sh**: temperature logging with Arduino Mega ADK, over USB CDC
* **runconf_ionpump1.sh**: External Ion Pump measurement with Varian DualGauge

## Explanation the used of configuration variables

* **hosts=** the list of MongoDB hostnames:port values to try to connect to, a single replica set, eg. localhost:27017,otherhost:31000
* **database=** name of database used in the MongoDB server
* **collection=** name of collection used in the database
* **baud=** when used, setting the baud rate of the serial connection
* **dbid=** the ID used in the database for that sensor (should be unique among sensors)
* **gaugeid=**: the Ion Gauge ID set in the controller
* **devid=**: ion pump device ID set in the controller (internal ion pumps)
* **comid=**: set COM port for turbo pump, in the form of comid=XYZ results in using `/dev/ttyXYZ`
* **com=**: for thermologger the serial number of the ACM-type USB device (ie. the x in ttyACMx)

## Running

For example `sudo ./runforever runconf_thermologger.sh` to start the thermologger.

[tpg261]: http://www.pfeiffer-vacuum.com/products/measurement/activeline/controllers/onlinecatalog.action?detailPdoId=3523 "Pfeiffer site for TPG261"
[xgs600]: http://www.chem.agilent.com/en-US/products-services/Instruments-Systems/Vacuum-Technologies/Vacuum-Measurement/XGS-600-Controller/Pages/default.aspx "Product website"
