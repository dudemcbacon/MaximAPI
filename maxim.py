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
		self.foo = bar