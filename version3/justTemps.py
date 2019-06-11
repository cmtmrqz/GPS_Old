import serial
import time
import bluetooth

from datetime import datetime
from temps import *

try:
	from camion import camioncito
except:
	pass

bd_addr = "B8:27:EB:79:24:4F"
port = 1

tConPast = None
tRefPast = None
tConNow = None
tRefNow = None

hConPast = None
hRefPast = None
hConNow = None
hRefNow = None

deltatie = 360
lastSentCon = datetime.datetime.now() - datetime.timedelta(seconds=deltatie)
lastSentRef = datetime.datetime.now() - datetime.timedelta(seconds=deltatie)

try:
	while True:
		conge,refri = getTemps()
		tConNow = conge["Temperatura"]
		tRefNow = refri["Temperatura"]

		hConNow = conge["Humedad"]
		hRefNow = refri["Humedad"]

		if (tConNow != tConPast or hConNow != hConPast) or (datetime.datetime.strptime(conge["fecha"],"%Y-%m-%d %H:%M:%S") - lastSentCon).total_seconds() > deltatie:
			print(conge)
			sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
			sock.connect((bd_addr, port))
			sock.send(str(conge))
			sock.close()
			lastSentCon = datetime.datetime.strptime(conge["fecha"],"%Y-%m-%d %H:%M:%S")
		time.sleep(0.5)
		if (tRefNow != tRefPast or hRefNow != hRefPast) or (datetime.datetime.strptime(refri["fecha"],"%Y-%m-%d %H:%M:%S") - lastSentRef).total_seconds() > deltatie:
			print(refri)
			sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
			sock.connect((bd_addr, port))
			sock.send(str(refri))
			sock.close()
			lastSentRef = datetime.datetime.strptime(refri["fecha"],"%Y-%m-%d %H:%M:%S")

		tRefPast = tRefNow
		tConPast = tConNow

		hRefPast = hRefNow
		hConPast = hConNow
		time.sleep(180)
except KeyboardInterrupt:
	print('Apagando')
