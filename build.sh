#!/usr/bin/env bash
# MingLi 一键打包脚本 (Linux/macOS，仅用于交叉测试)
# 实际 exe 构建请在 Windows 上执行 build.bat
set -e
cd "$(dirname "$0")"

echo "[1/3] 清理..."
rm -rf build dist **/__pycache__

echo "[2/3] PyInstaller..."
python3 -m PyInstaller --clean --noconfirm MingLi.spec

echo "[3/3] 完成：dist/MingLi/"
ls -lh dist/
