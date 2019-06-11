import serial
import time
import re

from datetime import timedelta
from temps import *

try:
	from camion import camioncito
except:
	camioncito = "0"

from datetime import datetime

ser = serial.Serial("/dev/ttyS0",115200)

## AT commands to use
#pause = 10000  ## time to wait for the data to do the http POST
gprs = ['at+sapbr=3,1,"Contype","GPRS"\r\n','at+sapbr=3,1,"APN","internet.itelcel.com"\r\n','at+sapbr=1,1\r\n','at+sapbr=2,1\r\n']

ser.flushInput()
## Setting the GPRS Connection
for command in gprs:
	ser.write(command)
	time.sleep(0.5)

#ser.flushInput()
def isConnected():
	response = ""
	while ser.inWaiting() > 0:
		response += ser.read(ser.inWaiting())
	print(response)
	if len(re.findall(r'\"\d*\.\d*\.\d*\.\d*\"',response))>0:
		return True
	else:
		return False

if __name__ == "__main__":
	x =isConnected()
	print(x)
