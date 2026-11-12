# SECURITY — 云服务器加固操作单（红线来自 PLAN-20260922c §五）

## §0 基础（无 docker 时）

- Ubuntu/Debian：`curl -fsSL https://get.docker.com | sh`（国内慢用阿里源脚本）
- 2G swap：`fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile` + 写入 fstab
- SSH：`PasswordAuthentication no`（先确认密钥能登录再改）+ 禁 root 直登（建普通用户 + sudo）

## §1 防火墙（只开 443 + 80[ACME] + 22[改密钥登录后可换端口]）

```bash
ufw default deny incoming && ufw allow OpenSSH && ufw allow 80,443/tcp && ufw enable
```
云厂商安全面板同步只放 22/80/443。**6333/5678/8000 一律不对外。**

## §2 服务层

- Qdrant：API key 已在 compose；容器不发布宿主端口，仅内网 + Caddy 反代（api-key 头认证）
- n8n：owner 账号首次访问时设置强密码；N8N_ENCRYPTION_KEY 必须进 .env
- ST：Caddy basicAuth 双层门（bcrypt hash，不用明文）
- MemPalace：仅容器内网；对外如需 HTTP MCP，先过 Caddy + key 再说

## §3 备份（对齐四备份纪律）

- cron 每日 `tar` 四卷：`data/sillytavern data/n8n data/mempalace` + Qdrant 快照目录 → 本地拉回
- Qdrant 五库快照：`migrate_qdrant.py pull --collection <各库> --src 云端 --dst 本地`（回本地跑）
- 家目录外一律只读纪律同样适用于云：改配置先 cp 一份 .bak-日期

## §4 收尾自检

- [ ] `ufw status` 只有 22/80/443
- [ ] `ss -tlnp` 无 6333/5678/8000 监听公网
- [ ] 无 key curl 云 Qdrant → 401
- [ ] `docker compose ps` 全部 healthy/restarting=0
