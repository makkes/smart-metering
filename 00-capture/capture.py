import time
import sys
import random

class DummyGPIO:
    def input(self, pin):
        return random.randint(0,1)
    def cleanup():
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: {} CURRENT_METER_VALUE".format(sys.argv[0]))
        sys.exit(1)

    PIN = 14

    if len(sys.argv) >= 3 and sys.argv[2] == "DUMMY":
        GPIO = DummyGPIO()
    else:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.IN, pull_up_down = GPIO.PUD_OFF)

    meterVal = float(sys.argv[1])
    print("{},{:.2f}".format(time.strftime("%x %X", time.localtime()), meterVal))
    sys.stdout.flush()

    curVal = -1
    try:
        while True:
            newVal = GPIO.input(PIN)
            if newVal != curVal:
                if newVal == 1:
                    meterVal += 0.01
                    print("{},{:.2f}".format(time.strftime("%x %X", time.localtime()), meterVal))
                    sys.stdout.flush()
                curVal = newVal
            time.sleep(.5)
    except:
        GPIO.cleanup()
