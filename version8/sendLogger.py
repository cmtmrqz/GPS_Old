import subprocess as sbp

command = 'mpack -s "Test" /home/pi/test.log cmtmrqz@gmail.com'

try:
	process = sbp.Popen(command.split(),stdout=sbp.PIPE)
	out,error = process.communicate()
	with open('/home/pi/test.log', 'w'):
		pass
except:
	pass
