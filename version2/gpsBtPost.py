import serial
import time
import re
import json
import bluetooth

from datetime import timedelta
from temps import *
from fileManagement import *
from threading import Thread
from Queue import Queue
from clases import *

time.sleep(10)
try:
	from camion import camioncito
except:
	camioncito = "0"
try:
        notSent = readNotSent('notSentGPS.txt')
except:
        notSent = ""

tempsInfo = Queue()

from datetime import datetime

def readTemps():
	try:
		while True:
			server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

			port=1
			server_sock.bind(("", port))
			server_sock.listen(1)

			client_sock, address = server_sock.accept()
			#print "Accepted Connection from ", address

			data = client_sock.recv(1024)
			tempsInfo.put(data)
			#print "received [%s]" % data

			client_sock.close()
			server_sock.close()
	except KeyboardInterrupt:
		print('Apagando Bluetooth Socket')
		if data != None:
			client_sock.close()
			server_sock.close()

## Create thread to put information in the Queue
thread1 = Thread(target=readTemps)
thread1.setDaemon(True)
thread1.start()


## Variables for GPS
gps = {}
deltatie = 600
lastSentGPS = datetime.now() - timedelta(seconds=deltatie)
fechaAct = ""
fechaAnt = ""
lonAnt = None
latAnt = None
guardian = guardian("/dev/ttyS0",115200,camioncito)

if not(guardian.isOn()):
        guardian.turnOn()

guardian.setGPRS()
#connection = guardian.isConnected()

toSend = notSent.split('@')
#print(toSend)

try:
	while True:
                try :
                        notSent = readNotSent('notSentGPS.txt')
                except:
                        notSent = ""

		connection = guardian.isConnected()
		toSend = notSent.split('@')
		toSend.pop()
		#print(len(toSend))
		if len(toSend)>0:
			data = toSend.pop(0)
                #print(data)
                	if (data!= '@' and data!='' and data != ' ') and connection:
                		if len(re.findall(r'longitud',data))>0:
                                	#print('entre')
                                	guardian.post(data,'GPS')
                        	else:
                                	guardian.post(data,'Temps')
			notSent = '@'.join(toSend)+'@'
                	time.sleep(0.6)
			#print(len(toSend))
        		if connection and len(toSend)==0:
                		try:
                        		executeBashCommand('rm /home/pi/notSentGPS.txt')
                		except:
                        		pass

		## Checks tempsInfo
		if tempsInfo.qsize() > 0:
			while tempsInfo.qsize() > 0:
				if connection:
					info = tempsInfo.get()
					guardian.post(info,'Temps')
					print(info)
					time.sleep(0.5)
				else:
					createNotSent(notSent + str(info)+'@','notSentGPS.txt')

		gps,status,fix = guardian.getGPS()
		nowGPS = datetime.strptime(gps["fecha"],"%Y-%m-%d %H:%M:%S")
		fechaAct = gps["fecha"]
#		print ((nowGPS - lastSentGPS).total_seconds())
		print(latAnt,lonAnt)
		if ((fechaAct != fechaAnt) and gps['latitud'] != "" and gps['longitud']!= "" and gps['latitud'] != latAnt and gps['longitud'] != lonAnt):
			print(gps,status,fix,connection)
			if connection:
				guardian.post(gps,"GPS")
				#print("envie")
			else:
				createNotSent(notSent + str(gps)+'@','notSentGPS.txt')
			lastSentGPS = nowGPS
		elif ((nowGPS - lastSentGPS).total_seconds() > deltatie) and gps['latitud'] != "" and gps['longitud']!= "":
			print(gps,status,fix,connection)
			if connection:
				guardian.post(gps,"GPS")
				#print("envie")
			else:
				createNotSent(notSent + str(gps)+'@','notSentGPS.txt')
			lastSentGPS = nowGPS

		fechaAnt = fechaAct
		lonAnt = gps['longitud']
		latAnt = gps['latitud']
		data = ""
		time.sleep(120)
except KeyboardInterrupt:
	print('Apagando')
	guardian.desertar()
