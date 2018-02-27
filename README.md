# gponmgmt
This script will help you to provide documentation about your ONU's. It stores basic informations about ONU, and also it gathers mac addresses connected to ONUs.

Tested with OLT V8102
First of all, you'll need OIDs from Dasan.
If you already got them, copy OIDs to dasanOids.py.example and rename it to dasanOids.py

Change settings.py file.
1. bridgeProfiles - set name of profile that's working as bridge. If ONU acts as router it'll only get MAC corresponding to NAT IP Address.
2. databaseVars - change ip address, user, password for your database
3. mgmtAddressPrefix - tell script how it can know that this address is ONU mgmt address. For example: my mgmt address always starts with 10.99, so mgmtAddressPrefix = "10.99."
Usage: python gpon.py 


