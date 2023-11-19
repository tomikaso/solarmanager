# Module to control relais
import RPi.GPIO as GPIO

def init_relais():
    GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
    GPIO.setup(5, GPIO.OUT) # heat_pump_blocked
    GPIO.setup(6, GPIO.OUT) # boiler
    GPIO.setup(13, GPIO.OUT) # plug1
    GPIO.setup(18, GPIO.OUT) # check_led
    GPIO.setup(19, GPIO.OUT) # heat_pump_appreciated


def plug1_on():
    GPIO.output(13, GPIO.HIGH) # on plug1 = 13
    
def plug1_off():
    GPIO.output(13, GPIO.LOW) # off plug1 = 13
    
def boiler_on():
    GPIO.output(6, GPIO.HIGH) # on boiler = 6
    
def boiler_off():
    GPIO.output(6, GPIO.LOW) # off boiler = 6

def heatpump_blocked():
    GPIO.output(5, GPIO.LOW) # happreciated = 5
    GPIO.output(19, GPIO.HIGH) # blocked = 19

def heatpump_enabled():
    GPIO.output(5, GPIO.LOW) # appreciated = 5
    GPIO.output(19, GPIO.LOW) # blocked = 19

def heatpump_appreciated():
    GPIO.output(5, GPIO.HIGH) # appreciated = 5
    GPIO.output(19, GPIO.LOW) # blocked = 19

def led_on():
    GPIO.output(18, GPIO.HIGH) # on led = 18

def led_off():
    GPIO.output(18, GPIO.LOW) # off led = 18
    





