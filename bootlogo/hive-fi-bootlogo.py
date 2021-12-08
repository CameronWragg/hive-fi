#!/usr/bin/env python3
from sys import exit

import RPi.GPIO as GPIO
from PIL import Image
from ST7789 import BG_SPI_CS_FRONT, ST7789


def main() -> int:
    try:
        display = ST7789(
            port=0,
            cs=BG_SPI_CS_FRONT, 
            dc=9,
            spi_speed_hz=80 * 1000 * 1000
        )

        image = Image.open("/home/pi/hive-fi/bootlogo/hive-fi.jpeg")
        image = image.resize((display.width, display.height))
        display.display(image)
        return 0

    except Exception:
        GPIO.cleanup()
        return 1


if __name__ == "__main__":
    exit(main())
