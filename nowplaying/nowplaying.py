#!/usr/bin/env python3
from sys import argv, exit

import RPi.GPIO as GPIO
from PIL import Image
from requests import get
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from ST7789 import BG_SPI_CS_FRONT, ST7789


def main() -> int:
    try:
        display = ST7789(
            port=0,
            cs=BG_SPI_CS_FRONT, 
            dc=9,
            spi_speed_hz=80 * 1000 * 1000
        )

        display.reset()

        with open("/usr/local/bin/nowplaying") as file:
            lines = [line.rstrip() for line in file.readlines()]

        event = lines[0]
        print(event)
        track_id = lines[1]
        spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=argv[1], client_secret=argv[2]))
        print(track_id)
        track = spotify.track(track_id)
        print(track["album"]["images"][0]['url'])
        res = get(track["album"]["images"][0]['url'])
        img = Image.open(res.raw)
        img = img.resize((display.width, display.height))
        display.display(img)

        return 0

    except Exception:
        GPIO.cleanup()
        return 1


if __name__ == "__main__":
    exit(main())
