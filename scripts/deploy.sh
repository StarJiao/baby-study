#!/usr/bin/env bash
#
# 一键分享部署脚本（GitHub Pages + jsDelivr 音频方案）
#
# 流程：
#   1. 把 src/audioConfig.ts 的 AUDIO_BASE 切到 jsDelivr（CDN 音频）
#   2. npm run build:share 生成轻量 dist（不含 mp3，约 300KB）
#   3. 把 dist 推到 GitHub 仓库的 gh-pages 分支
#   4. GitHub Pages 自动从该分支发布（需在仓库 Settings -> Pages 选择 gh-pages 分支）
#
# 使用前需准备：
#   - GitHub 仓库（公开）：math-practice-web，已用 SSH 配置好推送权限
#   - 首次部署后到仓库 Settings -> Pages 选择 deploy 分支为 gh-pages / root
#
# 用法：
#   ./scripts/deploy.sh
#
set -eo pipefail

# ============ 可配置变量 ============
GH_USER="StarJiao"
GH_REPO="math-practice-web"
AUDIO_CDN="https://cdn.jsdelivr.net/gh/StarJiao/word-audio"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIO_CONFIG_FILE="$ROOT_DIR/src/audioConfig.ts"
DIST_DIR="$ROOT_DIR/dist"
PAGES_BRANCH="gh-pages"

echo "==> [1/3] 切换音频源为 jsDelivr CDN"
if grep -q "export const AUDIO_BASE = '/audio'" "$AUDIO_CONFIG_FILE"; then
  sed -i '' "s#export const AUDIO_BASE = '/audio'#export const AUDIO_BASE = '$AUDIO_CDN'#" "$AUDIO_CONFIG_FILE"
  echo "    已切换为: $AUDIO_CDN"
else
  echo "    当前 AUDIO_BASE 已是 CDN 或格式不符，跳过切换（请检查 $AUDIO_CONFIG_FILE）"
fi

echo "==> [2/3] 构建分享版（build:share，排除本地音频）"
cd "$ROOT_DIR"
npm run build:share

echo "==> [3/3] 推送 dist 到 GitHub Pages 分支 $GH_USER/$GH_REPO@$PAGES_BRANCH"
DEPLOY_TMP="$ROOT_DIR/.deploy-tmp"
rm -rf "$DEPLOY_TMP"
mkdir -p "$DEPLOY_TMP"
cp -r "$DIST_DIR/." "$DEPLOY_TMP/"

cd "$DEPLOY_TMP"
git init -q
git config user.name "jimx"
git config user.email "mingxingjiao@qq.com"
git remote remove origin 2>/dev/null || true
git remote add origin "git@github.com:$GH_USER/$GH_REPO.git"
git add -A
git commit -q -m "deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "    无变更，跳过提交"
git push -u origin "HEAD:$PAGES_BRANCH" 2>&1 | tail -5 || {
  echo "    推送失败：请确认仓库 $GH_USER/$GH_REPO 已在 GitHub 创建且 SSH 可推送"
  exit 1
}

rm -rf "$DEPLOY_TMP"

echo ""
echo "==> 完成。访问地址：https://$GH_USER.github.io/$GH_REPO/"
echo "    首次部署后需到仓库 Settings -> Pages 选择分支 $PAGES_BRANCH、目录 /(root) 并保存。"
echo "    （GitHub Pages 启用后约 1-2 分钟生效，之后每次运行本脚本自动更新）"
