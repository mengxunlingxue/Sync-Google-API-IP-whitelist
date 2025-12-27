#!/bin/bash
# 创建 GitHub Release 的辅助脚本

set -euo pipefail

REPO="mengxunlingxue/Sync-Google-API-IP-whitelist"
TAG_NAME="${1:-v$(date +'%Y%m%d-%H%M%S')}"
RELEASE_NAME="Google IP CIDR 更新 - $(date +'%Y-%m-%d %H:%M:%S') UTC"

# 检查是否有 token
if [ -z "${GITHUB_TOKEN:-}" ]; then
    echo "错误: 请先设置 GITHUB_TOKEN 环境变量"
    echo ""
    echo "使用方法:"
    echo "  export GITHUB_TOKEN=\"your_token_here\""
    echo "  $0 [tag_name]"
    echo ""
    echo "或者手动在 GitHub 网页创建:"
    echo "  https://github.com/$REPO/releases/new"
    exit 1
fi

# 生成 release notes
if [ -f "release_notes.txt" ]; then
    RELEASE_BODY=$(cat release_notes.txt | python3 -c 'import sys, json; print(json.dumps(sys.stdin.read()))')
else
    echo "警告: release_notes.txt 不存在，使用空内容"
    RELEASE_BODY='""'
fi

# 检查文件是否存在
FILES=("data/goog.json" "data/cloud.json" "data/goog.cidr.txt" "data/cloud.cidr.txt")
MISSING_FILES=()

for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "警告: 以下文件不存在:"
    printf '  - %s\n' "${MISSING_FILES[@]}"
    echo ""
fi

# 创建 release
echo "创建 Release: $TAG_NAME"
echo "名称: $RELEASE_NAME"
echo ""

RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/releases" \
  -d "{
    \"tag_name\": \"$TAG_NAME\",
    \"name\": \"$RELEASE_NAME\",
    \"body\": $RELEASE_BODY,
    \"draft\": false,
    \"prerelease\": false
  }")

# 提取 upload_url
UPLOAD_URL=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('upload_url', '').split('{')[0])" 2>/dev/null || echo "")

if [ -z "$UPLOAD_URL" ]; then
    echo "错误: 创建 release 失败"
    echo "$RESPONSE" | python3 -m json.tool
    exit 1
fi

echo "$RESPONSE" | python3 -m json.tool
echo ""

# 上传文件
echo "上传文件..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        FILENAME=$(basename "$file")
        echo "  上传: $file -> $FILENAME"
        curl -s -X POST \
          -H "Authorization: token $GITHUB_TOKEN" \
          -H "Content-Type: application/octet-stream" \
          --data-binary "@$file" \
          "$UPLOAD_URL?name=$FILENAME" > /dev/null
    fi
done

echo ""
echo "Release 创建成功！"
echo "查看: https://github.com/$REPO/releases/tag/$TAG_NAME"

