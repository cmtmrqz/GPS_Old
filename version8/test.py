from clases import *
g = guardian("/dev/ttyS0",115200,"13")
print g.post({'latitud': '32.486719', 'idCamion': 13, 'fecha': '2019-06-29 16:54:10', 'velocidad': '0.00', 'longitud': '-116.941037'}, 'GPS')
