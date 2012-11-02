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

## Running

For example `sudo ./runforever runconf_thermologger.sh` to start the thermologger.

[tpg261]: http://www.pfeiffer-vacuum.com/products/measurement/activeline/controllers/onlinecatalog.action?detailPdoId=3523 "Pfeiffer site for TPG261"
[xgs600]: http://www.chem.agilent.com/en-US/products-services/Instruments-Systems/Vacuum-Technologies/Vacuum-Measurement/XGS-600-Controller/Pages/default.aspx "Product website"
