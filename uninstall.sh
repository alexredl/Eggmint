#!/bin/bash
# Undo everything install.sh did, using what it recorded in /var/eggmint/backup/.
# Restores the original files byte-for-byte (including the boot archives, if no system
# updates were installed in between), the boot-theme setting incl. its auto/manual mode,
# and the timestamps of the touched folders. Finally removes /var/eggmint itself.
#
#   sudo /var/eggmint/uninstall.sh     # the copy install.sh left on your system
#   sudo ./uninstall.sh                # or from the project folder - same thing
#
# Live-USB twin: uninstall-from-live.sh (runs this very script inside your system via chroot).
# Project home: https://github.com/alexredl/Eggmint
set -euo pipefail

APP=/var/eggmint
BK=$APP/backup
LEGACY_BK=/var/backups/eggmint          # location used by early EggMint versions
THEME_DIR=/usr/share/plymouth/themes/eggmint
CONF=/etc/lightdm/slick-greeter.conf

say() { printf '\n\033[1;33m[EggMint]\033[0m %s\n' "$*"; }
[ "$(id -u)" -eq 0 ] || { echo "run with sudo: sudo $0"; exit 1; }

# This script deletes /var/eggmint - if it was started from there, continue from a RAM copy.
SELF="$(readlink -f "$0")"
if [ -z "${EGGMINT_FROM_RAM:-}" ] && [ "${SELF#"$APP"/}" != "$SELF" ]; then
  cp "$SELF" /run/eggmint-uninstall.sh
  EGGMINT_FROM_RAM=1 exec /bin/bash /run/eggmint-uninstall.sh "$@"
fi

if [ ! -d "$BK" ] && [ -d "$LEGACY_BK" ]; then BK=$LEGACY_BK; fi

PLYMOUTH_PREV=/usr/share/plymouth/themes/mint-logo/mint-logo.plymouth
ALT_STATUS=manual
DPKG_MD5=""
CONF_EXISTED=1
AVATAR_USER=""
if [ -f "$BK/state" ]; then
  # shellcheck disable=SC1091
  . "$BK/state"
elif [ -f "$BK/state.tmp" ]; then
  . "$BK/state.tmp"
else
  say "no backup state found - restoring Mint defaults"
fi

say "1/4 Restoring login screen settings"
if [ -f "$BK/slick-greeter.conf.orig" ]; then
  cp -a "$BK/slick-greeter.conf.orig" "$CONF"
elif [ "$CONF_EXISTED" = "0" ]; then
  rm -f "$CONF"
fi
if [ -n "$AVATAR_USER" ]; then
  ICON=/var/lib/AccountsService/icons/$AVATAR_USER
  ACC=/var/lib/AccountsService/users/$AVATAR_USER
  if [ -f "$BK/avatar-icon.orig" ]; then cp -a "$BK/avatar-icon.orig" "$ICON"; else rm -f "$ICON"; fi
  if [ -f "$BK/avatar-user.orig" ]; then cp -a "$BK/avatar-user.orig" "$ACC"; else rm -f "$ACC"; fi
fi
rm -rf /usr/share/eggmint /usr/share/themes/EggMint

say "2/4 Restoring boot splash setting ($PLYMOUTH_PREV, $ALT_STATUS mode)"
update-alternatives --remove default.plymouth "$THEME_DIR/eggmint.plymouth" 2>/dev/null || true
if [ "$ALT_STATUS" = "auto" ]; then
  update-alternatives --auto default.plymouth
elif [ -f "$PLYMOUTH_PREV" ]; then
  update-alternatives --set default.plymouth "$PLYMOUTH_PREV"
fi
rm -rf "$THEME_DIR"

say "3/4 Restoring boot archives (initramfs)"
restore_ok=1
[ -n "$DPKG_MD5" ] && [ "$(md5sum /var/lib/dpkg/status | cut -d' ' -f1)" = "$DPKG_MD5" ] || restore_ok=0
for i in /boot/initrd.img-*; do
  case "$i" in *.bak|*.old*|*.dpkg-*) continue;; esac
  [ -f "$BK/initrd/$(basename "$i")" ] || restore_ok=0
done
if [ "$restore_ok" = 1 ]; then
  echo "   no packages changed since install: putting the original files back byte-for-byte"
  for f in "$BK"/initrd/initrd.img-*; do cp -a "$f" /boot/; done
else
  echo "   system was updated since install: rebuilding the boot archives instead"
  update-initramfs -u -k all
fi

say "4/4 Removing $APP (project copy + backup) and restoring folder timestamps"
MT=""
[ -f "$BK/mtimes" ] && MT="$(cat "$BK/mtimes")"
# update-alternatives logged our two changes: put its log back as it was
[ -f "$BK/alternatives.log.orig" ] && cp -a "$BK/alternatives.log.orig" /var/log/alternatives.log
rm -rf "$APP" "$LEGACY_BK" /var/backups/eggmint.restored-*
if [ -n "$MT" ]; then
  printf '%s\n' "$MT" | while IFS='|' read -r d t; do
    if [ -e "$d" ] || [ -L "$d" ]; then touch -h -m -d "$t" "$d"; fi
  done
fi
rm -f /run/eggmint-uninstall.sh
say "Done - Mint look restored. Reboot to see it."
