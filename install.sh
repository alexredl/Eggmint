#!/bin/bash
# EggMint theme installer for Linux Mint 21.x (Cinnamon/MATE/Xfce, LightDM + slick-greeter)
#
#   sudo ./install.sh                 # boot splash + login screen
#   sudo ./install.sh --avatar USER   # also set the pixel Eierbaer as USER's user picture
#
# Only ADDS files and changes two settings. A copy of this whole project is kept in
# /var/eggmint/ and everything it touches is recorded and backed up to /var/eggmint/backup/
# first, so you can always undo it with:  sudo /var/eggmint/uninstall.sh
# (that puts the system back exactly as it was and removes /var/eggmint itself).
# Live-USB twin: install-from-live.sh (runs this very script inside your system via chroot).
# Project home: https://github.com/alexredl/Eggmint
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
APP=/var/eggmint
BK=$APP/backup
THEME_DIR=/usr/share/plymouth/themes/eggmint
SHARE=/usr/share/eggmint
GTK_THEME=/usr/share/themes/EggMint
CONF=/etc/lightdm/slick-greeter.conf
# folders/links whose modification time changes when we add/remove things (restored on uninstall)
MTIME_DIRS="/boot /etc/lightdm /usr/share /usr/share/plymouth/themes /usr/share/themes \
/var /var/lib/dpkg/alternatives /var/lib/AccountsService/icons /var/lib/AccountsService/users \
/etc/alternatives /etc/alternatives/default.plymouth /usr/share/plymouth/themes/default.plymouth \
/var/lib/dpkg/alternatives/default.plymouth /var/tmp /var/log"
# log file that update-alternatives appends to (restored on uninstall)
ALT_LOG=/var/log/alternatives.log

AVATAR_USER=""
if [ "${1:-}" = "--avatar" ]; then AVATAR_USER="${2:?usage: --avatar USERNAME}"; fi

say() { printf '\n\033[1;33m[EggMint]\033[0m %s\n' "$*"; }
die() { printf '\n\033[1;31m[EggMint] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run with sudo: sudo $0"
grep -qi "linuxmint" /etc/os-release || die "this is not Linux Mint - stopping."
for f in plymouth/eggmint/eggmint.plymouth plymouth/eggmint/eggmint.script \
         plymouth/eggmint/portrait.png plymouth/eggmint/stache-24-0.png \
         greeter/background.png greeter/logo.png greeter/avatar.png \
         greeter/gtk-3.0/gtk.css greeter/index.theme; do
  [ -f "$HERE/$f" ] || die "missing $f - copy the whole eggmint-theme folder."
done
[ -e /etc/alternatives/default.plymouth ] || die "no default.plymouth alternative found - unexpected system layout, nothing changed."
ls /boot/initrd.img-* >/dev/null 2>&1 || die "no /boot/initrd.img-* found (is /boot a separate partition that isn't mounted?) - nothing changed."
if [ -e "$APP" ] || [ -e /var/backups/eggmint/state ]; then
  die "EggMint is already installed (found $APP). Uninstall first: sudo $APP/uninstall.sh (running PC) or ./uninstall-from-live.sh (live stick)."
fi
if [ -n "$AVATAR_USER" ]; then id "$AVATAR_USER" >/dev/null 2>&1 || die "user $AVATAR_USER does not exist"; fi

say "1/5 Recording current state and backing up to $BK"
MTIMES="$(for d in $MTIME_DIRS; do if [ -e "$d" ] || [ -L "$d" ]; then stat -c '%n|%y' "$d"; fi; done)"
mkdir -p "$BK"
chmod 755 "$APP"; chmod 700 "$BK"
printf '%s\n' "$MTIMES" > "$BK/mtimes"
[ -f "$ALT_LOG" ] && cp -a "$ALT_LOG" "$BK/alternatives.log.orig"
{
  echo "PLYMOUTH_PREV=$(readlink -f /etc/alternatives/default.plymouth)"
  echo "ALT_STATUS=$(update-alternatives --query default.plymouth | sed -n 's/^Status: //p')"
  echo "DPKG_MD5=$(md5sum /var/lib/dpkg/status | cut -d' ' -f1)"
  if [ -f "$CONF" ]; then echo "CONF_EXISTED=1"; else echo "CONF_EXISTED=0"; fi
  echo "AVATAR_USER=$AVATAR_USER"
  echo "DATE=$(date -Is)"
} > "$BK/state.tmp"
[ -f "$CONF" ] && cp -a "$CONF" "$BK/slick-greeter.conf.orig"
mkdir -p "$BK/initrd"
for i in /boot/initrd.img-*; do
  case "$i" in *.bak|*.old*|*.dpkg-*) continue;; esac
  cp -a "$i" "$BK/initrd/"
