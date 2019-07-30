import subprocess as sbp

from camion import camioncito

command = "mpack -s \"Camion" + str(camioncito) + "\" /home/pi/test.log cmtmrqz@gmail.com"
print(command)
try:
	process = sbp.Popen(command.split(),stdout=sbp.PIPE)
	out,error = process.communicate()
	with open('/home/pi/test.log', 'w'):
		pass
except Exception as e:
	print(e)
	pass
