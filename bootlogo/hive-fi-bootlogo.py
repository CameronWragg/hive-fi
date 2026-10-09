#!/usr/bin/env python3
"""Draw the hive-fi logo on the Pirate Audio LCD at boot.

This is a one-shot: it paints the panel and exits.  The ST7789 keeps its
framebuffer without a host attached, so the logo stays up until something
else — normally hive-fi-nowplaying — draws over it.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from PIL import Image, ImageOps

LOG = logging.getLogger("hive-fi-bootlogo")

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOGO = REPO_ROOT / "bootlogo" / "hive-fi.jpeg"

SIZE = 240
DC_PIN = 9
SPI_PORT = 0
SPI_SPEED_HZ = 80 * 1000 * 1000


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--logo",
        default=str(DEFAULT_LOGO),
        help="image to display (default: %(default)s)",
    )
    parser.add_argument(
        "--rotation",
        type=int,
        choices=(0, 90, 180, 270),
        default=90,
        help="display rotation in degrees (default: %(default)s)",
    )
    parser.add_argument(
        "--spi-speed",
        type=int,
        default=SPI_SPEED_HZ,
        help="SPI clock in Hz (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        from st7789 import BG_SPI_CS_FRONT, ST7789

        display = ST7789(
            port=SPI_PORT,
            cs=BG_SPI_CS_FRONT,
            dc=DC_PIN,
            width=SIZE,
            height=SIZE,
            rotation=args.rotation,
            spi_speed_hz=args.spi_speed,
        )

        with Image.open(args.logo) as image:
            logo = ImageOps.fit(
                ImageOps.exif_transpose(image).convert("RGB"),
                (SIZE, SIZE),
                method=Image.LANCZOS,
            )

        display.display(logo)
    except Exception:
        LOG.exception("could not display %s", args.logo)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
