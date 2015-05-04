import zerorpc
import RPi.GPIO as GPIO
import time

class IngredientBox(object):
    
    def __init__(self):
        self.sensor = 0
        self.weight = [1,1,1,1,1,1] # update array based on readings from GPIOs
        self.angle = [180,90,180,90,180,90] #Save stepper motor angle for reaching each container
        self.initStepperMotor()

    def initStepperMotor(self):
        GPIO.setmode(GPIO.BOARD)
        self.coil_A_1_pin = 24
        self.coil_A_2_pin = 23
        self.coil_B_1_pin = 22
        self.coil_B_2_pin = 21

        GPIO.setup(self.coil_A_1_pin,GPIO.OUT)
        GPIO.setup(self.coil_A_2_pin,GPIO.OUT)
        GPIO.setup(self.coil_B_1_pin,GPIO.OUT)
        GPIO.setup(self.coil_B_2_pin,GPIO.OUT)

        self.state_array = [0x06,0x02,0x0A,0x08,0x09,0x01,0x05,0x04]
    
    def get_sensor_value(self):
        return str(self.weight[self.sensor])

    def ingredient_done(self):
    time.sleep(1)
        self.rotate(self.angle[self.sensor])
    self.sensor = (self.sensor + 1) % 6
        return "done"

    def rotate(self, angle, speed = 0.01):
        steps = int(round(angle / 0.9))
        idx = 0
    
        for cycle in xrange(steps):
            if self.state_array[idx] & (1<<0):  
                GPIO.output(self.coil_A_1_pin,GPIO.HIGH)
            else:
                GPIO.output(self.coil_A_1_pin,GPIO.LOW)

            if self.state_array[idx] & (1<<1):
                GPIO.output(self.coil_A_2_pin,GPIO.HIGH)
            else:
                GPIO.output(self.coil_A_2_pin,GPIO.LOW)

            if self.state_array[idx] & (1<<2):  
                GPIO.output(self.coil_B_1_pin,GPIO.HIGH)
            else:
                GPIO.output(self.coil_B_1_pin,GPIO.LOW)

            if self.state_array[idx] & (1<<3):
                GPIO.output(self.coil_B_2_pin,GPIO.HIGH)
            else:
                GPIO.output(self.coil_B_2_pin,GPIO.LOW)
            if idx == 7:
                idx = 0
            else:
                idx += 1
            time.sleep(speed)   

s = zerorpc.Server(IngredientBox())
s.bind("tcp://0.0.0.0:4242")
s.run()