import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

coil_A_1_pin = 24
coil_A_2_pin = 23
coil_B_1_pin = 22
coil_B_2_pin = 21

GPIO.setup(coil_A_1_pin,GPIO.OUT)
GPIO.setup(coil_A_2_pin,GPIO.OUT)
GPIO.setup(coil_B_1_pin,GPIO.OUT)
GPIO.setup(coil_B_2_pin,GPIO.OUT)

state_array = [0x06,0x02,0x0A,0x08,0x09,0x01,0x05,0x04]

def rotate(angle, speed = 0.01):
    temp = int(round(angle / 0.9))
    idx = 0
    for cycle in xrange(temp):
        if state_array[idx] & (1<<0):  
            GPIO.output(coil_A_1_pin,GPIO.HIGH)
        else:
            GPIO.output(coil_A_1_pin,GPIO.LOW)

        if state_array[idx] & (1<<1):
            GPIO.output(coil_A_2_pin,GPIO.HIGH)
        else:
            GPIO.output(coil_A_2_pin,GPIO.LOW)

        if state_array[idx] & (1<<2):  
            GPIO.output(coil_B_1_pin,GPIO.HIGH)
        else:
            GPIO.output(coil_B_1_pin,GPIO.LOW)

        if state_array[idx] & (1<<3):
            GPIO.output(coil_B_2_pin,GPIO.HIGH)
        else:
            GPIO.output(coil_B_2_pin,GPIO.LOW)
        if idx == 7:
            idx = 0
        else:
            idx += 1
        time.sleep(speed)

rotate(90)        
