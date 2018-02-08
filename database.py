import MySQLdb

class databaseInterface():
	def __init__(self,ip,user,password,db):
		sqldb = MySQLdb.connect(ip,user,password,db)
		cursor = sqldb.cursor(MySQLdb.cursors.DictCursor)
	def getAll(self,query):
		cursor.execute(query)
		output = cursor.fetchall()
		return output
	def getOne(self,query):
		cursor.execute(query)
		output = cursor.fetchone()
		return output	
	def closeDB(self):
		sqldb.close()
	def execute(self,query):
		cursor.execute(query)
		sqldb.commit()
		pass
	def addOnuToDB(self,onu):
		print "Dodaje do bazy danych"

