import subprocess as sbp

def executeBashCommand(command):
	process = sbp.Popen(command.split(),stdout=sbp.PIPE)
	out,error = process.communicate()
	return out

def readNotSent(filename):
	file = open('/home/pi/'+filename,'r+')
	fileStr = file.read()
	return file, fileStr

def createNotSent(text,filename,type):
    file = open('/home/pi/'+filename,'a+')
    if type == True:
        file.write(text+'@')
    else:
        file.write(text)
        
        
        
        
    file.close()
