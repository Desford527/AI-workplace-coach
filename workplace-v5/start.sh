#!/usr/bin/env bash
set -eu
export AHC_AUTO_OPEN=1
cd "$(dirname "$0")"
printf '正在启动 AI职场沟通训练师 v5…\n'
exec python3 -u server.py "${1:-8000}"
