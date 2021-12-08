#!/usr/bin/env python3
from sys import exit

from PIL import Image
from ST7789 import ST7789
import RPi.GPIO as GPIO


def main() -> int:
    try:
        disp = ST7789(
            height=240,
            rotation=90,
            port=0,
            cs=ST7789.BG_SPI_CS_FRONT, 
            dc=9,
            backlight=None,
            spi_speed_hz=80 * 1000 * 1000,
            offset_left=0,
            offset_top=0
        )
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(13, GPIO.OUT)
        backlight = GPIO.PWM(13, 500)

        WIDTH = disp.width
        HEIGHT = disp.height

        disp.begin()
        image = Image.open("/home/pi/hive-fi/bootlogo/hive-fi.jpeg")
        image = image.resize((WIDTH, HEIGHT))
        backlight.start(30)
        disp.display(image)
        return 0

    except Exception:
        return 1


if __name__ == "__main__":
    exit(main())
