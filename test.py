#!/usr/bin/python
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from array import array
import maxim, unittest, time, sys, StringIO, HTMLTestRunner, logging
from maxim import MaximException

#_SELECT_PSE = [0x00, 0xA4, 0x04, 0x00, 0x0E, 0x31, 0x50, 0x41, 0x59, 0x2E, 0x53, 0x59, 0x53, 0x2E, 0x44, 0x44, 0x46, 0x30, 0x31]

_ANY_INTERFACE = 00
_MAG_INTERFACE = 01
_EMV_INTERFACE = 02
_LCD_INTERFACE = 04
_PIN_INTERFACE = 05
_LED_INTERFACE = 06
_UNK_INTERFACE = 07

class GetVersionTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		
	def testReturnValue(self):
		r = self.max.GetVersion()
		print("Running version {0}".format(r))
		self.assertTrue(isinstance(r, unicode))

class GetInterfaceMapTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
	
	def testReturnValue(self):
		r = self.max.GetInterfaceMap(01)
		self.assertTrue(isinstance(r, list))

class ResetTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.UnknownInterfaces = [3, 7]
	
	def testHardResetAllInterface(self):
		self.max.Reset(00)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
			
	def testHardResetMagReader(self):
		self.max.Reset(1)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testHardResetEMVReader(self):
		self.max.Reset(2)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testHardResetDisplay(self):
		self.max.Reset(4)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testHardResetPinPad(self):
		self.max.Reset(5)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testHardResetLED(self):
		self.max.Reset(6)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
	
	def testSoftResetAllInterface(self):
		self.max.Reset(00, 1)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
			
	def testSoftResetMagReader(self):
		self.max.Reset(1, 1)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testSoftResetEMVReader(self):
		self.max.Reset(2, 1)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testSoftResetDisplay(self):
		self.max.Reset(4, 1)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testSoftResetPinPad(self):
		self.max.Reset(5, 1)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testSoftResetLED(self):
		self.max.Reset(6, 1)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testResetUnknownInterface(self):
		for i in self.UnknownInterfaces:
			self.assertRaises(MaximException, self.max.Reset, i)
			apdu = self.max.last_received
			self.assertEquals(apdu[len(apdu)-2:], [0x6A, i])
			
class WriteTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.UnknownInterfaces = [3, 7]
		
	def testWriteEMV(self):
		self.assertTrue(self.max.Write(_EMV_INTERFACE, [0x00, 0x00]))
		
	def testWriteLCD(self):
		self.assertTrue(self.max.Write(_LCD_INTERFACE, [0x68, 0x65, 0x6c, 0x6c, 0x6f]))
	
	def testWriteLED(self):
		self.assertTrue(self.max.Write(_LED_INTERFACE, [0b11111111]))
	
	def testWriteToReadOnlyMagStripe(self):
		self.assertRaises(MaximException, self.max.Write, (_MAG_INTERFACE, [0x00]))
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, _MAG_INTERFACE])
		
	def testWriteToReadOnlyKeypad(self):
		self.assertRaises(MaximException, self.max.Write, (_LED_INTERFACE, [0x00]))
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, _LED_INTERFACE])
		
	def testWriteToDisabled(self):
		self.assertFalse(self.max.Enable(_LCD_INTERFACE, 0x00))
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, 0x02])
		
	def testWriteToUnknown(self):
		for i in self.UnknownInterfaces:
			self.assertRaises(MaximException, self.max.Write, (i, [0x00]))
			apdu = self.max.last_received
			self.assertEquals(apdu[len(apdu)-2:], [0x64, i])
		
	def testMalformedCommand(self):
		apdu = [0xA0, 0x56, 0x01, 0x43, 0x32, 0x35, 0x23, 0x23, 0x23]
		data, sw1, sw2 = self.max._send_apdu(apdu)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6F, 0x00])

class ReadTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.UnknownInterfaces = [3, 7]
		self.timeout = 0b10000111 # 7 seconds
		
	def testReadMag(self):
		logging.info("Press Enter to read from MAG interface.")
		raw_input()
		self.max.Read(_MAG_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[0:1], [0xE1])
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
		
	def testReadEMV(self):
		logging.info("Press Enter to read from EMV interface.")
		raw_input()
		self.max.Read(_EMV_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[0:1], [0xE2])
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testReadNFC(self):
		self.assertTrue(False)
		
	def testReadLED(self):
		logging.info("Press Enter to read from LED interface.")
		raw_input()
		self.max.Read(_LED_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[0:1], [0xE4])
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testReadPIN(self):
		logging.info("Press Enter to read from PIN interface.")
		raw_input()
		self.max.Read(_PIN_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[0:1], [0xE3])
		self.assertEquals(apdu[len(apdu)-2:], [0x90, 0x00])
		
	def testReadWriteOnly(self):
		self.max.Read(_LCD_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, 0x00])
		
	def testReadDisabled(self):
		self.assertTrue(False)
		
	def testReadTimeoutMS(self):
		timeout = 0b1010 # 10ms
		t1 = time.time()
		self.max.Read(_LED_INTERFACE, timeout, [], 0)
		t2 = time.time()
		self.assertFalse(False) # TODO: Fix when timeout works correctly.
		
	def testReadTimeoutS(self):
		timeout = 0b1010 # 10ms
		t1 = time.time()
		self.max.Transact(_LED_INTERFACE, timeout, [], 0)
		t2 = time.time()
		self.assertFalse(False) # TODO: Fix when timeout works correctly.
		
	def testReadTimeoutForever(self):
		timeout = 0b1010 # 10ms
		t1 = time.time()
		self.max.Transact(_LED_INTERFACE, timeout, [], 0)
		t2 = time.time()
		self.assertFalse(False) # TODO: Fix when timeout works correctly.
		
	def testReadUnknownInterface(self):
		self.assertRaises(MaximException, self.max.Read, _UNK_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6A, _UNK_INTERFACE])
		
	def testMalformedCommand(self):
		apdu = [0xA0, 0x54, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
		data, sw1, sw2 = self.max._send_apdu(apdu)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6F, 0x00])
		
class TransactTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.UnknownInterfaces = [3, 7]
		self.timeout = 0b10000111 # 7 seconds
		
	def testTransactMag(self):
		self.assertRaises(MaximException, self.max.Transact, _MAG_INTERFACE, self.timeout, [], 0)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, 0x01])
	
	def testTransactEMV(self):
		self.max.Transact(_EMV_INTERFACE, self.timeout, [], 0)
		
	def testTransactNFC(self):
		self.assertTrue(False)
		
	def testTransactLCD(self):
		self.max.Transact(_LCD_INTERFACE, self.timeout, [], 0)
	
	def testTransactOnDisabled(self):
		self.assertTrue(False)
	
	def testTransactOnWriteOnly(self):
		pass
		
	def testTransactTimeoutMS(self):
		timeout = 0b1010 # 10ms
		t1 = time.time()
		self.max.Transact(_LCD_INTERFACE, timeout, [], 0)
		t2 = time.time()
		self.assertFalse(False) # TODO: Fix when timeout works correctly.
		
	def testTransactTimeoutSec(self):
		timeout = 0b10001010 # 10s
		t1 = time.time()
		self.max.Transact(_LCD_INTERFACE, timeout, [], 0)
		t2 = time.time()
		self.assertFalse(False) # TODO: Fix when timeout works correctly.
		
	def testTransactTimeoutFF(self):
		timeout = 0xFF # Forever
		t1 = time.time()
		self.max.Transact(_LCD_INTERFACE, timeout, [], 0)
		t2 = time.time()
		self.assertFalse(False) # TODO: Fix when timeout works correctly.
		
	def testTransactUnknownInterface(self):
		self.assertRaises(MaximException, self.max.Transact, _UNK_INTERFACE, self.timeout, [], 0)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6A, _UNK_INTERFACE])
		
	def testMalformedCommand(self):
		apdu = [0xA0, 0x58, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
		data, sw1, sw2 = self.max._send_apdu(apdu)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6F, 0x00])
		
class EnableTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.UnknownInterfaces = [3, 7]
		self._ENABLE = 0x00
		self._DISABLE = 0x01
		self._READ = 0b10000000
		
	def testEnableMag(self):
		self.assertTrue(self.max.Enable(_MAG_INTERFACE, self._ENABLE))
		
	def testEnableEMV(self):
		self.assertTrue(self.max.Enable(_EMV_INTERFACE, self._ENABLE))
		
	def testEnableLCD(self):
		self.assertTrue(self.max.Enable(_LCD_INTERFACE, self._ENABLE))
		
	def testEnableKeypad(self):
		self.assertTrue(self.max.Enable(_PIN_INTERFACE, self._ENABLE))
		
	def testEnableLED(self):
		self.assertTrue(self.max.Enable(_LED_INTERFACE, self._ENABLE))
		
	def testDisableMag(self):
		self.assertFalse(self.max.Enable(_MAG_INTERFACE, self._DISABLE))
		
	def testDisableEMV(self):
		self.assertFalse(self.max.Enable(_EMV_INTERFACE, self._DISABLE))
		
	def testDisableLCD(self):
		self.assertFalse(self.max.Enable(_LCD_INTERFACE, self._DISABLE))
		
	def testDisableKeypad(self):
		self.assertFalse(self.max.Enable(_PIN_INTERFACE, self._DISABLE))
		
	def testDisableLED(self):
		self.assertFalse(self.max.Enable(_LED_INTERFACE, self._DISABLE))
		
	def testReadMag(self):
		self.max.Enable(_MAG_INTERFACE, self._ENABLE)
		self.assertTrue(self.max.Enable(_MAG_INTERFACE, self._READ))
		
	def testReadEMV(self):
		self.max.Enable(_EMV_INTERFACE, self._ENABLE)
		self.assertTrue(self.max.Enable(_EMV_INTERFACE, self._READ))
		
	def testReadLCD(self):
		self.max.Enable(_LCD_INTERFACE, self._ENABLE)
		self.assertTrue(self.max.Enable(_LCD_INTERFACE, self._READ))
		
	def testReadKeypad(self):
		self.max.Enable(_PIN_INTERFACE, self._ENABLE)
		self.assertTrue(self.max.Enable(_PIN_INTERFACE, self._READ))
		
	def testReadLED(self):
		self.max.Enable(_LED_INTERFACE, self._ENABLE)
		self.assertTrue(self.max.Enable(_LED_INTERFACE, self._READ))
		
	def testEnableUnknown(self):
		self.assertRaises(MaximException, self.max.Enable, (_UNK_INTERFACE, self._ENABLE))
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6A, _UNK_INTERFACE])
		
	def testDisableUnknown(self):
		self.assertRaises(MaximException, self.max.Enable, (_UNK_INTERFACE, self._DISABLE))
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6A, _UNK_INTERFACE])
		
	def testReadUnknown(self):
		self.assertRaises(MaximException, self.max.Enable, (_UNK_INTERFACE, self._READ))
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6A, _UNK_INTERFACE])
		
	def testMalformedCommand(self):
		apdu = [0xA0, 0x5A, 0x01, 0x43, 0x32, 0x35, 0x23, 0x23, 0x23]
		data, sw1, sw2 = self.max._send_apdu(apdu)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6F, 0x00])
		
class WaitForCardTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.CardInterfaces = [1,2]
		self.UnknownInterfaces = [3, 7]
		self.timeout = 0b10000111
		
	def testWaitForAny(self):
		logging.info("Press Enter to start waiting on ANY interface.")
		raw_input()
		int = self.max.WaitForCard(_ANY_INTERFACE, self.timeout)
		self.assertTrue(int in self.CardInterfaces)
		
	def testWaitForMag(self):
		logging.info("Press Enter to start waiting on MAG interface.")
		raw_input()
		int = self.max.WaitForCard(_MAG_INTERFACE, self.timeout)
		self.assertTrue(int == _MAG_INTERFACE)
	
	def testWaitForEMV(self):
		logging.info("Press Enter to start waiting on EMV interface.")
		raw_input()
		int = self.max.WaitForCard(_EMV_INTERFACE, self.timeout)
		self.assertTrue(int == _EMV_INTERFACE)
		
	def testWaitForNFC(self):
		self.assertTrue(False)
	
	def testWaitForList(self):
		list = [_MAG_INTERFACE, _EMV_INTERFACE]
		logging.info("Press Enter to start waiting on for list interface.")
		raw_input()
		int = self.max.WaitForCard(0xFF, self.timeout, list)
		self.assertTrue(int in list)
		
	def testWaitForTimeoutMS(self):
		timeout = 0b1010 # 100ms timeout
		logging.info("Remove any card and press Enter to start 100ms Timeout test.")
		raw_input()
		t1 = time.time()
		self.assertRaises(MaximException, self.max.WaitForCard, _ANY_INTERFACE, timeout)
		t2 = time.time()
		self.assertFalse((t2-t1)>100)
		
	def testWaitForTimeoutSec(self):
		timeout = 0b10001010 # 10s timeout
		logging.info("Remove any card and press Enter to start 10s Timeout test.")
		raw_input()
		t1 = time.time()
		self.assertRaises(MaximException, self.max.WaitForCard, _ANY_INTERFACE, timeout)
		t2 = time.time()
		self.assertFalse((t2-t1)>100)
		
	def testWaitForTimeoutFF(self):
		timeout = 0xFF # 10s timeout
		logging.info("Remove any card and press Enter to start 10s Timeout test.")
		raw_input()
		t1 = time.time()
		self.assertRaises(MaximException, self.max.WaitForCard, _ANY_INTERFACE, timeout)
		t2 = time.time()
		self.assertFalse((t2-t1)>100)
		
	def testWaitForNonCardReadingLCD(self):
		self.assertRaises(MaximException, self.max.WaitForCard, _LCD_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, 0x00])
	
	def testWaitForNonCardReadingPIN(self):
		self.assertRaises(MaximException, self.max.WaitForCard, _PIN_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, 0x00])
		
	def testWaitForNonCardReadingLED(self):
		self.assertRaises(MaximException, self.max.WaitForCard, _LED_INTERFACE, self.timeout)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, 0x00])
		
	def testWaitForDisabled(self):
		self.assertTrue(False)
		
	def testWaitForMalformedCommand(self):
		apdu = [0xA0, 0x5C, 0xFF, 0x1010, 0x32, 0x35, 0x23, 0x23, 0x23]
		data, sw1, sw2 = self.max._send_apdu(apdu)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6A, 0x80])
	
class KeypadTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.timeout = 0b10000111
		s
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
		i = logging.info("Did the green LED light up? (y/n)")
		raw_input()
		self.assertEquals(i, 'y')
		
	def testLED2(self):
		self.max.write()
		i = logging.info("Did the red LED light up? (y/n)")
		raw_input()
		self.assertEquals(i, 'y')
		
class CardReaderTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.timeout = 0b10000111
		
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

class BugTests(unittest.TestCase):
	def setUp(self):
		r = readers()
		self.max = maxim.MaximAPI(r[0])
		self.max.Connect()
		self.timeout = 0xFF
		
	def testM4(self):
		self.max.GetInterfaceMap(01)
		self.assertEquals(self.max.last_received[0], '0xC0')
		
	def testM5(self):
		r = self.max.GetInterfaceMap(07)
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x6A, 0x07])
		
	def testM6(self):
		self.max.Read(01, self.timeout, 00)
		apdu = self.max.last_received
		self.assertEquals(apdu[0:4], [0xE1, 0x5D, 0x04, 0x5B])
		
	def testM7(self):
		self.max.Write(04, [0x00, 0x00])
		apdu = self.max.last_received
		self.assertEquals(apdu[len(apdu)-2:], [0x64, 0x01])
		
	def testM8(self):
		self.max.Enable(04)
		apdu = self.max.last_received
		self.assertNotEquals(apdu[len(apdu)-2:], [0x90, 0x00])

class Test_HTMLTestRunner(unittest.TestCase):
	def test_main(self):
		logging.basicConfig(format='\n%(message)s',level=logging.DEBUG)
		self.suite = unittest.TestSuite()
		self.suite.addTests([
			unittest.defaultTestLoader.loadTestsFromTestCase(GetVersionTests),
			unittest.defaultTestLoader.loadTestsFromTestCase(GetInterfaceMapTests),
			unittest.defaultTestLoader.loadTestsFromTestCase(ResetTests),
			unittest.defaultTestLoader.loadTestsFromTestCase(ReadTests),
			unittest.defaultTestLoader.loadTestsFromTestCase(WriteTests),
			unittest.defaultTestLoader.loadTestsFromTestCase(TransactTests),
			unittest.defaultTestLoader.loadTestsFromTestCase(EnableTests),
			unittest.defaultTestLoader.loadTestsFromTestCase(WaitForCardTests)
			])
			
		buf = StringIO.StringIO()	
		runner = HTMLTestRunner.HTMLTestRunner(
			stream=buf,
			title='Findlay Tests',
			description='Lorem ipsum dollar sit amut'
			)
			
		runner.run(self.suite)
		byte_output = buf.getvalue()
		print byte_output
		
def main():
	unittest.main(defaultTest='ReadTests')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        argv = sys.argv
    else:
        argv=['test_HTMLTestRunner.py', 'Test_HTMLTestRunner']
    unittest.main(argv=argv)
