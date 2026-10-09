# Hardware

A [Pirate Audio: Line-out](https://shop.pimoroni.com/products/pirate-audio-line-out) on
a Raspberry Pi Zero 2 W: PCM5100A DAC with a 3.5 mm line-level jack, a 1.3" 240×240
ST7789 LCD on SPI, and four active-low buttons.

## Pins

| Signal | GPIO | Used by |
| --- | --- | --- |
| I²S audio | BCM 18, 19, 21 | `hifiberry-dac` overlay |
| DAC enable | BCM 25 | `gpio=25=op,dh` |
| LCD SPI | SPI0 CE1, SCLK, MOSI (BCM 7, 11, 10) | nowplaying, bootlogo |
| LCD data/command | BCM 9 | nowplaying, bootlogo |
| LCD backlight | BCM 13 | buttons (PWM) |
| Buttons A, B, X, Y | BCM 5, 6, 16, 24 | buttons |

Only `hive-fi-buttons` drives the backlight. Anything else you add that uses the panel
should leave BCM 13 alone.

## Boot configuration

Add to `/boot/firmware/config.txt` and reboot:

```ini
dtparam=spi=on
dtoverlay=hifiberry-dac
gpio=25=op,dh
# Optional: disable onboard audio so the DAC is the only ALSA device
dtparam=audio=off
```

Check both took effect:

```console
$ aplay -l
card 0: sndrpihifiberry [snd_rpi_hifiberry_dac], device 0: HifiBerry DAC HiFi pcm5102a-hifi-0 ...
$ ls /dev/spidev*
/dev/spidev0.0  /dev/spidev0.1
```

The driver names the PCM5102A. That's expected, because the PCM5100A is compatible.

## Permissions

The services get the `gpio` and `spi` groups through `SupplementaryGroups=`. To run the
scripts by hand, add your own account and log in again:

```bash
sudo usermod -aG gpio,spi "$USER"
```
