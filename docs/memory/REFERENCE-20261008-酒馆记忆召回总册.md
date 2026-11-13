# REFERENCE-20261008-酒馆记忆召回总册（Docs-as-Code 正本·版本锚定）

> **定位**：酒馆/桌宠/服务全记忆管线的唯一总册。改桥/改台/改管线 = **同一天更新本册版本锚行**（Docs-as-Code 家法，20261008 用户令立）。
> **版本锚**：代码正本仓 = 云机 `/root/core/bridge`（旧路径 `/root/work/cloud-config` 为 symlink，git 解析到真身），commit **`bedf9ad`**（2026-10-08；fa72a9d=首提交 109 文件+钥匙误入已全史铲除，bedf9ad=+/palace/recall 课堂直通）。查当前版：`cd /root/work/cloud-config && git log --oneline -1`。
> **1113 追记（桥 v4.5.2，云仓 `0a079b9`）**：前情提要（chat_summary）触发从 `n%20==0` 精确取模改**水位线 `n−上一段摘要 up_to ≥ 20`**——旧边沿触发被单边写回（空回复轮只写 user）翻奇偶后整代空转，st-live 现账本 171 条奇数 + chat_summary 0 点实锤（上代账本 200/220/240 三发正常=换嵌重建前偶态史）；up_to=摘要点 payload 既有字段零新状态，读侧注入零改动。另钉死：重启日志「第三绑定失败 Address already in use」=设计性自撞非故障——正典脚本 `BRIDGE_BIND=172.19.0.1` 使 bind1 已占 docker OWI 口，bind3 再绑同址必炸；ss 实证双口在岗，OWI 口由 bind1 服务，每次重启必现勿再排查。
> **1113 追记（桥 v4.5.3，云仓 `3473669`）**：角色扮演浓度两旋钮上线（管理台桥参数页热调，_P 每请求现读下一句生效）：①`rp_level` 演出浓度挡 1-4（**真步进滑条** min1 max4 step1 只停四格）——1 轻度块/2 标准=零注入默认/3 加强块/4 全沉浸块+现实锚标签【现实世界】→【此刻】（日期天气数据保留只降标签出戏度）；②`kb_topk` 台词库/场景库/单人台词参考注入条数 1-10 独立数字框（默认 3=历史现状，与挡位脱钩）。注入点=english_block 同三点位；验收=云端活体加载在役文件×活参数三态矩阵（块文本/条数/锚头全对）+lv4+kb5 全链实弹。回滚=拖回 2/填 3 免重启。
> **参数判卷**：本册数字全部实测校准过；冲突仲裁 = 本册 > 桥源码注释 > 旧 HANDOFF/OPS。

## 〇、管线全图（一屏版）

```
用户话 → 桥（unified-v4.1.5-glmfree）
  ├─ 注入区（system 顶部，用户定序）：现实锚→关怀钩子→[时光羁绊]→双人库→场景库→前情提要→记忆宫→（英语模式可叠加）
  ├─ 脑分支：ds(魔搭DS)/cli(外脑探活)/clideg(书生397B)/glmfree(4.7关思维)/glm(智谱带档位)
  ├─ 写回 A：每轮 {role,text,ts,sessionId} → 云 Qdrant chat_memory（正本）
  ├─ 写回 B：执行小票 turn_receipt JSONL（30 天后归档 receipt_expired）
  └─ 裸测[裸测]模式：写回/摘要/入宫/好感度全跳过 = 零记忆污染
派生层：
  ├─ chat_journal（往日日志，一天一条）← 21:00 diary/trigger（日记+生图入队 fail-open）
  └─ digest 链：本地 digest_sync(A源OLV+B源课堂PG) → 桥 /digest/inbox(覆盖写幂等) → 21:10 阀门 digest_valve(5.3摘要+密度评级)
备份：04:30 backup_memory.py → server-backups；周日 20:00 本地 OneDrive 异地（只增不滚）
```

## 一、召回注入：各库与实测参数（判卷级数字）

| 块 | 来源集合 | limit | 分数线 | 备注 |
|---|---|---|---|---|
| 双人库（叙事回忆） | dual_dialogues | top3 | **0.55** | v3.4.13 统一阈值；正例 0.72 / 噪声带 0.42-0.46，0.55=河中央 |
| 场景库（原著台词参考） | remram_lines | top3 | **0.55** | 失败静默空串 |
| 台词参考（solo 单人） | ram_dialogues / rem_dialogues | top3 | **0.55** | who 过滤只取本角色线 |
| 前情提要（往日日志） | chat_journal | top2 | **0.45** | JOURNAL_RECALL_MIN；0927 实测日总结余弦系统性偏低(带 0.43~0.56)，0.55 会全灭→单列低阈值 |
| 记忆宫 | 宫桥 /recall（9236） | top3 | **0.55** | 正例 0.72 / 噪声 0.42-0.46，与酒馆统一（v3.7.1） |
| 现实锚 reality_block | 无检索 | — | — | 时间戳缓存优化 v3.8.2（不再占前缀首位） |
| 关怀钩子 checkin | chat_memory 最新 user ts | — | — | 未了结事进展/天气节日顺口提 |
| 时光羁绊 | chat_memory 最早 ts | — | — | 相识第 N 天，首算后缓存账本 |
| 英语模式 english_block | 热读开关文件 | — | — | 默认关，开=en_learning 语境 |

