#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

GOOG_URL = "https://www.gstatic.com/ipranges/goog.json"
CLOUD_URL = "https://www.gstatic.com/ipranges/cloud.json"


def get_remote_metadata(url: str) -> dict | None:
    """通过 HEAD 请求获取远端文件的 ETag 和 Last-Modified"""
    try:
        req = Request(url, method="HEAD")
        req.add_header("User-Agent", "Mozilla/5.0")
        with urlopen(req, timeout=30) as resp:
            headers = resp.headers
            return {
                "etag": headers.get("ETag"),
                "last_modified": headers.get("Last-Modified"),
            }
    except (HTTPError, OSError) as e:
        print(f"ERROR: Failed to check {url}: {e}", file=sys.stderr)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="检查远端 IP 范围文件是否有更新")
    parser.add_argument(
        "--out",
        dest="out_path",
        default="data/ipranges.remote.json",
        help="输出元数据文件路径（默认：data/ipranges.remote.json）",
    )
    args = parser.parse_args()

    goog_meta = get_remote_metadata(GOOG_URL)
    cloud_meta = get_remote_metadata(CLOUD_URL)

    if not goog_meta or not cloud_meta:
        return 1

    remote_data = {
        "goog": {"url": GOOG_URL, **goog_meta},
        "cloud": {"url": CLOUD_URL, **cloud_meta},
    }

    out_path = Path(args.out_path).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 检查是否有变化
    changed = True
    if out_path.exists():
        try:
            local_data = json.loads(out_path.read_text(encoding="utf-8"))
            if (
                local_data.get("goog", {}).get("etag") == goog_meta.get("etag")
                and local_data.get("goog", {}).get("last_modified") == goog_meta.get("last_modified")
                and local_data.get("cloud", {}).get("etag") == cloud_meta.get("etag")
                and local_data.get("cloud", {}).get("last_modified") == cloud_meta.get("last_modified")
            ):
                changed = False
        except (json.JSONDecodeError, KeyError):
            pass

    out_path.write_text(json.dumps(remote_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # 输出到 stdout（workflow 会重定向到 GITHUB_OUTPUT）
    print(f"changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

