import serial
import time
import re
import json

from datetime import timedelta
from temps import *
from fileManagement import *

try:
	from camion import camioncito
except:
	camioncito = "0"

try:
	notSentGPS = readNotSent('notSentGPS.txt')
except:
	notSentGPS = ""

try:
	notSentCon = readNotSent('notSentCon.txt')
except:
	notSentCon = ""

try:
	notSentRef = readNotSent('notSentRef.txt')
except:
	notSentRef = ""

def isConnected():
	response = ""
	while ser.inWaiting() > 0:
		response += ser.read(ser.inWaiting())
	if len(re.findall(r"\"\d*\.\d*\.\d*\.\d*\"",response))>0:
		return True
	else:
		return False


def post(data,tipo):
	pause = 10000  ## time to wait for the data to do the http POST
	if tipo == "GPS":
		http = ['at+httpinit\r\n','at+httppara="CID",1\r\n','at+httppara="URL","http://201.170.127.72:8092/api/GPS"\r\n','at+httppara="CONTENT","application/json"\r\n','at+httpdata=319488,'+str(pause)+'\r\n','at+httpaction=1\r\n','at+httpread\r\n','at+httpterm\r\n']
	elif tipo == "Temps":
		http = ['at+httpinit\r\n','at+httppara="CID",1\r\n','at+httppara="URL","http://201.170.127.72:8092/api/Temps"\r\n','at+httppara="CONTENT","application/json"\r\n','at+httpdata=319488,'+str(pause)+'\r\n','at+httpaction=1\r\n','at+httpread\r\n','at+httpterm\r\n']

	for hCom in http:
		com = hCom.split('=')
		if com[0] == "at+httpdata":
			ser.write(hCom)
			time.sleep(1)
			ser.write(str(data))
			time.sleep(pause/1000)
		elif com[0] == "at+httpaction":
			ser.write(hCom)
			time.sleep(4.5)
			response = ""
		else:
			ser.write(hCom)
		time.sleep(0.5)
	return response
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

connection = isConnected()
toSend = (notSentGPS + notSentCon + notSentRef).split('@')
print(toSend)
try:
	for data in toSend:
		print(data)
		if (data != ''and data !='@'and data !=' ') and connection:
			if 'longitud' in json.loads(data).keys():
				post(data,'GPS')
			else:
				post(data,'Temps')
		time.sleep(0.5)
except KeyboardInterrupt:
	print('Apagando')
	if ser != None:
		ser.write("at+httpterm\r\n")
		ser.close()

