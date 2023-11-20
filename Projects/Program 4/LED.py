import RPi.GPIO as GPIO
import time

LED_pin = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_pin, GPIO.OUT)

def BlinkLed():
  GPIO.output(LED_pin, GPIO.HIGH)
  time.sleep(0.5)
  GPIO.output(LED_pin,GPIO.LOW)
  time.sleep(0.5)
  return
