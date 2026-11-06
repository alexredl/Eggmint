#!/bin/bash
# Fingerprint an installed system (mounted READ-ONLY) so two states can be diffed.
#   sudo tools/manifest.sh /dev/sda2 out.txt
# Records for EVERY file/dir/link on the root filesystem: path, type, size, permissions,
# owner, modification time and link target; plus an md5 checksum of every file in
# /etc, /boot, /var/lib, /var/backups and /usr/share/plymouth|themes.
set -euo pipefail
DEV="$1"; OUT="$2"; M=/mnt/eggmint-manifest
mkdir -p "$M"; mount -o ro "$DEV" "$M"
trap 'cd /; umount "$M"; rmdir "$M"' EXIT
cd "$M"
find . -xdev \( -path ./proc -o -path ./sys -o -path ./dev -o -path ./run -o -path ./tmp \) -prune -o \
  -printf '%p|%y|%s|%m|%u:%g|%T@|%l\n' | LC_ALL=C sort > "$OUT"
find ./etc ./boot ./var/lib ./var/backups ./usr/share/plymouth ./usr/share/themes -xdev -type f -print0 \
  | LC_ALL=C sort -z | xargs -0 md5sum | sed 's/^/MD5 /' >> "$OUT"
echo "$(wc -l < "$OUT") entries -> $OUT"
