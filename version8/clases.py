# coding=utf-8
import sys
import json
import serial
import time
import re
import bluetooth
import RPi.GPIO as gpio
import logging

from datetime import timedelta
from datetime import datetime
from pytz import timezone

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
            
            try:
                logging.basicConfig(filename='/home/pi/test.log',filemode='a', level=logging.DEBUG)
            except Exception as e:
                print(e)

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
            e = True
            #print(str(self.ser.inWaiting()))
            start = time.time()
            while self.ser.inWaiting() > 0:
                    response += self.ser.read(self.ser.inWaiting())
                    end = time.time()
                    if ('ERROR' in response) or (((end-start)/60) >= 5):
                        e = False
                        break
                    
            self.ser.write('at+httpterm\r\n')
            time.sleep(0.5)
            
            return e

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
                            #print(gpsData[2])
                            status,fix = gpsData[0], gpsData[1]
                            gps["latitud"] = gpsData[3] # latitud
                            gps["longitud"] = gpsData[4] # longitud
                            gps["velocidad"] = gpsData[6] # velocidad
                            gps["idCamion"] = self.camion
                            ##gps["fecha"] = datetime.now()
                            
                            try:
                                naive = self.timeInfo('GPS',gpsData)
                                gps["fecha"] = naive
                                print(naive)
                            except Exception as e:
                                print(str(e) + "GPS")
                                gps["fecha"] = datetime.now()
                            
            #self.ser.write("at+cgnspwr=0\r\n")
            time.sleep(0.5)
            return gps,status,fix

    def getGPSbyGSM(self,mode):
    #	Esta funcion le sirve a nuestro guardian para obtiener la latitud,
    #	longitud y velocidad a traves del posicionamiento de GSM,
    #	configurado al momento de configurar el GPRS.
    ##	Regresa los datos de solicitados en un diccionario.
    #	return: dict
            data = ""
            gpsData = None
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
                            
                            if mode != 'Clock':
                                gps = {}
                                try:
                                        gps["latitud"] = gpsData[2] # latitud
                                        gps["longitud"] = gpsData[1] # longitud
                                except:
                                        gps["latitud"] = ""
                                        gps["longitud"] = ""
                                gps["velocidad"] = 0 # velocidad
                                gps["idCamion"] = self.camion
                                
                                try:
                                    naive = self.timeInfo("",gpsData)
                                    gps["fecha"] = naive
                                    print(naive)
                                except Exception as e:
                                    print(str(e) + "GSM")
                                    gps["fecha"] = datetime.now()

            time.sleep(0.5)
            return gps

    def getClock(self):
    #	Esta funcion le sirve a nuestro guardian para obtiener la latitud,
    #	longitud y velocidad a traves del posicionamiento de GSM,
    #	configurado al momento de configurar el GPRS.
    ##	Regresa los datos de solicitados en un diccionario.
    #	return: dict
##            data,status,fix = "","",""
            data = ""
            gpsData = None
            self.ser.flushInput()
            self.ser.write("at+cipgsmloc=1,1\r\n")
            time.sleep(10)

            timeGSM = ""
            fechaGSM = ""
            
            while self.ser.inWaiting() > 0:
                    data += self.ser.read(self.ser.inWaiting())
            if data != "":
                    data = data.split()
                    if 'at+cipgsmloc=1,1' in data and '+CIPGSMLOC:' in data:
                            gpsData = data[data.index('+CIPGSMLOC:') + 1]
                            gpsData = gpsData.split(",")
                            try:
                                    naive = self.timeInfo("",gpsData)
                                    naive = str(naive)
                                    naive = naive.split()
                                    timeGSM = naive[1]
                                    fechaGSM = naive[0]
                                    
                            except Exception as e:
                                    print(e)
                                    timeGSM = ""
                                    fechaGSM = ""
            time.sleep(0.5)
            return fechaGSM,timeGSM

    def timeInfo(self,method,gpsData):
        if method != "GPS":
            date = gpsData[3][0:4]+"-"+gpsData[3][5:7]+"-"+gpsData[3][8:10]
            dateTime = date+" "+gpsData[4]
        else:
            dateTime = gpsData[2]
            dateTime = dateTime[0:4]+'-'+dateTime[4:6]+'-'+dateTime[6:8]+' '+dateTime[8:10]+':'+dateTime[10:12]+':'+dateTime[12:14]
            
        string = datetime.strptime(dateTime, "%Y-%m-%d %H:%M:%S")
        datetime_obj_GMT = timezone('GMT').localize(string)
        now_pacific = datetime_obj_GMT.astimezone(timezone('US/Pacific'))
        naive = now_pacific.replace(tzinfo=None)
        
        return naive
        
    def desertar(self):
    #	Esta funcion sirve para terminar el periodo de vigilia de nuestro
    #	guardian.
    #	Cierra el proceso de http
    #	Cierra la conexion serial.
            self.ser.write("at+cgnspwr=0\r\n")
            time.sleep(0.5)
            self.ser.close()
            
    def sendSMS(self):
        data = ""
        self.ser.flushInput()

        self.ser.write('AT+CMGS="2222"\r')
        time.sleep(3)
        self.ser.write('BAJA'+chr(26))
        time.sleep(3)

        while self.ser.inWaiting() > 0:
            data += self.ser.read(self.ser.inWaiting())
            print(data)
            
    def readSMS(self):
        stats = False
        reboot = False
        data = ""
        cReadSMS = ["AT+CMGF=1\r\n",'AT+CPMS="SM"\r\n']
        try:
            for command in cReadSMS:
                self.ser.write(command)
                time.sleep(0.5)
            self.ser.write('AT+CMGL="ALL"\r\n')
            time.sleep(0.5)
            while self.ser.inWaiting() > 0:
                data += self.ser.read(self.ser.inWaiting())
            if "stats" in data:
                stats = True
            if "reboot" in data:
                reboot = True
            self.ser.flushInput()
            self.ser.write('AT+CMGD=1,4\r\n')
            time.sleep(0.5)
        except Exception as e:
            logging.info(str(e))
        
        return(stats,reboot)
                
    def delete(self):
        data=""
        self.ser.flushInput()
        self.ser.write('AT+CMGD=1,4\r\n')
        time.sleep(0.5)
        while self.ser.inWaiting() > 0:
            data += self.ser.read(self.ser.inWaiting())
        print(data)
            
    def sendMail(self):
        data=""
        self.ser.flushInput()
        self.ser.write('AT+EMAILCID=1\r\n')
        time.sleep(0.5)
        self.ser.write('AT+EMAILTO=30\r\n')
        time.sleep(0.5)
        self.ser.write('AT+SMTPSRV="smtp.gmail.com",465\r\n')
        time.sleep(0.5)
        self.ser.write('AT+SMTPAUTH=1,"pruebaafal@gmail.com","C3ty$2017"\r\n')
        time.sleep(0.5)
        self.ser.write('AT+SMTPFROM="pruebaafal@gmail.com","Prueba"\r\n')
        time.sleep(0.5)
        self.ser.write('AT+SMTPRCPT=0,0,"nataliacornejob@gmail.com","Natalia"\r\n')
        time.sleep(0.5)
        self.ser.write('AT+SMTPSUB="Test"\r\n')
        time.sleep(0.5)
        self.ser.write('AT+SMTPBODY\r\n')
        time.sleep(3)
        self.ser.write('This is a test mail. Hello, Natalia.'+chr(26))
        time.sleep(3)
        self.ser.write('AT+SMTPSEND\r')
        time.sleep(0.5)
        while self.ser.inWaiting() > 0:
            data += self.ser.read(self.ser.inWaiting())
        return(data)
        