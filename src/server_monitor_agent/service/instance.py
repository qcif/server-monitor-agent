import platform
import socket


class Instance:
    @property
    def hostname(self) -> str:
        hostname = ""

        if not hostname:
            hostname = socket.getfqdn()

        if not hostname:
            hostname = platform.node()

        return hostname


# lsblk --ascii --pairs --noheading --paths --output NAME,TYPE,MOUNTPOINT,SERIAL
# findmnt --ascii --pairs --noheading --kernel --output TARGET,SOURCE,FSTYPE,UUID,OPTIONS,LABEL
# --source "device" --source "UUID=uuid" --source "LABEL=label" --mountpoint "${INPUT_MOUNT_POINT}"
# --json --bytes --canonicalize
# --kernel, --fstab, --mtab
# findmnt --raw --noheadings --kernel --source "${CURRENT_DEVICE_PATH}" --output UUID
# device, label, uuid (--source)
# path (--mountpoint)
#

# file -s "${CURRENT_DEVICE_PATH}"
