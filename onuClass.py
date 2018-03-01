import netsnmp 
from dasanOids import *
from settings import *
#from database import databaseGpon
from termcolor import colored
import time
#self.dbase = databaseGpon('localhost','root','','gpon')
def prettify(mac_string):
    return ':'.join('%02x' % ord(b) for b in mac_string)

class onuList(list):
	def search(self,serial):
		for onu in self:
			if serial in onu.ONUSerial:
				return onu
class onu:
	onulist = onuList()
	#global self.dbase
	def __init__(self,OLTip, OLTinterface, ONUid, ONUProfile, ONUModel, ONURX, ONUDistance, ONUStatus,ONUSerial,_snmp_session,dbase,ONUUptime):
		self.dbase=dbase
		self.OLTIP=OLTip
		self.OLTinterface=OLTinterface
		self.ONUid=ONUid
		self.ONUProfile=ONUProfile
		self.ONUModel=ONUModel
		self.ONURX=ONURX
		self.ONUDistance=ONUDistance
		self.ONUStatus=ONUStatus
		self.ONUSerial=ONUSerial
		self.ONUUptime = 0
		if ONUUptime:
			self.ONUUptime = ONUUptime

		self.onulist.append(self)
		self.__getPortCount()
		self._snmp_session=_snmp_session
		self.macAddressTable=[]
		self.__createSNMPVars()
		self.getIpAddress()
		self.getMacAddressTable()
		
		
		#print self.ipaddr
	def getCurrentIPAddress(self):
		pass
	def getCurrentStatus(self):
		pass
	def __getPortCount(self):
		if 'h665' in self.ONUModel.lower():
			self.portCount=1
		else:
			self.portCount=4

	def getMacAddressTable(self):
		if not self.ONUModel or not self.ONUProfile:
			return
		if 'h665' not in self.ONUModel.lower() and self.ONUProfile.lower() not in bridgeProfiles:
			self.getRouterAddress()
		else:	
			self.getMacs()
		self.printData('macaddrtable')

	def __createSNMPVars(self):
		self._vars_checkMacAddressTable = netsnmp.VarList(netsnmp.Varbind(".1.3.6.1.4.1.6296.101.23.19.1.1.4.{}.{}.{}".format(self.OLTinterface,self.ONUid, '1')))
		self._vars_checkMacAddressTableVirtEth = netsnmp.VarList(netsnmp.Varbind(".1.3.6.1.4.1.6296.101.23.19.1.1.4.{}.{}.{}".format(self.OLTinterface,self.ONUid, '5')))
		self._vars_CurrentIP = netsnmp.VarList(netsnmp.Varbind(sleGponOnuHostCurrentIp+".{}.{}".format(self.OLTinterface,self.ONUid)))
		self._vars_ipMacs = netsnmp.VarList(netsnmp.Varbind(sleGponOnuMacTable+".{}.{}".format(self.OLTinterface,self.ONUid)))
		self._oid_getIpAddress = netsnmp.VarList(netsnmp.Varbind(".1.3.6.1.4.1.6296.101.23.12.1.1.13.{}.{}.1".format(self.OLTinterface, self.ONUid)))

	def getMacs(self):
		self.updateOnuMacAddressTable()
		__macaddr = self._snmp_session.walk(self._vars_checkMacAddressTable)
		__temp_macaddr=[]
		if not __macaddr:
			self.updateOnuMacAddressTable('5')
			__macaddr = self._snmp_session.walk(self._vars_checkMacAddressTableVirtEth)
		[__temp_macaddr.append(prettify(x)) for x in __macaddr]
		for i in __temp_macaddr:
			if i not in self.macAddressTable:
				self.macAddressTable.append(i)

	def getRouterAddress(self):
		for i in range(2,7):
			UpdateResult = self.updateOnuIpHost(i)
		self.macAddrUpdateStatus = UpdateResult
		ipaddrRo = self._snmp_session.walk(self._vars_CurrentIP)
		macaddr = self._snmp_session.walk(self._vars_ipMacs)
		macAddressTable=[]
		[macAddressTable.append(prettify(x)) for x in macaddr]

		for x in xrange(0,len(macAddressTable)):
			if mgmtAddressPrefix not in ipaddrRo[x] and ipaddrRo[x] != '0.0.0.0': 
				self.macAddressTable.append(macAddressTable[x])

	def printData(self,extra=None):
		print "[{}] GPON {} / {} SN:{} Status:{} M:{} P:{} RX:{}".format(self.OLTIP,self.OLTinterface,self.ONUid,self.ONUSerial,self.ONUStatus,self.ONUModel,self.ONUProfile,self.ONURX)
		if extra==None:
			pass
		elif extra=="macaddrtable":
			if self.macAddrUpdateStatus == 'Failure':
				print colored(self.macAddrUpdateStatus,'red')
			else:
				print colored(self.macAddressTable,'green')

	def updateOnuIpHost(self,controlid):
		#time.sleep(1)
		_vars = netsnmp.VarList(
			netsnmp.Varbind(iso,sleGponOnuHostControlRequest, '2','INTEGER'),
			netsnmp.Varbind(iso,sleGponOnuHostControlOltId, self.OLTinterface,'INTEGER'),
			netsnmp.Varbind(iso,sleGponOnuHostControlOnuId, self.ONUid,'INTEGER'),
			netsnmp.Varbind(iso,sleGponOnuHostControlId, str(controlid),'INTEGER'),
			netsnmp.Varbind(iso,sleGponOnuHostControlTimer, '0','INTEGER')
			)
		status = self._snmp_session.set(_vars)
		#time.sleep(0.5)
		if status == 1:
			result = "Success"
		else:
			result = "Failure"
		return result

	def getIpAddress(self):
		self.updateOnuIpHost(1)
		ipaddr = self._snmp_session.get(self._oid_getIpAddress)
		self.ipaddr = ipaddr[0]

	def updateOnuMacAddressTable(self,slotindex=None):
		if not slotindex:
			slotindex=1
		status = "Failure"
		#time.sleep(1)
		for i in range(1,self.portCount+1):
			_vars_UpdateMacAddressTable = netsnmp.VarList(
				netsnmp.Varbind(iso,sleGponOnuMacControlRequest,'1','INTEGER'),
				netsnmp.Varbind(iso,sleGponOnuMacControlOltIndex, self.OLTinterface,'INTEGER'),
				netsnmp.Varbind(iso,sleGponOnuMacControlOnuIndex, self.ONUid,'INTEGER'),
				netsnmp.Varbind(iso,sleGponOnuMacControlSlotIndex,slotindex,'INTEGER'),
				netsnmp.Varbind(iso,sleGponOnuMacControlPortIndex,str(i),'INTEGER'),
				netsnmp.Varbind(iso,sleGponOnuMacControlTimer,'0','INTEGER')
				)
			if self._snmp_session.set(_vars_UpdateMacAddressTable) == 1:
				status = "Success"
		#time.sleep(0.5)
		self.macAddrUpdateStatus = status
		return status
	def addToDatabase(self):
		self.dbase.addOnuToDB(self)

	def updateData(self):
		self._snmp_session = netsnmp.Session(DestHost=self.OLTIP, Version = 2,Community = 't0p$3cr37', UseNumeric=1, Timeout=10000000)
		self.getBasicData()
		self.getIpAddress()
		self.updateOnuMacAddressTable()

	def getBasicData(self):
		self.ONURX = self._snmp_session.get (netsnmp.VarList (netsnmp.Varbind ("{}.{}.{}".format (sleGponOnuRxPower, self.OLTinterface, self.ONUid))))[0]
		self.ONUStatus = self._snmp_session.get (netsnmp.VarList (netsnmp.Varbind ("{}.{}.{}".format (sleGponOnuStatus, self.OLTinterface, self.ONUid))))[0]
		self.ONUProfile = self._snmp_session.get (netsnmp.VarList (netsnmp.Varbind ("{}.{}.{}".format (sleGponOnuProfile, self.OLTinterface, self.ONUid))))[0]
		self.ONUDistance = self._snmp_session.get (netsnmp.VarList (netsnmp.Varbind ("{}.{}.{}".format (sleGponOnuDistance, self.OLTinterface, self.ONUid))))[0]


