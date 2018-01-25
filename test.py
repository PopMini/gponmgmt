import netsnmp

#olt('192.168.230.106','t0p$3cr37')
#snmpset -v2c -c t0p$ecr37 192.168.230.106 iso.3.6.1.4.1.6296.101.23.19.2.1.0 i 1
#snmpset -v2c -c t0p$ecr37 192.168.230.106 iso.3.6.1.4.1.6296.101.23.19.2.6.0 i 2000001
#snmpset -v2c -c t0p$ecr37 192.168.230.106 iso.3.6.1.4.1.6296.101.23.19.2.7.0 i 1
#snmpset -v2c -c t0p$ecr37 192.168.230.106 iso.3.6.1.4.1.6296.101.23.19.2.8.0 i 1
#snmpset -v2c -c t0p$ecr37 192.168.230.106 iso.3.6.1.4.1.6296.101.23.19.2.9.0 i 1
#snmpset -v2c -c t0p$ecr37 192.168.230.106 iso.3.6.1.4.1.6296.101.23.19.2.3.0 i 0
#6296.101.23.19.1.1.4.{}.{}.{}.{}".format(oltid,onuid, slotindex,portindex)
community = 't0p$3cr37'
def prettify(mac_string):
    return ':'.join('%02x' % ord(b) for b in mac_string)
ip = '192.168.230.106'
iso = ".1.3.6.1.4.1"
sleGponOnuMacControlRequest ="6296.101.23.19.2.1"
sleGponOnuMacControlOltIndex ="6296.101.23.19.2.6"
sleGponOnuMacControlOnuIndex ="6296.101.23.19.2.7"
sleGponOnuMacControlSlotIndex = "6296.101.23.19.2.8"
sleGponOnuMacControlPortIndex = "6296.101.23.19.2.9"
sleGponOnuMacControlTimer ="6296.101.23.19.2.3"
sleGponOnuSerial='6296.101.23.3.1.1.4'#

sleGponOnuHostControlRequest = "6296.101.23.12.2.1.0"
sleGponOnuHostControlOltId ="6296.101.23.12.2.6.0"
sleGponOnuHostControlOnuId = "6296.101.23.12.2.7.0"
sleGponOnuHostControlId = "6296.101.23.12.2.8.0"
sleGponOnuHostControlTimer ="6296.101.23.12.2.3.0"



MACADD = "6296.101.23.19.1.1.4"
xdxd = "6296.101.23.19.1.1"
MACADDb = netsnmp.Varbind(iso,xdxd)
_snmp_session = netsnmp.Session(DestHost=ip, Version = 2,Community = community, UseNumeric=1)
oid = netsnmp.Varbind('sysDescr')
_vars = netsnmp.VarList(
	netsnmp.Varbind(iso,sleGponOnuMacControlRequest,'1','INTEGER'),
	netsnmp.Varbind(iso,sleGponOnuMacControlOltIndex,'2000003','INTEGER'),
	netsnmp.Varbind(iso,sleGponOnuMacControlOnuIndex,'2','INTEGER'),
	netsnmp.Varbind(iso,sleGponOnuMacControlSlotIndex,'1','INTEGER'),
	netsnmp.Varbind(iso,sleGponOnuMacControlPortIndex,'1','INTEGER'),
	netsnmp.Varbind(iso,sleGponOnuMacControlTimer,'0','INTEGER')
	)
print "Xd"
#print _snmp_session.set(netsnmp.VarList(netsnmp.Varbind(sleGponOnuMacControlRequest,'0','2','INTEGER')))
#print _snmp_session.set(netsnmp.VarList(netsnmp.Varbind(sleGponOnuMacControlOltIndex,'0','2000001','INTEGER')))
#print _snmp_session.set(netsnmp.VarList(netsnmp.Varbind(sleGponOnuMacControlOnuIndex,'0','1','INTEGER')))
#print _snmp_session.set(netsnmp.VarList(netsnmp.Varbind(sleGponOnuMacControlSlotIndex,'0','1','INTEGER')))
#print _snmp_session.set(netsnmp.VarList(netsnmp.Varbind(sleGponOnuMacControlPortIndex,'0','1','INTEGER')))
#print _snmp_session.set(netsnmp.VarList(netsnmp.Varbind(sleGponOnuMacControlTimer,'0','0','INTEGER')))
#print _snmp_session.walk(netsnmp.VarList(MACADDb))
print _snmp_session.set(_vars)
#print _snmp_session.walk(netsnmp.VarList(MACADDb))
