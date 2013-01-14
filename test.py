#!/usr/bin/python
from smartcard.System import readers
from array import array
import maxim

_SELECT_PSE = [0x00, 0xA4, 0x04, 0x00, 0x0E, 0x31, 0x50, 0x41, 0x59, 0x2E, 0x53, 0x59, 0x53, 0x2E, 0x44, 0x44, 0x46, 0x30, 0x31]

r = readers()
max = maxim.MaximAPI(r[0])
max.Connect()
print max.GetVersion()
for int in max.GetInterfaceMap():
	print int
	

print max.Transact(02, 0x8F, _SELECT_PSE, 26)
print max.Read(02, 0x8F)


