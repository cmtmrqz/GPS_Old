# coding=utf-8
import sys
import json
import serial
import time
import re
import bluetooth
import RPi.GPIO as gpio
import time

from datetime import timedelta
from datetime import datetime

class guardian:
    def __init__(self,device,bdrate,camion):
            self.device = device
            self.bdrate = bdrate
            self.camion = camion
            self.ser = serial.Serial(self.device,self.bdrate)
            self.pause = 10000 ## time to wait for the data to do the http POST
            self._cPostGPS = ['at+httpinit\r\n','at+httppara="CID",1\r\n','at+httppara="URL","http://201.170.127.72:8092/api/GPS"\r\n','at+httppara="CONTENT","application/json"\r\n','at+httpdata=319488,'+str(self.pause)+'\r\n','at+httpaction=1\r\n','at+httpread\r\n','at+httpterm\r\n']
            self._cPostTemps = ['at+httpinit\r\n','at+httppara="CID",1\r\n','at+httppara="URL","http://201.170.127.72:8092/api/Temps"\r\n','at+httppara="CONTENT","application/json"\r\n','at+httpdata=319488,'+str(self.pause)+'\r\n','at+httpaction=1\r\n','at+httpread\r\n','at+httpterm\r\n']
            self._cSetGPRS = ['at+cgatt=1\r\n','at+sapbr=3,1,"Contype","GPRS"\r\n','at+sapbr=3,1,"APN","internet.itelcel.com"\r\n','at+sapbr=1,1\r\n','at+sapbr=2,1\r\n']
            self._cGetGPS = ["at+cgnsinf\r\n"]

    def setGPRS(self):
    #	Esta funcion configura el servicio de telefonia movil en la HAT. 
    #	Tambien configura el servicio de posicionamiento de telefonia movil,
    #	que sera utilizado despues para enviar la longituda y latitud si el 
    #	servicio de GNSS pierde fix.

            self.ser.flushInput()
            for command in self._cSetGPRS:
                    self.ser.write(command)
                    time.sleep(0.5)

    def isOn(self):
    #	Esta funcion detecta si el HAT se encuentra encendido. 
    #	Regresa un True en caso de estar encendido y un False si 
    #	se encuentra pagado
    #	return: bool

        self.ser.flushInput()
        response = ""
        for command in self._cSetGPRS:
                self.ser.write(command)
                time.sleep(0.5)
        while self.ser.inWaiting() > 0:
                response += self.ser.read(self.ser.inWaiting())
        if response != '':
                return True
        return False

    def turnOn(self):
    #	Esta funcion cambio de estado el HAT, es decir 
    #	si el HAT se encuentra apagado lo enciende y viceversa
            gpio.setmode(gpio.BOARD)
            gpio.setup(7,gpio.OUT)

            gpio.output(7,gpio.LOW)
            time.sleep(4)
            gpio.output(7,gpio.HIGH)
            gpio.cleanup()

    def isConnected(self):
    #	Con esta funcion el guardian detecta si el HAT cuenta con red de datos moviles.
    #	Los datos moviles son utilizados para realizar el POST al WEB API.
    #	Para detectar si existe red de datos moviles se configura el GPRS, 
    #	si el GPRS se encuentra bin configurado se solicita el ip asignado. 
    #	Si existe ip entonces si hay conexion de datos moviles. 
    #	return: bool
            self.ser.flushInput()
            response = ""
            for command in self._cSetGPRS:
                    self.ser.write(command)
                    time.sleep(0.5)
            while self.ser.inWaiting() > 0:
                    response += self.ser.read(self.ser.inWaiting())
            ip = re.findall(r'\"\d*\.\d*\.\d*\.\d*\"',response)
            if len(ip)>0 and "0.0.0.0" not in ip:
                    return True
            else:
                    return False

    def post(self,data,tipo):
    #	Con esta funcion el guardian realiza el POST al WEB API.
    #	parameter: data,String contiene el diccionario a enviar al WEB API.
    #	parameter: tipo,String especifica si se enviaran datos de temps o GPS
    #	return: None
            print("Trying to post")
            self.ser.flushInput()
            response =""
            if tipo == 'GPS':
                    http = self._cPostGPS
            elif tipo == 'Temps':
                    http = self._cPostTemps
            else:
                    http = ''

            if http != '':
                    for hCom in http:
                            com = hCom.split('=')
                            if com[0] == "at+httpdata":
                                self.ser.write(hCom)
                                time.sleep(1)
                                self.ser.write(str(data))
                                time.sleep(self.pause/1000)
                            elif com[0] == "at+httpaction":
                                self.ser.write(hCom)
                                time.sleep(4.5)
                            else:
                                self.ser.write(hCom)
                            time.sleep(0.5)
            while self.ser.inWaiting() > 0:
                    response += self.ser.read(self.ser.inWaiting())
            self.ser.write('at+httpterm\r\n')
            time.sleep(0.5)
            
            print(response)
            if('ERROR' in response):
                    return False
            else:
                    return True
            

    def getGPS(self):
    #	Esta funcion le sirve a nuestro guadian para obtiener
    #	los datos de longitud, latitud, velocidad a traves de; servicio
    #	de GNSS.
    #	Regresa una tuple:
    #		posicion 0: diccionario que contiene los datos solicitados
    #		posicion 1: status del servicio de GNSS
    #		posicion 2: status del fix de GPS
    #	return: tuple
            data,status,fix = "","",""
            gpsData = None
            gps = {}
            self.ser.flushInput()
            self.ser.write("at+cgnspwr=1\r\n")
            time.sleep(0.5)

            self.ser.write(self._cGetGPS[0])
            time.sleep(0.5)
            while self.ser.inWaiting() > 0:
                    data += self.ser.read(self.ser.inWaiting())
            if data != "":
                    data = data.split()
                    if 'at+cgnsinf' in data and '+CGNSINF:' in data:
                            gpsData = data[data.index('+CGNSINF:') + 1]
                            gpsData = gpsData.split(",")
                            #print(gpsData)
                            status,fix = gpsData[0], gpsData[1]
                            gps["latitud"] = gpsData[3] # latitud
                            gps["longitud"] = gpsData[4] # longitud
                            gps["velocidad"] = gpsData[6] # velocidad
                            gps["idCamion"] = self.camion
                            #nowGPS = datetime.now()
                            #gps["fecha"] = nowGPS.strftime("%Y-%m-%d %H:%M:%S")
                            gps["fecha"] = datetime.now()

            #self.ser.write("at+cgnspwr=0\r\n")
            time.sleep(0.5)
            return gps,status,fix

    def getGPSbyGSM(self):
    #	Esta funcion le sirve a nuestro guardian para obtiener la latitud,
    #	longitud y velocidad a traves del posicionamiento de GSM,
    #	configurado al momento de configurar el GPRS.
    ##	Regresa los datos de solicitados en un diccionario.
    #	return: dict
            data,status,fix = "","",""
            gpsData = None
            gps = {}
            self.ser.flushInput()
            self.ser.write("at+cipgsmloc=1,1\r\n")
            time.sleep(10)

            while self.ser.inWaiting() > 0:
                    data += self.ser.read(self.ser.inWaiting())
            if data != "":
                    data = data.split()
                    if 'at+cipgsmloc=1,1' in data and '+CIPGSMLOC:' in data:
                            gpsData = data[data.index('+CIPGSMLOC:') + 1]
                            gpsData = gpsData.split(",")
                            try:
                                    gps["latitud"] = gpsData[2] # latitud
                                    gps["longitud"] = gpsData[1] # longitud
                            except:
                                    gps["latitud"] = ""
                                    gps["longitud"] = ""
                            gps["velocidad"] = 0 # velocidad
                            gps["idCamion"] = self.camion
                            nowGPS = datetime.now()
                            #gps["fecha"] = nowGPS.strftime("%Y-%m-%d %H:%M:%S")
                            gps["fecha"] = nowGPS

            time.sleep(0.5)
            return gps

    def getClock(self):
    #	Esta funcion le sirve a nuestro guardian para obtiener la latitud,
    #	longitud y velocidad a traves del posicionamiento de GSM,
    #	configurado al momento de configurar el GPRS.
    ##	Regresa los datos de solicitados en un diccionario.
    #	return: dict
            data,status,fix = "","",""
            gpsData = None
            gps = {}
            timeGSM = ""
            fechaGSM = ""
            self.ser.flushInput()
            self.ser.write("at+cipgsmloc=1,1\r\n")
            time.sleep(10)

            while self.ser.inWaiting() > 0:
                    data += self.ser.read(self.ser.inWaiting())
            if data != "":
                    data = data.split()
                    if 'at+cipgsmloc=1,1' in data and '+CIPGSMLOC:' in data:
                            gpsData = data[data.index('+CIPGSMLOC:') + 1]
                            gpsData = gpsData.split(",")
                            try:
                                    timeGSM = gpsData[4] # latitud
                                    fechaGSM = gpsData[3]
                            except:
                                    timeGSM = ""
                                    fechaGSM = ""
            time.sleep(0.5)
            return fechaGSM,timeGSM



    def desertar(self):
    #	Esta funcion sirve para terminar el periodo de vigilia de nuestro
    #	guardian.
    #	Cierra el proceso de http
    #	Cierra la conexion serial.
            self.ser.write("at+cgnspwr=0\r\n")
            time.sleep(0.5)
            self.ser.close()
