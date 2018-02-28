from oltClass import olt
from onuClass import onu
from multiprocessing.pool import ThreadPool



if __name__ == '__main__':
	pool = ThreadPool(processes = 6)

	olt6 = olt('10.99.8.1','t0p$3cr37')
	olt6.getOnuInfo()


