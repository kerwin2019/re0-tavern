#!/bin/sh
# 桥 canonical 重启脚本（20261007 bind 事故后立，正本在云 /root/work/cloud-config/）
# 铁律：必须带 BRIDGE_BIND=172.19.0.1（docker 自定义网桥 br-2aa1d7396b26 的网关，OWI 容器与
# diary cron 都从这条口进桥）。不带 = 桥只绑 127.0.0.1 + 10.14.14.1，OWI 下拉丢五入口、
# rem/ram/emt 说话失败、21 点日记 cron 静默失败（1007 v4.0.0 手术徒手重启漏 env 实弹血案）。
# 病历：OPS-20261007 追记六；查表：REFERENCE-20260925-云酒馆桥完全知识册 §查表。
set -e
OLD=$(ss -tlnp | grep ':18170' | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$OLD" ]; then
  echo "停旧桥 pid=$OLD"
  kill "$OLD"
  for i in 1 2 3 4 5 6 7 8; do
    sleep 1
    ss -tlnp | grep -q ':18170' || break
  done
fi
BRIDGE_BIND=172.19.0.1 setsid nohup /root/memvenv/bin/python3 /root/work/cloud-config/tavern-bridge-cloud.py >> /root/work/logs/tavern-bridge.log 2>&1 < /dev/null &
sleep 3
echo '===监听==='; ss -tlnp | grep ':18170'
echo '===healthz==='; curl -s -m 6 http://172.19.0.1:18170/healthz | head -c 200; echo
echo '完成：应见 172.19.0.1 + 10.14.14.1 双口。'
