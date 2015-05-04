import Adafruit_BBIO.GPIO as GPIO
import time

PD_SCK = "P8_10"
DOUT = "P8_12"
GAIN = 1
OFFSET = 0
SCALE = 660.0

def setUp():
	GPIO.setup(DOUT, GPIO.IN)
	GPIO.setup(PD_SCK, GPIO.OUT)
	#setGain()	

def isReady():
	if GPIO.input(DOUT):
		return 0
	else:
		return 1

def loop():
	GPIO.output("P8_8",GPIO.HIGH);
        for j in range(2,-1,-1):
                for i in range(7,-1,-1):
                        GPIO.output(PD_SCK, GPIO.HIGH)
                        if (GPIO.input(DOUT)==0):
                                a = 1
                        else:
                                a = 2
                        GPIO.output(PD_SCK,GPIO.LOW)
	GPIO.output("P8_8",GPIO.LOW);

def read():
	data = [0,0,0]
	while (isReady()==0):
		continue
	for j in range(2,-1,-1):
		for i in range(7,-1,-1):
			GPIO.output(PD_SCK, GPIO.HIGH)
			if (GPIO.input(DOUT)==0):	
				data[j] = data[j] & ~(1<<i)
			else:
				data[j] = data[j] | (1<<i)
			GPIO.output(PD_SCK,GPIO.LOW)			
	
	for i in range(GAIN):	
		GPIO.output(PD_SCK,GPIO.HIGH)
		GPIO.output(PD_SCK,GPIO.LOW)

	data[2] = data[2] ^ 0x80;

	val =  (data[2]<<16) | (data[1] << 8) | (data[0])
	return val

def setGain():
	print 'setGain'
        GPIO.output(PD_SCK,GPIO.LOW)
        read()

def readAverage():
	sum = 0;
	for i in range(10):
		sum+=read()
	print sum
	return sum/10.0;

def getValue():
	return read()-OFFSET;

def getUnits():
	return getValue()/SCALE;

def powerDown():
	GPIO.output(PD_SCK,GPIO.LOW)
	GPIO.output(PD_SCK,GPIO.HIGH)
def powerUp():
	GPIO.output(PD_SCK,GPIO.LOW)
def tare():
	sum = readAverage();
	offset = sum;

setUp()
GPIO.setup("P8_8",GPIO.OUT);
#tare()
while 1:
#	loop()	
	print getUnits()
	powerDown()
	time.sleep(5)	
	powerUp()
