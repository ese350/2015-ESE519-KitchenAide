import zerorpc
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.UART as UART
import time
import threading
import serial

# UART 1 - RX P9_26
# UART 1 - TX P9_24

PWM_freq = 100
stepTime = 1.0/PWM_freq
dutyCycle = 50
channel = "P9_16"



class IngredientBox(object):

    def serialThread(self):
        while 1:
                self.weight = self.ser.readline()

    def __init__(self):
        self.sensor = 0
	self.buzz = "P9_14"	
        self.angle = [180,90,180,90,180,90] #Save stepper motor angle for reaching each container
        self.initStepperMotor()
	self.initFluidMotor()
	ADC.setup()
	UART.setup("UART1")
	self.ser = serial.Serial(port="/dev/ttyO1",baudrate=115200)
	self.ser.close()
	self.ser.open()
	GPIO.setup(self.buzz, GPIO.OUT)
	GPIO.output(self.buzz,GPIO.LOW)
	self.weight = "0.0"
	t = threading.Thread(target=self.serialThread)
	t.start()

    def initFluidMotor(self):
	self.fluidLeft = "P8_16"
	self.fluidRight = "P8_18"
	GPIO.setup(self.fluidLeft, GPIO.OUT)
	GPIO.setup(self.fluidRight, GPIO.OUT)
        GPIO.output(self.fluidLeft, GPIO.LOW)
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
    
    def fluidStart(self):
	GPIO.output(self.fluidLeft, GPIO.HIGH)
	GPIO.output(self.fluidRight, GPIO.LOW)

	val = (0.99*(self.volume))+0.75
	time.sleep(val)

        GPIO.output(self.fluidLeft, GPIO.LOW)
        GPIO.output(self.fluidRight, GPIO.LOW)

    def fluidMotor(self,volume):
	print 'rpc'
	print volume
	self.volume = float(volume)
	t = threading.Thread(target=self.fluidStart)
	t.start()
	print 'returning rpc'
	return "Filling"
    
    def get_sensor_value(self):
        #samp = []
        #for i in range(500):
        #        value =  ADC.read_raw("P9_40")
        #        diff = value - self.offset
        #        gram = self.scale *diff
        #        samp.append(gram)
        #avg_gram = sum(samp)*1.0 / len(samp)
	#print avg_gram
	print self.weight
	return self.weight
        
    
    def buzzer(self):
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

    def sound(self):
	print 'Got RPC'
	t = threading.Thread(target=self.buzzer)
	t.start()
	print 'returning RPC'
	return "Buzzed"

    def ingredient_done(self):
        self.rotate(self.angle[self.sensor])
        self.sensor = (self.sensor + 1) % 6
        return "done"

    def rotate(self, angle):
	PWM.start(channel,dutyCycle, PWM_freq)
	steps = 0
	num_steps = angle / 1.846
	time.sleep(stepTime*num_steps)
	PWM.stop(channel)
	return

#x = IngredientBox()
#while 1:
#	x.get_sensor_value()
#	time.sleep(2)
s = zerorpc.Server(IngredientBox())
s.bind("tcp://0.0.0.0:4242")
s.run()
