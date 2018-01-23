import MySQLdb
class databaseInterface():
	def __init__(self,ip,user,password,db):
		self.ip = ip
		self.password = password
		self.user = user
		self.db = db
		self.sqldb = MySQLdb.connect(self.ip,self.user,self.password,self.db)
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

