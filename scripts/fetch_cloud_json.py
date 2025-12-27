#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _fetch_ipranges_common import fetch_json

CLOUD_URL = "https://www.gstatic.com/ipranges/cloud.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="从 Google 拉取 cloud.json")
    parser.add_argument(
        "--out",
        dest="out_path",
        default="data/cloud.json",
        help="输出文件路径（默认：data/cloud.json）",
    )
    args = parser.parse_args()

    out = Path(args.out_path).expanduser()
    if fetch_json(CLOUD_URL, out):
        print(f"OK: {CLOUD_URL} -> {out}", file=sys.stderr)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

