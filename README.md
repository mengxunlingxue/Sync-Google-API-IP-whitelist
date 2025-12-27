# Sync-Google-API-IP-whitelist

同步 Google API 和其他谷歌云服务的默认网域使用的 IP 地址范围

## 数据源

- `goog.json` 来源：`https://www.gstatic.com/ipranges/goog.json`
- `cloud.json` 来源：`https://www.gstatic.com/ipranges/cloud.json`

## 使用方法

### 1. 拉取最新的 IP 段（goog.json / cloud.json）

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

### 2. 解析为纯 CIDR 列表（每行一个）

把下载后的 JSON 解析为"纯 CIDR"文本（不包含其他字段）：

```bash
python3 scripts/export_goog_cidrs.py
python3 scripts/export_cloud_cidrs.py
```

默认输出到：
- `data/goog.cidr.txt` - 所有 Google 服务的 IP 范围
- `data/cloud.cidr.txt` - Google Cloud 的 IP 范围

输出到 stdout（方便管道处理）：

```bash
python3 scripts/export_goog_cidrs.py --out -
python3 scripts/export_cloud_cidrs.py --out -
```

## GitHub Actions 自动更新

已提供 workflow：`.github/workflows/update-cidrs.yml`

**触发方式**：
- **定时触发**：每小时整点 UTC 自动运行
- **手动触发**：在 GitHub 仓库的 Actions 页面点击 "Run workflow" 可随时手动运行

**更新逻辑**：
- 先通过 HEAD 请求获取远端 `ETag/Last-Modified`，并与仓库中的 `data/ipranges.remote.json` 对比
- **仅在源数据变化时**才会下载 JSON、生成 CIDR 文件并提交更新
- 若两者都未变化，则直接结束，不更新也不提交

**自动 Release**：
- 当检测到 CIDR 列表有更新并成功提交后，**会自动创建一个 GitHub Release**
- Release 包含：
  - CIDR 统计信息（goog.cidr.txt 和 cloud.cidr.txt 的数量）
  - 数据源的最后修改时间
  - 文件说明和数据源链接
- Release 标签格式：`vYYYYMMDD-HHMMSS`（例如：`v20251227-153000`）
- **Release 附件文件**：
  - `goog.json` - 原始 Google API IP 范围 JSON 文件
  - `cloud.json` - 原始 Google Cloud IP 范围 JSON 文件
  - `goog.cidr.txt` - 解析后的 Google API CIDR 列表
  - `cloud.cidr.txt` - 解析后的 Google Cloud CIDR 列表

**生成的文件**（位于 `data/` 目录）：
- `goog.cidr.txt` - 所有 Google API服务的 IP 范围（纯 CIDR 列表）
- `cloud.cidr.txt` - Google Cloud 的 IP 范围（纯 CIDR 列表）
- `ipranges.remote.json` - 远端元数据（用于变化检测）

## 文件结构

```
Sync-Google-API-IP-whitelist/
├── .github/
│   └── workflows/
│       └── update-cidrs.yml    # GitHub Actions 自动更新配置
├── scripts/
│   ├── _fetch_ipranges_common.py    # 公共工具函数
│   ├── fetch_goog_json.py            # 拉取 goog.json
│   ├── fetch_cloud_json.py          # 拉取 cloud.json
│   ├── export_goog_cidrs.py         # 导出 goog.cidr.txt
│   ├── export_cloud_cidrs.py        # 导出 cloud.cidr.txt
│   └── check_ipranges_remote.py     # 检查远端是否有更新
├── data/
│   ├── goog.json              # 原始 JSON（不跟踪到 Git）
│   ├── cloud.json            # 原始 JSON（不跟踪到 Git）
│   ├── goog.cidr.txt         # 纯 CIDR 列表（跟踪到 Git）
│   ├── cloud.cidr.txt        # 纯 CIDR 列表（跟踪到 Git）
│   └── ipranges.remote.json  # 远端元数据（跟踪到 Git）
├── .gitignore
└── README.md
```

