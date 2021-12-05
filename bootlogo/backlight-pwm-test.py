#!/usr/bin/env python

import time
import math
import RPi.GPIO as GPIO
from ST7789 import ST7789
from PIL import Image, ImageDraw


print("Press Ctrl+C to exit.")

SPI_SPEED_MHZ = 90

image = Image.new("RGB", (240, 240), (255, 0, 255))
draw = ImageDraw.Draw(image)

st7789 = ST7789(
    rotation=90,
    port=0,
    cs=1,
    dc=9,
    backlight=None,
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)

GPIO.setmode(GPIO.BCM)

GPIO.setup(13, GPIO.OUT)

backlight = GPIO.PWM(13, 500)

backlight.start(100)

while True:
    brightness = ((math.sin(time.time()) + 1) / 2.0) * 100
    backlight.ChangeDutyCycle(brightness)

    draw.rectangle((0, 0, 240, 240), (255, 0, 255))

    bar_width = int((220 / 100.0) * brightness)
    draw.rectangle((10, 220, 10 + bar_width, 230), (255, 255, 255))

    st7789.display(image)
    time.sleep(1.0 / 30)

backlight.stop()
