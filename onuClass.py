class onu():
	def __init__(self,OLTip, OLTinterface, ONUid, ONUProfile, ONUModel, ONURX, ONUDistance, ONUStatus, InternetVlan):
		self.OLTIP=OLTip
		self.OLTinterface=OLTinterface
		self.ONUid=ONUid
		self.ONUProfile=ONUProfile
		self.ONUModel=ONUModel
		self.ONURX=ONURX
		self.ONUDistance=ONUDistance
		self.ONUStatus=ONUStatus
		self.Vlan= InternetVlan
	def getCurrentIPAddress(self):
		pass
	def getCurrentStatus(self):
		pass
	def getMacAddressTable(self):
		pass