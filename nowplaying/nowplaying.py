#!/usr/bin/env python3
from sys import argv, exit

from PIL import Image
from requests import get
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from ST7789 import BG_SPI_CS_FRONT, ST7789


def main() -> int:
    try:
        with open("/etc/default/nowplaying") as file:
            _lines = [line.rstrip() for line in file.readlines()]

        _event = _lines[0]
        _track_id = _lines[1]
        _spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=argv[1], client_secret=argv[2]))
        print(_track_id)
        _track = _spotify.track(_track_id)
        print(_track["album"]["images"][0]['url'])
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
