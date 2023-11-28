import RPi.GPIO as GPIO
import time

LED_pin = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_pin, GPIO.OUT)

#Blink the LED in a 50% duty cycle every Period seconds NumBlinks times
def BlinkLed(Period, NumBlinks):
  for Blink in range(NumBlinks):
    GPIO.output(LED_pin, GPIO.HIGH)
    time.sleep(Period/2)
    GPIO.output(LED_pin,GPIO.LOW)
    time.sleep(Period/2)
  return
