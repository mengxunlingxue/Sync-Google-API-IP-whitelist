#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _fetch_ipranges_common import extract_cidrs


def main() -> int:
    parser = argparse.ArgumentParser(description="将 cloud.json 解析为纯 CIDR 列表（每行一个）")
    parser.add_argument("--in", dest="in_path", default="data/cloud.json", help="输入 JSON 文件路径（默认：data/cloud.json）")
    parser.add_argument(
        "--out",
        dest="out_path",
        default="cloud.cidr.txt",
        help="输出文件路径；使用 '-' 表示输出到 stdout（默认：cloud.cidr.txt）",
    )
    args = parser.parse_args()

    parsed = json.loads(Path(args.in_path).expanduser().read_text(encoding="utf-8"))
    cidrs = extract_cidrs(parsed)
    content = "\n".join(cidrs)

    if args.out_path == "-":
        sys.stdout.write(content)
        return 0

    out = Path(args.out_path).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"OK: {args.in_path} -> {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


