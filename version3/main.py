import serial
import time

from datetime import timedelta
from temps import *
from clases import *
from fileManagement import *

time.sleep(10)
try:
	from camion import camioncito
except:
	camioncito = "0"
try:
        notSent = readNotSent('notSentGPS.txt')
except:
        notSent = ""


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
lonAnt = None
latAnt = None
guardian = guardian("/dev/ttyS0",115200,camioncito)

if not(guardian.isOn()):
        guardian.turnOn()

guardian.setGPRS()
#connection = guardian.isConnected()


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


		conge,refri = getTemps()
		tConNow = conge["Temperatura"]
		tRefNow = refri["Temperatura"]

		hConNow = conge["Humedad"]
		hRefNow = refri["Humedad"]

		if (tConNow != tConPast or hConNow != hConPast) and (tConNow != "" and hConNow != ""):
			print(conge)
			if connection:
				guardian.post(conge,"Temps")
			else:
				createNotSent(notSent + str(conge)+ '@','notSentGPS.txt')
				notSent = notSent + str(conge)+ '@'
			lastSentCon = datetime.strptime(conge["fecha"],"%Y-%m-%d %H:%M:%S")
		elif (datetime.strptime(conge["fecha"],"%Y-%m-%d %H:%M:%S") - lastSentCon).total_seconds() > deltatie and (tConNow != "" and hConNow != ""):
			print(conge)
			if connection:
				guardian.post(conge,"Temps")
			else:
				createNotSent(notSent + str(conge) + '@','notSentGPS.txt')
				notSent = notSent + str(conge)+ '@'
			lastSentcon = datetime.strptime(conge["fecha"],"%Y-%m-%d %H:%M:%S")
		time.sleep(1)
		if (tRefNow != tRefPast or hRefNow != hRefPast) and (tRefNow != "" and hRefNow != ""):
			print(refri)
			if connection:
				guardian.post(refri,"Temps")
			else:
				createNotSent(notSent + str(refri) + '@','notSentGPS.txt')
				notSent = notSent + str(conge)+ '@'
			lastSentRef = datetime.strptime(refri["fecha"],"%Y-%m-%d %H:%M:%S")
		elif (datetime.strptime(refri["fecha"],"%Y-%m-%d %H:%M:%S") - lastSentCon).total_seconds() > deltatie and (tRefNow != "" and hRefNow != ""):
			print(refri)
			if connection:
				guardian.post(refri,"Temps")
			else:
				createNotSent(notSent + str(refri) + '@','notSentGPS.txt')
				notSent = notSent + str(conge)+ '@'
			lastSentRef = datetime.strptime(refri["fecha"],"%Y-%m-%d %H:%M:%S")
		tRefPast = tRefNow
		tConPast = tConNow

		hRefPast = hRefNow
		hConPast = hConNow
		time.sleep(1)

#		print(gps)
		gps,status,fix = guardian.getGPS()
		nowGPS = datetime.strptime(gps["fecha"],"%Y-%m-%d %H:%M:%S")
		fechaAct = gps["fecha"]
#		print ((nowGPS - lastSentGPS).total_seconds())
		if ((fechaAct != fechaAnt) and gps["latitud"] != '' and gps["longitud"]!= '' and gps['latitud'] != latAnt and gps['longitud'] != lonAnt):
			print(gps,status,fix,connection)
			if connection:
				guardian.post(gps,"GPS")
				#print("envie")
			else:
				createNotSent(notSent + str(gps) + '@','notSentGPS.txt')
				notSent = notSent + str(conge)+ '@'
			lastSentGPS = nowGPS
		elif ((nowGPS - lastSentGPS).total_seconds() > deltatie) and gps['latitud'] != "" and gps['longitud'] != "":
			print(gps,status,fix,connection)
			if connection:
				guardian.post(gps,"GPS")
				#print("envie")
			else:
				createNotSent(notSent + str(gps) + '@', 'notSentGPS.txt')
				notSent = notSent + str(conge)+ '@'
			lastSentGPS = nowGPS
		fechaAnt = fechaAct
		lonAnt = gps['longitud']
		latAnt = gps['latitud']
		data = ""
		time.sleep(90)
except KeyboardInterrupt:
	print('Apagando')
	guardian.desertar()
