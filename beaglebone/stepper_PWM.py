import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time
import sys

freq = 100
stepTime = 1.0 / freq
dutyCycle = 50
channel = "P8_13"

#----------
enable = "P8_8"
GPIO.setup(enable,GPIO.OUT)
GPIO.output(enable, GPIO.HIGH)

iterationCnt = 1
iter = 0
while iter < iterationCnt:

	#time.sleep(3)
	print "Starting motor--"
	GPIO.output(enable,GPIO.LOW)    # Enable is activated
	#-----------


	PWM.start(channel, dutyCycle, freq,0)   # PWM is started on step pin

	steps = 0
	precision = 1.846

	#total_steps = int(sys.argv[1]) / 2 + 10
	total_steps = (int(sys.argv[1]) / 1.846) * 2 # Total steps is calculated
	while steps < total_steps:
		steps += 1
		time.sleep(stepTime)    # PWM is enabled for stepTime * num of steps

	PWM.stop(channel) # PWM is stopped

	#------------
	time.sleep(1)
	GPIO.output(enable,GPIO.HIGH) #Enable is deactivated
	iter += 1
