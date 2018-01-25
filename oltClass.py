import netsnmp,os,subprocess
from database import databaseInterface
def prettify(mac_string):
    return ':'.join('%02x' % ord(b) for b in mac_string)
dbase = databaseInterface('localhost','root','','gpon')
class olt():
	global dbase
	sleGponOnuID='.1.3.6.1.4.1.6296.101.23.3.1.1.1'#
	sleGponOnuSerial='.1.3.6.1.4.1.6296.101.23.3.1.1.4'#
	sleGponOnuStatus='.1.3.6.1.4.1.6296.101.23.3.1.1.2'#
	sleGponOnuRxPower='.1.3.6.1.4.1.6296.101.23.3.1.1.16'#
	sleGponOnuProfile= '.1.3.6.1.4.1.6296.101.23.3.1.1.8'
	sleGponOnuDistance= '.1.3.6.1.4.1.6296.101.23.3.1.1.10'
	sleGponOnuModelName= '.1.3.6.1.4.1.6296.101.23.3.1.1.17'
	sleGponOltId= '.1.3.6.1.4.1.6296.101.23.2.1.1.1'
	sleGponOltActiveOnuCount=".1.3.6.1.4.1.6296.101.23.2.1.1.21"
	sleGponOnuHostOnuId=".1.3.6.1.4.1.6296.101.23.12.1.1.2"
	sleGponOnuHostId = '.1.3.6.1.4.1.6296.101.23.12.1.1.3'
	sleGponOnuHostIpAddr='.1.3.6.1.4.1.6296.101.23.12.1.1.4'
	sleGponOnuLinkUpTime='.1.3.6.1.4.1.6296.101.23.3.1.1.23'
	sleGponOnuCurrIpAddr = '.1.3.6.1.4.1.6296.101.23.12.1.1.13'
	mib_listprofiles ='.1.3.6.1.4.1.6296.101.23.5.1.1.1.2'
	iso = ".1.3.6.1.4.1"
	sleGponOnuHostControlRequest = "6296.101.23.12.2.1"
	sleGponOnuHostControlOltId ="6296.101.23.12.2.6"
	sleGponOnuHostControlOnuId = "6296.101.23.12.2.7"
	sleGponOnuHostControlId = "6296.101.23.12.2.8"
	sleGponOnuHostControlTimer ="6296.101.23.12.2.3"
	sleGponOnuMacControlRequest ="6296.101.23.19.2.1"
	sleGponOnuMacControlOltIndex ="6296.101.23.19.2.6"
	sleGponOnuMacControlOnuIndex ="6296.101.23.19.2.7"
	sleGponOnuMacControlSlotIndex = "6296.101.23.19.2.8"
	sleGponOnuMacControlPortIndex = "6296.101.23.19.2.9"
	sleGponOnuMacControlTimer ="6296.101.23.19.2.3"
	onuList = []

	def __init__(self,oltip,snmpCommunity):
		self._snmp_session = netsnmp.Session(DestHost=oltip, Version = 2,Community = snmpCommunity, UseNumeric=1)
		self.oltip = oltip
		self.snmpCommunity = snmpCommunity
		self.activeOlt= self.getActiveOltID() # Get active gpon interfaces
		#print self.getOnuInfo()

	def getActiveOltID(self):
		_vars_activeOlts = netsnmp.VarList(netsnmp.Varbind(self.sleGponOltId))
		_vars_activeOnuCount = netsnmp.VarList(netsnmp.Varbind(self.sleGponOltActiveOnuCount))
		counter = 0
		activeOlt = []
		OltID = self._snmp_session.walk(_vars_activeOlts)
		ActiveOnuCount = self._snmp_session.walk(_vars_activeOnuCount)
		for i in range (0,len(OltID)):
			if int(ActiveOnuCount[i])>0:
				activeOlt.append(OltID[i])
		return activeOlt

	def getOnuInfo(self,oltid=None):
		if oltid!=None:
			self.activeOlt = []
			self.activeOlt.append(oltid)
		print self.activeOlt
		for oltid in self.activeOlt:

			Serial = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuSerial, oltid))))
			RxPower = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuRxPower, oltid))))
			OnuID = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuID, oltid))))
			Status = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuStatus, oltid))))
			Profile = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuProfile, oltid))))
			Distance = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuDistance, oltid))))
			Model = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuModelName, oltid))))

			for i in range (0, len(Serial)):
				print Serial[i], RxPower[i], OnuID[i], Status[i], Profile[i], Distance[i], Model[i], oltid
				ipaddr = self.getIpAddress(oltid, OnuID[i], Model[i],Profile[i])
				if not Model[i] or not Profile[i]:
					continue
				if 'h665' not in Model[i].lower() and "bridge" not in Profile[i].lower() and "KISSJAMES" not in Profile[i]:
					try:
						ipAddrRo,macAddress = self.getRouterAddress(oltid,OnuID[i])
						macAddressTable=[macAddress]
					except TypeError:
						macAddressTable=[]
					
				else:
					macAddressTable = self.getMacAddressTable(oltid,OnuID[i],Model[i])

				try:
					self.onuList.append({
					"serial":Serial[i],
					"rxpower":RxPower[i],
					"onuid":OnuID[i],
					"oltid":oltid,
					"status":Status[i],
					"profile":Profile[i],
					"distance":Distance[i],
					"model":Model[i],
					"ipaddr":ipaddr,
					"macs":macAddressTable,
					"oltip":self.oltip})
				except IndexError:
					continue

	def getRouterAddress(self,oltid,onuid):
		
		FNULL = open(os.devnull, 'w')
		for i in range(2,7):
			_vars = netsnmp.VarList(
				netsnmp.Varbind(self.iso,self.sleGponOnuHostControlRequest,'2','INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuHostControlOltId,oltid,'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuHostControlOnuId,onuid,'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuHostControlId,str(i),'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuHostControlTimer,'0','INTEGER')
				)
			print self._snmp_session.set(_vars)
			ipaddrRo = self._snmp_session.get(".1.3.6.1.4.1.6296.101.23.12.1.1.13."+oltid+"."+onuid+"."+str(i))
			if ipaddrRo[0] != '0.0.0.0':
				macaddr = self._snmp_session.get(".1.3.6.1.4.1.6296.101.23.12.1.1.10."+oltid+"."+onuid+"."+str(i))
				if macaddr[0]:
					print "[{}] ROUTER IP {} MAC {}".format(self.oltip,ipaddrRo[0],prettify(macaddr[0]))
					return ipaddrRo[0],prettify(macaddr[0])
				else:
					return None, None
	def getIpAddress(self,oltid,onuid,model,profile):
		_oid_getIpAddress = netsnmp.VarList(netsnmp.Varbind(".1.3.6.1.4.1.6296.101.23.12.1.1.13.{}.{}.1".format(oltid, onuid)))
		_vars = netsnmp.VarList(
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlRequest, '2', 'INTEGER'),
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlOltId, oltid, 'INTEGER'),
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlOnuId, onuid, 'INTEGER'),
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlId, '1', 'INTEGER'),
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlTimer, '0', 'INTEGER'))

		print self._snmp_session.set(_vars)
		ipaddr = self._snmp_session.get(_oid_getIpAddress)
		print "[{}] IP: {}".format(self.oltip,ipaddr)
		return ipaddr
	def getMacAddressTable(self,oltid,onuid,model):
		slotindex=1
		portindex=1
		macAddressTable = []
		print "[{}] Mac Address Table {} {} {}".format(self.oltip,oltid,onuid,model)
		portCount = 1
		if 'h665' not in model.lower():
			portCount = 4
			print "[{}] Checking all 4 ports:".format(self.oltip)
		else:
			portCount = 1
		print type(portCount)
		for i in range(1, portCount+1):
			print "[{}] Checking {} of {}:".format(self.oltip,i,portCount)
			print type(portCount)
			_vars = netsnmp.VarList(
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlRequest,'1','INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlOltIndex, oltid,'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlOnuIndex, onuid,'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlSlotIndex,'1','INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlPortIndex,str(i),'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlTimer,'0','INTEGER')
				)
			print self._snmp_session.set(_vars)
		_vars_checkMacAddressTable = netsnmp.VarList(netsnmp.Varbind(".1.3.6.1.4.1.6296.101.23.19.1.1.4.{}.{}.{}".format(oltid,onuid, slotindex)))
		macaddr = self._snmp_session.walk(_vars_checkMacAddressTable)
		for i in macaddr:
			macAddressTable.append(prettify(i))
		print "[{}] MAC: {}".format(self.oltip,macAddressTable)
		return macAddressTable
	def addToDatabase(self):
		for onu in self.onuList:
			id = dbase.getAll("SELECT id from onuList where serial='{}'".format(onu['serial']))
			if id:
				if onu['ipaddr'][0]!='0.0.0.0' and onu['ipaddr'][0]!=None:
					dbase.execute("""UPDATE onuList set ip='{}',rx='{}', status='{}', distance='{}', profile='{}', model='{}', oltid='{}', onuid='{}', oltip='{}' where serial='{}'""".format(onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'], onu['model'],onu['oltid'],onu['onuid'],onu['oltip'],onu['serial']))
				else:
					dbase.execute("""UPDATE onuList set rx='{}', status='{}', distance='{}', profile='{}', model='{}', oltid='{}', onuid='{}', oltip='{}' where serial='{}'""".format(onu['rxpower'],onu['status'],onu['distance'],onu['profile'], onu['model'],onu['oltid'],onu['onuid'],onu['oltip'],onu['serial']))

			else:
				print onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'],onu['model'],onu['serial'],onu['oltid'],onu['onuid'],onu['oltip']
				dbase.execute("""INSERT INTO onuList (ip,rx,status,distance,profile,model, serial,oltid, onuid,oltip) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'],onu['model'],onu['serial'],onu['oltid'],onu['onuid'],onu['oltip']))
			id = dbase.getAll("SELECT id from onuList where serial='{}'".format(onu['serial']))
			id=id[0]['id']
			print id
			for i in onu['macs']:
				print i
				if not i:
					continue
				mac = dbase.getOne("SELECT * from onuMacs where mac='{}';".format(i))
				if mac:
					print "MAC exists"
					dbase.execute("update onuMacs set lastseen=current_timestamp() where id='{}'".format(mac['id']))
				else:
					dbase.execute("INSERT INTO onuMacs (onuid, mac, created) values ('{}','{}',CURRENT_TIMESTAMP())".format(id, i))