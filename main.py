#!/usr/bin/env python3
"""Hand in the finished Daily Atlas page.

draw.py rendered the artwork ahead of time and committed it beside this
file as entry.png. At hand-in there is nothing to redraw: copy that PNG
into the directory named by the MAKEFUN_OUTPUT_DIR environment variable
(falling back to /output when the variable is not set), then verify the
copy is byte-identical before reporting success.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    src = Path(__file__).resolve().parent / "entry.png"
    if not src.is_file():
        print("entry.png missing beside main.py", file=sys.stderr)
        return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    if dst.resolve() != src.resolve():
        shutil.copyfile(src, dst)
    if _sha256(dst) != _sha256(src):
        print("copied entry.png does not match the original", file=sys.stderr)
        return 1
    print("delivered %s (%d bytes)" % (dst, dst.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
