#!/bin/bash
# Live-USB twin of install.sh: installs EggMint into an installed Linux Mint while the PC is
# booted from a Mint live USB stick. Does exactly what install.sh does (it runs install.sh
# inside your system via chroot) - your system itself is never started.
#
#   sudo ./install-from-live.sh                          # find your Mint system (changes nothing)
#   sudo ./install-from-live.sh /dev/sda2                # install into it
#   sudo ./install-from-live.sh /dev/sda2 --avatar alex  # ... and set alex's user picture
#
# Undo with ./uninstall-from-live.sh (live stick) or sudo /var/eggmint/uninstall.sh (running PC).
# Project home: https://github.com/alexredl/Eggmint
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=live-common.sh
. "$HERE/live-common.sh"

require_root "$@"
if [ $# -eq 0 ]; then
  find_systems
  echo
  echo "Then run:  sudo $0 /dev/XXX        (optionally: --avatar USERNAME)"
  exit 0
fi

DEV="$1"; shift
mount_target "$DEV"
run_inside install.sh "$@"
