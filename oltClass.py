import netsnmp,os,subprocess
def prettify(mac_string):
    return ':'.join('%02x' % ord(b) for b in mac_string)
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
	sleGponOnuHostControlRequest = ".1.3.6.1.4.1.6296.101.23.12.2.1.0"
	sleGponOnuHostControlOltId =".1.3.6.1.4.1.6296.101.23.12.2.6.0"
	sleGponOnuHostControlOnuId = ".1.3.6.1.4.1.6296.101.23.12.2.7.0"
	sleGponOnuHostControlId = ".1.3.6.1.4.1.6296.101.23.12.2.8.0"
	sleGponOnuHostControlTimer =".1.3.6.1.4.1.6296.101.23.12.2.3.0"
	sleGponOnuMacControlRequest =".1.3.6.1.4.1.6296.101.23.19.2.1.0"
	sleGponOnuMacControlOltIndex =".1.3.6.1.4.1.6296.101.23.19.2.6.0"
	sleGponOnuMacControlOnuIndex =".1.3.6.1.4.1.6296.101.23.19.2.7.0"
	sleGponOnuMacControlSlotIndex = ".1.3.6.1.4.1.6296.101.23.19.2.8.0"
	sleGponOnuMacControlPortIndex = ".1.3.6.1.4.1.6296.101.23.19.2.9.0"
	sleGponOnuMacControlTimer =".1.3.6.1.4.1.6296.101.23.19.2.3.0"
	onuList = []

	def __init__(self,oltip,snmpCommunity):
		self.oltip = oltip
		self.snmpCommunity = snmpCommunity
		self.activeOlt= self.getActiveOltID() # Get active gpon interfaces
		

	def getActiveOltID(self):
		self.oltids = netsnmp.snmpwalk(self.sleGponOltId, Version=2, DestHost=self.oltip, Community=self.snmpCommunity)
		self.onucount = netsnmp.snmpwalk(self.sleGponOltActiveOnuCount, Version=2, DestHost=self.oltip, Community=self.snmpCommunity)
		counter = 0
		activeOlt = []
		for i in range (0,len(self.oltids)):
			if int(self.onucount[i])>0:
				print self.oltids[i],self.onucount[i]
				activeOlt.append(self.oltids[i])
		return activeOlt

	def getOnuInfo(self):
		for oltid in self.activeOlt:
			Serial = netsnmp.snmpwalk(self.sleGponOnuSerial+"."+oltid, Version=2, DestHost=self.oltip, Community=self.snmpCommunity)
			RxPower = netsnmp.snmpwalk(self.sleGponOnuRxPower+"."+oltid, Version=2, DestHost=self.oltip, Community=self.snmpCommunity)
			OnuID = netsnmp.snmpwalk(self.sleGponOnuID+"."+oltid, Version=2, DestHost=self.oltip, Community=self.snmpCommunity)
			Status = netsnmp.snmpwalk(self.sleGponOnuStatus+"."+oltid,Version=2, DestHost=self.oltip, Community=self.snmpCommunity)
			Profile = netsnmp.snmpwalk(self.sleGponOnuProfile+"."+oltid,Version=2, DestHost=self.oltip,Community=self.snmpCommunity)
			Distance = netsnmp.snmpwalk(self.sleGponOnuDistance+"."+oltid,Version=2, DestHost=self.oltip,Community=self.snmpCommunity)
			Model = netsnmp.snmpwalk(self.sleGponOnuModelName+"."+oltid,Version=2,DestHost=self.oltip,Community=self.snmpCommunity)
			
			for i in range (0,len(Serial)):
				#print Serial[i], RxPower[i], OnuID[i], Status[i], Profile[i], Distance[i], Model[i], oltid
				ipaddr = self.getIpAddress(oltid, OnuID[i], Model[i],Profile[i])
				if not Model[i] or not Profile[i]:
					continue
				if 'h665' not in Model[i].lower() and "bridge" not in Profile[i].lower():
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
		print "getRouterAddress"
		FNULL = open(os.devnull, 'w')
		for i in range(2,7):
			subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlRequest,'i','2'],stdout=FNULL, stderr=subprocess.STDOUT)
			subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlOltId,'i',oltid],stdout=FNULL, stderr=subprocess.STDOUT)
			subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlOnuId,'i',onuid],stdout=FNULL, stderr=subprocess.STDOUT)
			subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlId,'i',str(i)],stdout=FNULL, stderr=subprocess.STDOUT)
			subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlTimer,'i','0'],stdout=FNULL, stderr=subprocess.STDOUT)
			ipaddrRo = netsnmp.snmpget(".1.3.6.1.4.1.6296.101.23.12.1.1.13."+oltid+"."+onuid+"."+str(i),Version=2,DestHost=self.oltip,Community=self.snmpCommunity)
			if ipaddrRo[0] != '0.0.0.0':
				macaddr = netsnmp.snmpget(".1.3.6.1.4.1.6296.101.23.12.1.1.10."+oltid+"."+onuid+"."+str(i),Version=2,DestHost=self.oltip,Community=self.snmpCommunity)
				if macaddr[0]:
					return ipaddrRo[0],prettify(macaddr[0])
				else:
					return None, None
	def getIpAddress(self,oltid,onuid,model,profile):
		#ipaddr = netsnmp.snmpget(".1.3.6.1.4.1.6296.101.23.12.1.1.13."+oltid+"."+onuid+".1",Version=2,DestHost=self.oltip,Community=self.snmpCommunity)
		#if ipaddr[0] != '0.0.0.0' and ipaddr[0] != None:
		#	print ipaddr, "IP Address is valid"
		#	return ipaddr
		FNULL = open(os.devnull, 'w') # Don't print output from snmpset
		print "Refreshing..."
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlRequest,'i','2'],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlOltId,'i',oltid],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlOnuId,'i',onuid],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlId,'i','1'],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuHostControlTimer,'i','0'],stdout=FNULL, stderr=subprocess.STDOUT)
		ipaddr = netsnmp.snmpget(".1.3.6.1.4.1.6296.101.23.12.1.1.13."+oltid+"."+onuid+".1",Version=2,DestHost=self.oltip,Community=self.snmpCommunity)
		print "IP Address (after request):",ipaddr
		return ipaddr
	def getMacAddressTable(self,oltid,onuid,model):
		#if 'h665' not in model.lower():
		#	pass
		FNULL = open(os.devnull, 'w')
		macAddressTable = []
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuMacControlRequest,'i','1'],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuMacControlOltIndex,'i',oltid],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuMacControlOnuIndex,'i',onuid],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuMacControlSlotIndex,'i','1'],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuMacControlPortIndex,'i','1'],stdout=FNULL, stderr=subprocess.STDOUT)
		subprocess.call(['snmpset','-v2c','-c',self.snmpCommunity,self.oltip,self.sleGponOnuMacControlTimer,'i','0'],stdout=FNULL, stderr=subprocess.STDOUT)
		slotindex=1
		portindex=1
		macAddrOID = ".1.3.6.1.4.1.6296.101.23.19.1.1.4.{}.{}.{}.{}.2".format(oltid,onuid, slotindex,portindex)
		macaddr = netsnmp.snmpwalk(".1.3.6.1.4.1.6296.101.23.19.1.1.4.{}.{}.{}.{}".format(oltid,onuid, slotindex,portindex),Version=2,DestHost=self.oltip,Community=self.snmpCommunity)
		for i in macaddr:
			macAddressTable.append(prettify(i))

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