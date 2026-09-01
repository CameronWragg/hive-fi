#!/usr/bin/env bash
#
# Install (or remove) the hive-fi systemd services.
#
# The unit files in this repository carry placeholders instead of hard-coded
# paths, because Raspberry Pi OS no longer ships a user called "pi" and the
# repository can live anywhere. This script fills them in.
#
#   sudo ./install.sh                 # install and start everything
#   sudo ./install.sh --user cameron  # install for a specific account
#   sudo ./install.sh --uninstall     # stop, disable and remove the units
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMD_DIR=/etc/systemd/system
SUDOERS_FILE=/etc/sudoers.d/hive-fi
VENV="$REPO_ROOT/.venv"

SERVICES=(
  "bootlogo/hive-fi-bootlogo.service"
  "buttons/hive-fi-buttons.service"
  "nowplaying/hive-fi-nowplaying.service"
)

SERVICE_USER="${SUDO_USER:-$(id -un)}"
UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) SERVICE_USER="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

if [[ $(id -u) -ne 0 ]]; then
  echo "install.sh needs root: run it with sudo." >&2
  exit 1
fi

unit_names() { for s in "${SERVICES[@]}"; do basename "$s"; done; }

if [[ $UNINSTALL -eq 1 ]]; then
  for unit in $(unit_names); do
    systemctl disable --now "$unit" 2>/dev/null || true
    rm -f "$SYSTEMD_DIR/$unit"
  done
  rm -f "$SUDOERS_FILE"
  systemctl daemon-reload
  echo "hive-fi services removed."
  exit 0
fi

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  echo "no such user: $SERVICE_USER (pass --user)" >&2
  exit 1
fi
SERVICE_GROUP="$(id -gn "$SERVICE_USER")"

# Prefer the repository virtualenv, so a pip-installed st7789 is picked up.
if [[ -x "$VENV/bin/python" ]]; then
  PYTHON="$VENV/bin/python"
else
  PYTHON="$(command -v python3)"
  echo "note: no virtualenv at $VENV, using $PYTHON"
fi

echo "installing hive-fi"
echo "  repository : $REPO_ROOT"
echo "  user       : $SERVICE_USER:$SERVICE_GROUP"
echo "  interpreter: $PYTHON"

# The buttons service runs unprivileged but has to be able to power the Pi off.
install -m 0440 /dev/stdin "$SUDOERS_FILE" <<SUDOERS
# Installed by hive-fi install.sh -- lets hive-fi-buttons power down the Pi.
$SERVICE_USER ALL=(root) NOPASSWD: /sbin/shutdown
SUDOERS
visudo -cf "$SUDOERS_FILE" >/dev/null

for service in "${SERVICES[@]}"; do
  unit="$(basename "$service")"
  sed \
    -e "s|__HIVE_FI_ROOT__|$REPO_ROOT|g" \
    -e "s|__HIVE_FI_USER__|$SERVICE_USER|g" \
    -e "s|__HIVE_FI_GROUP__|$SERVICE_GROUP|g" \
    -e "s|__HIVE_FI_PYTHON__|$PYTHON|g" \
    "$REPO_ROOT/$service" > "$SYSTEMD_DIR/$unit"
  chmod 0644 "$SYSTEMD_DIR/$unit"
  echo "  wrote $SYSTEMD_DIR/$unit"
done

systemctl daemon-reload
systemctl enable --now $(unit_names)

echo
systemctl --no-pager --lines=0 status $(unit_names) || true
