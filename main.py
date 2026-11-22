#!/usr/bin/env python3
"""Deliver the finished Daily Atlas page for the grader.

The artwork itself is rendered ahead of time by draw.py and stored in
this folder as entry.png. At hand-in time there is nothing left to draw:
this script simply places a copy of that PNG into whichever directory
the MAKEFUN_OUTPUT_DIR environment variable points at, falling back to
/output when the variable is absent.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

FALLBACK_DIR = "/output"
ARTWORK_NAME = "entry.png"


def digest(path):
    """SHA-256 of a file, read in chunks so size never matters."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            hasher.update(block)
    return hasher.hexdigest()


def deliver():
    artwork = Path(__file__).resolve().parent / ARTWORK_NAME
    if not artwork.is_file():
        sys.exit("cannot hand in: %s not found" % artwork)

    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", FALLBACK_DIR))
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / ARTWORK_NAME

    if target.resolve() != artwork:
        shutil.copyfile(artwork, target)

    if digest(target) != digest(artwork):
        sys.exit("copy of %s does not match the original" % target)

    print("handed in %s (%d bytes)" % (target, target.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(deliver())
