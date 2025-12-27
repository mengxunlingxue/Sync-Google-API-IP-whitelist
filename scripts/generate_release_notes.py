#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def count_cidrs(file_path: Path) -> int:
    """统计 CIDR 文件的行数"""
    if not file_path.exists():
        return 0
    try:
        return len([line for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()])
    except Exception:
        return 0


def get_metadata_info(file_path: Path) -> dict | None:
    """获取元数据信息"""
    if not file_path.exists():
        return None
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    goog_cidr_path = Path("data/goog.cidr.txt")
    cloud_cidr_path = Path("data/cloud.cidr.txt")
    metadata_path = Path("data/ipranges.remote.json")

    goog_count = count_cidrs(goog_cidr_path)
    cloud_count = count_cidrs(cloud_cidr_path)
    metadata = get_metadata_info(metadata_path)

    # 生成 release notes
    notes = []
    notes.append("## 📦 Google IP CIDR 列表更新\n")
    notes.append(f"**更新时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    notes.append("### 📊 CIDR 统计\n")
    notes.append(f"- `goog.cidr.txt`: **{goog_count}** 个 CIDR（Google API 服务）\n")
    notes.append(f"- `cloud.cidr.txt`: **{cloud_count}** 个 CIDR（Google Cloud）\n")

    if metadata:
        notes.append("\n### 🔄 数据源信息\n")
        if metadata.get("goog", {}).get("last_modified"):
            notes.append(f"- goog.json 最后修改: `{metadata['goog']['last_modified']}`\n")
        if metadata.get("cloud", {}).get("last_modified"):
            notes.append(f"- cloud.json 最后修改: `{metadata['cloud']['last_modified']}`\n")

    notes.append("\n### 📁 文件说明\n")
    notes.append("- `data/goog.cidr.txt` - 所有 Google API 服务的 IP 范围（纯 CIDR 列表）\n")
    notes.append("- `data/cloud.cidr.txt` - Google Cloud 的 IP 范围（纯 CIDR 列表）\n")
    notes.append("\n### 🔗 数据源\n")
    notes.append("- goog.json: https://www.gstatic.com/ipranges/goog.json\n")
    notes.append("- cloud.json: https://www.gstatic.com/ipranges/cloud.json\n")

    release_body = "".join(notes)
    print(release_body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

