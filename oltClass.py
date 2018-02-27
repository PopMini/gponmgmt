import netsnmp,os,subprocess
from database import databaseGpon
from dasanOids import databaseVars
import time
import os
from onuClass import *
from settings import *
from dasanOids import *
def prettify(mac_string):
    return ':'.join('%02x' % ord(b) for b in mac_string)

_updateCounter=0
_newOnuCounter=0



class olt():
	#global self.dbase

	onuList = []

	def __init__(self,oltip,snmpCommunity):
		self._snmp_session = netsnmp.Session(DestHost=oltip, Version = 2,Community = snmpCommunity, UseNumeric=1, Timeout=10000000)
		self.oltip = oltip
		self.snmpCommunity = snmpCommunity
		#print self._snmp_session 
		self.activeOlt= self.getActiveOltID()
		self.dbase = databaseGpon(databaseVars['address'],databaseVars['user'],databaseVars['password'],databaseVars['database'])
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
			#time.sleep(1)
			Serial, RxPower, OnuID, Status, Profile, Distance, Model = self.getBasicData(oltid)
			#[onu(self.oltip, oltid, OnuID[i],Profile[i],Model[i],RxPower[i],Distance[i],Status[i],Serial[i],self._snmp_session) for i in range(0,len(Serial))]
			for i in xrange(0,len(Serial)):
				if onu.onulist.search(Serial[i]):
					onu.onulist.search(Serial[i]).updateData()
					onu.onulist.search(Serial[i]).addToDatabase()
				else:
					x=onu(self.oltip, oltid, OnuID[i],Profile[i],Model[i],RxPower[i],Distance[i],Status[i],Serial[i],self._snmp_session,self.dbase)
					x.addToDatabase()
		#self.dbase.closeDB()


	def getBasicData(self,oltid):
		Serial = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuSerial, oltid))))
		RxPower = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuRxPower, oltid))))
		OnuID = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuID, oltid))))
		Status = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuStatus, oltid))))
		Profile = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuProfile, oltid))))
		Distance = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuDistance, oltid))))
		Model = self._snmp_session.walk (netsnmp.VarList (netsnmp.Varbind ("{}.{}".format (sleGponOnuModelName, oltid))))
		return Serial, RxPower, OnuID, Status, Profile, Distance, Model

	def updateBasicData(self):
		for i in self.activeOlt:
			Serial, RxPower, OnuID, Status, Profile, Distance, Model = self.getBasicData(i)
			for y in xrange(0,len(Serial)):
				if onu.onulist.search(Serial[y]):
					onu.onulist.search(Serial[y]).ONURX=RxPower[y]
					onu.onulist.search(Serial[y]).ONUStatus="10"
					onu.onulist.search(Serial[y]).ONUDistance = Distance[y]
					onu.onulist.search(Serial[y]).ONUProfile = Profile[y]
					onu.onulist.search(Serial[y]).addToDatabase()