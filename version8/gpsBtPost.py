#!/usr/bin/python

import serial
import time
import re
import json
import bluetooth
import logging
import copy

from datetime import timedelta
from datetime import datetime
from fileManagement import *
from threading import Thread
from Queue import Queue
from clases import *

def connect(sock, bd_addr, port):
    logging.info('connect() ' + str(datetime.now()))
    lock = False
    while not(lock):
        try:
            sock.connect((bd_addr,port))
            logging.info('Bluetooth conectado.'+ str(datetime.now()))
            print('Bluetooth conectado.')
            return True
        except Exception as e:
            sock.close()
            time.sleep(2)
            sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)

def readTemps(bd_addr, port, tempsInfo, camioncito):
    logging.info('readTemps() ' + str(datetime.now()))
    sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
    connected = connect(sock, bd_addr, port)

    while connected:
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
            logging.info('Se perdio conexion bluetooth. Intentando conectar. '+ str(datetime.now()))
            print('Se perdio conexion bluetooth. Intentando conectar. ')
            sock.close()
            time.sleep(2)
            sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
            connected = connect(sock, bd_addr, port)
			
def setDate(guardian_):
	logging.info('setDate() ' + str(datetime.now()))
	count = 0
	setFecha = ""
	while setFecha == "" and count <= 5:
		if count < 3:
			print("Trying to get fecha GPS")
			gps, status, fix = guardian_.getGPS()
			#timeDate = str(gps["fecha"]).split()
			if gps != {}:
				timeDate = str(gps["fecha"]).split()
				setFecha = timeDate[0]
				setTime = timeDate[1]
		else:
			print("Trying to get fecha GSM")
			setFecha,setTime = guardian_.getClock()
		count = count +1
		time.sleep(5)
		
	print([setFecha,setTime])
	
	if(setFecha != "" or setTime !=""):
		try:
			#executeBashCommand('sudo timedatectl set-timezone GMT')
			executeBashCommand('sudo timedatectl set-timezone US/Pacific')
			executeBashCommand('sudo date -s ' + str(setFecha))
			executeBashCommand('sudo date -s ' + str(setTime))
		
			logging.info('Cambie la fecha'+ str(datetime.now()))
			print("Cambie la fecha")
			return True
		except Exception as e:
			#pass
			print(e)
			return False

def getGPS(guardian_):
	#Try to get GPS fix. If unable to get GPS fix, try to get data by GSM.
	#Input parameter: Instance of guardian object
	#Return: Dictionary with GPS data, gps status, gps fix status.
	logging.info('getGPS() ' + str(datetime.now()))
	count = 0
	while count < 3:
		gps,status,fix = guardian_.getGPS()
		if fix == '1':
			break
		count += 1
	if fix != '1':
		if guardian_.isConnected():
				try:
					gps,status,fix = guardian_.getGPSbyGSM(""),'1','1'
					print([gps,status,fix,'GSM'])
					return (gps,status,fix)
				except:
					return (gps,status,fix)
		else:
			logging.info('GPS FAILED.'+ str(datetime.now()))
			print('GPS FAILED')
			return (gps,status,fix)
	else:
		print([gps,status,fix,'GPS'])
		return (gps,status,fix)

def postLog(guardian_):
	count = 0
	file, currentLog = readNotSent('logGPS.txt')
	lenLogs = len(re.findall(r'@',currentLog))
	if lenLogs != 0:
		if lenLogs >= 5:
			num = 5
		else:
			num = lenLogs
		logging.info("Trying to post logs/temps")
		print('Trying to post logs/temps')
		logs = currentLog.split('@',num)
		for i in range(num):
			if len(re.findall(r'longitud',logs[0])) > 0:
				posted = guardian_.post(logs[0],'GPS')
				if posted:
					logging.info('POSTED GPS Log' + logs[0])
					print('POSTED GPS Log' + logs[0])
					logs.pop(0)
				else:
					count+=1
			else:
				posted = guardian_.post(logs[0],'Temps')
				if posted:
					logging.info('POSTED TEMPS'+logs[0])
					print('POSTED TEMPS'+logs[0])
					logs.pop(0)
				else:
					count+=1
				
		seperator = '@'
		content = seperator.join(logs)
		file.truncate(0)
		if len(content) != 0:
			createNotSent(content,'logGPS.txt',False)
			
		if count >= num:
			rebootHat(guardian_)
        
