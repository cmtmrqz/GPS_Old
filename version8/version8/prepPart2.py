from clases import *
from fileManagement import *

camionNum = raw_input("Numero de camion: ")

try:
	file = open('/home/pi/Desktop/version8/camion.py','a+')
	file.truncate(0)
	file.write('camioncito = ' + camionNum) 
	file.close() 
	
except Exception as e:
	print e

from camion import camioncito
print camioncito
g = guardian("/dev/ttyS0",115200,camioncito)
g.isOn()
g.setGPRS()
#g.sendSMS('','+526642048642')
g.sendSMS('Mi numerito','+526642873248')
print("Se envio telefono")
g.sendSMS('BAJA','2222')
print("Se solicito baja")
g.delete()
print("Se borraron mensajes")
connected = g.isConnected
if connected:
	print("Datos moviles")
