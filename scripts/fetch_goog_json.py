#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from _fetch_ipranges_common import cli_download_one


def main() -> int:
    return cli_download_one(
        url="https://www.gstatic.com/ipranges/goog.json",
        default_out="data/goog.json",
    )


if __name__ == "__main__":
    raise SystemExit(main())


