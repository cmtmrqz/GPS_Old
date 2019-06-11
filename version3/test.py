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

bd_addr = "98:D3:31:FB:1A:D6" #//The address from the HC-05 sensor
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
			print("Host down, closing socket "+str(e))
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
                                		rec = rec.replace('*', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                		rec = rec.replace('Camioncito',str(camioncito))
						print (rec)
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

print('----')
while True:
	try:
		if tempsInfo.qsize>0:
			print(tempsInfo.get(),'2')
		time.sleep(1)
	except KeyboardInterrupt:
		sock.close()
		break
