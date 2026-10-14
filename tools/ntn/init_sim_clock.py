#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-CSSL-1.0

import argparse
import mmap
import os
import struct
from ntn_metadata import load_metadata

MAGIC = 0x4F414953494D434C
VERSION = 1
RECORD = struct.Struct("=QIIQ")


def main():
    parser = argparse.ArgumentParser(description="Initialize the shared sample-time clock before starting OCUDU")
    parser.add_argument("metadata", help="NTN startup metadata JSON")
    parser.add_argument("--name", default="/oai_sim_clock", help="POSIX shared-memory name")
    args = parser.parse_args()

    try:
        start_unix_ns = round(load_metadata(args.metadata)["start_unix_s"] * 1e9)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    path = "/dev/shm/" + args.name.lstrip("/")
    try:
        fd = os.open(path, os.O_RDWR)
    except FileNotFoundError:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o666)
        except FileExistsError:
            fd = os.open(path, os.O_RDWR)
    try:
        os.fchmod(fd, 0o666)
        os.ftruncate(fd, RECORD.size)
        with mmap.mmap(fd, RECORD.size) as shared:
            shared[:] = RECORD.pack(MAGIC, VERSION, 0, start_unix_ns)
            shared.flush()
    finally:
        os.close(fd)
    print(f"Initialized {args.name} at Unix {start_unix_ns / 1e9:.6f} s")


if __name__ == "__main__":
    main()
