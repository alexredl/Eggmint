#!/bin/bash
# Live-USB twin of uninstall.sh: removes EggMint from an installed Linux Mint while the PC is
# booted from a Mint live USB stick. Does exactly what uninstall.sh does (it runs uninstall.sh
# inside your system via chroot) - your system itself is never started.
# Works no matter whether EggMint was installed from the live stick or the running system,
# and prefers the uninstall.sh that install.sh stored in /var/eggmint on your system.
# Project home: https://github.com/alexredl/Eggmint
#
#   sudo ./uninstall-from-live.sh              # find your Mint system + EggMint status (changes nothing)
#   sudo ./uninstall-from-live.sh /dev/sda2    # uninstall from it
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=live-common.sh
. "$HERE/live-common.sh"

require_root "$@"
if [ $# -eq 0 ]; then
  find_systems
  echo
  echo "Then run:  sudo $0 /dev/XXX"
  exit 0
fi

DEV="$1"
mount_target "$DEV"
run_inside uninstall.sh
