#!/usr/bin/env bash
# ============================================================
# 宫桥唯一启动件（1020 用户令立）——宫桥重启只准跑本件，禁手拼 ssh 命令
# 血案史：1009（384 维拒搜）、1019（identity mismatch 拒搜四轮才破案），
# 真根=每次手拼启动命令都可能漏带三项嵌入 env。本件把 env 焊死，忘无可忘。
# 用法:
#   bash restart-palace.sh                     # 常规重启（跑云上现役文件）
#   bash restart-palace.sh --new <新文件.py>    # 部署新版本（编译→备份→inode保形覆写→重启）
# 重启后 30s 自检：日志看「[自检] 嵌入器 OK」或爆红横幅；healthz embedder 字段三态。
# ============================================================
set -e
export MEMPALACE_EMBEDDING_MODEL=openai-compat
export MEMPALACE_EMBEDDING_API_URL=http://172.19.0.1:18300/v1/embeddings
export MEMPALACE_EMBEDDING_API_MODEL=qwen3-emb
APP=/root/work/cloud-config/palace-bridge-cloud-v3.py
LOG=/root/work/logs/palace.log
BK=/root/work/server-backups

cd /root/work/cloud-config
if [ "$1" = "--new" ]; then
  NEW="$2"
  [ -f "$NEW" ] || { echo "新文件不存在: $NEW"; exit 1; }
  /root/memvenv/bin/python3 -m py_compile "$NEW" && echo NEW_COMPILE_OK
  mkdir -p "$BK"
  cp -a "$APP" "$BK/palace-bridge-cloud-v3.py.bak-$(date +%Y%m%d-%H%M%S)"
  echo "== inode before:"; ls -i "$APP"
  cat "$NEW" > "$APP"
  rm -f "$NEW"
  echo "== inode after:"; ls -i "$APP"
fi

PID=$(ss -tlnp | grep 9236 | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$PID" ]; then
  echo "== kill old pid=$PID"
  kill "$PID"
  sleep 2
fi
cd /root/work
setsid nohup /root/memvenv/bin/python3 "$APP" >> "$LOG" 2>&1 < /dev/null &
sleep 5
echo "== listener:"; ss -tlnp | grep 9236
echo "== healthz (embedder 字段 30s 后才出真值):"
curl -s -m8 http://127.0.0.1:9236/healthz
echo
echo "== 35s 后验收自检: tail -8 $LOG | grep 自检"
