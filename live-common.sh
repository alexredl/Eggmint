#!/bin/bash
# Shared helpers for install-from-live.sh and uninstall-from-live.sh (not run directly).
# Finds / mounts the installed Mint system, enters it with chroot and runs install.sh or
# uninstall.sh INSIDE it. The package is staged in the live session's RAM (/run) - nothing
# temporary is ever written to your disk.

MNT=/mnt/eggmint-target
STAGE=/run/eggmint-pkg

say() { printf '\n\033[1;36m[EggMint-live]\033[0m %s\n' "$*"; }
die() { printf '\n\033[1;31m[EggMint-live] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

require_root() { [ "$(id -u)" -eq 0 ] || die "run with sudo: sudo $0 $*"; }

# list partitions + every installed Mint system with its users, boot splash and EggMint status
find_systems() {
  say "Partitions on this computer:"
  lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT
  say "Looking for installed Linux Mint systems (read-only check)..."
  local found=0 probe=/mnt/eggmint-probe name fstype dev root ver users
  mkdir -p "$probe"
  while read -r name fstype; do
    case "$fstype" in ext4|ext3|btrfs|xfs) ;; *) continue;; esac
    dev="/dev/$name"
    findmnt -rn -S "$dev" >/dev/null && continue
    if mount -o ro "$dev" "$probe" 2>/dev/null; then
      for root in "$probe" "$probe/@"; do
        grep -qi linuxmint "$root/etc/os-release" 2>/dev/null || continue
        ver=$(sed -n 's/^PRETTY_NAME="\(.*\)"/\1/p' "$root/etc/os-release")
        echo "  -> $dev   ($ver)"; found=1
        users=$(awk -F: '$3 >= 1000 && $3 < 60000 {printf "%s (%s)  ", $1, $5}' "$root/etc/passwd" | sed 's/,,,//g')
        echo "       users:       ${users:-none}"
        if [ -L "$root/etc/alternatives/default.plymouth" ]; then
          echo "       boot splash: $(basename "$(readlink "$root/etc/alternatives/default.plymouth")")"
        else
          echo "       boot splash: Plymouth not installed - EggMint cannot be installed here"
        fi
        local st=""
        for st in "$root/var/eggmint/backup/state" "$root/var/backups/eggmint/state" ""; do
          [ -f "$st" ] && break
        done
        if [ -n "$st" ]; then
          echo "       EggMint:     installed ($(sed -n 's/^DATE=//p' "$st"))"
        else
          echo "       EggMint:     not installed"
        fi
      done
      umount "$probe"
    fi
  done < <(lsblk -rno NAME,FSTYPE)
  rmdir "$probe" 2>/dev/null || true
  [ "$found" = 1 ] || echo "  none found. Encrypted disk? Unlock it first, see README."
}

cleanup() {
  set +e
  cd /
  rm -rf "$STAGE"
  for m in run sys proc dev/pts dev boot; do mountpoint -q "$MNT/$m" && umount -l "$MNT/$m"; done
  mountpoint -q "$MNT" && umount -l "$MNT"
  rmdir "$MNT" 2>/dev/null
}

# mount_target /dev/XXX : mount the system (+ separate /boot) and bind /dev /proc /sys /run
mount_target() {
  local dev="$1" bootspec bootdev
  [ -b "$dev" ] || die "$dev is not a block device. Run without arguments to list partitions."
  if findmnt -rn -S "$dev" >/dev/null; then
    die "$dev is already mounted at $(findmnt -rn -S "$dev" -o TARGET | head -1). Unmount it first (e.g. eject it in the file manager)."
  fi
  grep -q "boot=casper" /proc/cmdline || say "warning: this doesn't look like a live session - continuing anyway"
  trap cleanup EXIT

  say "Mounting $dev"
  mkdir -p "$MNT"
  mount "$dev" "$MNT"
  if [ ! -f "$MNT/etc/os-release" ] && [ -f "$MNT/@/etc/os-release" ]; then
    umount "$MNT"; mount -o subvol=@ "$dev" "$MNT"   # btrfs with @ subvolume
  fi
  grep -qi linuxmint "$MNT/etc/os-release" 2>/dev/null || die "$dev does not contain a Linux Mint system."
  say "Found: $(sed -n 's/^PRETTY_NAME="\(.*\)"/\1/p' "$MNT/etc/os-release")"

  if ! ls "$MNT"/boot/initrd.img-* >/dev/null 2>&1; then
    bootspec=$(awk '$1 !~ /^#/ && $2 == "/boot" {print $1}' "$MNT/etc/fstab" | head -1)
    [ -n "$bootspec" ] || die "no /boot/initrd.img-* and no separate /boot in fstab - unexpected layout."
    case "$bootspec" in
      UUID=*) bootdev=$(blkid -U "${bootspec#UUID=}") ;;
      *) bootdev="$bootspec" ;;
    esac
    say "Mounting separate /boot partition $bootdev"
    mount "$bootdev" "$MNT/boot"
    ls "$MNT"/boot/initrd.img-* >/dev/null 2>&1 || die "still no initrd in /boot"
  fi

  for m in dev dev/pts proc sys run; do mount --bind "/$m" "$MNT/$m"; done
}

# run_inside script.sh [args] : stage the package in RAM and run the script inside the system.
# For uninstall.sh the copy that install.sh left in /var/eggmint is preferred (it belongs to
# exactly the version that was installed); otherwise the one from this folder is used.
run_inside() {
  local script="$1"; shift
  rm -rf "$STAGE"; mkdir -p "$STAGE"
  if [ "$script" = uninstall.sh ] && [ -f "$MNT/var/eggmint/uninstall.sh" ]; then
    say "Using the uninstall.sh stored on your system (/var/eggmint), staged in RAM ($STAGE)"
    cp "$MNT/var/eggmint/uninstall.sh" "$STAGE/"
  else
    say "Staging package in RAM ($STAGE) and running $script inside the system"
    cp -r "$HERE"/. "$STAGE"/
  fi
  chmod +x "$STAGE"/*.sh
  chroot "$MNT" /bin/bash "$STAGE/$script" "$@"
  sync
  say "All done. Unmounting. You can now remove the USB stick and reboot into your system."
}
