#!/usr/bin/python
from smartcard.System import readers
from smartcard.util import toHexString

class MaximAPI:

	_PASSTHRU = [0x00, 0x00, 0x00, 0x00]
	
	def __init__(self, reader, a=0xA0, debug=True):
		if reader.__doc__ != "PCSC reader class.":
			raise TypeError("reader not PCSC reader class")
		else:
			self.reader = reader
		self.a = a
		self.debug = True
	
	def Connect(self):
		SELECT = [0x00, 0xA4, 0x04, 0x00, 0x06]
		KREMLIN_APP = [0xA0, 0x00, 0x00, 0x05, 0x35, 0x01]
		PASSTHRU = [0x00, 0x00, 0x00, 0x00]
		
		con = self.reader.createConnection()
		con.connect()
		
		if con.getATR() == '':
			raise MaximException("Could not connect to reader.")
		else:
			self.connection = con
		
		data, sw1, sw2 = self._send_apdu( SELECT + KREMLIN_APP )

		if sw1 == 0x90 and sw2 == 0x00:
			pass
		else:
			raise MaximException("Could not select Kremlin app.")

		raw_input("Please enter passthru mode on Kremlin I. Press any key to continue.")

		data, sw1, sw2 = self._send_apdu( PASSTHRU )

		if sw1 == 0x00 and sw2 == 0x04:
			pass
		else:
			raise MaximException("Could not enter passthru mode.")
		
	def GetVersion(self):
		A = self.a
		INS = 0x6F
		P1 = 0x00
		P2 = 0x00
		L = 0x00
		
		APDU = self._create_apdu(A, INS, P1, P2, L)
		
		
		data, sw1, sw2 = self._send_apdu( APDU )
		
		if sw1 == 0x90 and sw2 == 0x00:
			len = data[1]
			return self._convert_to_unicode(data[2:])
		else:
			raise MaximException("Unsuccessful. Returned %s %s." % (toHexString([sw1]), toHexString([sw2])))
			
		
		
		
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

	def _create_apdu(self, A, INS, P1, P2, L):
		apdu = []
		apdu.append(A)
		apdu.append(INS)
		apdu.append(P1)
		apdu.append(P2)
		apdu.append(L)
		return(apdu)
		
	def _convert_to_unicode(self, int_data):
		str = u''
		for int in int_data:
			str = str + unichr(int)
		return str
		
	def _send_apdu(self, apdu):
		if self.debug == True:
			print("--> {0}".format(toHexString(apdu)))
		data, sw1, sw2 = self.connection.transmit(apdu)
		if self.debug == True:
			print("<-- {0}".format(toHexString(data)))
			print("<-- {0}".format(toHexString([sw1, sw2])))
		return data, sw1, sw2
		
class MaximException(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return repr(self.message)