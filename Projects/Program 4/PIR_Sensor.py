import RPi_GPIO as GPIO
import time

PIR_pin = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)

#Returns boolean value. True if presence detected, false otherwise
def PollPIR():
  return GPIO.input(PIR_pin)
