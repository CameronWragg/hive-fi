# Installation

## 1. Prepare the Pi

1. Flash **Raspberry Pi OS Bookworm or later, 64-bit**. Lite is fine. Set the user,
   Wi-Fi and SSH in Raspberry Pi Imager. The services run as whichever account you
   create.
2. Set up the [boot configuration](hardware.md#boot-configuration).
3. Build and configure [shairport-sync](shairport-sync.md). Check you get sound over
   AirPlay before going on.

Use 64-bit: `gpiod` has no 32-bit ARM wheels and would have to be compiled.

## 2. Python dependencies

The system Python refuses `pip install` (PEP 668). Take the heavy libraries from apt
and use a virtualenv that can see them:

```bash
sudo apt install python3-venv python3-pil python3-numpy python3-spidev \
                 python3-gpiozero python3-lgpio fonts-dejavu-core
git clone https://github.com/CameronWragg/hive-fi.git ~/hive-fi
cd ~/hive-fi
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
```

pip may fetch a newer NumPy into the virtualenv, which is fine. Without
`fonts-dejavu-core` the display falls back to a small bitmap font.

To check the panel, run `.venv/bin/python bootlogo/hive-fi-bootlogo.py`. If it stays
dark, that's the backlight: it only comes on once the buttons service is running.

## 3. Services

```bash
sudo ./install.sh                    # or: --user someone-else
```

This fills in the `__HIVE_FI_*__` placeholders in the [unit files](services.md),
installs and starts them, and adds `/etc/sudoers.d/hive-fi` so the buttons can shut
down and reboot.

Check it:

```bash
journalctl -u hive-fi-nowplaying -f
```

Look for `reading metadata from /tmp/shairport-sync-metadata`. Play something and the
cover art should replace the logo.

## Updating and removing

```bash
git pull && .venv/bin/pip install -r requirements.txt && sudo ./install.sh
sudo ./install.sh --uninstall        # removes the units and sudoers file only
```
