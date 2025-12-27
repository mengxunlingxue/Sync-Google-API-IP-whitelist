# Sync-Google-API-IP-whitelist
同步Google API 和其他谷歌服务的默认网域使用的 IP 地址范围

## 拉取最新的 IP 段（goog.json / cloud.json）

- `goog.json` 来源：`https://www.gstatic.com/ipranges/goog.json`
- `cloud.json` 来源：`https://www.gstatic.com/ipranges/cloud.json`

在仓库根目录执行：

```bash
python3 scripts/fetch_goog_json.py
python3 scripts/fetch_cloud_json.py
```

默认会输出到：
- `data/goog.json`
- `data/cloud.json`

你也可以自定义输出路径，例如：

```bash
python3 scripts/fetch_goog_json.py --out /tmp/goog.json
python3 scripts/fetch_cloud_json.py --out /tmp/cloud.json
```

## 解析为纯 CIDR 列表（每行一个）

把下载后的 JSON 解析为“纯 CIDR”文本（不包含其他字段）：

```bash
python3 scripts/export_goog_cidrs.py
python3 scripts/export_cloud_cidrs.py
```

默认输出到：
- `goog.cidr.txt`
- `cloud.cidr.txt`

输出到 stdout（方便管道处理）：

```bash
python3 scripts/export_goog_cidrs.py --out -
python3 scripts/export_cloud_cidrs.py --out -
```

## GitHub Actions 自动更新

已提供 workflow：`.github/workflows/update-cidrs.yml`  
会定时（每天）和手动触发去拉取最新数据并更新：
- `goog.cidr.txt`
- `cloud.cidr.txt`

为减少无效下载，workflow 会先通过 HEAD 获取远端 `ETag/Last-Modified`，并与仓库中的 `ipranges.remote.json` 对比；若两者都未变化，则会直接结束，不更新也不提交。
