# cloud/ — 云上酒馆弹药包（③ 产物，PLAN-20260922c 一期~三期）

> 造于 20260922 傍晚。SSH 到手后按本目录顺序执行即是一期开工。

## 文件清单

| 文件 | 用途 |
|---|---|
| docker-compose.yml | 五件套，profiles 分期：core=Qdrant+MemPalace（一期），full=+ST+n8n+Caddy（二三期） |
| .env.example | 密钥模板 → 复制成 .env 改掉 |
| Caddyfile | 443 反代三子域；Qdrant 靠 api-key 头 |
| mempalace/Dockerfile | MemPalace 容器（serve 旗标部署时实测） |
| migrate_qdrant.py | 快照推拉+对账（五库） |
| st_data_manifest.md | 酒馆数据目录迁移清单 |
| SECURITY.md | 安全红线操作化清单 |
| ACCEPTANCE.md | 一~三期逐条验收 |

## 上服务器后的顺序（一期）

1. 盘点：`free -h`、`df -h`、`docker -v`（无 docker 先装，见 SECURITY §0）
2. 传弹药：`scp -r cloud/ root@IP:/opt/tavern/`
3. `cd /opt/tavern && cp .env.example .env` 生成两把随机密钥（`openssl rand -hex 16`）
4. `docker compose --profile core up -d --build`
5. 灌库（本地跑）：
   `python migrate_qdrant.py push --collection dual_dialogues --src http://127.0.0.1:6333 --dst http://IP:临时直连` ——**注意**：一期若域名未就绪，临时在云防火墙放行 6333 给家里 IP（装完就关），或直接 ssh 隧道 `ssh -L 6334:localhost:6333`+Caddy 预先反代
6. MemPalace palace 迁移（当前宫殿为空，跳过亦可）：
   `tar czf palace.tgz -C "C:/Users/yourname/.config/mempalace" palace && scp palace.tgz root@IP:/opt/tavern/ && ssh root@IP "tar xzf /opt/tavern/palace.tgz -C /opt/tavern/data/mempalace"`
7. 验收：ACCEPTANCE.md 一期三条

## 二期差异（酒馆上云时）

- `docker compose --profile full up -d`
- ST 数据：按 st_data_manifest.md 从本地 data/default-user 打包传 ./data/sillytavern/
- n8n：本地导出 L4 流 JSON（公网 API GET workflow → 存文件）→ 云 n8n UI 导入 → **改端点**：Qdrant 指容器名 `http://qdrant:6333`（不用 api-key，内网直连），LLM 大脑指所选云端 API（PLAN §四方案 A）
- 本地 L4 链改指云端记忆库（一期验收项）：n8n 三个 Qdrant HTTP 节点 URL 换 `https://qdrant.域名` + 加 `api-key` 请求头（公网 API PUT nodes，已有全套脚本范式）
