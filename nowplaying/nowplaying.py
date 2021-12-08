#!/usr/bin/env python3
from os import environ, system
from sys import argv, exit

from PIL import Image
from requests import get
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from ST7789 import BG_SPI_CS_FRONT, ST7789


def main() -> int:
    try:
        system(f"export SPOTIPY_CLIENT_ID='{argv[1]}'")
        system(f"export SPOTIPY_CLIENT_SECRET='{argv[2]}'")

        _track_id = environ.get("TRACK_ID")
        _spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())
        _track = _spotify.track(_track_id)
        _res = get(_track["album"]["images"][0]['url'])
        _img = Image.open(_res.raw)

        _display = ST7789(
            height=240,
            rotation=90,
            port=0,
            cs=BG_SPI_CS_FRONT, 
            dc=9,
            backlight=None,
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
    exit(main())
