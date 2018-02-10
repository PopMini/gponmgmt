import MySQLdb

class databaseInterface():
	def __init__(self,ip,user,password,db):
		self.sqldb = MySQLdb.connect(ip,user,password,db)
		self.cursor = self.sqldb.cursor(MySQLdb.cursors.DictCursor)
	def getAll(self,query):
		self.cursor.execute(query)
		output = self.cursor.fetchall()
		return output
	def getOne(self,query):
		self.cursor.execute(query)
		output = self.cursor.fetchone()
		return output	
	def closeDB(self):
		self.sqldb.close()
	def execute(self,query):
		self.cursor.execute(query)
		self.sqldb.commit()
		pass


class databaseGpon(databaseInterface):
	def addOnuToDB(self,onu):
		self.addToDatabase(onu)

	def updateLastSeen(self,macid):
		dbase.execute("UPDATE onuMacs SET lastseen=current_timestamp() WHERE id='{}'".format(macid))

	def addMacAddress(self,onu,mac):
		dbase.execute("INSERT INTO onuMacs (onuid, mac, created) values ('{}','{}',CURRENT_TIMESTAMP())".format(onu.ONUid, mac))

	def getMacID(self,mac):
		return dbase.getOne("SELECT * from onuMacs where mac='{}';".format(mac))

	def updateDatabase_ONU(self,onu):
		if onu.ipaddr!='0.0.0.0' and onu.ipaddr!=None:
			print "UPDATE LONG",onu.ipaddr,onu.ONURX,onu.ONUStatus,onu.ONUDistance,onu.ONUProfile, onu.ONUModel,onu.OLTinterface,onu.ONUid,onu.OLTIP,onu.ONUSerial
			dbase.execute("""UPDATE onuList set ip='{}',rx='{}', status='{}', distance='{}', profile='{}', model='{}', oltid='{}', onuid='{}', oltip='{}' 
				where serial='{}'
				""".format(onu.ipaddr,onu.ONURX,onu.ONUStatus,onu.ONUDistance,onu.ONUProfile, onu.ONUModel,onu.OLTinterface,onu.ONUid,onu.OLTIP,onu.ONUSerial))
		else:
			print "UPDATE SHORT",onu.ONURX,onu.ONUStatus,onu.ONUDistance,onu.ONUProfile, onu.ONUModel,onu.OLTinterface,onu.ONUid,onu.OLTIP,onu.ONUSerial
			dbase.execute("""UPDATE onuList set rx='{}', status='{}', distance='{}', profile='{}', model='{}', oltid='{}', onuid='{}', oltip='{}' 
				where serial='{}'
				""".format(onu.ONURX,onu.ONUSerial,onu.ONUDistance,onu.ONUProfile, onu.ONUModel,onu.OLTinterface,onu.ONUid,onu.OLTIP,onu.ONUSerial))

	def checkIfONUExists(self,onu):
		return dbase.getAll("SELECT id from onuList where serial='{}'".format(onu.ONUSerial))

	def addOnuToDatabase(self,onu):
		dbase.execute("""INSERT INTO onuList (ip,rx,status,distance,profile,model, serial,oltid, onuid,oltip) 
			values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')
			""".format(onu.ipaddr,onu.ONURX,onu.ONUSerial,onu.ONUDistance,onu.ONUProfile,onu.ONUModel,onu.ONUSerial,onu.OLTinterface,onu.ONUid,onu.OLTIP))

	def addToDatabase(self,onu):
		id = self.checkIfONUExists(onu)
		if id:
			self.updateDatabase_ONU(onu)
		else:
			self.addOnuToDatabase(onu)
			id = self.checkIfONUExists(onu)
		id=id[0]['id']
		print "checkIfONUExists",id
		for mac in onu.macAddressTable:
			if not mac:
				continue
			_mac = self.getMacID(mac)
			if _mac:
				self.updateLastSeen(_mac['id'])
			else:
				self.addMacAddress(onu, mac)
dbase = databaseGpon('localhost','root','','gpon')