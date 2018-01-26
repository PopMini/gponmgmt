import netsnmp,os,subprocess
from database import databaseInterface
import time
def prettify(mac_string):
    return ':'.join('%02x' % ord(b) for b in mac_string)
dbase = databaseInterface('localhost','root','','gpon')
_updateCounter=0
_newOnuCounter=0
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
		self._snmp_session = netsnmp.Session(DestHost=oltip, Version = 2,Community = snmpCommunity, UseNumeric=1, Timeout=5000000)
		self.oltip = oltip
		self.snmpCommunity = snmpCommunity
		self.activeOlt= self.getActiveOltID()


	def getActiveOltID(self):
		_vars_activeOlts = netsnmp.VarList(netsnmp.Varbind(self.sleGponOltId))
		_vars_activeOnuCount = netsnmp.VarList(netsnmp.Varbind(self.sleGponOltActiveOnuCount))
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

		for oltid in self.activeOlt:
			Serial, RxPower, OnuID, Status, Profile, Distance, Model = self.getBasicData(oltid)

			for i in range (0, len(Serial)):
				print Serial[i], RxPower[i], OnuID[i], Status[i], Profile[i], Distance[i], Model[i], oltid
				ipaddr = self.getIpAddress(oltid, OnuID[i], Model[i],Profile[i])
				time.sleep(1)
				if not Model[i] or not Profile[i]:
					continue

				if 'h665' not in Model[i].lower() and "bridge" not in Profile[i].lower() and "KISSJAMES" not in Profile[i]:

					try:
						ipAddrRo,macAddress = self.getRouterAddress(oltid,OnuID[i])
						macAddressTable=[macAddress]
						time.sleep(1)
					except TypeError:
						macAddressTable=[]
					
				else:
					macAddressTable = self.getMacAddressTable(oltid,OnuID[i],Model[i])
					time.sleep(1)

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
		for i in range(2,7):
			UpdateResult = self.updateOnuIpHost(oltid,onuid,i)
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
		UpdateResult = self.updateOnuIpHost(oltid,onuid,1)
		ipaddr = self._snmp_session.get(_oid_getIpAddress)
		print "[{}] IP: {}".format(self.oltip,ipaddr)
		return ipaddr

	def getMacAddressTable(self,oltid,onuid,model):
		slotindex=1
		portindex=1
		macAddressTable = []
		_vars_checkMacAddressTable = netsnmp.VarList(netsnmp.Varbind(".1.3.6.1.4.1.6296.101.23.19.1.1.4.{}.{}.{}".format(oltid,onuid, slotindex)))

		print "[{}] Mac Address Table {} {} {}".format(self.oltip,oltid,onuid,model)
		if 'h665' not in model.lower():
			portCount = 4
		else:
			portCount = 1
		print "[{}] Mac UPDATE | OLTID: {}  ONUID: {} PortCount: {} Status: {}".format(self.oltip,oltid,onuid,portCount,self.updateOnuMacAddressTable(oltid,onuid,portCount))
		time.sleep(1)
		macaddr = self._snmp_session.walk(_vars_checkMacAddressTable)
		for i in macaddr:
			macAddressTable.append(prettify(i))
		print "[{}] MAC: {}".format(self.oltip,macAddressTable)
		return macAddressTable

	def addToDatabase(self):
		for onu in self.onuList:
			id = self.checkIfONUExists(onu['serial'])
			if id:
				self.updateDatabase_ONU(onu)
			else:
				self.addOnuToDatabase(onu)
			id = self.checkIfONUExists(onu['serial'])
			id=id[0]['id']
			for mac in onu['macs']:
				if not mac:
					continue
				_mac = self.getMacID(mac)
				if _mac:
					self.updateLastSeen(_mac['id'])
				else:
					self.addMacAddress(id, mac)


	def updateOnuMacAddressTable(self,oltid,onuid,portCount):
		status = "Failure"
		for i in range(1,portCount+1):
			_vars = netsnmp.VarList(
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlRequest,'1','INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlOltIndex, oltid,'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlOnuIndex, onuid,'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlSlotIndex,'1','INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlPortIndex,str(i),'INTEGER'),
				netsnmp.Varbind(self.iso,self.sleGponOnuMacControlTimer,'0','INTEGER')
				)
			if self._snmp_session.set(_vars) == 1:
				status = "Success"
		return status

	def updateLastSeen(self,macid):
		dbase.execute("UPDATE onuMacs SET lastseen=current_timestamp() WHERE id='{}'".format(macid))

	def addMacAddress(self,onuid, mac):
		dbase.execute("INSERT INTO onuMacs (onuid, mac, created) values ('{}','{}',CURRENT_TIMESTAMP())".format(id, mac))

	def getMacID(self,mac):
		return dbase.getOne("SELECT * from onuMacs where mac='{}';".format(mac))

	def updateDatabase_ONU(self,onu):
		global _updateCounter
		_updateCounter+=1
		if onu['ipaddr'][0]!='0.0.0.0' and onu['ipaddr'][0]!=None:
			print "UPDATE LONG",onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'], onu['model'],onu['oltid'],onu['onuid'],onu['oltip'],onu['serial']
			dbase.execute("""UPDATE onuList set ip='{}',rx='{}', status='{}', distance='{}', profile='{}', model='{}', oltid='{}', onuid='{}', oltip='{}' where serial='{}'""".format(onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'], onu['model'],onu['oltid'],onu['onuid'],onu['oltip'],onu['serial']))
		else:
			print "UPDATE SHORT",onu['rxpower'],onu['status'],onu['distance'],onu['profile'], onu['model'],onu['oltid'],onu['onuid'],onu['oltip'],onu['serial']
			dbase.execute("""UPDATE onuList set rx='{}', status='{}', distance='{}', profile='{}', model='{}', oltid='{}', onuid='{}', oltip='{}' where serial='{}'""".format(onu['rxpower'],onu['status'],onu['distance'],onu['profile'], onu['model'],onu['oltid'],onu['onuid'],onu['oltip'],onu['serial']))

	def checkIfONUExists(self,serial):
		return dbase.getAll("SELECT id from onuList where serial='{}'".format(serial))

	def addOnuToDatabase(self,onu):
		global _newOnuCounter
		_newOnuCounter+=1
		print onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'],onu['model'],onu['serial'],onu['oltid'],onu['onuid'],onu['oltip']
		dbase.execute("""INSERT INTO onuList (ip,rx,status,distance,profile,model, serial,oltid, onuid,oltip) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'],onu['model'],onu['serial'],onu['oltid'],onu['onuid'],onu['oltip']))

	def getBasicData(self,oltid):
		Serial = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuSerial, oltid))))
		RxPower = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuRxPower, oltid))))
		OnuID = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuID, oltid))))
		Status = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuStatus, oltid))))
		Profile = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuProfile, oltid))))
		Distance = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuDistance, oltid))))
		Model = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (self.sleGponOnuModelName, oltid))))
		return Serial, RxPower, OnuID, Status, Profile, Distance, Model

	def updateOnuIpHost(self, oltid, onuid,controlid):
		_vars = netsnmp.VarList(
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlRequest,'2','INTEGER'),
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlOltId,oltid,'INTEGER'),
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlOnuId,onuid,'INTEGER'),
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlId,str(controlid),'INTEGER'),
			netsnmp.Varbind(self.iso,self.sleGponOnuHostControlTimer,'0','INTEGER')
			)
		status = self._snmp_session.set(_vars)
		if status == 1:
			result = "Success"
		else:
			result = "Failure"
		return result