- 嵌入：自家嵌入席向量（`_vec_for`）；**嵌入席挂=退化 FNV 伪向量**（分数会假，检索失败/低分一律静默空串，干净不带）。
- chat_memory 视野：**40 条（20 轮）**（v3.9 快速档从 12 条对齐到 40）。
- 单人模式（OWI 模型层带底稿）：摘双人库/场景库注入，底稿换传入 system。

## 二、digest 发件箱链（本地↔云摘要管线）

1. **本地 digest_sync.py**（scripts git `65c3339`，计划任务 digest-sync：开机+3min+每 6h）
   - A 源：OLV `chat_history/` 白名单 conf=`rem_localbrain-001`+`en_learning*`（mansion_sisters_001=云端自有管线，禁重复收）
   - B 源（1008 夜接入）：课堂 PG 5433 `runtime_records`（kind=chat_message、Error 裸串剔除、user→human/assistant→ai、conf=classroom；psql row_to_json 零依赖；PG 挂不阻断 A）
   - 幂等：按天覆盖写；done 清单防重；今天文件只推不删
2. **云端阀门 digest_valve.py**（cron 21:10）：5.3 摘要+密度评级，high→archive 带本地快闪标，none/low 盖戳
3. 桥端点：`/digest/inbox`（POST 覆盖写）+`/digest/done`（GET 清单）

## 三、运行态与守护

- cron：`@reboot` 20s 记忆栈（Qdrant/宫）/45s 三服务（宫桥/酒馆桥/管理台）；21:00 diary；21:10 阀门；04:30 备份；04:15 小票 30 天归档
- 桥重启唯一正道：`/root/work/cloud-config/restart-bridge-canonical.sh`（改桥前 cp 备份进 server-backups + git commit 同提交）
- 管理台：`:5679`（SSH 隧道 15679，basicAuth 凭据=/root/work/.console_auth）；公网口 5879
- 表情柜正本：容器 /app/build/expr/，本台 /api/expr 组同步（docker cp 原子生效）

## 四、今夜三修（20261008 夜战，全部已验）

1. **06l 双棒 KeyError**：scene_brain 返回无 provider 键（v4.0.0 漏改）→provider 从 glm 布尔现推+调用方人话兜底。26.8s 双棒轮转全绿。
2. **9g7 管理台整页死**：alert 字符串裸 `\n` 被 python 解码成真换行→主 script 块 SyntaxError 全灭→所有面板永远「加载中」。修=一句连写。**家法：py 内嵌 JS 的换行转义必须 `\\n` 双写（python 侧），或干脆避免。**
3. **78k 桌宠换脑**：conf.yaml→本地 CLI 8317/study，底稿 4825→1864 字（conf 在本地机，不入本仓）。
4. **xdt 课堂接宫**：桥 `/palace/recall` 直通（bedf9ad）+课堂 `lib/chat/pi/palace-recall.ts` stale-while-revalidate 注入（宪法旁，limit3/0.55 线/单条150字≤600tok）。宫桥 9236 只绑云回环=老坑再现，桥双口当跳板。实测热 0.2s/冷 ~7s（嵌入席现算），故课堂侧永不阻塞。桥日志实证：`[palace] 课堂召回 q=… 200`。

## 五、碎片档指针（细节查这里，本册不重复）

- 桥症状→解法查表：`REFERENCE-20260925-云酒馆桥完全知识册.md`
- 备份管道：记忆卡 `memory-offsite-backup-pipeline`（OneDrive 周日 20:00）
- digest 设计：OPS-20261007 追记（发件箱四步）；源 B=今夜 OPS-20261008
- 记忆宫宫桥：`REFERENCE-20260928-云上作业踩坑指南.md` + 宫桥 v2 记录
- 桌宠/课堂接线：`REFERENCE-20261008-桌宠课堂扩展点地图.md`
- 嵌入席：记忆卡 `docrag-qwen3-swap`（嵌入禁云铁令/批量重嵌禁令）

——正本册完。改管线先读我，改完写我（版本锚行+变更日志段）。
