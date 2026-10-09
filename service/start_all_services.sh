#!/bin/bash
set -e
set -x

# Must be run as sudo
if [ $EUID -ne 0 ]; then
  echo "Please run with sudo!"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Setup / ensure virtualenv exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
  TARGET_USER="${SUDO_USER:-birdofprey}"
  python3 -m venv "$PROJECT_ROOT/venv" || python3 -m venv --without-pip "$PROJECT_ROOT/venv"
  if [ ! -f "$PROJECT_ROOT/venv/bin/pip" ]; then
    curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
    "$PROJECT_ROOT/venv/bin/python" /tmp/get-pip.py
    rm -f /tmp/get-pip.py
  fi
  "$PROJECT_ROOT/venv/bin/pip" install -r "$PROJECT_ROOT/requirements.txt"
  chown -R "$TARGET_USER:$TARGET_USER" "$PROJECT_ROOT/venv"
fi

cp "$SCRIPT_DIR/bbc-anlt.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable bbc-anlt.service
systemctl restart bbc-anlt.service

