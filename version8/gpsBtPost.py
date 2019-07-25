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
    lock = False
    while not(lock):
        try:
            sock.connect((bd_addr,port))
            logging.info('Bluetooth conectado.')
            return True
        except Exception as e:
            sock.close()
            time.sleep(2)
            sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)

def readTemps(bd_addr, port, tempsInfo, camioncito):
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
            logging.info('Se perdio conexion bluetooth. Intentando conectar.')
            sock.close()
            time.sleep(2)
            sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
            connected = connect(sock, bd_addr, port)
			
def setDate(guardian_):
        count = 0
        setFecha = ""
        while setFecha == "" and count <3:
            setFecha,setTime = guardian_.getClock()
            count = count +1
        try:
            executeBashCommand('sudo timedatectl set-timezone GMT')
            executeBashCommand('sudo date -s ' + setFecha)
            executeBashCommand('sudo date -s ' + setTime)
            executeBashCommand('sudo timedatectl set-timezone US/Pacific')
        except:
            pass

def getGPS(guardian_):
        #Try to get GPS fix. If unable to get GPS fix, try to get data by GSM.
        #Input parameter: Instance of guardian object
        #Return: Dictionary with GPS data, gps status, gps fix status.
        gps,status,fix = guardian_.getGPS()
        if fix != '1':
            if guardian_.isConnected():
                    try:
                        gps,status,fix = guardian_.getGPSbyGSM(),'1','1'
                        return (gps,status,fix)
                    except:
                        logging.info('No se recupero GSM.')
                        return (gps,status,fix)
            else:
                logging.info('HAT desconectado.')
                return (gps,status,fix)
        else:
            return (gps,status,fix)

def postLog(guardian_):
    try:
        file, currentLog = readNotSent('logGPS.txt')
        lenLogs = len(re.findall(r'@',currentLog))
        if lenLogs >= 5:
            num = 5
        else:
            num = lenLogs
        if num != 0:
            logs = currentLog.split('@',num)
            for i in range(num):
                try:
                    if len(re.findall(r'longitud',logs[0])) > 0:
                        guardian_.post(logs[0],'GPS')
                    else:
                        guardian_.post(logs[0],'Temps')
                    logs.pop(0)
                except:
                    return
            file.truncate(0)
            if len(logs) != 0:
                createNotSent(logs[0],'logGPS.txt',False)
                
    except Exception as e:
        return

def rebootHat(guardian_):
    check = 0
    while check <= 3:
        logging.info('Reiniciando HAT.')
        guardian_.turnOn()
        time.sleep(30)
        guardian_.turnOn()
        check += 1
        connection = guardian_.isConnected()
        if connection:
            break

def postOrLog(guardian_,gps):
    stringGPS = copy.deepcopy(gps)
    stringGPS["fecha"] = stringGPS["fecha"].strftime("%Y-%m-%d %H:%M:%S")
    connection = guardian_.isConnected()
    if connection:
        guardian_.post(stringGPS,"GPS")
    else:
        logging.info('Sin datos moviles.')
        createNotSent(str(stringGPS),'logGPS.txt',True)        
    
def Main():
    
    ##Log configuration
    logging.basicConfig(filename='test.log',filemode='a', level=logging.DEBUG)
    logging.info('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
    
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
    
    setDate(guardian_)
    
    logging.info('Se establecio fecha.')
    
    ## Variables for GPS
    deltaGPS = 120
    deltaPost = 0
    noFix = 0
    gps = {"latitud": "0.00", "longitud":"0.00", "velocidad":"", "idCamion":"", "fecha":(datetime.now() - timedelta(seconds=deltaGPS))}
    lastPostGPS = datetime.now()- timedelta(seconds=deltaPost)
    
    while True:
        connection = guardian_.isConnected()
        if not connection:
            rebootHat(guardian_)

        deltaGPSAct = datetime.now()-gps["fecha"]
        minuteDeltaGPS = (deltaGPSAct.seconds//60)%60
        
        deltaPostAct = datetime.now()- lastPostGPS
        minuteDeltaPost = (deltaPostAct.seconds//60)%60
        
        if minuteDeltaGPS >= 2:
            lastGPS = copy.deepcopy(gps)
            noFix = 0
            while noFix <= 20:
                time.sleep(10)
                gps, status, fix = getGPS(guardian_)
                if gps != {}:
                    if gps["latitud"] != '' and fix == '1':
                        break
                    noFix += 1
                elif noFix == 10:
                    rebootHat(guardian_)
                    noFix += 1
                else:
                    noFix += 1
        
            if gps["latitud"] != '' and fix == '1':
                deltaLatitud = float(gps["latitud"]) - float(lastGPS["latitud"])
                deltaLongitud = float(gps["longitud"]) - float(lastGPS["longitud"])
                
                if (deltaLatitud >= 0.001 or deltaLongitud >= 0.001):
                    postOrLog(guardian_,gps)
                    lastPostGPS = datetime.now()
            
        #Check if 10 minutes have gone by since last post, or if position has changed significantly.
        #If fix available, try to post. If offline, store location in log.
        
        if minuteDeltaPost >= 10: 
            postOrLog(guardian_,gps)
            lastPostGPS = datetime.now()
                    
        else:
            tempData = ''
            while tempsInfo.qsize() > 0:
                tempData += (str(tempsInfo.get())+'@')
            createNotSent(tempData,'logGPS.txt',False)
            connection = guardian_.isConnected()
            if connection:
                postLog(guardian_)
Main()

