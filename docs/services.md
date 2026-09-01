# Services

Three systemd units, all running unprivileged as the account `install.sh` was run for,
with `SupplementaryGroups=gpio spi` for access to `/dev/gpiochip*` and `/dev/spidev*`.

| Unit | Type | Owns |
| --- | --- | --- |
| `hive-fi-bootlogo.service` | one-shot | The panel, briefly, at boot |
| `hive-fi-buttons.service` | long-running | Buttons (BCM 5, 6, 16, 24) and the backlight (BCM 13) |
| `hive-fi-nowplaying.service` | long-running | The panel (SPI0 CE1, BCM 9) |

`hive-fi-bootlogo` is ordered `Before=hive-fi-nowplaying.service` so the two do not race
for the panel at boot. It is optional — `hive-fi-nowplaying` shows the same logo when
nothing is playing — but it gets an image up sooner, before Python has finished
importing Pillow.

---

## hive-fi-nowplaying

Reads the shairport-sync metadata pipe and redraws the panel. See
[shairport-sync.md](shairport-sync.md#the-metadata-format) for the wire format.

It is deliberately tolerant of shairport-sync: it starts before the pipe exists, holds
the pipe open across play sessions, follows the FIFO if it is recreated, and keeps
running through a `systemctl restart shairport-sync`. It never touches the backlight.

### Options

Every option has an environment variable equivalent, so `systemctl edit
hive-fi-nowplaying` can override them without editing the unit.

| Flag | Environment | Default | Meaning |
| --- | --- | --- | --- |
| `--pipe` | `HIVE_FI_METADATA_PIPE` | `/tmp/shairport-sync-metadata` | Metadata pipe to read. Must match `pipe_name` in `shairport-sync.conf` |
| `--logo` | `HIVE_FI_LOGO` | `bootlogo/hive-fi.jpeg` | Image shown when nothing is playing |
| `--rotation` | `HIVE_FI_ROTATION` | `90` | Panel rotation: 0, 90, 180 or 270 |
| `--spi-speed` | — | `80000000` | SPI clock in Hz |
| `--log-level` | `HIVE_FI_LOG_LEVEL` | `INFO` | `DEBUG` logs every parsed item |
| `--clear-on-exit` | — | off | Restore the idle logo when the service stops. The unit sets this |
| `--preview PATH` | — | off | Write frames to a PNG instead of the LCD |

Example override:

```bash
sudo systemctl edit hive-fi-nowplaying
```

```ini
[Service]
Environment=HIVE_FI_ROTATION=270
Environment=HIVE_FI_LOG_LEVEL=DEBUG
```

### Redraw behaviour

The service is idle-cheap: it blocks on `select()` for up to a second at a time and only
pushes a frame when something changed. While playing it redraws twice a second to move
the progress bar, and ten times a second only while a line of text is long enough to
need scrolling. Each frame is a full 240 × 240 SPI transfer, which is the expensive
part on a Pi Zero 2 W, so the cadence is kept modest on purpose.

---

## hive-fi-buttons

| Button | GPIO | Action |
| --- | --- | --- |
| A | BCM 5 | Unassigned — logs the press |
| B | BCM 6 | Cycle the backlight: 50% → 75% → 100% → off → 25% |
| X | BCM 16 | Shut down |
| Y | BCM 24 | Reboot |

Buttons are active low with a 200 ms debounce. The backlight is PWM on BCM 13, starting
at 25%.

Shutdown and reboot run `sudo -n /sbin/shutdown`, which needs the sudoers drop-in
`install.sh` writes to `/etc/sudoers.d/hive-fi`. Without it the press is logged as a
failure and nothing happens.

---

## hive-fi-bootlogo

Draws `bootlogo/hive-fi.jpeg` and exits. `RemainAfterExit=yes`, so systemd reports it as
active rather than dead. `--logo`, `--rotation` and `--spi-speed` work the same way as
in `hive-fi-nowplaying`.

The ST7789 holds its framebuffer without a host attached, so the image stays up until
something draws over it.

---

## Troubleshooting

Start here:

```bash
systemctl status hive-fi-nowplaying hive-fi-buttons hive-fi-bootlogo
journalctl -u hive-fi-nowplaying -b --no-pager
```

| Symptom | Likely cause |
| --- | --- |
| Panel completely dark | The backlight (BCM 13) is off. `hive-fi-buttons` is not running, or the B button cycled it to 0% |
| Logo shows, never changes | No metadata reaching the pipe. Check `shairport-sync -V` contains `metadata`, and that `enabled = "yes"` is set |
| Text appears, no album art | `include_cover_art` is not `"yes"`, or the source is not sending art |
| `waiting for metadata pipe … to appear` | shairport-sync has not created the FIFO. Check it is running and that `pipe_name` matches `--pipe` |
| `Permission denied` on `/dev/spidev0.1` | The service account is not in the `spi` group, or `dtparam=spi=on` is missing |
| `BadPinFactory: Unable to load any default pin factory` | `python3-lgpio` is not installed, so gpiozero has no usable pin factory |
| Image rotated or mirrored | Set `--rotation` / `HIVE_FI_ROTATION` |
| Buttons X and Y do nothing | `/etc/sudoers.d/hive-fi` is missing. Re-run `sudo ./install.sh` |
| Display and buttons fight over the backlight | Something other than `hive-fi-buttons` is driving BCM 13. Only one process may |
| Cover art missing on large images | shairport-sync gave up on a blocked pipe. Raise `pipe_timeout` |

To watch the metadata stream directly, stop the display service first — see
[Watching the pipe by hand](shairport-sync.md#watching-the-pipe-by-hand).

### Running a service by hand

Stop the unit, then run the script from the virtualenv so you can see the logs live:

```bash
sudo systemctl stop hive-fi-nowplaying
~/hive-fi/.venv/bin/python ~/hive-fi/nowplaying/hive-fi-nowplaying.py --log-level DEBUG
```

`DEBUG` reports undecodable payloads and unparsable progress and volume strings, which
is usually enough to tell a source problem from a display problem.