done
# keep a copy of the whole project next to the backup, so uninstall.sh is always at hand
tar -C "$HERE" --exclude=./.git --exclude=./backup -cf - . | tar -C "$APP" --no-same-owner -xf -
chmod -R go-w "$APP"; chmod 755 "$APP"/*.sh

say "2/5 Installing boot splash theme to $THEME_DIR"
mkdir -p "$THEME_DIR"
cp "$HERE"/plymouth/eggmint/* "$THEME_DIR/"
chmod 644 "$THEME_DIR"/*

say "3/5 Selecting EggMint as boot splash and rebuilding initramfs (takes ~1 min)"
update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth \
  "$THEME_DIR/eggmint.plymouth" 100
update-alternatives --set default.plymouth "$THEME_DIR/eggmint.plymouth"
update-initramfs -u -k all

say "4/5 Installing login screen look"
mkdir -p "$SHARE" "$GTK_THEME"
cp "$HERE"/greeter/background.png "$HERE"/greeter/logo.png "$HERE"/greeter/avatar.png "$SHARE/"
cp -r "$HERE"/greeter/gtk-3.0 "$GTK_THEME/"
cp "$HERE"/greeter/index.theme "$GTK_THEME/"
chmod -R a+rX "$SHARE" "$GTK_THEME"

[ -f "$CONF" ] || printf '[Greeter]\n' > "$CONF"
grep -q '^\[Greeter\]' "$CONF" || sed -i '1i [Greeter]' "$CONF"
set_key() {  # set_key key value  (replace if present, else add under [Greeter])
  if grep -q "^$1=" "$CONF"; then
    sed -i "s|^$1=.*|$1=$2|" "$CONF"
  else
    sed -i "/^\[Greeter\]/a $1=$2" "$CONF"
  fi
}
set_key background "$SHARE/background.png"
set_key background-color "#5494DB"
set_key draw-user-backgrounds false
set_key draw-grid false
set_key logo "$SHARE/logo.png"
set_key theme-name EggMint
set_key font-name "DejaVu Sans Mono Bold 11"

if [ -n "$AVATAR_USER" ]; then
  say "   setting user picture for $AVATAR_USER"
  ACC=/var/lib/AccountsService/users/$AVATAR_USER
  ICON=/var/lib/AccountsService/icons/$AVATAR_USER
  mkdir -p /var/lib/AccountsService/icons /var/lib/AccountsService/users
  [ -f "$ICON" ] && cp -a "$ICON" "$BK/avatar-icon.orig"
  [ -f "$ACC" ] && cp -a "$ACC" "$BK/avatar-user.orig"
  cp "$SHARE/avatar.png" "$ICON"; chmod 644 "$ICON"
  if [ -f "$ACC" ] && grep -q '^Icon=' "$ACC"; then
    sed -i "s|^Icon=.*|Icon=$ICON|" "$ACC"
  elif [ -f "$ACC" ]; then
    grep -q '^\[User\]' "$ACC" || printf '[User]\n' >> "$ACC"
    sed -i "/^\[User\]/a Icon=$ICON" "$ACC"
  else
    printf '[User]\nIcon=%s\n' "$ICON" > "$ACC"
  fi
fi

mv "$BK/state.tmp" "$BK/state"
say "5/5 Done! Reboot to see it.
          To undo:  sudo $APP/uninstall.sh   (running PC; a copy of the project lives in $APP)
               or:  sudo ./uninstall-from-live.sh /dev/XXX   (from a live stick)"
