#!/usr/bin/env python3
from sys import argv, exit

import RPi.GPIO as GPIO
from PIL import Image
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from requests import get
from ST7789 import BG_SPI_CS_FRONT, ST7789


def main() -> int:
    try:
        display = ST7789(
            port=0, cs=BG_SPI_CS_FRONT, dc=9, spi_speed_hz=80 * 1000 * 1000
        )

        spotify = Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=argv[1], client_secret=argv[2]
            )
        )

        with open("/etc/default/nowplaying") as file:
            event_and_trackid = [line.rstrip() for line in file.readlines()]

        if event_and_trackid[0] != "stopped":
            track = spotify.track(event_and_trackid[1])
            display.display(
                Image.open(get(track["album"]["images"][0]["url"]).raw).resize((display.width, display.height))
            )
        else:
            display.display(
                Image.open("/home/pi/hive-fi/bootlogo/hive-fi.jpeg").resize(
                    (display.width, display.height)
                )
            )

        return 0

    except Exception:
        GPIO.cleanup()
        return 1


if __name__ == "__main__":
    exit(main())
