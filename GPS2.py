#!/bin/python3

import gps
import sys
import smtplib
import time

from datetime import datetime
##Variables for data transmition
camion = "2"
#now = time.strftime("%Y-%m-%d %H*%M*%S", time.localtime())
now = datetime.now().strftime("%y-%m-%d %H*%M*%S")
originalMsg = camion + ","  + now + "," + "Nan,Nan,Nan,Nan,"
connectionMail = False

try:
    server  = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login('pruebaafal@gmail.com','C3ty$2017')
    me = 'pruebaafal@gmail.com'
    target = 'pruebaafal@gmail.com'
    msg = ""
    connectionMail = True
except:
    print("Unreacheable connection to Mail Server.")

##Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost","2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

if connectionMail:
    while msg == "":
        try:
            report = session.next()
##        Wait for a 'TPV' report amd display the curremt time
##        To see all report data, uncomment the line below
##        print (report)
            if report["class"] == "TPV":
##            if hasattr(report,"time"):
##                print (report.time)
                if hasattr(report, "lat"):
                    msg = originalMsg + str(report.lat) + ","
##                print(report.lat)
                if hasattr(report, "lon"):
                    msg = msg + str(report.lon) + ","
##                print(report.lon)
                if hasattr(report, "speed"):
                    msg = msg + str(round(report.speed * gps.MPS_TO_KPH,5))
##                print(report.speed * gps.MPS_TO_KPH)
                server.sendmail(me, target, msg)
                print(msg)
        except KeyError:
            pass
        except KeyboardInterrupt:
            server.quit()
            quit()
        except StopIteration:
            session = None
            server.quit()
            print ("GPSD has terminated")
    server.quit()

