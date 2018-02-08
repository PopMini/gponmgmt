from oltClass import olt
from onuClass import onu
from multiprocessing.pool import ThreadPool



if __name__ == '__main__':
	pool = ThreadPool(processes = 6)
	olt1 = olt('192.168.230.106','t0p$3cr37')
	olt2 = olt('192.168.60.200','t0p$3cr37')
	olt3 = olt('192.168.97.50','t0p$3cr37')
	olt4 = olt('192.168.35.23','t0p$3cr37')
	olt6 = olt('10.99.8.1','t0p$3cr37')
	olt7 = olt('10.99.10.1','t0p$3cr37')
	olt1x = pool.apply_async(olt1.getOnuInfo,)
	
	olt2x = pool.apply_async(olt2.getOnuInfo,)
	
	olt3x = pool.apply_async(olt3.getOnuInfo,)
	
	olt4x = pool.apply_async(olt4.getOnuInfo,)
	
	olt6x = pool.apply_async(olt6.getOnuInfo,)
	#olt4.getOnuInfo()
	
	#olt7.getOnuInfo()
	olt7x = pool.apply_async(olt7.getOnuInfo,)
	olt1y = olt1x.get()
	olt2y = olt2x.get()
	olt3y = olt3x.get()
	olt4y = olt4x.get()
	olt6y = olt6x.get()
	olt7y = olt7x.get()
	#olt1.addToDatabase()
	#olt2.addToDatabase()
	#o#lt3.addToDatabase()
	#olt4.getOnuInfo()
	#olt4.addToDatabase()

	#olt6.addToDatabase()
	#olt7.addToDatabase()

	for i in onu.onulist:
		i.addToDatabase()
		print "xxxxxxxxxxxxxxx"
