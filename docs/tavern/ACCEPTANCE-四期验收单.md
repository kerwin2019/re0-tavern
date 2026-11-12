# ACCEPTANCE — 分期验收单（PLAN-20260922c §六）

## 一期·记忆中枢上云（做完这期，本地聊天体验不变、云上记忆在长）

- [ ] `docker compose --profile core ps` 两件 Up
- [ ] migrate_qdrant.py 五库逐库 push 后对账全 OK（346/1147/2970/0/0 起步）
- [ ] 本地 L4 链 6333 端点切到云端（含 api-key 头）→ 聊一轮 → 云端 chat_memory count +2
- [ ] 本地冒烟：检索召回内容与切云前一致（同问题同命中）
- [ ] 回滚演练：本地端点切回 127.0.0.1:6333 一条命令可用

## 二期·酒馆上云（大脑=云端 API 方案 A）

- [ ] --profile full 五件 Up，容器重启一轮数据仍在（卷挂载生效）
- [ ] 云 ST 导入角色卡/设置后，界面选双人卡能连上大脑
- [ ] 完整聊一轮：文字回复 + 云端 chat_memory 增长 + 检索标签出现在链路里
- [ ] n8n owner 密码已设，N8N_ENCRYPTION_KEY 持久

## 三期·手机端

- [ ] 外网手机浏览器 https://st.域名 basicAuth 后完整聊天
- [ ] ufw 只有 22/80/443；无 key 访问 qdrant.域名 → 401
- [ ] 备份 cron 在跑，本地能拉回云卷包

## 四期·穿透与语音（远期，暂不动）

- [ ] frp/Tailscale 选型定案后补验收项
