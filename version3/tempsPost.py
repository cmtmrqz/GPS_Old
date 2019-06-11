import serial
import time

from datetime import datetime
from temps import *
from fileManagement import *

try:
	from camion import camioncito
except:
	pass

def isConnected():
	response = ""
	while ser.inWaiting() > 0:
		response += ser.read(ser.inWaiting())
	if len(re.findall(r'\"\d*\.\d*\.\d*\.\d*\"',response))>0:
		return True
	else:
		return False

tConPast = None
tRefPast = None
tConNow = None
tRefNow = None

hConPast = None
hRefPast = None
hConNow = None
hRefNow = None

ser = serial.Serial("/dev/ttyS0",115200)

## AT commands to use
pause = 10000  ## time to wait for the data to do the http POST
gprs = ['at+sapbr=3,1,"Contype","GPRS"\r\n','at+sapbr=3,1,"APN","internet.itelcel.com"\r\n','at+sapbr=1,1\r\n','at+sapbr=2,1\r\n']
http = ['at+httpinit\r\n','at+httppara="CID",1\r\n','at+httppara="URL","http://201.170.127.72:8092/api/Temps"\r\n','at+httppara="CONTENT","application/json"\r\n','at+httpdata=319488,'+str(pause)+'\r\n','at+httpaction=1\r\n','at+httpread\r\n','at+httpterm\r\n']

ser.flushInput()
## Setting the GPRS Connection
for command in gprs:
	ser.write(command)
	time.sleep(0.5)

connection = isConnected()

data=""
num=0

try:
	while True:
		try:
		        notSentCon = readNotSent('notSentCon.txt')
		except:
        		notSentCon = ""

		try:
        		notSentRef = readNotSent('notSentRef.txt')
		except:
       	 		notSentRef = ""

		conge,refri = getTemps()
		tConNow = conge["Temperatura"]
		tRefNow = refri["Temperatura"]

		hConNow = conge["Humedad"]
		hRefNow = refri["Humedad"]

		if (tConNow != tConPast or hConNow != hConPast) and connection:
			print(conge)
			for hCom in http:
				com = hCom.split('=')
				#print(hCom,com)
				if com[0] == "at+httpdata":
					ser.write(hCom)
					time.sleep(1)
					ser.write(str(conge))
					time.sleep(pause/1000)
				elif com[0] == "at+httpaction":
					ser.write(hCom)
					time.sleep(4.5)
				else:
					ser.write(hCom)
	#			print(ser.read(ser.inWaiting()))
				time.sleep(0.5)
		elif not connection and (tConNow != tConPast or hConNow != hConPast):
			createNotSent(notSentCon + str(conge)+'@','notSentCon.txt')
		if (tRefNow != tRefPast or hRefNow != hRefPast) and connection:
			print(refri)
                        for hCom in http:
                                com = hCom.split('=')
                                if com[0] == "at+httpdata":
                                        ser.write(hCom)
                                        time.sleep(1)
                                        ser.write(str(refri))
                                        time.sleep(pause/1000)
                                elif com[0] == "at+httpaction":
                                        ser.write(hCom)
                                        time.sleep(4.5)
                                else:
                                        ser.write(hCom)
        #                       print(ser.read(ser.inWaiting()))
                                time.sleep(0.5)
		if (tRefNow != tRefPast or hRefNow != hRefPast) and not(connection):
			createNotSent(notSentRef  + str(refri)+'@','notSentRef.txt')

		tRefPast = tRefNow
		tConPast = tConNow

		hRefPast = hRefNow
		hConPast = hConNow
except KeyboardInterrupt:
	print('Apagando')
	if ser != None:
		ser.write("at+httpterm\r\n")
		ser.close()

