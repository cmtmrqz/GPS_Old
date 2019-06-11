import subprocess as sbp

def executeBashCommand(command):
	process = sbp.Popen(command.split(),stdout=sbp.PIPE)
	out,error = process.communicate()
	return out

def readNotSent(filename):
	file = open(filename,'r').read()
	return file

def createNotSent(text,name):
	file = open(name,'w')
	file.write(text)
	file.close()
