#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(text, encoding="utf-8")
    os.replace(tmp_path, path)


def fetch_json(
    url: str,
    *,
    timeout_s: float = 30.0,
    retries: int = 3,
    backoff_s: float = 1.0,
) -> tuple[str, Any]:
    """
    返回 (raw_text, parsed_json)，失败会 raise 最后一次异常。
    """
    headers = {
        "User-Agent": "Sync-Google-API-IP-whitelist/1.0 (+fetch ipranges)",
        "Accept": "application/json",
    }

    last_err: BaseException | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read().decode("utf-8")
            parsed = json.loads(raw)
            return raw, parsed
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_s * attempt)
                continue
            raise

    assert last_err is not None
    raise last_err


def cli_download_one(*, url: str, default_out: str) -> int:
    parser = argparse.ArgumentParser(description=f"下载 {url} 到本地 JSON 文件（并做 JSON 校验）")
    parser.add_argument(
        "--out",
        default=default_out,
        help=f"输出文件路径（默认：{default_out}）",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="请求超时秒数（默认：30）")
    parser.add_argument("--retries", type=int, default=3, help="重试次数（默认：3）")
    args = parser.parse_args()

    out_path = Path(args.out).expanduser().resolve()
    _, parsed = fetch_json(url, timeout_s=args.timeout, retries=args.retries)

    # 规范化输出：确保 utf-8，无 BOM，且以换行结尾，便于 diff/审计
    pretty = json.dumps(parsed, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    _atomic_write_text(out_path, pretty)

    print(f"OK: {url} -> {out_path}")
    return 0


def extract_cidrs(parsed: Any) -> list[str]:
    """
    从 ipranges JSON 中提取 CIDR 列表（仅返回 'x.x.x.x/yy' 或 'xxxx::/zz' 形式），
    按原始顺序去重。
    """
    prefixes = parsed.get("prefixes", []) if isinstance(parsed, dict) else []
    out: list[str] = []
    seen: set[str] = set()
    for item in prefixes:
        if not isinstance(item, dict):
            continue
        cidr = item.get("ipv4Prefix") or item.get("ipv6Prefix")
        if not isinstance(cidr, str):
            continue
        if cidr in seen:
            continue
        seen.add(cidr)
        out.append(cidr)
    return out


if __name__ == "__main__":
    print("This is a shared module. Use scripts/fetch_goog_json.py or scripts/fetch_cloud_json.py", file=sys.stderr)
    sys.exit(2)


