#!/usr/bin/env python3
from os import environ
from sys import exit
from requests import get

from PIL import Image
import ST7789 as ST7789
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


def main() -> int:
    try:
        _track_id = environ.get("TRACK_ID")
        _spotify = Spotify(auth_manager=SpotifyClientCredentials())
        _track = _spotify.track(_track_id)
        _res = get(_track["album"]["images"][0]['url'])
        _img = Image.open(_res.raw)

        _display = ST7789.ST7789(
            height=240,
            rotation=90,
            port=0,
            cs=ST7789.BG_SPI_CS_FRONT, 
            dc=9,
            backlight=19,
            spi_speed_hz=80 * 1000 * 1000,
            offset_left=0,
            offset_top=0
        )

        WIDTH = _display.width
        HEIGHT = _display.height

        _display.begin()
        _img = _img.resize((WIDTH, HEIGHT))
        _display.display(_img)

        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    environ["SPOTIPY_CLIENT_ID"] = "8ec7c3d0cfea4d5da920f02f000a84c9"
    environ["SPOTIPY_CLIENT_SECRET"] = "17fc8571cf484e4c9d857b6a3651e9de"
    exit(main())