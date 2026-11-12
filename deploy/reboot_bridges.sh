#!/bin/bash
# 三服务开机拉起（2026-09-26 用户点头加装；手工同款姿势，细则=aiDocs llama/md/OPS-20260926 §八）
# 顺序无所谓先后，靠 sleep 错峰；任一失败不影响其它（日志各自落账）
cd /root/work || exit 1
MEMPALACE_EMBEDDING_MODEL=openai-compat MEMPALACE_EMBEDDING_API_URL=http://172.19.0.1:18300/v1/embeddings MEMPALACE_EMBEDDING_API_MODEL=qwen3-emb setsid nohup /root/memvenv/bin/python3 /root/work/cloud-config/palace-bridge-cloud-v3.py >> /root/work/logs/palace.log 2>&1 < /dev/null &
sleep 3
BRIDGE_BIND=172.19.0.1 setsid nohup /root/memvenv/bin/python3 /root/work/cloud-config/tavern-bridge-cloud.py >> /root/work/logs/tavern-bridge.log 2>&1 < /dev/null &
sleep 3
setsid nohup /root/memvenv/bin/python3 /root/work/cloud-config/tavern-console.py >> /root/work/logs/console.log 2>&1 < /dev/null &
echo "$(date '+%F %T') reboot_bridges.sh fired (palace/bridge/console)"
