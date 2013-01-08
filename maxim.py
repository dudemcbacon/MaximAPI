#!/usr/bin/python
from smartcard.System import readers
from smartcard.util import toHexString

class MaximAPI:

	_PASSTHRU = [0x00, 0x00, 0x00, 0x00]
	
	def __init__(self, reader, a=0xA0):
		if reader.__doc__ != "PCSC reader class.":
			raise TypeError("reader not PCSC reader class")
		else:
			self.reader = reader
		self.a = a
		
	def GetVersion(self):
		INS = 0x6F
		P1 = 0x00
		P2 = 0x00
		L = 0x00
		
	def GetInterfaceMap(self, interface=0):
		"""Returns a list of currently attached interfaces.
		
		Key arguments:
		interface -- the interface class to be returned (default 0 - all)
		"""
		INS = 0x50
		P2 = 0x00
		L = 0x00
		
		if interface in range(0,8):
			P1 = 0x00