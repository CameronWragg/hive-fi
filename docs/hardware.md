# Hardware

## The board

[Pirate Audio: Line-out](https://shop.pimoroni.com/products/pirate-audio-line-out) is a
mini HAT (65 × 30.5 × 9.5 mm) that fits any 40-pin Raspberry Pi. hive-fi runs it on a
Raspberry Pi Zero 2 W.

| | |
| --- | --- |
| DAC | PCM5100A, 24-bit / 192 kHz, I²S |
| Output | 3.5 mm stereo jack, line level |
| Display | 1.3" IPS LCD, 240 × 240, ST7789 controller, SPI |
| Buttons | Four tactile buttons, active low |

## Pin usage

| Signal | GPIO | Used by |
| --- | --- | --- |
| I²S audio (BCK, LRCK, DIN) | BCM 18, 19, 21 | `hifiberry-dac` overlay |
| DAC enable | BCM 25 | `gpio=25=op,dh` in `config.txt` |
| LCD chip select | SPI0 CE1 (BCM 7) | `hive-fi-nowplaying`, `hive-fi-bootlogo` |
| LCD data/command | BCM 9 | `hive-fi-nowplaying`, `hive-fi-bootlogo` |
| LCD clock and data | SPI0 SCLK/MOSI (BCM 11, 10) | `hive-fi-nowplaying`, `hive-fi-bootlogo` |
| LCD backlight | BCM 13 | `hive-fi-buttons` (PWM) |
| Button A | BCM 5 | `hive-fi-buttons` |
| Button B | BCM 6 | `hive-fi-buttons` |
| Button X | BCM 16 | `hive-fi-buttons` |
| Button Y | BCM 24 | `hive-fi-buttons` |

The LCD has no reset line, and SPI0 CE0 is left free.

**The backlight belongs to `hive-fi-buttons`.** It drives BCM 13 with PWM so that the B
button can dim the panel. `hive-fi-nowplaying` therefore constructs its display object
without a `backlight` argument, so the two services never contend for the line. If you
add a service of your own that touches the panel, leave BCM 13 alone too.

## Boot configuration

On Raspberry Pi OS Bookworm and later this file is `/boot/firmware/config.txt`
(it was `/boot/config.txt` on Buster and Bullseye).

```ini
# SPI, for the LCD
dtparam=spi=on

# Pirate Audio DAC
dtoverlay=hifiberry-dac
gpio=25=op,dh

# Optional: the onboard headphone/HDMI audio just gets in the way here, and
# removing it means ALSA has one obvious default device.
dtparam=audio=off
```

Reboot, then confirm the card is present:

```console
$ aplay -l
card 0: sndrpihifiberry [snd_rpi_hifiberry_dac], device 0: HifiBerry DAC HiFi pcm5102a-hifi-0 ...
```

The kernel driver is named for the PCM5102A; the PCM5100A on this board is register
compatible, so that line is expected.

Check SPI too — the LCD is on `spidev0.1`:

```console
$ ls /dev/spidev*
/dev/spidev0.0  /dev/spidev0.1
```

If either is missing, the overlay or `dtparam` line has not taken effect.

## Permissions

The services run unprivileged. The account they run as needs to be in the `gpio` and
`spi` groups, which own `/dev/gpiochip*` and `/dev/spidev*` on Raspberry Pi OS. The
unit files request both through `SupplementaryGroups=`, so no manual `usermod` is
needed, but you can add them to your login account as well if you want to run the
scripts by hand:

```bash
sudo usermod -aG gpio,spi "$USER"
```

Group changes only apply to new logins.

## Thermal note

The Pi Zero 2 W throttles under sustained load in a closed case. hive-fi is light —
the display redraws at most ten times a second, and only while text is scrolling — but
shairport-sync's resampling is not free. If you enclose the board, leave the DAC and
the SoC some air.
