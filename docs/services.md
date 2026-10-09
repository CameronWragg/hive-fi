# Services

All three units run unprivileged as the account `install.sh` was run for.

| Unit | Does |
| --- | --- |
| `hive-fi-bootlogo` | Shows the logo once at boot, before `hive-fi-nowplaying` starts |
| `hive-fi-nowplaying` | Draws what shairport-sync is playing |
| `hive-fi-buttons` | [Buttons](../README.md#buttons) and the backlight (PWM, starts at 25%) |

## hive-fi-nowplaying

Reads the [metadata pipe](shairport-sync.md#how-hive-fi-reads-the-pipe) and redraws
only when something changes: twice a second while playing, ten times a second while
text scrolls. It copes with shairport-sync starting late or restarting.

| Flag | Environment | Default | Meaning |
| --- | --- | --- | --- |
| `--pipe` | `HIVE_FI_METADATA_PIPE` | `/tmp/shairport-sync-metadata` | Must match `pipe_name` in `shairport-sync.conf` |
| `--logo` | `HIVE_FI_LOGO` | `bootlogo/hive-fi.jpeg` | Shown when idle |
| `--rotation` | `HIVE_FI_ROTATION` | `90` | 0, 90, 180 or 270 |
| `--spi-speed` | | `80000000` | SPI clock in Hz |
| `--log-level` | `HIVE_FI_LOG_LEVEL` | `INFO` | `DEBUG` logs every item |
| `--clear-on-exit` | | off | Show the logo on stop (the unit sets this) |
| `--preview PATH` | | off | Write frames to a PNG instead of the LCD |

Override with `sudo systemctl edit hive-fi-nowplaying`:

```ini
[Service]
Environment=HIVE_FI_ROTATION=270
```

`hive-fi-bootlogo` takes the same `--logo`, `--rotation` and `--spi-speed` flags.

## Troubleshooting

```bash
systemctl status hive-fi-nowplaying hive-fi-buttons hive-fi-bootlogo
journalctl -u hive-fi-nowplaying -b
```

| Symptom | Likely cause |
| --- | --- |
| Panel dark | Backlight off: `hive-fi-buttons` isn't running, or B cycled it to off |
| Logo never changes | No metadata. `shairport-sync -V` must include `metadata`, and the `metadata` section needs `enabled = "yes"` |
| No cover art | `include_cover_art` isn't `"yes"`. For large images only, raise `pipe_timeout` |
| `waiting for metadata pipe` | shairport-sync isn't running, or `pipe_name` doesn't match `--pipe` |
| `Permission denied` on `/dev/spidev0.1` | SPI isn't enabled, or the account isn't in the `spi` group |
| `BadPinFactory` | `python3-lgpio` isn't installed |
| Image rotated | Set `HIVE_FI_ROTATION` |
| X and Y do nothing | `/etc/sudoers.d/hive-fi` is missing. Re-run `sudo ./install.sh` |

To see logs live, stop the unit and run the script yourself:

```bash
sudo systemctl stop hive-fi-nowplaying
~/hive-fi/.venv/bin/python ~/hive-fi/nowplaying/hive-fi-nowplaying.py --log-level DEBUG
```
