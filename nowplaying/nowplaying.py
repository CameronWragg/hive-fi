#!/usr/bin/env python3
from os import environ
from sys import exit
from requests import get

from PIL import Image
import ST7789 as ST7789
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


def main() -> int:
    if environ.get("NP_MUTEX") == "unlocked":
        environ["NP_MUTEX"] = "locked"

        _track_id = environ.get("TRACK_ID")
        _spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=environ.get("SPOTIFY_CLIENT_ID"), client_secret=environ.get("SPOTIFY_CLIENT_SECRET")))
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

        environ["NP_MUTEX"] = "unlocked"
        return 0
    else:
        return 0


if __name__ == "__main__":
    environ["NP_MUTEX"] = "unlocked" # Fix
    exit(main())