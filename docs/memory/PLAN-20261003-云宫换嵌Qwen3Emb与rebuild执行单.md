# PLAN-20261003-云宫换嵌Qwen3Emb与rebuild执行单（主窗执行工单）

> **执行窗**：主窗口（本窗=辅助窗，只出勘察与工单，不执行；执行中可随时回来问，咨询口见 §八）。
> **用户令**：「可以，那赶紧换上去啊」+「生成一份详细说明，我让主窗口去跑」。
> **目标**：云宫（MemPalace@SERVER_IP，wing=主人）嵌入模型从 embeddinggemma 换成自家嵌入席 Qwen3-Emb（:18300），并 rebuild 全部向量——根治「排序埋没真货+中文搜不动+池 60 只看 3%」三病。
> **回滚哲学**：每步有锚；rebuild 自带备份+原子替换+失败可重试，最坏=白跑几分钟重来，不存在坏库。

---

## 一、背景速览（为什么干）

1. 云宫现状 **1,942 抽屉**（对话实录 1,880 + 交易 33/项目调试 11/生活 8/健康 5/心理 5；taxonomy 实查 1003 凌晨）。
2. 云宫现用嵌入=embeddinggemma（300M，384 维 Matryoshka 截断）——多语言能用但排序区分度弱；**本机 MemPalace 默认 all-MiniLM-L6-v2 是英文专用训练，中文基本不可用**（上游 embedding.py 官方注释自认）。
3. 实测病：最相关条目被 MemPalace 排到 9 名开外（1002 标定，正例「分页」0.721/反例『挂单设好。走了。』0.431 是 qwen3-emb 打的）；宫桥扩池仅 max(50,limit×3)≈60 条，对 1,942=每次召回只见 3%。
4. 换模型后：MemPalace 自身排序=与台词库/酒馆召回同尺（qwen3-emb），排序可信、分数线（桥 0.55/台 0.30）直接兼容，无需重标。

## 二、源码勘察硬结论（3.10.0，主窗免重查）

