#!/bin/bash
#
# Security Shield Installer
# 安全盾牌安装脚本
#

set -e

INSTALL_DIR="$HOME/.openclaw/skills/security-shield"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛡️ OpenClaw Security Shield 安装向导"
echo "===================================="
echo ""

# 检查 OpenClaw
if [[ ! -d "$HOME/.openclaw" ]]; then
    echo "❌ 未找到 OpenClaw 目录"
    echo "   请先安装 OpenClaw"
    exit 1
fi

# 创建目录
echo "📁 创建安装目录..."
mkdir -p "$INSTALL_DIR"

# 复制文件
echo "📦 复制文件..."
cp -r "$REPO_DIR/_meta.json" "$INSTALL_DIR/"
cp -r "$REPO_DIR/SKILL.md" "$INSTALL_DIR/"
cp -r "$REPO_DIR/src" "$INSTALL_DIR/"
cp -r "$REPO_DIR/scripts" "$INSTALL_DIR/"

# 设置权限
chmod +x "$INSTALL_DIR/scripts/security-shield.sh"
chmod +x "$INSTALL_DIR/src/security_core.py"
chmod +x "$INSTALL_DIR/src/watchdog.py"

# 创建符号链接（可选）
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
if [[ ! -L "$BIN_DIR/security-shield" ]]; then
    ln -s "$INSTALL_DIR/scripts/security-shield.sh" "$BIN_DIR/security-shield"
    echo "✅ 已创建命令链接: $BIN_DIR/security-shield"
fi

# 检查依赖
echo ""
echo "🔍 检查依赖..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "⚠️  Python3 未安装，部分功能可能不可用"
fi

# 检查 OpenClaw 版本
echo "✅ OpenClaw: 已安装"

echo ""
echo "===================================="
echo "🎉 安装完成！"
echo ""
echo "使用方法:"
echo "  1. 直接运行: $INSTALL_DIR/scripts/security-shield.sh status"
echo "  2. 或通过符号链接: security-shield status"
echo "  3. 或重启 OpenClaw 后使用 skill 命令"
echo ""
echo "快速开始:"
echo "  security-shield status      # 查看安全状态"
echo "  security-shield protect    # 一键保护"
echo "  security-shield clean safe # 清理浏览器数据"
echo ""
