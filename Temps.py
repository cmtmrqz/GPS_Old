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
import smtplib 
import Adafruit_DHT
import time
from datetime import datetime

#Variables used for data transmition
GPIOs = [3,4]
sensor = Adafruit_DHT.AM2302
camion = "2"
#now = time.strftime("%Y-%m-%d %H*%M*%S", time.gmtime())
now = datetime.now().strftime("%y-%m-%d %H*%M*%S")
temps = camion + "," + now + ","
server  = smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
##server.connect('smtp.gmail.com',465)
##print('conect')
server.login('pruebaafal@gmail.com','C3ty$2017')
me = 'pruebaafal@gmail.com'
target = 'pruebaafal@gmail.com'
# Parse command line parameters.
##sensor_args = { '11': Adafruit_DHT.DHT11,
##                '22': Adafruit_DHT.DHT22,
##                '2302': Adafruit_DHT.AM2302 }
##if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
##    sensor = sensor_args[sys.argv[1]]
##    pin = sys.argv[2]
##else:
##    print('Usage: sudo ./Adafruit_DHT.py [11|22|2302] <GPIO pin number>')
##    print('Example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO pin #4')
##    sys.exit(1)

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
for i in range(2):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, GPIOs[i])
# Un-comment the line below to convert the temperature to Fahrenheit.
# temperature = temperature * 9/5.0 + 32

# Note that sometim es you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!
    if humidity is not None and temperature is not None:
        temps = temps + str(round(humidity,2))+ "," + str (round((temperature*1.8)+32,2)) + ","
       
    else:
        temps = temps + "NaN," + "NaN,"
        sys.exit(1)

msg = temps+"Nan,Nan,Nan"
server.sendmail(me, target, msg)
server.quit()

