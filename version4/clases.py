#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import json
import Adafruit_DHT
import serial
import time
import re
import bluetooth
import RPi.GPIO as gpio
import time

from datetime import timedelta
from datetime import datetime

class tempsCaptain:
	def __init__(self,camion):
		self.camion = camion
		self.gpios = [6,12]
		self.sensor = Adafruit_DHT.AM2302

	def getTemps(self):
		now = datetime.now()

		humidityCon = None
		temperatureCon = None
		humidityRef = None
		temperatureRef = None

		for i in range(2):
			humidity,temperature = Adafruit_DHT.read_retry(self.sensor,self.gpios[i])
			if i == 0:
				humidityCon = humidity
				temperatureCon = temperature
			else:
				humidityRef = humidity
				temperatureRef = temperature
		dataCon = {
			"idCamion": self.camion,
			"Equipo":"Congelador",
			"Humedad":round(humidityCon,2),
			"Temperatura": round(temperatureCon,2),
			"fecha": now.strftime("%Y-%m-%d %H:%M:%S")
		}

		dataRef = {
			"idCamion": self.camion,
			"Equipo": "Refrigerador",
			"Humedad": round(humidityRef,2),
			"Temperatura": round(temperatureRef,2),
			"fecha": now.strftime("%Y-%m-%d %H:%M:%S")
		}
		return (dataCon,dataRef)

	def send(self,bd_addr,data):
		port = 1

		sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		sock.connect((bd_addr,port))
		sock.send(str(data))
		sock.close()
		time.sleep(0.5)

class guardian:
	def __init__(self,device,bdrate,camion):
		self.device = device
		self.bdrate = bdrate
		self.camion = camion
		self.ser = serial.Serial(self.device,self.bdrate)
		self.pause = 10000 ## time to wait for the data to do the http POST
		self._cPostGPS = ['at+httpinit\r\n','at+httppara="CID",1\r\n','at+httppara="URL","http://201.170.127.72:8092/api/GPS"\r\n','at+httppara="CONTENT","application/json"\r\n','at+httpdata=319488,'+str(self.pause)+'\r\n','at+httpaction=1\r\n','at+httpread\r\n','at+httpterm\r\n']
		self._cPostTemps = ['at+httpinit\r\n','at+httppara="CID",1\r\n','at+httppara="URL","http://201.170.127.72:8092/api/Temps"\r\n','at+httppara="CONTENT","application/json"\r\n','at+httpdata=319488,'+str(self.pause)+'\r\n','at+httpaction=1\r\n','at+httpread\r\n','at+httpterm\r\n']
		self._cSetGPRS = ['at+sapbr=3,1,"Contype","GPRS"\r\n','at+sapbr=3,1,"APN","internet.itelcel.com"\r\n','at+sapbr=1,1\r\n','at+sapbr=2,1\r\n']
		self._cGetGPS = ["at+cgnsinf\r\n"]

	def setGPRS(self):
		self.ser.flushInput()
		for command in self._cSetGPRS:
			self.ser.write(command)
			time.sleep(0.5)

	def isOn(self):
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
		gpio.setmode(gpio.BOARD)
		gpio.setup(7,gpio.OUT)

		gpio.output(7,gpio.LOW)
		time.sleep(4)
		gpio.output(7,gpio.HIGH)
		gpio.cleanup()

	def isConnected(self):
		self.ser.flushInput()
		response = ""
		for command in self._cSetGPRS:
                        self.ser.write(command)
                        time.sleep(0.5)
		while self.ser.inWaiting() > 0:
			response += self.ser.read(self.ser.inWaiting())
		if len(re.findall(r'\"\d*\.\d*\.\d*\.\d*\"',response))>0:
			return True
		else:
			return False

	def post(self,data,tipo):
		self.ser.flushInput()
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
		self.ser.write('at+httpterm\r\n')
		time.sleep(0.5)

	def getGPS(self):
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
				status,fix = gpsData[0],gpsData[1]
				gps["latitud"] = gpsData[3] # latitud
				gps["longitud"] = gpsData[4] # longitud
				gps["velocidad"] = gpsData[6] # velocidad
				gps["idCamion"] = self.camion
				nowGPS = datetime.now()
				gps["fecha"] = nowGPS.strftime("%Y-%m-%d %H:%M:%S")

		#self.ser.write("at+cgnspwr=0\r\n")
		time.sleep(0.5)
		return gps,status,fix

	def desertar(self):
		self.ser.write("at+cgnspwr=0\r\n")
		time.sleep(0.5)
		self.ser.close()
