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

try:
	from camion import camioncito
except:
	camioncito = "0"
try:
        notSent = readNotSent('notSentGPS.txt')
except:
        notSent = ""

tempsInfo = Queue()

def isConnected():
	response = ""
	while ser.inWaiting() > 0:
		response += ser.read(ser.inWaiting())
	if len(re.findall(r'\"\d*\.\d*\.\d*\.\d*\"',response))>0:
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
ser = serial.Serial("/dev/ttyS0",115200)

## AT commands to use
#pause = 10000  ## time to wait for the data to do the http POST
gprs = ['at+sapbr=3,1,"Contype","GPRS"\r\n','at+sapbr=3,1,"APN","internet.itelcel.com"\r\n','at+sapbr=1,1\r\n','at+sapbr=2,1\r\n']
w_buff = ["at+cgnsinf\r\n"]

ser.flushInput()
## Setting the GPRS Connection
for command in gprs:
	ser.write(command)
	time.sleep(0.5)

connection = isConnected()

toSend = notSent.split('@')
#print(toSend)
if len(toSend)>0:
	if len(toSend)>2160:
		toSend = toSend[:2161]
	for data in toSend:
		#print(data)
		if (data!= '@' and data!='' and data != ' ') and connection:
			if len(re.findall(r'longitud',data))>0:
				#print('entre')
				post(data,'GPS')
			else:
				post(data,'Temps')
		time.sleep(0.6)
	if connection:
		try:
			executeBashCommand('rm notSentGPS.txt')
		except:
			pass

ser.write("at+cgnspwr=1\r\n")
time.sleep(0.5)
ser.write("at+cgnsinf\r\n")
time.sleep(0.5)
ser.write("at+cgnspwr=0\r\n")
time.sleep(1)
ser.write("at+cgnspwr=1\r\n")
time.sleep(0.5)
ser.write("at+cgnsinf\r\n")
time.sleep(1)
data=""
num=0
prueba = -1

try:
	while True:
		## Checks tempsInfo
		if tempsInfo.qsize() > 0:
			while tempsInfo.qsize() > 0:
				if connection:
					info = tempsInfo.get()
					post(info,'Temps')
					print(info)
					time.sleep(0.5)
				else:
					createNotSent(notSent + str(info)+'@','notSentGPS.txt')

		prueba += 1
		while ser.inWaiting() > 0:
			data += ser.read(ser.inWaiting())
		if data != "":
			time.sleep(0.5)
			ser.write(w_buff[0])
			data = data.split()

			if 'at+cgnsinf' in data and  '+CGNSINF:' in data:
				gpsData = data[data.index('+CGNSINF:') +1]
#				print(gpsData)
				gpsData = gpsData.split(",")
				status,fix = gpsData[0],gpsData[1]
				gps["latitud"] = gpsData[3] # latitud
				gps["longitud"] = gpsData[4] # longitud
				gps["velocidad"] = gpsData[6] # velocidad
				gps["idCamion"] = camioncito
				nowGPS = datetime.now()
				gps["fecha"] = nowGPS.strftime("%Y-%m-%d %H:%M:%S")

#			print(gps)
			fechaAct = gps["fecha"]
#			print ((nowGPS - lastSentGPS).total_seconds())
			try :
				notSent = readNotSent('notSentGPS.txt')
			except:
				notSent = ""
			print(latAnt,lonAnt)
			if ((fechaAct != fechaAnt) and gps['latitud'] != "" and gps['longitud']!= "" and gps['latitud'] != latAnt and gps['longitud'] != lonAnt):
				print(gps,status,fix,connection)
				if connection:
					post(gps,"GPS")
					#print("envie")
				else:
					createNotSent(notSent + str(gps)+'@','notSentGPS.txt')
				lastSentGPS = nowGPS
			elif ((nowGPS - lastSentGPS).total_seconds() > deltatie) and gps['latitud'] != "" and gps['longitud']!= "":
				print(gps,status,fix,connection)
				if connection:
					post(gps,"GPS")
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
	if ser != None:
		ser.write("AT+CGNSTST=0\r\n")
		ser.write("AT+CGNSPWR=0\r\n")
		ser.write("at+httpterm\r\n")
		ser.close()

