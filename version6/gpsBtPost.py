import serial
import time
import re
import json
import bluetooth

from datetime import timedelta
from datetime import datetime
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

def resendLog(data):
	if (data!= '@' and data!='' and data != ' '): #and connection:
        	if len(re.findall(r'longitud',data))>0:
                	guardian.post(data,'GPS')
        	else:
                	guardian.post(data,'Temps')
                notSent = '@'.join(toSend)+'@'
                createNotSent(notSent,'notSentGPS.txt')
                time.sleep(0.6)
                if len(toSend)==0:
                	try:
                      		executeBashCommand('rm /home/pi/notSentGPS.txt')
                        except:
                       		pass

def connect(sock):
	lock = False
	while not(lock):
		try:
			sock.connect((bd_addr,port))
			print ("Connected")
			return True
		except Exception as e:
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
						if len(re.findall(r'Host',rec))==0 and len(re.findall(r'NAN',rec))==0:
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
			sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
			print ("Reconnecting...")
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
numFalse = 0
noFix = 0
antFix = None
guardian = guardian("/dev/ttyS0",115200,camioncito)

## Checking the status of the HAT: On/Off
if not(guardian.isOn()):
        guardian.turnOn()

guardian.setGPRS()

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

		if numFalse >= 5:
			## agregar todo el queue al documento
			toDoc = ""
			while tempsInfo.qsize() > 0:
				toDoc += str(tempsInfo.get()) +'@'
			createNotSent(notSent + toDoc,'notSentGPS.txt')
			guardian.turnOn()
			executeBashCommand('sudo reboot')

		## Checks tempsInfo
		if len(executeBashCommand('cat /home/pi/notSentGPS.py'))>0:
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

		if str(fix) == '0' or str(fix) =='':
			gps,status,fix = guardian.getGPSbyGSM(),'byGSM','byGSM'

		if noFix >= 5:
			toDoc = ""
                        while tempsInfo.qsize() > 0:
                                toDoc += str(tempsInfo.get()) +'@'
                        createNotSent(notSent + toDoc,'notSentGPS.txt')
			guardian.turnOn()
			executeBashCommand('sudo reboot')

		print(latAnt,lonAnt)
		try:
			nowGPS = datetime.strptime(gps["fecha"],"%Y-%m-%d %H:%M:%S")
                        fechaAct = gps["fecha"]

			if ((fechaAct != fechaAnt) and gps['latitud'] != "" and gps['longitud']!= "" and (gps['latitud'] != latAnt or gps['longitud'] != lonAnt)):
				print(gps,status,fix,connection)
				if connection:
					guardian.post(gps,"GPS")
				else:
					createNotSent(notSent + str(gps)+'@','notSentGPS.txt')
				lastSentGPS = nowGPS
			elif ((nowGPS - lastSentGPS).total_seconds() > deltatie) and gps['latitud'] != "" and gps['longitud']!= "":
				print(gps,status,fix,connection)
				if connection:
					guardian.post(gps,"GPS")
				else:
					createNotSent(notSent + str(gps)+'@','notSentGPS.txt')
				lastSentGPS = nowGPS

			fechaAnt = fechaAct
                	lonAnt = gps['longitud']
                	latAnt = gps['latitud']
                	data = ""
			noFix = 0
		except KeyboardInterrupt:
			print('Apagando')
        		guardian.desertar()
		except:
			noFix += 1
			print('No hay datos. Probablemente no tengo FIX el GPS.')


		try :
                        notSent = readNotSent('notSentGPS.txt')
                except:
                        notSent = ""

                toSend = notSent.split('@')
                toSend.pop()
                if len(toSend)>0:
			if len(toSend)>=5 and connection:
				for i in range(5):
					data = toSend.pop(0)
					resendLog(data)
			elif len(toSend) <5 and connection:
				dif = 5 - len(toSend)
                                for i in range(len(toSend)):
                                        data = toSend.pop(0)
					resendLog(data)
				time.sleep(dif*20)
			else:
				time.sleep(100)
		elif tempsInfo.qsize > 0:
                        if tempsInfo.qsize() >= 5 and connection:
				for i in range(5):
                        		info = tempsInfo.get()
                                	if connection:
                                        	#info = tempsInfo.get()
                                        	guardian.post(info,'Temps')
                                        	print(info)
                                        	time.sleep(0.5)
                                	else:
                                        	createNotSent(notSent + str(info)+'@','notSentGPS.txt')
			elif tempsInfo.qsize() < 5:
				dif = 5-tempsInfo.qsize()
				iter = tempsInfo.qsize()
				for i in range(iter):
                                        info = tempsInfo.get()
                                        if connection:
                                                guardian.post(info,'Temps')
                                                print(info)
                                                time.sleep(0.5)
                                        else:
                                                createNotSent(notSent + str(info)+'@','notSentGPS.txt')
				time.sleep(dif*20)
			else:
				time.sleep(100)
		else:
			time.sleep(100)

except KeyboardInterrupt:
	print('Apagando')
	guardian.desertar()
