#!/bin/bash
# 埃姆的 AI 洞察 - 内容更新脚本
# 用法: bash update.sh "文章标题" arch|agent|industry "内容摘要" [链接]

set -e

REPO_DIR="$HOME/Desktop/36kr/ai-insight"
TODAY=$(date +%Y-%m-%d)

if [ "$1" = "deploy" ]; then
  # 仅推送部署，不添加内容
  cd "$REPO_DIR"
  git add -A
  git commit -m "update: $(date '+%Y-%m-%d %H:%M') 内容更新" 2>/dev/null || echo "无变更"
  git push origin main
  echo "✅ 已推送到 GitHub Pages"
  exit 0
fi

echo "📡 埃姆的 AI 洞察 - 今日更新准备"
echo "日期: $TODAY"
echo ""
echo "本脚本用于将新内容添加到信息站"
echo "当前站点: https://ammpnk.github.io/ai-insight/"
echo ""
echo "可用命令:"
echo "  bash update.sh deploy        # 推送最新变更到 GitHub Pages"
echo "  bash update.sh check         # 检查今天是否已更新"

if [ "$1" = "check" ]; then
  cd "$REPO_DIR"
  LAST_COMMIT=$(git log -1 --format="%ci %s" 2>/dev/null)
  echo ""
  echo "最近提交: $LAST_COMMIT"
fi
