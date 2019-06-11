import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BOARD)
gpio.setup(7,gpio.OUT)

gpio.output(7,gpio.LOW)
time.sleep(4)
gpio.output(7,gpio.HIGH)
gpio.cleanup()

