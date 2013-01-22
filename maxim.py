#!/usr/bin/python
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from array import array

class MaximAPI:

	_PASSTHRU = [0x00, 0x00, 0x00, 0x00]
	
	def __init__(self, reader, a=0xA0, debug=True):
		if reader.__doc__ != "PCSC reader class.":
			raise TypeError("reader not PCSC reader class")
		else:
			self.reader = reader
		self.a = a
		self.debug = debug
		self.last_sent = ''
		self.last_received = ''
	
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

		#raw_input("Please enter passthru mode on Kremlin I. Press any key to continue.")

		#data, sw1, sw2 = self._send_apdu( PASSTHRU )

		#if sw1 == 0x00 and sw2 == 0x04:
		#	pass
		#else:
		#	raise MaximException("Could not enter passthru mode.")
		
	def GetVersion(self):
		"""Returns a unicode string of the current firmware version running on the board
		"""
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
			self._decode_error_response(sw1, sw2)
			
	def GetInterfaceMap(self, interface=0):
		"""Returns a list of currently attached interfaces.
		
		Key arguments:
		interface -- the interface class to be returned (default 0 - all)
		"""
		A = self.a
		INS = 0x50
		P2 = 0x00
		L = 0x00
		
		if interface in range(0,8):
			P1 = interface
		else:
			raise MaximException("Invalid interface.")
			
		APDU = self._create_apdu(A, INS, P1, P2, L)
		data, sw1, sw2 = self._send_apdu( APDU )
		parsed = []
		
		if sw1 == 0x90 and sw2 == 0x00:
			if data[0:1] == [0xE0]:
				data = toHexString(data[2:]).replace(" ", "").split("C002")
				for str in data:
					if str != '':
						parsed.append(self._decode_interface_map(toBytes(str)))
				return parsed
			elif data[0:1] == [0x10]:
				print("Warning: incorrect list response from GetInterfaceMap().")
				data = toHexString(data[1:]).replace(" ", "").split("C002")
				for str in data:
					if str != '':
						parsed.append(self._decode_interface_map(toBytes(str)))
				return parsed
			elif data[0:1] == [0xC0]:
				# TODO: Add case for single item response
				print "finish this section"
			else:
				raise MaximException("Invalid response: {0}".format(toHexString(data)))
		else:
			self._decode_error_response(sw1, sw2)
	
	def Read(self, interface, timeout, expected_data = 0):
		"""Reads information from the requested interface.
		
		Key arguments:
		interface -- the specified interface (int)
		timeout -- 1ms (0b1-------), 10ms interval (0b0-------), wait until reset (0xFF)
		expected_data (optional) -- size of the expected response data
		"""
		A = self.a
		INS = 0x54
		
		if interface in range(0,8):
			P1 = interface
		else:
			raise MaximException("Invalid interface.")
			
		if timeout <= 255:
			P2 = timeout
		else:
			raise MaximException("Timeout value must be one byte.")
		
		Le = self._format_byte_length(expected_data)

		#TODO: add expected data length to APDU
		APDU = self._create_apdu(A, INS, P1, P2)
		data, sw1, sw2 = self._send_apdu( APDU )
		
		if sw1 == 0x90 and sw2 == 0x00:
			return data
		else:
			self._decode_error_response(sw1, sw2)
		
	def Transact(self, interface, timeout, data, expected_bytes):
		"""Executes a write-followed-by-read transaction on the specified interface.
		
		Key arguments:
		interface -- the specified interface (int)
		timeout -- 10ms (0b1-------), 1s interval (0b0-------), wait until reset (0xFF)
		data -- the data to be written to the device
		"""
		A = self.a
		INS = 0x58
		
		if interface in range(0,8):
			P1 = interface
		else:
			raise MaximException("Invalid interface.")
			
		if timeout < 255:
			P2 = timeout
		else:
			raise MaximException("Timeout value must be one byte.")
		
		Lc = self._format_byte_length(len(data))
		
		Le = self._format_byte_length(expected_bytes)
		
		APDU = self._create_apdu(A, INS, P1, P2, *Lc + data + Le)
		data, sw1, sw2 = self._send_apdu( APDU )
		
		if sw1 == 0x90 and sw2 == 0x00:
			return data
		else:
			self._decode_error_response(sw1, sw2)
	
	def Reset(self, interface=0x00, type=0):
		"""Resets the interface identified byte the specified ID.
		
		Key arguments:
		interface -- the specified interface (default 0 - all)
		type -- reset type: 0 - hard reset, 1 - soft reset
		"""
		A = self.a
		INS = 0x52
		
		if interface in range(0,8):
			P1 = interface
		else:
			raise MaximException("Invalid interface.")
			
		if type in range(0,2):
			P2 = type
		else:
			raise MaximException("Invalid reset-type.")
			
		APDU = self._create_apdu(A, INS, P1, P2)
		data, sw1, sw2 = self._send_apdu( APDU )
		
		if sw1 == 0x90 and sw2 == 0x00:
			return True
		else:
			self._decode_error_response(sw1, sw2)		

	def Write(self, interface, byte_array=[]):
		"""Writes information to the specified interface
		
		Key arguments:
		interface -- the specified interface
		byte_array -- byte list of data to be written to interface
		"""
		A = self.a
		INS = 0x56
		P2 = 0x00
		
		if interface in range(0,8):
			P1 = interface
		else:
			raise MaximException("Invalid interface.")
		
		if byte_array == []:
			raise MaximException("byte_array contains no data.")
		
		L = self._format_byte_length(len(byte_array))
		#if len(byte_array) < 256:
		#	L = array('b', [len(byte_array)])
		#elif len(byte_array) > 256 and len(byte_array) < 65536:
		#	L = array('b', [0x00, len(byte_array)])

		APDU = self._create_apdu(A, INS, P1, P2, *L + byte_array)
		data, sw1, sw2 = self._send_apdu( APDU )
		
		if sw1 == 0x90 and sw2 == 0x00:
			return True
		else:
			self._decode_error_response(sw1, sw2)
			
	def Enable(self, interface, req=128):
		"""Sets or gets the enable state of a specified interface.
		
		Key arguments:
		req -- 0: disable interface, 1: enable interface, 128: read interface state
		"""
		A = self.a
		INS = 0x5A
		P2 = req
		if interface in range(0,8):
			P1 = interface
		else:
			raise MaximException("Invalid interface.")
			
		if req == 0 or req == 1 or req == 128:
			P2 = req
		else:
			MaximException("req must be equal to 0, 1, or 128.")
			
		APDU = self._create_apdu(A, INS, P1, P2)
		data, sw1, sw2 = self._send_apdu( APDU )
		
		if req == 128:
			if sw1 == 0x90 and sw2 == 0x00:
				return True
		
		if sw1 == 0x90:
			if sw2 == 0x00:
				return False
			if sw2 == 0x01:
				return True
		else:
			self._decode_error_response(sw1, sw2)
			
	def WaitForCard(self, interface, timeout, list=[]):
		"""
		Waits for a card to be presented on one or more interfaces.
		
		Key arguments:
		interface -- 0x00 (all; default), 0x01-0x07 (the specified interface), 0xFF (list of interfaces) 
		timeout -- 10ms interval (0b1-------), 1s interval (0b0-------), wait until reset (0xFF)
		list -- byte array of interfaces (interface must be set to 0xFF)
		"""
		A = self.a
		INS = 0x5C
		
		if interface != 0xFF:
			if interface in range(0,8):
				P1 = interface
			else:
				raise MaximException("Invalid interface.")
		else:
			P1 = interface
		
		if timeout < 255:
			P2 = timeout
		else:
			raise MaximException("Timeout value must be one byte.")
		
		if P1 == 0xFF:
			L = len(list)
		else:
			L = 0x00
			
		APDU = self._create_apdu(A, INS, P1, P2, L, *list)
		data, sw1, sw2 = self._send_apdu( APDU )	
		
		if sw1 == 0x90:
			return sw2
		else:
			self._decode_error_response(sw1, sw2)
			
	def IOCTL(self, interface, command, expected_data):
		"""Perform an interface-specific I/O Control operation
		
		Key arguments:
		interface -- interface -- the specified interface
		command -- byte array of the command data
		expected_data -- size of the expected response data
		"""
		A = self.a
		INS = 0x6E
		P2 = 0x00
		
		if interface in range(0,8):
			P1 = interface
		else:
			raise MaximException("Invalid interface.")
		
		Lc = self._format_byte_length(len(command))		
			
		Le = self._format_byte_length(expected_data)
		
		APDU = self._create_apdu(A, INS, P1, P2, *Lc + command + Le)
		data, sw1, sw2 = self._send_apdu( APDU )
		
		if sw1 == 0x90 and sw2 == 0x00:
			return data
		else:
			self._decode_error_response(sw1, sw2)
		
		
		
	def _create_apdu(self, *arg):
		apdu = []
		for i in arg:
			apdu.append(i)
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
		self.last_sent = apdu
		self.last_received = data + [sw1, sw2]
		if self.debug == True:
			print("<-- {0}".format(toHexString(data)))
			print("<-- {0}".format(toHexString([sw1, sw2])))
			print("")
		return data, sw1, sw2
		
	def _decode_interface_map(self, b):
		idbits = b[0] >> 5
		classbits = (b[0] & 28) >> 2
		rwbits = b[0] & 3
		datatype = b[1] >> 2
		bcbits = b[1] & 3
		
		decoded_bytes = {'id':idbits, 'class':self._class(classbits), 'r/w':self._rw(rwbits), 'data':self._data(datatype), "b/c":self._bc(bcbits)}
		
		return decoded_bytes
	
	def _decode_error_response(self, sw1, sw2):
		if sw1 == 0x64 and sw2 == 0x00:
			raise MaximException("Read not allowed on interface.")
		elif sw1 == 0x64 and sw2 == 0x01:
			raise MaximException("Write not allowed on interface.")
		elif sw1 == 0x64 and sw2 == 0x02:
			raise MaximException("Interface is disabled.")
		elif sw1 == 0x65 and sw2 == 0x00:
			raise MaximException("Read timeout on interface {0}.".format(toHexString([sw2])))
		elif sw1 == 0x6A and sw2 == 0x80:
			raise MaximException("Malformed command.")
		elif sw1 == 0x6A:
			raise MaximException("Unrecognized interface: {0}".format(toHexString([sw2])))
		elif sw1 == 0x6F and sw2 == 0x00:
			raise MaximException("Interface error.")
		else:
			raise MaximException("Unrecognized return code: %s %s." % (toHexString([sw1]), toHexString([sw2])))
		
	def _format_byte_length(self, expected_data):
		if expected_data < 256:
			Le = array('b', [expected_data])
		elif expected_data > 256 and expected_data < 65536:
			Le = array('b', [0x00, expected_data])
		else:
			raise MaximException("Expected data length can not be above 65535.")
			
		return Le.tolist()
	
	def _class(self, x):
		return {
			0 : 'Unknown',
			1 : 'Card Reader (magnetic)',
			2 : 'Card Reader (contact)',
			3 : 'Card Reader (contactless)',
			4 : 'Display',
			5 : 'Input (alphanumberic)',
			6 : 'Reserved',
			7 : 'Reserved'
			}.get(x, 0)
	
	def _data(self, x):
		if x > 4: x = 5
		return {
			0 : 'Null Data',
			1 : 'Track Data',
			2 : 'Card Data',
			3 : 'AlphaNum Data',
			4 : 'LED Matrix Data',
			5 : 'Reserved'
			}.get(x, 0)
			
	def _rw(self, x):
		return {
			0 : 'N/A',
			1 : 'Write-only',
			2 : 'Read-only',
			3 : 'Read/Write'
			}.get(x, 0)
			
	def _bc(self, x):
		return {
			0 : 'N/A',
			1 : 'Character-only',
			2 : 'Block-only',
			3 : 'Block + Character'
			}.get(x, 0)
		
class MaximException(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return repr(self.message)