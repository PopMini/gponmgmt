from oltClass import olt
from onuClass import onu
from database import databaseInterface




if __name__ == '__main__':
	dbase = databaseInterface('localhost','root','','gpon')
	olt1 = olt ('192.168.230.106','t0p$3cr37')
	olt1.addToDatabase()
        print "done"
