from oltClass import olt
from onuClass import onu
import threading
import time
import os
	

if __name__ == '__main__':
	print "START"
	olt1 = olt('192.168.230.106','t0p$3cr37')
	olt2 = olt('192.168.60.200','t0p$3cr37')
	olt4 = olt('192.168.97.50','t0p$3cr37')
	olt3 = olt('192.168.35.23','t0p$3cr37')
	#olt5 = olt('10.99.8.1','t0p$3cr37')
	olt6 = olt('10.99.10.1','t0p$3cr37')
	#olts = [olt1,olt2,olt3, olt4, olt5,olt6]
	#olt1.getOnuInfo()
	#olt2.getOnuInfo()
	#olt3.getOnuInfo()
	#olt4.getOnuInfo()

	
	#for i in onu.onulist:
	#	i.addToDatabase()
	print "starting threads"
	th_olt4 = threading.Thread(target=olt4.getOnuInfo)
	th_olt6 = threading.Thread(target=olt6.getOnuInfo)
	th_olt1 = threading.Thread(target=olt1.getOnuInfo)

	th_olt2 = threading.Thread(target=olt2.getOnuInfo)
	th_olt3 = threading.Thread(target=olt3.getOnuInfo)
	#th_olt5 = threading.Thread(target=olt5.getOnuInfo)
	print "how long does it take"
	#Threads = []
	#Threads.append(t)
	#Threads.append(c)
	counter=0
	while True:
		counter+=1
		if not th_olt4.isAlive():
			print "th_olt4 is not alive, staring th_olt4..."
			th_olt4 = threading.Thread(target=olt4.getOnuInfo)
			th_olt4.start()
		time.sleep(2)
		if not th_olt6.isAlive():
			print "th_olt6 is not alive, staring th_olt6..."
			th_olt6 = threading.Thread(target=olt6.getOnuInfo)
			th_olt6.start()
		time.sleep(2)
		if not th_olt1.isAlive():
			print "th_olt1 is not alive, staring th_olt1..."
			th_olt1 = threading.Thread(target=olt1.getOnuInfo)
			th_olt1.start()
		time.sleep(2)
		if not th_olt2.isAlive():
			print "th_olt2 is not alive, staring th_olt2..."
			th_olt2 = threading.Thread(target=olt2.getOnuInfo)
			th_olt2.start()
		time.sleep(2)
		if not th_olt3.isAlive():
			print "th_olt3 is not alive, staring th_olt3..."
			th_olt3 = threading.Thread(target=olt3.getOnuInfo)
			th_olt3.start()
		#if not th_olt5.isAlive():
		#	print "th_olt5 is not alive, staring th_olt5..."
		#	th_olt5 = threading.Thread(target=olt5.getOnuInfo)
		#	th_olt5.start()
		time.sleep(2)
		#if counter == 15:
		#	os.system('clear')
		#	counter=0
		#print "Counter",counter
		#if counter>300:
		#	counter=0
		#	print "UPDATING BASIC DATA"
		##	olt4up = threading.Thread(target=olt4.updateBasicData)
		#	olt6up = threading.Thread(target=olt6.updateBasicData)
		##	olt4up.start()
		#	olt6up.start()

			#olt4.updateBasicData()
			#olt6.updateBasicData()

		
		
