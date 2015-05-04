import zerorpc
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.UART as UART
import time
import threading
import serial
import os

# UART 1 - RX P9_26
# UART 1 - TX P9_24

PWM_freq = 100
stepTime = 1.0/PWM_freq
dutyCycle = 50
channel = "P9_16"   # Stepper Motor's Step Pin
enable = "P8_8"		# Stepper Motor's Enable Pin

GPIO.setup(enable,GPIO.OUT)		# Set enable GPIO to output
GPIO.output(enable, GPIO.HIGH)	# Disable Enable initially


def rotate(angle):				# Method for rotating stepper by a certain angle
	command = "python stepper_PWM.py " + str(angle)	
	print command
	os.system(command)
	return

# Main class for RPC. Contains methods that the server can access

class IngredientBox(object):

    def serialThread(self):			# Read the weight from arduino continously using UART
        while 1:
            self.weight = self.ser.readline()

    def __init__(self):
		self.sensor = 0
		self.buzz = "P9_14"	
		self.angle = [90,90,60,60,60] #Save stepper motor angle for reaching each container
		self.weight = "0.0"				# Weight variable updated by thread
		self.ingredient = []

		self.initStepperMotor()			# Initialize the stepper motor pins
		self.initFluidMotor()			# Initialize the fluid motor pins
		ADC.setup()
		UART.setup("UART1")				# Initialize the UART to communicated with Arduino
		self.ser = serial.Serial(port="/dev/ttyO1",baudrate=115200)
		self.ser.close()
		self.ser.open()
		GPIO.setup(enable,GPIO.OUT)
		GPIO.output(enable, GPIO.HIGH)
		GPIO.setup(self.buzz, GPIO.OUT)	# Disable the buzzer pin initially
		GPIO.output(self.buzz,GPIO.LOW)
		t = threading.Thread(target=self.serialThread)
		t.start()

    def initFluidMotor(self):
	self.fluidLeft = "P8_16"
	self.fluidRight = "P8_18"
	GPIO.setup(self.fluidLeft, GPIO.OUT)	# Configure the motor pins as output
	GPIO.setup(self.fluidRight, GPIO.OUT)
     	GPIO.output(self.fluidLeft, GPIO.LOW)	# Disable the motor initially
	GPIO.output(self.fluidRight, GPIO.LOW)
	
    def initStepperMotor(self):			
        self.coil_A_1_pin = "P8_8"
        self.coil_A_2_pin = "P8_10"
        self.coil_B_1_pin = "P8_12"
        self.coil_B_2_pin = "P8_14"

        GPIO.setup(self.coil_A_1_pin,GPIO.OUT)
        GPIO.setup(self.coil_A_2_pin,GPIO.OUT)
        GPIO.setup(self.coil_B_1_pin,GPIO.OUT)
        GPIO.setup(self.coil_B_2_pin,GPIO.OUT)

        self.state_array = [0x06,0x02,0x0A,0x08,0x09,0x01,0x05,0x04]

    def tare(self):			# Tare function for weighing scale
	self.ser.write('T')
	self.ser.flushOutput();	#Flush the serial buffer for Arduino
    	return "taring"
    
    def fluidStart(self):	#Thread function for dispensing fluid
	GPIO.output(self.fluidLeft, GPIO.HIGH)
	GPIO.output(self.fluidRight, GPIO.LOW)
	val = (0.99*(self.volume))+0.75 	# Calculate the time to dispense based on volume
	time.sleep(val)						# Water is assumed

        GPIO.output(self.fluidLeft, GPIO.LOW)
        GPIO.output(self.fluidRight, GPIO.LOW)

    def fluidMotor(self,volume): # RPC api for server to dispense the motor
	print 'rpc'
	print volume
	self.volume = float(volume)
	t = threading.Thread(target=self.fluidStart)
	t.start()
	print 'returning rpc'
	return "Filling"
    
    def get_sensor_value(self):	# Return weight from the thread
	print self.weight
	return self.weight
            
    def buzzer(self):		# Method for activating buzzer ; Generates PWM on buzz pin
	print 'starting buzz..'
	PWM.start(self.buzz,90,8000,0)
	#GPIO.output(self.buzz,GPIO.HIGH)
	time.sleep(5)
	PWM.stop(self.buzz)
	PWM.start(self.buzz,90,4000,0)
	time.sleep(5)	
	PWM.stop(self.buzz)
	#GPIO.output(self.buzz,GPIO.LOW)
	return

    def sound(self):	# RPC api for server
	print 'Got RPC'
	t = threading.Thread(target=self.buzzer)
	t.start()
	print 'returning RPC'
	return "Buzzed"

    def ingredient_done(self, name):	# Method for rotating the stepper, taring when ingredient is done
    	self.ingredient.append(name)
        rotate(self.angle[self.sensor])
        self.sensor = (self.sensor + 1) % len(self.angle)
	self.ser.write('T')
	self.ser.flushOutput()
        return "done"

    def order(self,lst):	# RPC method to spin the disc based on ingredients; Server provides list
	if lst == '':
	  return "done"
	lst = lst.split('@') 	# List is parsed
	t = threading.Thread(target=self.orderIngredient,args=(lst,))
	t.start()
	return "done"

    def orderIngredient(self, lst):	# Thread method to spin the disc based on ingredients 
	print self.ingredient 		# Used for each step
	for ingr in lst:
	  print ingr
	  nextIdx = self.ingredient.index(ingr) # Get the index of the ingredient specified by the server
	  print self.calculateAngle(nextIdx)
	  rotate(self.calculateAngle(nextIdx)) 	#rotate the stepper for the ingredient
	  self.sensor = nextIdx
	  time.sleep(3)

    def calculateAngle(self, target):  #Calculates the angle
	if target < self.sensor:
		if target == 0:
			res = sum(self.angle[self.sensor:])
		else:
			res = sum(self.angle[self.sensor:]) + sum(self.angle[0:target])
	elif target == self.sensor:
		res = 0
	else:
		res = sum(self.angle[self.sensor:target])
	return int(res)
'''
rotate(60)
time.sleep(3)
rotate(60)
time.sleep(3)
rotate(90)
'''

#while 1:

#x = IngredientBox()
#x.buzzer()
#while 1:
#	x.get_sensor_value()
#	time.sleep(2)

#initiaite the RPC server

s = zerorpc.Server(IngredientBox())
s.bind("tcp://0.0.0.0:4242")
s.run()