def rebootHat(guardian_):
    check = 0
    while check <= 2:
        logging.info('Reiniciando HAT.'+str(datetime.now()))
        print('Reiniciando HAT')
        guardian_.turnOn()
        time.sleep(5)
        guardian_.turnOn()
        time.sleep(30)
        check += 1
        connection = guardian_.isConnected()
        if connection:
            break

def postOrLog(guardian_,gps):
	logging.info('postOrLog() ' + str(datetime.now()))
	stringGPS = copy.deepcopy(gps)
	stringGPS["fecha"] = stringGPS["fecha"].strftime("%Y-%m-%d %H:%M:%S")
	print(stringGPS)
	posted = guardian_.post(stringGPS,'GPS')
	if posted:
		logging.info('POSTED GPS'+stringGPS["fecha"])
		print('postLog POSTED GPS')
	else:
		logging.info('Sin datos moviles. guardando' + stringGPS["fecha"])
		print('Sin datos moviles. guardando')
		createNotSent(str(stringGPS),'logGPS.txt',True)
	reboot, stats = guardian_.readSMS()
	print([reboot,stats])
	if reboot == True:
		logging.info('SMS instructed to reboot')
		executeBashCommand('sudo reboot')
	if stats == True:
		print('Log requested')
		logging.info('Log requested')
		mail = guardian_.sendMail()
		if mail == False:
			guardian_.sendSMS('Mail no enviado')
    
def Main():
    
    ##Log configuration
    try:
        logging.basicConfig(filename='/home/pi/test.log',filemode='a', level=logging.DEBUG)
        logging.info('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
    except Exception as e:
        pass
    
    try:
        from camion import camioncito
    except:
        camioncito = "13"
        
    try:
        from macAddress import bd_addr
    except:
        bd_addr = "98:D3:31:FB:1A:D6" #//The address from the HC-05 sensor

    port = 1
    tempsInfo = Queue()

    ## Create thread to put information in the Queue
    thread1 = Thread(target=readTemps, args=[bd_addr, port, tempsInfo, camioncito])
    thread1.setDaemon(True)
    thread1.start()

    guardian_ = guardian("/dev/ttyS0",115200,camioncito)
    
    ## Check the status of the HAT: On/Off
    if not(guardian_.isOn()):
            guardian_.turnOn()

    guardian_.setGPRS()
    
    date = setDate(guardian_)
    
    ## Variables for GPS
    deltaGPS = 120
    deltaPost = 0
    noFix = 0
    gps = {"latitud": "0.00", "longitud":"0.00", "velocidad":"", "idCamion":"", "fecha":(datetime.now() - timedelta(seconds=deltaGPS))}
    lastPostGPS = datetime.now()- timedelta(seconds=deltaPost)
    
    while True:
        if date == False:
            date = setDate(guardian_)

        deltaGPSAct = datetime.now()-gps["fecha"]
        minuteDeltaGPS = (deltaGPSAct.seconds//60)%60
        
        deltaPostAct = datetime.now()- lastPostGPS
        minuteDeltaPost = (deltaPostAct.seconds//60)%60
        
        if minuteDeltaGPS >= 2:
            lastGPS = copy.deepcopy(gps)
            noFix = 0
            while noFix <= 20:
                gps, status, fix = getGPS(guardian_)
                if gps != {} and gps["latitud"] != '' and fix == '1':
                    deltaLatitud = float(gps["latitud"]) - float(lastGPS["latitud"])
                    deltaLongitud = float(gps["longitud"]) - float(lastGPS["longitud"])  
                    if (deltaLatitud >= 0.001 or deltaLongitud >= 0.001) or minuteDeltaPost >= 10:
                        postOrLog(guardian_,gps)
                        lastPostGPS = datetime.now()
                    break
                elif noFix == 10:
                    rebootHat(guardian_)
                    noFix += 1
                else:
                    time.sleep(10)
                    noFix += 1
            if gps == {}:
                gps = {"latitud": "0.00", "longitud":"0.00", "velocidad":"", "idCamion":"", "fecha":(datetime.now() - timedelta(seconds=deltaGPS))}
                    
        else:
            tempData = ''
            while tempsInfo.qsize() > 0:
                tempData += (str(tempsInfo.get())+'@')
            createNotSent(tempData,'logGPS.txt',False)
            postLog(guardian_)
                    
Main()

