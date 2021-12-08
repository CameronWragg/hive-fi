import signal
from os import system
from sys import exit

import RPi.GPIO as GPIO


def main() -> int:
    try:
        BUTTONS = [5, 6, 16, 24]
        LABELS = ['A', 'B', 'X', 'Y']
        BL_CYCLE = [50, 75, 100, 0, 25]

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(13, GPIO.OUT)

        BACKLIGHT = GPIO.PWM(13, 500)
        BACKLIGHT.start(25)

        def default_behaviour(pin):
            label = LABELS[BUTTONS.index(pin)]
            print(f"{label} button pressed, no action currently assigned.")

        def backlight_change(pin) -> None:
            label = LABELS[BUTTONS.index(pin)]
            _next_b_cycle = BL_CYCLE.pop(0)
            print(f"{label} button pressed, backlight set to: {_next_b_cycle}.")
            BL_CYCLE.append(_next_b_cycle)
            BACKLIGHT.ChangeDutyCycle(_next_b_cycle)

        def safe_shutdown(pin) -> None:
            command = "sudo shutdown now -h"
            label = LABELS[BUTTONS.index(pin)]
            print(f"{label} button pressed, shutting down.")
            BACKLIGHT.stop()
            GPIO.cleanup()
            system(command)

        def safe_reboot(pin) -> None:
            command = "sudo shutdown now -r"
            label = LABELS[BUTTONS.index(pin)]
            print(f"{label} button pressed, rebooting.")
            BACKLIGHT.stop()
            GPIO.cleanup()
            system(command)


        GPIO.add_event_detect(BUTTONS[0], GPIO.FALLING, default_behaviour, bouncetime=200)
        GPIO.add_event_detect(BUTTONS[1], GPIO.FALLING, backlight_change, bouncetime=200)
        GPIO.add_event_detect(BUTTONS[2], GPIO.FALLING, safe_shutdown, bouncetime=200)
        GPIO.add_event_detect(BUTTONS[3], GPIO.FALLING, safe_reboot, bouncetime=200)

        signal.pause()

    except Exception:
        GPIO.cleanup()
        return 1


if __name__ == "__main__":
    exit(main())
