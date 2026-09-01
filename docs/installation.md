# Installation

This walks through a fresh Raspberry Pi OS install. If you already have the OS and
shairport-sync running, skip to [Install hive-fi](#install-hive-fi).

Order matters a little: the boot configuration needs a reboot, and shairport-sync
should be working before you put a display on top of it.

## 1. Operating system

Flash **Raspberry Pi OS Bookworm or later, 64-bit** (Lite is plenty) with Raspberry Pi
Imager, and use the imager's settings to configure the hostname, your user account,
Wi-Fi and SSH before first boot.

64-bit is worth insisting on: the `gpiod` package the display library depends on
publishes `aarch64` wheels but none for 32-bit ARM, so a 32-bit install has to compile
it against `libgpiod-dev` instead.

There is no longer a default `pi` user. Whatever account you create is the one the
services will run as — `install.sh` picks it up automatically.

## 2. Enable SPI and the DAC

Add the following to `/boot/firmware/config.txt` and reboot:

```ini
dtparam=spi=on
dtoverlay=hifiberry-dac
gpio=25=op,dh
dtparam=audio=off
```

Details and verification steps are in [hardware.md](hardware.md).

## 3. shairport-sync

Build it for AirPlay 2 with metadata, and configure the pipe. This is the longest step
and has its own page: **[shairport-sync.md](shairport-sync.md)**.

Confirm it works before continuing — AirPlay something to it and check you get sound.

## 4. Install hive-fi

### Python dependencies

Raspberry Pi OS marks its system Python as externally managed (PEP 668), so `pip
install` into it is refused. Take the packaged builds of the heavy libraries from apt,
then create a virtualenv that can see them for the rest:

```bash
sudo apt install python3-venv python3-pil python3-numpy python3-spidev \
                 python3-gpiozero python3-lgpio fonts-dejavu-core
```

`fonts-dejavu-core` supplies the display font. Without a TrueType font the service
falls back to Pillow's bitmap default, which looks poor at this size.

```bash
git clone https://github.com/CameronWragg/hive-fi.git ~/hive-fi
cd ~/hive-fi
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
```

`--system-site-packages` matters: it lets the virtualenv reuse the apt-installed Pillow
and NumPy instead of compiling its own. On Bookworm the packaged NumPy (1.24) is older
than the display library asks for, so pip will fetch a newer wheel into the virtualenv —
that is expected, and it does not disturb the system copy.

### Check it before installing services

```bash
.venv/bin/python bootlogo/hive-fi-bootlogo.py
```

The logo should appear. If the panel stays dark, the backlight is off — that is BCM 13,
which nothing has driven yet; press on to the buttons service, or check
[Troubleshooting](services.md#troubleshooting).

### Install the services

```bash
sudo ./install.sh
```

This writes three units into `/etc/systemd/system`, enables and starts them:

| Unit | What it does |
| --- | --- |
| `hive-fi-bootlogo.service` | Paints the logo once at boot |
| `hive-fi-buttons.service` | Buttons and backlight |
| `hive-fi-nowplaying.service` | The shairport-sync display |

It also installs `/etc/sudoers.d/hive-fi`, which lets the unprivileged buttons service
run `/sbin/shutdown` so the X and Y buttons work.

The unit files in the repository carry `__HIVE_FI_ROOT__`, `__HIVE_FI_USER__`,
`__HIVE_FI_GROUP__` and `__HIVE_FI_PYTHON__` placeholders; `install.sh` substitutes the
repository path, the invoking account and the virtualenv interpreter. Installing for a
different account:

```bash
sudo ./install.sh --user someone-else
```

## 5. Check

```bash
systemctl status hive-fi-nowplaying
journalctl -u hive-fi-nowplaying -f
```

You should see `reading metadata from /tmp/shairport-sync-metadata`, and the logo on
the panel. Start playing something over AirPlay and the artwork should replace it.

## Updating

```bash
cd ~/hive-fi
git pull
.venv/bin/pip install -r requirements.txt
sudo ./install.sh          # re-renders the units in case they changed
```

## Removing

```bash
sudo ./install.sh --uninstall
```

This stops and disables the services, removes the unit files and the sudoers drop-in,
and leaves the repository and shairport-sync alone.
