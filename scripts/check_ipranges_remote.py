#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _head(url: str, timeout_s: float) -> dict[str, str]:
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        # HTTPMessage: case-insensitive lookup, but we'll normalize keys
        headers = {k.lower(): v for k, v in resp.headers.items()}
    return headers


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stable_dump(obj: Any) -> str:
    # 保持字段顺序可读；不引入随机字段，避免无意义提交
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="通过 HEAD 获取 ETag/Last-Modified，判断 ipranges 是否更新")
    parser.add_argument("--timeout", type=float, default=15.0, help="HEAD 超时秒数（默认：15）")
    parser.add_argument(
        "--out",
        default="ipranges.remote.json",
        help="保存远端元数据的文件路径（默认：ipranges.remote.json）",
    )
    args = parser.parse_args()

    urls = {
        "goog": "https://www.gstatic.com/ipranges/goog.json",
        "cloud": "https://www.gstatic.com/ipranges/cloud.json",
    }

    prev_path = Path(args.out).expanduser()
    prev = _load_json(prev_path)
    prev = prev if isinstance(prev, dict) else {}

    current: dict[str, Any] = {}
    for name, url in urls.items():
        try:
            headers = _head(url, timeout_s=args.timeout)
            etag = headers.get("etag")
            last_modified = headers.get("last-modified")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            # 拿不到元数据时，保守起见认为“有变化”，以免漏更
            print(f"warn: HEAD failed for {url}: {e}", file=sys.stderr)
            etag = None
            last_modified = None

        current[name] = {
            "url": url,
            "etag": etag,
            "last_modified": last_modified,
        }

    changed = current != prev

    # 写入最新元数据（若无变化则内容相同，不会导致 git diff）
    prev_path.write_text(_stable_dump(current), encoding="utf-8")

    # 给 GitHub Actions 使用：将此行重定向到 $GITHUB_OUTPUT
    print(f"changed={'true' if changed else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


