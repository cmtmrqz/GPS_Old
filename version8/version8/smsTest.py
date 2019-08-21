from clases import *

g = guardian("/dev/ttyS0",115200,"13")
#print(g.getGPSbyGSM(""))
#g.turnOn()
#time.sleep(5)
#g.turnOn()

g.isOn()
g.setGPRS()

#g.delete()

g.sendSMS('Mail no enviado','+526642873248')




    