- MemPalace 嵌入三模式：`minilm`(默认)/`embeddinggemma`/**`openai-compat`**（第三方 OpenAI 兼容 /v1/embeddings 端点，**官方注释点名支持 Qwen3-Embedding**）。配置入口=env `MEMPALACE_EMBEDDING_MODEL` 或 config.json `embedding_model`；openai-compat 端点三项=`embedding_api_url`/`embedding_api_model`/`embedding_api_key`（env 对应 `MEMPALACE_EMBEDDING_API_URL/_MODEL/_KEY`）。
- **换模型=换向量空间，必须跑 `mempalace repair rebuild`**（ChromaDB 集合持久化 EF 名，不匹配拒读——所以没有"绕过 rebuild 只推向量"的正规通道）。
- rebuild 机制（repair.py）：抽取批 5000→备份 **仅 chroma.sqlite3**→建 temp collection 逐批 upsert→原子替换；**upsert 批=5000 不可配，但 EF 层固定按 `_EF_API_BATCH=64` 条/HTTP 请求切**（`_EF_API_TIMEOUT=120s`）；**CLI 不暴露批参数**（`python -m mempalace.repair rebuild --palace <路径>`）。
- rebuild 有 #1208 截断守卫：抽取数 vs SQLite 真值不一致时中止（TruncationDetected）——正常库不触发；若中止，先查原因，禁盲目绕过。
- 嵌入席现状：:18300 llama-server b11146 + qwen3-emb-q8.gguf，**-c 8192 -ub 8192 -t 4**，systemd `emb-seat.service` 托管（Restart=always）。无鉴权（api_key 可不配）。
- 云上宫桥：`/root/work/cloud-config/palace-bridge-cloud-v3.py`（v3.1.2），spawn `mempalace-mcp`（stdio），现启动 env 带 `MEMPALACE_EMBEDDING_MODEL=embeddinggemma`（漏带=拒搜）。启动脚本=`/root/work/cloud-config/reboot_bridges.sh`（crontab @reboot sleep45 调用）。

## 三、施工步骤（命令级；全程 ssh 家法：kill 与 restart 拆两条，kill 段内禁出现目标真名路径）

### 步 0：备份锚 + 长度分布测量（只读，定分叉）
```bash
# 锚（服务器上）
cp /etc/systemd/system/emb-seat.service /root/work/server-backups/emb-seat.service.bak-20261003-换嵌前
cp /root/work/cloud-config/reboot_bridges.sh /root/work/server-backups/reboot_bridges.sh.bak-20261003-换嵌前
cp /root/work/cloud-config/palace-bridge-cloud-v3.py /root/work/server-backups/palace-bridge-cloud-v3.py.bak-20261003-换嵌前
```
长度分布（用 mempalace 同款 python + chromadb API，读 documents 算字符长度 p50/p95/max）：
```bash
# 先探云端 mempalace 环境（uv tool? pip?）：which mempalace-mcp; ls ~/.local/share/uv/tools 2>/dev/null; pip show mempalace 2>/dev/null
# 然后用同一 python 跑：统计 ~/.mempalace/chroma.sqlite3 对应集合 documents 长度分布
```
**分叉判据**：p95 长度×64 条/批 折算 token（中文≈1 字≈0.6-1 token）< 6000 → 可跳过步 1 直接步 2；否则必须步 1。
（按对话实录 1,880 条多为聊天气泡的先验，大概率 p95 在几百字符内，但以实测为准。）

### 步 1：嵌入席 ctx 扩容 8192→16384（防 64 条/批爆 ctx）
```bash
ssh#1:  sed -i 's/-c 8192 -ub 8192/-c 16384 -ub 4096/' /etc/systemd/system/emb-seat.service   # 先 grep 确认原串再替换
ssh#1:  systemctl daemon-reload && systemctl restart emb-seat
# 验收：curl -s http://172.19.0.1:18300/v1/embeddings -H 'Content-Type: application/json' -d '{"model":"qwen3-emb","input":["冒烟"]}' 返回 dim=1024
# 杀狗验狗：kill -9 主进程 → 8 秒内 systemd 拉起新 PID → 二次冒烟
```
回滚：cp 锚回 + daemon-reload + restart。

### 步 2：宫桥启动 env 换 openai-compat
改 `/root/work/cloud-config/reboot_bridges.sh` 里宫桥段的 `MEMPALACE_EMBEDDING_MODEL=embeddinggemma` 为：
```
MEMPALACE_EMBEDDING_MODEL=openai-compat \
MEMPALACE_EMBEDDING_API_URL=http://172.19.0.1:18300/v1/embeddings \
MEMPALACE_EMBEDDING_API_MODEL=qwen3-emb
```
（api_key 不配——嵌入席无鉴权，EF 内部 `if self._api_key` 才加头。）
**注意**：若宫桥还有其他启动路径（nohup 手启/crontab 内联），逐一同步，禁双配置漂移。

### 步 3：重启宫桥 + rebuild（服务中断窗口=此步起至 rebuild 完成，几分钟，记忆佐料暂缺、对话不断）
```bash
ssh#1(kill):  pkill -f 'mempalace-mcp' ；kill 宫桥进程（模式串拼接断词，或 ps 拿 pid kill；拆条纪律）
ssh#2(restart): bash /root/work/cloud-config/reboot_bridges.sh   # 宫桥带新 env 起，spawn 新 mempalace-mcp
# 此时 MemPalace 集合 EF 名与新模型不匹配 → /recall 会报错（预期！）
# rebuild（用与 mempalace-mcp 同一个 python，带同样三项 env）：
MEMPALACE_EMBEDDING_MODEL=openai-compat \
MEMPALACE_EMBEDDING_API_URL=http://172.19.0.1:18300/v1/embeddings \
MEMPALACE_EMBEDDING_API_MODEL=qwen3-emb \
  python -m mempalace.repair rebuild --palace /root/.mempalace
# 预计 1,942 条÷64/批≈31 请求×数秒=几分钟；进度行会打 Backing up / Extracted 1942 drawers / upsert 进度
```
失败处理：报 EmbeddingAPIError→查嵌入席（curl 18300 冒烟）→修后**直接重跑 rebuild**（自带备份，幂等重建）；报 TruncationDetected→停下回报用户，禁绕过。

### 步 4：验收四查（全绿才算完）
1. **对账**：宫桥 `/taxonomy` 仍 1,942（房间数分毫不差）。
2. **自检索冒烟**：宫桥 `/recall` query=「分页」→ 分页设计取舍条目应在列且 score 0.7 量级（qwen3-emb 标定值域）。
3. **标定对复核**：同一「分页」query，正例（分页设计取舍）vs 反例（『挂单设好。走了。』）分数分离仍在（正例显著高于反例）。
4. **真实链路**：curl 桥（`X-OpenWebUI-Task` 头零污染姿势）打总入口一句→小票里 `recalls` 的「记忆宫」源有货带分数。
另核：`mempalace repair status`（或等价）无 corrupt；嵌入席 RSS 无异常（free -m 对比重建前后）。

### 步 5：宫桥 v3.1.3 扩池跟上（本地改→部署，照桥部署家法）
`palace-bridge-cloud-v3.py` 两处小改：
- recall 扩池：`max(50, int(limit) * 3)` → `300`（同尺后 MemPalace 排序可信，300=真 top300；纯 Python 余弦 300×1024 维毫秒级）；
- 预热线程：`range(10)` → `range(30)`（300 条池×10 条/轮补齐；`_EMB_CACHE` 断轮条件不变）。
版本号 v3.1.3、启动横幅同步；部署=备份锚→scp→py_compile→kill/restart 拆条→healthz→宫桥 /recall 冒烟。
（rescore/_rescore 的 0.55 桥线/0.30 台线不动。）

## 四、风险与 Plan B

| 风险 | 对策/触发 |
|---|---|
| 64 条/批超嵌入席 ctx | 步 1 扩容兜底；步 0 长度实测先行 |
| rebuild 中途失败 | 自动备份在，原集合无损，直接重跑 |
| 嵌入席 CPU 被占，桥台词召回变慢/降级 | 中断窗口仅几分钟；挑用户不聊天时段（已获用户选时授权） |
| 云上小内存（3.7G+3.9G swap） | 分批 64+120s 超时天然限流；重建期间 `free -m` 盯一眼 |
| Plan B（仅当云上反复失败） | 拉 chroma.sqlite3 回本地→本地 mempalace（3.10.0 同版）rebuild（openai-compat 指本地嵌入端点）→整文件推回——成本高，**未获批不启动** |

## 五、账务要求（完工必做）

1. OPS 追记：`aiDocs/llama/md/OPS-20261003-压缩后净眼复审-桥台宫桥三件.md` 追记「§十 云宫换嵌 qwen3-emb」或新立 OPS-20261003b（过程+验收数据+锚）。
2. TODO 档【主管窗】加完工行（勾销本单）。
3. 知识册更新：`REFERENCE-20260925-云酒馆桥完全知识册.md` 增补「云宫嵌入=openai-compat→:18300 qwen3-emb；换模型必 rebuild；EF 名校验」条目。
4. README 🆕 登记（≤3 条）。
5. 回滚锚登记进 OPS（步 0 三锚+rebuild 自动备份路径+emb-seat 旧参数）。

## 六、给用户的行为变化预告（完工汇报用）

- 姐妹的记忆宫召回从此"搜得准+搜得到老账"（1,880 条对话实录历史地层首次可搜；0.30 人眼线压噪）。
- 分数线照旧（0.55/0.30），无重新标定成本。
- 嵌入席 ctx 扩到 16384 后，台词召回单次承载上限变大（其余行为不变）。

## 七、本窗（辅助窗）勘察依据

上游源码（3.10.0 本机安装体逐行核）：embedding.py（三模式/_EF_API_BATCH=64/_EF_API_TIMEOUT=120/EF 名校验）、repair.py（rebuild 流程/备份范围/#1208 守卫/CLI 无批参数）、GitHub releases（最新=3.10.0=本机=云上）、PyPI 元数据、第三方审计与学术分析（技术内核采信：ChromaDB 包装+小模型粗排；"刷星"指控不采信不传播）。云宫 taxonomy/本机宫 1,881 抽屉均为 1003 凌晨实查。
