#!/usr/bin/python
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from array import array
import maxim, unittest

#_SELECT_PSE = [0x00, 0xA4, 0x04, 0x00, 0x0E, 0x31, 0x50, 0x41, 0x59, 0x2E, 0x53, 0x59, 0x53, 0x2E, 0x44, 0x44, 0x46, 0x30, 0x31]

class GetVersion(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		
	def testReturnValue(self):
		r = self.max.GetVersion()
		self.assertTrue(isinstance(r, unicode))
		
class KeypadTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.timeout = 0b10000111
		
	def testKeyOne(self):
		print("Press the 1 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 1)
		
	def testKeyTwo(self):
		print("Press the 2 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 2)
		
	def testKeyThree(self):
		print("Press the 3 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 3)
	
	def testKeyFour(self):
		print("Press the 4 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 4)
		
	def testKeyFive(self):
		print("Press the 5 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 5)
		
	def testKeySix(self):
		print("Press the 6 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 6)
		
	def testKeySeven(self):
		print("Press the 7 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 7)
		
	def testKeyEight(self):
		print("Press the 8 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 8)
		
	def testKeyNine(self):
		print("Press the 9 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 9)
		
	def testKeyZero(self):
		print("Press the 0 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 0)
		
	def testKeyEnter(self):
		print("Press the Enter key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 0x0D)
		
	def testKeyBackspace(self):
		print("Press the Backspace key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 0x08)
		
	def testKeyCancel(self):
		print("Press the Cancel key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 0x18)
		
	def testKeyFunction1(self):
		print("Press the F1 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 0x11)
		
	def testKeyFunction2(self):
		print("Press the F2 key.")
		r = self.max.Read(5, self.timeout, 1)
		self.assertTrue(r, 0x12)
		
class LEDTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		
	def testLED1(self):
		self.max.write()
		i = raw_input("Did the green LED light up? (y/n)")
		self.assertEquals(i, 'y')
		
	def testLED2(self):
		self.max.write()
		i = raw_input("Did the red LED light up? (y/n)")
		self.assertEquals(i, 'y')
		
class CardReaderTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		
	def testMagStripe(self):
		pass
		
	def testContactCard(self):
		pass
		
	def testContactlessCard(self):
		pass

class DisplayTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()

	def testOneLine(LCD):
		pass
	
	def testTwoLines(LCD):
		pass
		
def main():
	unittest.main(defaultTest='GetVersion')

if __name__ == '__main__':
	main()
