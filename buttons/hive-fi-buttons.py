import signal
import RPi.GPIO as GPIO


BUTTONS = [5, 6, 16, 24]
LABELS = ['A', 'B', 'X', 'Y']

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.OUT)

B_CYCLE = [0, 25, 50, 100]
BACKLIGHT = GPIO.PWM(13, 500)
BACKLIGHT.start(100)

def default_behaviour(pin):
    label = LABELS[BUTTONS.index(pin)]
    print(f"Button press detected on pin: {pin} label: {label}")

def backlight_change(pin) -> None:
    label = LABELS[BUTTONS.index(pin)]
    print(f"Button press detected on {label}, changing backlight brightness.")
    _next_b_cycle = B_CYCLE.pop(0)
    B_CYCLE.append(_next_b_cycle)
    BACKLIGHT.ChangeDutyCycle(_next_b_cycle)

GPIO.add_event_detect(BUTTONS[0], GPIO.FALLING, default_behaviour, bouncetime=100)
GPIO.add_event_detect(BUTTONS[1], GPIO.FALLING, backlight_change, bouncetime=100)
GPIO.add_event_detect(BUTTONS[2], GPIO.FALLING, default_behaviour, bouncetime=100)
GPIO.add_event_detect(BUTTONS[3], GPIO.FALLING, default_behaviour, bouncetime=100)

signal.pause()
