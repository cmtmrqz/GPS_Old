import serial
import time

from datetime import timedelta
from temps import *

try:
	from camion import camioncito
except:
	camioncito = "0"
try:
        notSent = readNotSent('notSentGPS.txt')
except:
        notSent = ""

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
		else:
			ser.write(hCom)
		time.sleep(0.5)

##Variables for Temps
deltatie = 600
tConPast = None
tRefPast = None
tConNow = None
tRefNow = None

hConPast = None
hRefPast = None
hConNow = None
hRefNow = None

from datetime import datetime
lastSentCon = datetime.now() - timedelta(seconds=deltatie)
lastSentRef = datetime.now() - timedelta(seconds=deltatie)

## Variables for GPS
gps = {}
lastSentGPS = datetime.now() - timedelta(seconds=deltatie)
fechaAct = ""
fechaAnt = ""
ser = serial.Serial("/dev/ttyS0",115200)

## AT commands to use
#pause = 10000  ## time to wait for the data to do the http POST
gprs = ['at+sapbr=3,1,"Contype","GPRS"\r\n','at+sapbr=3,1,"APN","internet.itelcel.com"\r\n','at+sapbr=1,1\r\n','at+sapbr=2,1\r\n']
w_buff = ["at+cgnsinf\r\n"]
#http = ['at+httpinit\r\n','at+httppara="CID",1\r\n','at+httppara="URL","http://201.170.127.72:8092/api/GPS"\r\n','at+httppara="CONTENT","application/json"\r\n','at+httpdata=319488,'+str(pause)+'\r\n','at+httpaction=1\r\n','at+httpread\r\n','at+httpterm\r\n']

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
		prueba += 1
		try:
        		notSent = readNotSent('notSentGPS.txt')
		except:
			notSent = ""

		conge,refri = getTemps()
		tConNow = conge["Temperatura"]
		tRefNow = refri["Temperatura"]

		hConNow = conge["Humedad"]
		hRefNow = refri["Humedad"]

		if tConNow != tConPast or hConNow != hConPast:
			print(conge)
			if connection:
				post(conge,"Temps")
			else:
				createNotSent(notSent + str(conge)+ '@','notSentCon.txt')
			lastSentCon = datetime.strptime(conge["fecha"],"%Y-%m-%d %H:%M:%S")
		elif (datetime.strptime(conge["fecha"],"%Y-%m-%d %H:%M:%S") - lastSentCon).total_seconds() > deltatie:
			print(conge)
			if connection:
				post(conge,"Temps")
			else:
				createNotSent(notSent + str(conge) + '@','notSentCon.txt')
			lastSentcon = datetime.strptime(conge["fecha"],"%Y-%m-%d %H:%M:%S")
		time.sleep(1)
		if tRefNow != tRefPast or hRefNow != hRefPast:
			print(refri)
			if connection:
				post(refri,"Temps")
			else:
				createNotSent(notSent + str(refri) + '@','notSentRef.txt')
			lastSentRef = datetime.strptime(refri["fecha"],"%Y-%m-%d %H:%M:%S")
		elif (datetime.strptime(refri["fecha"],"%Y-%m-%d %H:%M:%S") - lastSentCon).total_seconds() > deltatie:
			print(refri)
			if connection:
				post(refri,"Temps")
			else:
				createNotSent(notSent + str(refri) + '@','notSentRef.txt')
			lastSentRef = datetime.strptime(refri["fecha"],"%Y-%m-%d %H:%M:%S")
		tRefPast = tRefNow
		tConPast = tConNow

		hRefPast = hRefNow
		hConPast = hConNow
		time.sleep(1)

		while ser.inWaiting() > 0:
			data += ser.read(ser.inWaiting())
		if data != "":
			time.sleep(0.5)
			ser.write(w_buff[0])
			data = data.split()

#			print(data)

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
			if ((fechaAct != fechaAnt) and gps["latitud"] != '' and gps["longitud"]!= ''):
				print(gps,status,fix)
				if connection:
					post(gps,"GPS")
					print("envie")
				else:
					createNotSent(notSent + str(gps) + '@','notSentGPS.txt')
				lastSentGPS = nowGPS
			elif ((nowGPS - lastSentGPS).total_seconds() > deltatie):
				print(gps,status,fix)
				if connection:
					post(gps,"GPS")
					print("envie")
				else:
					createNotSent(notSent + str(gps) + '@', 'notSentGPS.txt')
				lastSentGPS = nowGPS
			fechaAnt = fechaAct
			data = ""
		time.sleep(120)
except KeyboardInterrupt:
	print('Apagando')
	if ser != None:
		ser.write("AT+CGNSTST=0\r\n")
		ser.write("AT+CGNSPWR=0\r\n")
		ser.write("at+httpterm\r\n")
		ser.close()

