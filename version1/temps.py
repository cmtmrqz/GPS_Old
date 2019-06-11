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
import time
import datetime
from camion import camioncito

def getTemps():
	#Variables used for data transmition
	GPIOs = [6,12]
	sensor = Adafruit_DHT.AM2302
	now = datetime.datetime.now()

	## data for API Post

	## Variables for data transmition
	humidityCon = None
	temperatureCon = None
	humidityRef = None
	temperatureRef = None
	now = datetime.datetime.now()

	for i in range(2):
		humidity, temperature = Adafruit_DHT.read_retry(sensor, GPIOs[i])
		if i == 0:
			humidityCon = humidity
			temperatureCon = temperature
		else:
			humidityRef = humidity
			temperatureRef = temperature
	dataCon = {
		"idCamion": camioncito,
		"Equipo": "Congelador",
		"Humedad": round(humidityCon,2),
		"Temperatura": round(temperatureCon,2),
		"fecha": now.strftime("%Y-%m-%d %H:%M:%S")
	}

	dataRef = {
		"idCamion": camioncito,
		"Equipo": "Refrigerador",
		"Humedad": round(humidityRef,2),
		"Temperatura": round(temperatureRef,2),
		"fecha": now.strftime("%Y-%m-%d %H:%M:%S")
	}
	return (dataCon,dataRef)


if __name__ == "__main__":
	print(getTemps())

