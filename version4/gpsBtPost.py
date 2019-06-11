import serial
import time
import re
import json
import bluetooth

from datetime import timedelta
from datetime import datetime
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

bd_addr = "98:D3:32:21:56:16" #//The address from the HC-05 sensor
port = 1
#sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)


def connect(sock):
	lock = False
	while not(lock):
		try:
			sock.connect((bd_addr,port))
			print ("Connected")
			return True
		except Exception as e:
			#print("Host down, closing socket "+str(e))
			sock.close()
			time.sleep(2)
			sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)

def readTemps():
	sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
	connected = connect(sock)

	while connected:
		print("Ok")
		try:
			data = ""
        		lock = False
       			while 1:
               			try:
                        		data += sock.recv(1024)
                        		data_end = data.find('\n')
                       			if data_end != -1:
                                		rec = data[:data_end+1]
                                		rec =  rec.replace('*', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                		rec = rec.replace('Camioncito',str(camioncito))
						if len(re.findall(r'Host',rec))==0:
							tempsInfo.put(rec.split('\n')[0])
						data = data[data_end+1:]
                		except KeyboardInterrupt:
                        		sock.close()
                        		break
        		sock.close()

		except Exception as e:
			print (e)
			print("Not ok")
			sock.close()
			time.sleep(2)
			#connected = False
			sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
			print ("Reconnecting...")
		#while not connected:
			connected = connect(sock)

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
numFalse = -1
guardian = guardian("/dev/ttyS0",115200,camioncito)

if not(guardian.isOn()):
        guardian.turnOn()

guardian.setGPRS()
lastConnection = guardian.isConnected()

toSend = notSent.split('@')

try:
	while True:
                try :
                        notSent = readNotSent('notSentGPS.txt')
                except:
                        notSent = ""

		connection = guardian.isConnected()

		if not(connection):
			numFalse += 1

		if numFalse >= 10:
			guardian.turnOn()
			executeBashCommand('sudo reboot')

		## Checks tempsInfo
		if tempsInfo.qsize() > 0:
			contador = 0
			while tempsInfo.qsize() > 0 and contador < 2:
				info = tempsInfo.get()
				if connection:
					#info = tempsInfo.get()
					guardian.post(info,'Temps')
					print(info)
					time.sleep(0.5)
				else:
					createNotSent(notSent + str(info)+'@','notSentGPS.txt')
				contador += 1

		gps,status,fix = guardian.getGPS()
		try:
			nowGPS = datetime.strptime(gps["fecha"],"%Y-%m-%d %H:%M:%S")
			fechaAct = gps["fecha"]
		except:
			nowGPS = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
			fechaAct = ""
			gps['latitud']=""
			gps['longitud']=""
#		fechaAct = gps["fecha"]
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


		try :
                        notSent = readNotSent('notSentGPS.txt')
                except:
                        notSent = ""

                toSend = notSent.split('@')
                toSend.pop()
                #print(len(toSend))
                if len(toSend)>0:
                        #data = toSend.pop(0)
                #print(data)
			if len(toSend)>=5 and connection:
				for i in range(5):
					data = toSend.pop(0)
                        		if (data!= '@' and data!='' and data != ' '): #and connection:
                                		if len(re.findall(r'longitud',data))>0:
                                        		#print('entre')
                                       	 		guardian.post(data,'GPS')
                                		else:
                                        		guardian.post(data,'Temps')
                                		notSent = '@'.join(toSend)+'@'
                                		createNotSent(notSent,'notSentGPS.txt')
                                		time.sleep(0.6)
                                		#print(len(toSend))
                                		if len(toSend)==0:
                                        		try:
                                                		executeBashCommand('rm /home/pi/notSentGPS.txt')
                                        		except:
                                                		pass
			elif len(toSend) <5 and connection:
				dif = 5 - len(toSend)
                                for i in range(len(toSend)):
                                        data = toSend.pop(0)
                                        if (data!= '@' and data!='' and data != ' ') and connection:
                                               	if len(re.findall(r'longitud',data))>0:
                                                       	#print('entre')
                                                       	guardian.post(data,'GPS')
                                               	else:
                                                       	guardian.post(data,'Temps')
                                               	notSent = '@'.join(toSend)+'@'
                                               	createNotSent(notSent,'notSentGPS.txt')
                                               	time.sleep(0.6)
                                               	#print(len(toSend))
                                               	if connection and len(toSend)==0:
                                                       	try:
                                                       	        executeBashCommand('rm /home/pi/notSentGPS.txt')
                                                       	except:
                                                               	pass
				time.sleep(dif*20)
			else:
				time.sleep(100)

		else:
			time.sleep(100)

except KeyboardInterrupt:
	print('Apagando')
	guardian.desertar()
