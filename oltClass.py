import netsnmp,os,subprocess
from database import databaseInterface
import time
import os
from onuClass import *
from dasanOids import *
def prettify(mac_string):
    return ':'.join('%02x' % ord(b) for b in mac_string)
dbase = databaseInterface('localhost','root','','gpon')
_updateCounter=0
_newOnuCounter=0



class olt():
	global dbase

	onuList = []

	def __init__(self,oltip,snmpCommunity):
		self._snmp_session = netsnmp.Session(DestHost=oltip, Version = 2,Community = snmpCommunity, UseNumeric=1, Timeout=5000000)
		self.oltip = oltip
		self.snmpCommunity = snmpCommunity
		#print self._snmp_session 
		self.activeOlt= self.getActiveOltID()
		print self.activeOlt

	def getActiveOltID(self):
		_vars_activeOlts = netsnmp.VarList(netsnmp.Varbind(sleGponOltId))
		_vars_activeOnuCount = netsnmp.VarList(netsnmp.Varbind(sleGponOltActiveOnuCount))
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
			[onu(self.oltip, oltid, OnuID[i],Profile[i],Model[i],RxPower[i],Distance[i],Status[i],Serial[i],self._snmp_session) for i in range(0,len(Serial))]


	def addToDatabase(self):
		for onu in self.onuList:
			id = self.checkIfONUExists(onu['serial'])
			if id:
				self.updateDatabase_ONU(onu)
			else:
				self.addOnuToDatabase(onu)
				id = self.checkIfONUExists(onu['serial'])
			id=id[0]['id']
			print "checkIfONUExists",id
			for mac in onu['macs']:
				if not mac:
					continue
				_mac = self.getMacID(mac)
				if _mac:
					self.updateLastSeen(_mac['id'])
				else:
					self.addMacAddress(id, mac)



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
		#print onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'],onu['model'],onu['serial'],onu['oltid'],onu['onuid'],onu['oltip']
		dbase.execute("""INSERT INTO onuList (ip,rx,status,distance,profile,model, serial,oltid, onuid,oltip) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(onu['ipaddr'][0],onu['rxpower'],onu['status'],onu['distance'],onu['profile'],onu['model'],onu['serial'],onu['oltid'],onu['onuid'],onu['oltip']))

	def getBasicData(self,oltid):
		Serial = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuSerial, oltid))))
		RxPower = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuRxPower, oltid))))
		OnuID = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuID, oltid))))
		Status = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuStatus, oltid))))
		Profile = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuProfile, oltid))))
		Distance = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuDistance, oltid))))
		Model = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuModelName, oltid))))
		return Serial, RxPower, OnuID, Status, Profile, Distance, Model

	def updateOnuIpHost(self, oltid, onuid,controlid):
		_vars = netsnmp.VarList(
			netsnmp.Varbind(iso,sleGponOnuHostControlRequest,'2','INTEGER'),
			netsnmp.Varbind(iso,sleGponOnuHostControlOltId,oltid,'INTEGER'),
			netsnmp.Varbind(iso,sleGponOnuHostControlOnuId,onuid,'INTEGER'),
			netsnmp.Varbind(iso,sleGponOnuHostControlId,str(controlid),'INTEGER'),
			netsnmp.Varbind(iso,sleGponOnuHostControlTimer,'0','INTEGER')
			)
		status = self._snmp_session.set(_vars)
		if status == 1:
			result = "Success"
		else:
			result = "Failure"
		return result
