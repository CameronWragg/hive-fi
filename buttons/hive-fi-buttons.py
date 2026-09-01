#!/usr/bin/env python3
"""Pirate Audio button handling for hive-fi.

The four buttons sit on BCM 5, 6, 16 and 24 (A, B, X, Y) and are active low.
The LCD backlight is on BCM 13 and is driven with PWM so it can be dimmed.

This service owns BCM 13.  hive-fi-nowplaying deliberately leaves the
backlight alone so the two do not fight over the same line.
"""

from __future__ import annotations

import argparse
import logging
import signal
import subprocess
import sys

from gpiozero import PWMLED, Button

LOG = logging.getLogger("hive-fi-buttons")

BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y = 5, 6, 16, 24
BACKLIGHT_PIN = 13

# Brightness steps cycled by the B button, as fractions of full brightness.
BACKLIGHT_LEVELS = (0.5, 0.75, 1.0, 0.0, 0.25)
BACKLIGHT_DEFAULT = 0.25

BOUNCE_SECONDS = 0.2


class Backlight:
    """Cycles the LCD backlight through a fixed set of brightness steps."""

    def __init__(
        self, pin: int = BACKLIGHT_PIN, initial: float = BACKLIGHT_DEFAULT
    ) -> None:
        self._led = PWMLED(pin, initial_value=initial)
        self._index = 0

    def cycle(self) -> None:
        level = BACKLIGHT_LEVELS[self._index]
        self._index = (self._index + 1) % len(BACKLIGHT_LEVELS)
        LOG.info("backlight set to %d%%", round(level * 100))
        self._led.value = level

    def close(self) -> None:
        self._led.close()


def power_command(action: str) -> list[str]:
    """`shutdown` needs root, and the service does not run as root."""
    return [
        "sudo",
        "-n",
        "/sbin/shutdown",
        "-h" if action == "poweroff" else "-r",
        "now",
    ]


def run_power_command(action: str, backlight: Backlight) -> None:
    LOG.info("%s requested", action)
    backlight.close()
    try:
        subprocess.run(power_command(action), check=True)
    except (OSError, subprocess.CalledProcessError):
        # Most likely a missing sudoers rule -- see docs/installation.md.
        LOG.exception("could not %s", action)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--log-level", default="INFO", help="logging level (default: %(default)s)"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(levelname)s %(message)s",
    )

    backlight = Backlight()
    buttons = {
        "A": Button(BUTTON_A, pull_up=True, bounce_time=BOUNCE_SECONDS),
        "B": Button(BUTTON_B, pull_up=True, bounce_time=BOUNCE_SECONDS),
        "X": Button(BUTTON_X, pull_up=True, bounce_time=BOUNCE_SECONDS),
        "Y": Button(BUTTON_Y, pull_up=True, bounce_time=BOUNCE_SECONDS),
    }

    buttons["A"].when_pressed = lambda: LOG.info("A pressed, no action assigned")
    buttons["B"].when_pressed = backlight.cycle
    buttons["X"].when_pressed = lambda: run_power_command("poweroff", backlight)
    buttons["Y"].when_pressed = lambda: run_power_command("reboot", backlight)

    LOG.info(
        "watching buttons on BCM %s",
        ", ".join(str(b.pin.number) for b in buttons.values()),
    )

    try:
        # gpiozero dispatches button callbacks from its own threads.
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        for button in buttons.values():
            button.close()
        backlight.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
