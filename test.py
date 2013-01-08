#!/usr/bin/python
from smartcard.System import readers
import maxim

r = readers()
max = maxim.MaximAPI(r[0])
max.Connect()
blah = max.GetVersion()

print(blah)

