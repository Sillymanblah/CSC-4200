import RPi.GPIO as GPIO
import time

LED_pin = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_pin, GPIO.OUT)

def BlinkLed(): # NOTE: This function needs to be able to handle a varied blink duration (sent by client)
  GPIO.output(LED_pin, GPIO.HIGH)
  time.sleep(0.5)
  GPIO.output(LED_pin,GPIO.LOW)
  time.sleep(0.5)
  return
