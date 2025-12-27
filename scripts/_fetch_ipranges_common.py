#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def fetch_json(url: str, out_path: Path) -> bool:
    """从 URL 下载 JSON 文件并保存到指定路径"""
    try:
        req = Request(url)
        req.add_header("User-Agent", "Mozilla/5.0")
        with urlopen(req, timeout=30) as resp:
            data = resp.read()
            # 验证是否为有效 JSON
            json.loads(data.decode("utf-8"))
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(data)
            return True
    except (HTTPError, OSError) as e:
        print(f"ERROR: Failed to fetch {url}: {e}", file=sys.stderr)
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from {url}: {e}", file=sys.stderr)
        return False


def extract_cidrs(data: dict) -> list[str]:
    """从 JSON 数据中提取所有 CIDR（IPv4 和 IPv6）"""
    cidrs = []
    for prefix in data.get("prefixes", []):
        if "ipv4Prefix" in prefix:
            cidrs.append(prefix["ipv4Prefix"])
        if "ipv6Prefix" in prefix:
            cidrs.append(prefix["ipv6Prefix"])
    return sorted(cidrs)

