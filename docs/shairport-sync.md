# shairport-sync

hive-fi needs shairport-sync built with **AirPlay 2** and **metadata**. Distribution
packages have neither. Check an existing build:

```console
$ shairport-sync -V
4.3.7-... -AirPlay2-metadata-alsa-soxr-avahi-...
```

## Build

```bash
sudo apt install --no-install-recommends build-essential git autoconf automake libtool \
    libpopt-dev libconfig-dev libasound2-dev avahi-daemon libavahi-client-dev libssl-dev \
    libsoxr-dev libplist-dev libsodium-dev uuid-dev libgcrypt-dev xxd libplist-utils \
    libavutil-dev libavcodec-dev libavformat-dev
```

On Debian 13 and later, also install `systemd-dev`. Do a dry run first
(`apt install --dry-run systemd-dev`), because with backports enabled it can pull in
more than you want.

AirPlay 2 needs [NQPTP](https://github.com/mikebrady/nqptp) for clock sync:

```bash
git clone https://github.com/mikebrady/nqptp.git && cd nqptp
autoreconf -fi && ./configure --with-systemd-startup && make
sudo make install && sudo systemctl enable --now nqptp
```

Then shairport-sync. This is the upstream recipe plus `--with-metadata`, and takes a
few minutes on a Zero 2 W:

```bash
git clone https://github.com/mikebrady/shairport-sync.git && cd shairport-sync
autoreconf -fi
./configure --sysconfdir=/etc --with-alsa --with-soxr --with-avahi \
    --with-ssl=openssl --with-systemd-startup --with-airplay-2 --with-metadata
make && sudo make install
```

## Configure

In `/etc/shairport-sync.conf` (see also
[`shairport-sync.conf.example`](../nowplaying/shairport-sync.conf.example)):

```
general = { name = "hive-fi"; };
alsa = { output_device = "hw:sndrpihifiberry"; };
metadata = {
    enabled = "yes";
    include_cover_art = "yes";
    pipe_name = "/tmp/shairport-sync-metadata";
    pipe_timeout = 5000;
};
```

`include_cover_art` is separate from `enabled`. `pipe_timeout` (ms) is how long
shairport-sync waits on a blocked pipe before dropping an item, and large cover art is
the item most likely to hit it.

```bash
sudo systemctl enable --now shairport-sync
```

## How hive-fi reads the pipe

shairport-sync skips writes when no reader is attached. `hive-fi-nowplaying` opens the
FIFO read-only and reopens it whenever shairport-sync closes its end, if the FIFO is
recreated, or once it first appears. It needs only read access.

## Metadata format

```
<item><type>73736e63</type><code>70626567</code><length>0</length></item>
<item><type>636f7265</type><code>6d696e6d</code><length>11</length>
<data encoding="base64">
U29tZSBUcmFjaw==</data></item>
```

`type` and `code` are hex four-character codes. `length` is the decoded payload size.
`core` items come from the AirPlay source, and `ssnc` items from shairport-sync.

| Type | Code | Payload | Meaning |
| --- | --- | --- | --- |
| `core` | `minm` / `asar` / `asal` | UTF-8 | Title / artist / album |
| `core` | `astm` | big-endian `uint32` | Track length, ms |
| `ssnc` | `mdst` / `mden` | | Metadata bundle start / end. The display commits on `mden` |
| `ssnc` | `PICT` | JPEG or PNG | Cover art. Empty clears it |
| `ssnc` | `pbeg` / `pend` | | Session start / end. `pend` shows the logo |
| `ssnc` | `prsm` `pres` / `pfls` `paus` | | Resume / pause |
| `ssnc` | `prgr` | `start/current/end` | Progress in RTP frames at 44.1 kHz, wrapping at 2³² |
| `ssnc` | `pvol` | `airplay,volume,low,high` | Volume: 0 to −30, −144 is mute |

`prgr` only arrives on track changes and seeks. Between messages the elapsed time is
interpolated while playing. Other codes are ignored. The
[metadata reader README](https://github.com/mikebrady/shairport-sync-metadata-reader)
lists them all.

To watch the raw stream, stop the display first, since only one reader gets the data:

```bash
sudo systemctl stop hive-fi-nowplaying
shairport-sync-metadata-reader < /tmp/shairport-sync-metadata   # or plain cat
```

Session messages with no `core` items mean the source sends no metadata. No
"Picture received" lines means `include_cover_art` is off.
