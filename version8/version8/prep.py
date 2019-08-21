import subprocess as sbp


command = ["git clone https://github.com/cmtmrqz/GPS.git",
			"rm -rfv Desktop/GPS","cp GPS Desktop/GPS",
			"cp -v Desktop/GPS/version8 Desktop/version8",
			"python Desktop/version8/prepPart2.py"]

for c in command:
	try:
		process = sbp.Popen(c.split(),stdout=sbp.PIPE)
		out,error = process.communicate()
	except:
		return out


