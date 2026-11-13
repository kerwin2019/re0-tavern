# -*- coding: utf-8 -*-
"""酒馆管理台 v1.0 :5679（0926 统一管线一期施工件，PLAN-20260926 §4）。
v2.4.0（1024·想法账本页，用户令「开工吧」；调研+DeepSeek 会诊定案）：新页签「🧠 想法账本」——
  浏览 ideas_ledger（桥 v4.4.5+ 写入的 decision journal）：左栏类目筛选（全部/未分类/六类，带计数）+
  版本链卡片（现行在上、点开折叠看每版结论/理由/类目/来源，旧版灰标）+ 单条改类目（v2.4.0 唯一写口：
  Qdrant payload 即时改+jsonl 留 retag 审计事件，「其他」可手选）+ 语义/关键词双模搜索（语义=嵌入席
  向量查询 0.5 宽阈值取20，命中映射回链头，命中旧版标注）+ 导出 MD/JSONL（只读台不锁数据）；
  端点：GET /api/ideas/list|search|export，POST /api/ideas/retag。数据零新表零迁移，分类词表=
  ideas_categories.json（显示名可改不动历史）。
v2.3.7（1018）：接力入口停用同步（用户令）——「人设底稿」页摘「接力·拉姆稿/接力·蕾姆稿」两页签（后端 /api/persona 路由保留，复活=还原两行 li）；脑绑定页与帮助文案同步改「已停用」。桥侧 DISABLED_BRAINS 同步上线（v4.1.9）。
v2.3.6（1011）：记忆库倒序（用户令：最新在前，免得翻到底才看到新货）——/api/memories 翻页方向掉头：每请求先拉纯 id 升序清单（不带 payload，一次滚动）再从尾倒着走，游标=倒序清单位置；q 过滤/首屏 total/前端懒加载零改动，九集合统一生效；翻页间隙被删的点跳过不报错。CSV 导出维持升序全量不动。\nv2.3.5（1011）：①「日志」页签下架（用户令：入口归一，chat_journal 只留记忆库下拉一个口）——导航项/pane/编辑弹窗/五个 jr* 函数/初始加载五件全摘，后端 /api/journal/* 路由保留（补账/改删接口无损，桥侧自动补账不受影响）；②表情柜加中文注解（love - 爱意 式，28 情绪 GoEmotions 标准集全配，格子/组面板标题/大图标题三处，未登记情绪回退裸名）。
v2.3.4（1011）：记忆库批量删除——表格加勾选列+表头全选（限已载入行）+「🗑 删除选中(N)」钮（0 选中置灰，切集合自动清空）；/api/delete 兼容旧单删 {'id':..} 并新增 {'ids':[..]} 批量（上限 1000/批），逐条先抄后撕留底、一条留底失败整批中止，Qdrant points/delete 原生一次多删；返回 deleted 计数+missing 清单。
v2.3.3（1011）：记忆库/导出下拉集合名加中文注解——chat_journal - 往日日志…九集合对照写死前端 loadColls，未登记新集合回退裸名；选项补显式 value 属性（中文进 option 文本后 .value 必须锚回纯集合名，防查询/导出/删改打错集合）。两处下拉（记忆库 #coll、导出 #csv-coll）同源同享。
v2.3.2（1011）：记忆库全貌滚动改版——①表容器限高 70vh 内滚+粘性表头+回顶钮（>400 显/<200 隐迟滞）+Home/End 键（补齐全台限高范式漏网的第五处）；②/api/memories 游标分页（Qdrant scroll offset 透传，200/批、触底 300px 预取、容器未满自动补批），n=200 硬帽废除=全量可滚到底；③total 真实命中数（q 空=Qdrant count 秒出，q 非空=全扫计数），「命中 200 条」谎报治好→「已载入 X / 共 Y 条」；④暗色 color-scheme 修正。CSV 导出全量路径不动。
v2.3.1（1011）：运行小票「非法路径」修复——/root/work/logs 自 1004 起为软链(→/root/data/logs)，_receipt_detail 把回传路径 realpath 解析后与未解析前缀比对必失配=点任何记录必报错；校验基准改 realpath(/root/work/logs)+os.sep（同 /api/review/img 既有正确范式），防穿越能力不变。
v2.2.0（1008 午·自拍线验收配套）：新增「目审台」独立页 /review（+/api/review/img 图片直出，realpath 防穿越）——读 /root/work/review/<批次>/ 网格展示，鉴权同主面板，零 JS（9g7 换行血案免疫）；用途=用户手机远程目审 AI 自产物。
v2.1.1（1008 深夜）：PROV_LABEL+glmfree（桌宠/服务新档展示）；柜 v2.3 回嫁——am9 深夜部署曾用无柜副本覆盖掉生图窗柜管理页（1008 透明底上云验收第④检揪出），donor=exprgroup_20261007/tavern-console_v23.py 六块回嫁（常量/函数/GET/POST/导航徽章/JS）。
v2.1.2（1009）：柜首开死修——六块回嫁漏调度器点火：点页签只切 pane 不调 exprLoad，首开永远「加载中」（Edge 实证：点击后 /api/expr/list 零请求）；调度器补 if(a.dataset.t==='expr')exprLoad(EXPR_WHO)。
v2.1.3（1009）：记忆宫搜索结果可点开——palRender 有 drawer_id 即绑 palOpen（无 id 保持只读）；配宫桥 v3.1.4 recall 透传 id。branch 窗用户令，ZCode 内置浏览器点验。
v2.1.4（1009）：夜间模式卡片文字隐形修复——theme-dark .card 补 color:#d6deeb（背景翻了文字没翻，card p-2 结构无 card-body 层漏网；内置浏览器实测底字同色实锤）。
v2.2.1（1009）：脑绑定档位下放开到 DeepSeek——ds 存 ds_effort(low/high/max,默认high=上游默认)，ds 时控件启用+标签改 DeepSeek 档位；配桥 v4.1.6 reasoning_effort 三档（官方文档查证）。
v2.2.2（1009）：examAdd 缺两收尾括号修复（v1.8/v1.9 上线时落下）——其后 Token 区+桥参数区整段被吞进函数作用域=tokLoad/bpLoad 全局未定义：Token 页刷新零请求、好感度当前值永空。补回括号两段函数回到顶层（内置浏览器 census 确诊）。
v2.3.0（1009）：本机资源总闸——新页签「资源总闸」+/api/gate GET/POST 薄代理（EasyTier→本机 proxy v4.3 /gate，4s 超时，本机不在线=ok:false）：语音=硬闸（关→/v1/audio/speech 秒 503 不拉引擎）生图=软闸（image-gen skill 开工必查 gpu_gate.json）；防生图/聊天互挤 8G 显存（用户令）。
v2.1.0（1007 深夜·am9 结案配套）：脑绑定/钥匙/状态三块对齐桥 v4.1.x 新架构。
  - 脑绑定：值域扩 cli（本地8317国外脑）/local；写侧只动 tavern 槽（v4.0.0 场景结构防整档覆写），
    get 返回展平视图+scenes 全量；选项带计费属性（GLM=按量付费/DS=魔搭按次/local·cli=免费）。
  - 钥匙页：智谱槽退役标注（桥不再读 .zhipu_key_cloud）、新增 cli 槽（/root/work/cliproxy/.api_key）、
    OWI#6 同步废（#6 现指云CLI）；_owi_key_write 防腐蚀=顺带把 base_urls[6] 钉到云CLI。
  - 新卡「云CLI 与本地脑状态」：余额红绿灯按钮（桥 /balance/ping，max_tokens=1 实弹）+
    手动探活按钮（桥 /brain/probe，2s×2路）+ CLI 官方管理页跳转；页面零自动轮询（按次计费渠道禁探活）。
v2.0.0（1006 凌晨·用户令「桥参数上面板」）：新增「桥参数」签——桥 v3.9.0 起热读
  bridge_params.json（每请求现读，改完下一句生效）：情感组（好感度当前分直调【双重确认+留底】/每日
  封顶/回忆杀概率+转考题概率+开关）记忆组（视野条数/摘要周期）回复组（温度）；全部带越界保护+
  改前留底 bridge_params_trash/+一键恢复默认。召回阈值类（0.55/0.45 特例）不上面板保持代码定标。
v1.9.0（1005 深夜·token 计量页）：新增「Token」签——桥 v3.8.1 起小票自带 usage，本签聚合近 7 天
  小票画日耗柱状图（Chart.js 本地 static）+今日按模式分布（酒馆/桌宠/晨报/考官谁在烧一眼可见）。
v1.8.0（1005 深夜·夜战令「把token跑干」）：新增「学习」签——题池管理（列表/加题/重置掌握度）+统计卡，与桥 v3.8.0 考官引擎同源同账；晨报 08:00 已接入 /exam/next 随口带一题。
v1.7.0（1005 晚·用户令「配钥匙放管理页」）：新增「API 钥匙」签——智谱云/.modelscope/OWI-智谱三个钥匙位
  自助换发：输入框默认打码，👁 小眼睛开关查看明文（明文本就住服务器文件 chmod600，本台仅自己用）；
  保存=旧钥匙就地 .bak-<时间戳> 留底+原子写+chmod600；智谱/魔搭保存后自动重启桥（约5秒断连，
  桥启动时读钥匙故必须重启）；智谱可勾选「同步到 OWI 网页模型」（停-改-起 OWI 约50秒）——
  治 1005 遗漏面（OWI 库旧钥匙 401 案，OPS-20261005d §七）。
v1.6.1（1004 ②批·用户令「白天和夜间模式」）：夜/昼主题切换——导航栏 🌙 按钮，偏好存
  localStorage（console-theme），进页先应用防白闪。服务器 tabler.min.css 为旧版（dark 规则
  仅零星），故手搓 body.theme-dark 覆盖块给台内实际用到的组件上色（card/table/badge/btn/
  form/nav/弹窗 #fff 内联/错误行 #fff5f5 内联），不依赖框架版本。
v1.6.0（1004 ②批·分支窗令）：新增「定时任务」签——root crontab 可视化：标题/备注/计划/命令
  + 启停开关 + 改计划时间。备注以 #@ 注释行存在 crontab 本体（跟任务走，不依赖台版本）；
  开关=行首 #DISABLED# 注释；改时间=替换计划字段；命令本体不做网页编辑（防误操作）。
  每次改动前自动备份 server-backups/crontab.bak-<时间戳>，crontab 安装失败自动回滚。
v1.5.0（1004 ①桶施工，用户令「把①②的干了吧」；方案定稿=HANDOFF-20261003b §四.A2）：
  双日志合一——「审计」+「执行小票」两签合并为「运行小票」一签（默认落点）：顶部三统计卡
  （轮次/各脑分布/平均耗时）数据源从 mentor-chain.log 改 turn_receipt（随所选日翻动）；
  小票表加「首字ms」列（吃桥 v3.7.4 埋点）；bridge.log 人读流水原样保留；
  mentor-chain.log 照写不停（一周观察期后再停，/api/audit 端点暂留可查）。
只读为主 + 两把钥匙：删除（前端二次确认）与 ST 存档导出（跑现成脚本）。
绑定 127.0.0.1，走 SSH 隧道访问；basicAuth 凭据只住 /root/work/.console_auth（chmod600，不入 aiDocs）。
依赖：/root/memvenv（httpx）。内存账 ~15MB 级。
API：
  GET  /healthz
  GET  /api/audit?n=200          审计尾 N 行+今日统计（v1.5.0 起 UI 不再用；端点暂留）
  GET  /api/bridge?n=100         桥运行日志尾 N 行（纯文本）
  GET  /api/collections          Qdrant 集合清单
  GET  /api/memories?coll=&q=&n= scroll 采样 + 关键词过滤（只读）
  POST /api/delete {coll,id}     删单点（用户亲手点）
  GET  /api/export/csv?coll=     流式 CSV（utf-8-sig，Excel 友好）
  POST /api/export/chats         跑 export_chats_20260925.py 后列产物
  GET  /api/journal/list         往日日志（chat_journal，一条=一天，按 ts 倒序）
  POST /api/journal/update       {date,text} 改日志正文（向量同步重嵌，召回不断档）
  POST /api/journal/delete       {date} 删一天日志（派生数据低风险直接删，chat_memory 才是正本）
  POST /api/journal/generate     {date} 手动补账/重生成（v1.4.2 起本台自带浓缩，不再代理桥）
  POST /api/brain/get            读当前脑绑定（v1.4.3 总闸两控件）
  POST /api/brain/binding        {provider,glm_effort} 切总闸（桥每请求现读，下一句生效）
  POST /api/persona/list         人设底稿五槽全文（duet/ram/rem/duet_ram/duet_rem；emilia 锁）
  POST /api/persona/save         {slot,text} 保存底稿（先抄后撕 persona_trash/，下一句生效）
  POST /api/cron/list            {} 定时任务列表（v1.6.0：items=idx/enabled/sched/cmd/title/note；解析 #@ 备注注释行）
  POST /api/cron/toggle          {idx,fp} 启停开关（行首 #DISABLED# 注释切换；fp=命令指纹防并发错位）
  POST /api/cron/settime         {idx,sched,fp} 改计划表达式（5 段 cron 或 @reboot/@daily/@hourly/@weekly/@monthly）
  POST /api/keys/list            {} 三钥匙位指纹（v1.7.0：slot/name/tail4/exists；不带明文）
  POST /api/keys/reveal          {slot} 取明文（小眼睛点开时回填；明文只住服务器）
  POST /api/keys/save            {slot,key,sync_owi} 保存（旧钥匙就地留底+原子写+chmod600；智谱/魔搭自动重启桥；智谱可勾选同步 OWI）
  POST /api/receipt/list         {date?} 执行小票按天列表（v1.4.5：dates+date+rows；v1.5.0 增 stats=所选日统计，源=turn_receipt）
  POST /api/receipt/detail       {file,line} 单轮小票全文（注入原文/召回分数/耗时/写回）
"""
import base64
from urllib.parse import unquote
import csv
import io
import json
import os
import re
import subprocess
import time
import http.server
import threading

import httpx

PORT = 5679
AUTH_FILE = "/root/work/.console_auth"
LOG_DIR = "/root/work/logs"
AUDIT_LOG = os.path.join(LOG_DIR, "mentor-chain.log")
BRIDGE_LOG = os.path.join(LOG_DIR, "tavern-bridge.log")
CONSOLE_DIR = "/root/work/cloud-config/console"
QDRANT = "http://127.0.0.1:6333"
EXPORT_SCRIPT = "/root/work/cloud-config/export_chats_20260925.py"
# v1.1 新增：记忆库 改/增 两路（0926 夜，用户问"修改可以吗？新增呢"）
# v1.2 新增：云端记忆宫代理（宫桥 v3 :9236 管理口）
# v1.3 新增：日志签（chat_journal 可检索日志，PLAN-20260927；浓缩逻辑住桥，本台管账面+代理补账）
BRIDGE = "http://172.19.0.1:18170"
PALACE = "http://127.0.0.1:9236"
_pq = httpx.Client(timeout=90)
ZEMB = "http://172.19.0.1:18300/v1/embeddings"
try:
    ZKEY = open("/root/work/.zhipu_key_cloud", encoding="utf-8").read().strip()
except Exception:
    ZKEY = ""


# ==== v2.1.0 表情柜（1007 夜战·用户令「后台管理页面新增删除替换」）====
# 三层数据流：本地正本 /root/work/expr_assets/<who>/<emo>.png（真身，容器重建不丢）
#   ⇄ 容器生效副本 open-webui-slim:/app/build/expr/<who>/<emo>.png（桥取图路径，容器层易失）
# 上传/删除先备份到 /root/work/expr_assets/_backup/<ts>/ 再动（先抄后撕家法）；
# 「同步到容器」=全量 docker cp（expr_into_owi.sh 失传后的内置恢复）；
# 「从容器补缺」=容器有正本无的格子拉回（只补缺不覆盖，防旧图翻新）。
EXPR_ASSETS = "/root/work/expr_assets"
EXPR_BAK = os.path.join(EXPR_ASSETS, "_backup")
REVIEW_ROOT = "/root/work/review"  # v2.2.0 目审台图源（批次=子目录，scp 推图即出）
EXPR_CTR = "open-webui-slim"
EXPR_CTR_DIR = "/app/build/expr"
EXPR_EMOTIONS = ("admiration amusement anger annoyance approval caring confusion curiosity desire "
                 "disappointment disapproval disgust embarrassment excitement fear gratitude grief joy "
                 "love nervousness neutral optimism pride realization relief remorse sadness surprise").split()
LOG_DIR = "/root/work/logs"
AUDIT_LOG = os.path.join(LOG_DIR, "mentor-chain.log")
BRIDGE_LOG = os.path.join(LOG_DIR, "tavern-bridge.log")
CONSOLE_DIR = "/root/work/cloud-config/console"
QDRANT = "http://127.0.0.1:6333"
EXPORT_SCRIPT = "/root/work/cloud-config/export_chats_20260925.py"
# v1.1 新增：记忆库 改/增 两路（0926 夜，用户问"修改可以吗？新增呢"）
# v1.2 新增：云端记忆宫代理（宫桥 v3 :9236 管理口）
# v1.3 新增：日志签（chat_journal 可检索日志，PLAN-20260927；浓缩逻辑住桥，本台管账面+代理补账）
BRIDGE = "http://172.19.0.1:18170"
PALACE = "http://127.0.0.1:9236"
_pq = httpx.Client(timeout=90)
ZEMB = "http://172.19.0.1:18300/v1/embeddings"
try:
    ZKEY = open("/root/work/.zhipu_key_cloud", encoding="utf-8").read().strip()
except Exception:
    ZKEY = ""



def _vec_for(text):
    """自家嵌入席向量；失败退化 FNV 伪向量（与桥同款）。"""
    try:
        e = httpx.post(ZEMB, timeout=10,
                       headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                       json={"model": "qwen3-emb", "input": [text]})
        v = e.json()["data"][0]["embedding"]
        if v and len(v) == 1024:
            return v
    except Exception:
        pass
    seed = 0x811c9dc5
    for ch in (text or "empty"):
        seed = ((seed ^ ord(ch)) * 0x01000193) & 0xFFFFFFFF
    v = []
    for _ in range(1024):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        v.append(((seed >> 7) & 0xFF) / 255.0 + 0.001)
    return v


def _point_full(coll, pid):
    """取单点 payload（Qdrant retrieve；result 可能是 list 也可能包一层 dict，都兼容）。"""
    r = _q.post(f"{QDRANT}/collections/{coll}/points", json={"ids": [pid], "with_payload": True})
    r.raise_for_status()
    res = r.json().get("result")
    pts = res.get("points") if isinstance(res, dict) else res
    pts = pts or []
    return (pts[0].get("payload") or {}) if pts else {}


def _palace(method, path, body=None, params=None):
    """宫桥 v3 代理；宫桥自己管 MCP 通道与删前备份。"""
    try:
        if method == "GET":
            r = _pq.get(PALACE + path, params={k: v for k, v in (params or {}).items() if v}, timeout=90)
        else:
            r = _pq.post(PALACE + path, json=body or {}, timeout=90)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"error": str(e)[:250]}
# ==== v2.3.0 本机资源总闸（用户令：管理台手动开关本地语音/生图，防互挤显存）====
GATE_URL = "http://10.14.14.2:9233/gate"
_gq = httpx.Client(timeout=4)
def _gate(method, body=None):
    """本机 proxy v4.3 /gate 代理；本机不在线=ok:false（前端红字，不抛错）。"""
    try:
        if method == "GET":
            r = _gq.get(GATE_URL)
        else:
            r = _gq.post(GATE_URL, json=body or {})
        d = r.json()
        d["ok"] = True
        return d
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
EXPORT_DST = "/root/work/exports/st_exports"

# ==== v1.4 入库工作台（用户令：勾选入库独立成签，桥零改动）====
ZHIPU_URL = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"
INGEST_SCRIBE = (
    "你是「记忆宫书记员」。记忆宫是主人的人生长期记忆库（MemPalace），只收『多年后仍值得知道』的事实、决定、领悟、"
    "心法、承诺、计划——不收寒暄、情绪流水账、临时玩笑。\n"
    "【本次任务】阅读下面的对话记录，把值得长期保存的内容提炼为记忆宫条目；没有值得保存的就输出 []。\n"
    "【房间分类（五选一）】交易 / 健康 / 心理 / 生活 / 项目调试\n"
    "【输出格式】只输出 JSON 数组，禁止输出其他文字：\n"
    '[{"room":"交易","title":"一句话标题（含日期更佳）","text":"完整条目正文，150-600字，数字/承诺/决定保留原话细节"}]\n'
    "【纪律】1) 禁止编造，对话里没有的不许写；2) 数字、日期、承诺原样保留；3) 一条只说一件事；4) 最多 4 条，宁缺毋滥。"
)


def _trash_dump(coll, pid, pl):
    """v1.4.1 先抄后撕：删除前把点全文存服务器回收站目录。成功返回路径，失败返回 None（调用方须中止删除）。"""
    tdir = f"/root/work/server-backups/console_trash/{time.strftime('%Y%m%d')}"
    try:
        os.makedirs(tdir, exist_ok=True)
        safe = re.sub(r"[^0-9A-Za-z_-]", "_", f"{coll}_{pid}")[:80]
        fp = os.path.join(tdir, safe + ".json")
        with open(fp, "w", encoding="utf-8") as tf:
            json.dump({"coll": coll, "id": pid, "trashed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                       "payload": pl}, tf, ensure_ascii=False, indent=1)
        return fp
    except Exception as e:
        print(f"[台] ⚠️ 留底失败 {coll}/{pid}: {e}", flush=True)
        return None


# ==== v2.2.0 目审台（1008 午·自拍线验收首用）====
def _review_page_html():
    """目审台独立页（零 JS——9g7 内嵌换行血案免疫）：列 /root/work/review/<批次>/ 图网格。"""
    import urllib.parse as _up
    batches = []
    try:
        for d in sorted(os.listdir(REVIEW_ROOT), reverse=True):
            dp = os.path.join(REVIEW_ROOT, d)
            if not os.path.isdir(dp) or d.startswith("."):
                continue
            files = [f for f in sorted(os.listdir(dp))
                     if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
            if files:
                batches.append((d, files))
    except Exception:
        pass
    p = ["<!doctype html><html><head><meta charset='utf-8'>",
         "<meta name='viewport' content='width=device-width,initial-scale=1'>",
         "<title>目审台</title><style>",
         "body{background:#111;color:#ddd;font-family:-apple-system,sans-serif;margin:16px}",
         "h1{font-size:1.3rem;color:#9ecbff}h2{font-size:1.05rem;color:#9ecbff;margin:20px 0 8px}",
         ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}",
         ".grid img{width:100%;height:auto;border-radius:8px;border:1px solid #333;background:#222}",
         ".note{color:#888;font-size:.85rem}",
         "</style></head><body>",
         "<h1>🖼️ 目审台</h1><p class='note'>AI 只过机检闸不看图，审美验收 100% 归你。</p>"]
    for d, files in batches:
        p.append(f"<h2>{d}</h2><div class='grid'>")
        for f in files:
            q = f"/api/review/img?d={_up.quote(d)}&f={_up.quote(f)}"
            p.append(f"<a href='{q}' target='_blank'><img loading='lazy' src='{q}' alt='{f}'></a>")
        p.append("</div>")
    if not batches:
        p.append("<p class='note'>/root/work/review/ 下暂无批次（scp 推图即出）</p>")
    p.append("</body></html>")
    return "".join(p)


# ==== v2.1.0 表情柜工具函数（1007 夜战）====
def _expr_who_dirs():
    """宿主正本角色清单（目录名清洗：小写字母数字下划线）。"""
    out = []
    try:
        for d in sorted(os.listdir(EXPR_ASSETS)):
            if os.path.isdir(os.path.join(EXPR_ASSETS, d)) and re.fullmatch(r"[a-z0-9_]{1,24}", d) and not d.startswith("_"):
                out.append(d)
    except Exception:
        pass
    return out


def _expr_docker(*args, binary_input=None):
    """docker 命令封装（超时 30s），返回 (ok, stdout+stderr)。"""
    r = subprocess.run(["docker", *args],
                       capture_output=True, text=True, timeout=30,
                       input=binary_input)
    return r.returncode == 0, (r.stdout or "") + (r.stderr or "")


def _expr_remote_set(who):
    """容器 /app/build/expr/<who>/ 现存文件名集合（无目录=空集）。"""
    ok, out = _expr_docker("exec", EXPR_CTR, "ls", f"{EXPR_CTR_DIR}/{who}/")
    if not ok:
        return set()
    return {x.strip() for x in out.splitlines() if x.strip().lower().endswith(".png")}


def _expr_backup_one(who, emo):
    """先抄后撕：正本+容器两侧旧图归档 _backup/<ts>/，返回备份路径清单。"""
    tdir = os.path.join(EXPR_BAK, time.strftime("%Y%m%d-%H%M%S"), who)
    os.makedirs(tdir, exist_ok=True)
    done = []
    lp = os.path.join(EXPR_ASSETS, who, f"{emo}.png")
    if os.path.exists(lp):
        try:
            import shutil
            shutil.copy2(lp, os.path.join(tdir, f"{emo}.png"))
            done.append("local")
        except Exception:
            pass
    ok, out = _expr_docker("cp", f"{EXPR_CTR}:{EXPR_CTR_DIR}/{who}/{emo}.png",
                           os.path.join(tdir, f"{emo}.remote.png"))
    if ok:
        done.append("remote")
    return done, tdir


def _expr_push_one(who, emo, src_path):
    """正本→容器单格同步（docker cp 覆盖=原子生效）。"""
    _expr_docker("exec", EXPR_CTR, "mkdir", "-p", f"{EXPR_CTR_DIR}/{who}")
    ok, out = _expr_docker("cp", src_path, f"{EXPR_CTR}:{EXPR_CTR_DIR}/{who}/{emo}.png")
    return ok, out[:200]


def _expr_group_files(who, emo):
    """情绪组文件夹里的图清单（v2.2 一词一组，20261007 用户令）。"""
    gd = os.path.join(EXPR_ASSETS, who, emo)
    if not os.path.isdir(gd):
        return []
    return sorted(f for f in os.listdir(gd) if f.lower().endswith(".png"))


def _expr_push_group(who, emo):
    """正本情绪组→容器同步（文件夹整体 docker cp，v2.2 一词一组）。"""
    _expr_docker("exec", EXPR_CTR, "mkdir", "-p", f"{EXPR_CTR_DIR}/{who}/{emo}")
    ok, out = _expr_docker("cp", os.path.join(EXPR_ASSETS, who, emo) + "/.",
                           f"{EXPR_CTR}:{EXPR_CTR_DIR}/{who}/{emo}/")
    return ok, out[:200]


def _expr_api_list():
    """三源对账：宿主正本 × 容器生效 × 28 标准情绪 → 每角色格子矩阵。"""
    whos = _expr_who_dirs()
    ok, out = _expr_docker("exec", EXPR_CTR, "ls", EXPR_CTR_DIR + "/")
    remote_whos = {x.strip() for x in out.splitlines() if x.strip()} if ok else set()
    result = []
    for who in sorted(set(whos) | {w for w in remote_whos if re.fullmatch(r"[a-z0-9_]{1,24}", w)}):
        adir = os.path.join(EXPR_ASSETS, who)
        local_files = {f[:-4] for f in os.listdir(adir) if f.lower().endswith(".png")} if os.path.isdir(adir) else set()
        remote_files = {f[:-4] for f in _expr_remote_set(who)}
        grid = []
        emos = list(EXPR_EMOTIONS) + sorted((local_files | remote_files) - set(EXPR_EMOTIONS))
        for emo in emos:
            grp = _expr_group_files(who, emo)
            grid.append({"emo": emo, "local": emo in local_files or bool(grp),
                         "remote": emo in remote_files, "grp_n": len(grp)})
        result.append({"who": who, "grid": grid,
                       "std_cover": sum(1 for e in EXPR_EMOTIONS if e in local_files)})
    return {"emotions_std": EXPR_EMOTIONS, "roles": result}



def _ingest_recent(n):
    """chat_memory 最近 n 条（order_by ts desc=服务端取真最近）→ 列表给工作台勾选。"""
    r = _q.post(f"{QDRANT}/collections/chat_memory/points/scroll", timeout=30,
                json={"limit": min(int(n), 300), "with_payload": True, "with_vector": False,
                      "order_by": {"key": "ts", "direction": "desc"}})
    pts = r.json()["result"]["points"]
    out = []
    for p in pts:
        pl = p.get("payload") or {}
        try:
            stamp = time.strftime("%m-%d %H:%M", time.localtime((pl.get("ts") or 0) / 1000))
        except Exception:
            stamp = ""
        out.append({"id": p["id"], "role": str(pl.get("role") or "?"),
                    "stamp": stamp, "text": str(pl.get("text") or "")[:220]})
    return {"count": len(out), "items": out}


def _ingest_submit(ids):
    """勾选点全文 → 台词稿 → 书记员(GLM high)提炼 → 宫桥 /ingest。页面即回执。"""
    r = _q.post(f"{QDRANT}/collections/chat_memory/points", timeout=30,
                json={"ids": [int(i) for i in ids], "with_payload": True, "with_vector": False})
    res = r.json().get("result")
    pts = res.get("points") if isinstance(res, dict) else res
    pts = [p for p in (pts or []) if p.get("payload")]
    if not pts:
        return {"error": "勾选的点一个都没取到（可能已被删除）"}
    pts.sort(key=lambda p: (p["payload"].get("ts") or 0))
    lines = []
    for p in pts:
        pl = p["payload"]
        who = "主人" if pl.get("role") == "user" else "姐妹"
        lines.append(f"{who}：{pl.get('text', '')}")
    transcript = "\n".join(lines)
    if len(transcript) < 50:
        return {"error": f"勾选内容共 {len(transcript)} 字，太短不值得入宫"}
    zr = httpx.post(ZHIPU_URL, timeout=300, headers={"Authorization": f"Bearer {ZKEY}",
                    "Content-Type": "application/json"}, json={
        "model": "glm-5.3-flash", "reasoning_effort": "high", "max_tokens": 8192, "temperature": 0.3,
        "messages": [{"role": "system", "content": INGEST_SCRIBE},
                     {"role": "user", "content": f"【主人的指令】请把这段讨论入库。\n\n【对话记录】\n{transcript}"}]})
    zr.raise_for_status()
    raw = (zr.json()["choices"][0]["message"].get("content") or "").strip()
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return {"error": f"书记员判断没有值得入宫的内容。原话：{raw[:100]}"}
    try:
        items = json.loads(m.group(0))
    except Exception:
        return {"error": "书记员输出格式没能解析，再点一次试试"}
    if not isinstance(items, list) or not items:
        return {"error": "书记员判断没有值得入宫的内容"}
    pr = _pq.post(PALACE + "/ingest", json={"items": items}, timeout=300)
    d = pr.json()
    return {"added": d.get("added", 0), "dup": d.get("dup", 0),
            "failed": d.get("failed", 0), "titles": d.get("titles", [])}


# ==== v1.4.2 日志补账自持化（原代理桥 /v1/journal/generate；浓缩逻辑自桥 _condense_day/_journal_write_day 单变量移植，桥删口后台独立）====
_CN_WD = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]


def _journal_generate(date):
    """指定日期（早于今天）从 chat_memory 当场浓缩/重生成日志，幂等覆盖写（同日 id 覆盖）。
    返回 (status, dict)；写侧姿势与 /api/journal/update 同款（payload+向量一起 PUT）。
    时区：服务器本机=CST，mktime 直出中国时区当日零点；ts 分组用 gmtime+8h 不依赖本机时区。"""
    try:
        r = _q.post(f"{QDRANT}/collections/chat_memory/points/scroll", timeout=60,
                    json={"limit": 5000, "with_payload": True, "with_vector": False})
        msgs = []
        for p in (r.json().get("result", {}).get("points") or []):
            pl = p.get("payload") or {}
            ts = pl.get("ts")
            if not isinstance(ts, (int, float)) or not (pl.get("text") or "").strip():
                continue
            if time.strftime("%Y-%m-%d", time.gmtime(ts / 1000 + 8 * 3600)) == date:
                msgs.append(pl)
        msgs.sort(key=lambda p: p["ts"])
        if not msgs:
            return 404, {"error": f"{date} 在 chat_memory 里没有对话记录"}
        wd = _CN_WD[int(time.strftime("%w", time.strptime(date, "%Y-%m-%d")))]
        head = f"{int(date[5:7])}月{int(date[8:10])}日 {wd}："
        lines = [("主人" if (p.get("role") == "user") else "姐妹") + "：" + (p.get("text") or "")
                 for p in msgs]
        prompt = ("把下面这一天主人和姐妹的对话浓缩成一段当日日志：第三人称叙事，严格不超过 300 字，"
                  "保留聊过的话题、情绪、未了结的事、承诺（人名/数字/关键原话尽量保留）。"
                  f"第一行必须以「{head}」这样的日期头开头，后面直接接正文。\n\n" + "\n".join(lines))
        zr = httpx.post(ZHIPU_URL, timeout=300, headers={"Authorization": f"Bearer {ZKEY}",
                        "Content-Type": "application/json"}, json={
            "model": "glm-5.3-flash", "thinking": {"type": "enabled"}, "reasoning_effort": "low",
            "max_tokens": 768, "temperature": 0.3,
            "messages": [{"role": "user", "content": prompt}]})
        zr.raise_for_status()
        raw = (zr.json()["choices"][0]["message"].get("content") or "").strip()
        if not raw:
            return 500, {"error": "浓缩结果为空（GLM 空回复）"}
        raw = re.sub(r"^\s*\d{1,2}\s*月\s*\d{1,2}\s*日\s*周[一二三四五六日天]\s*[：:]\s*", "", raw)
        text = (head + raw).strip()
        day0 = int(time.mktime(time.strptime(date, "%Y-%m-%d"))) * 1000
        wr = _q.put(f"{QDRANT}/collections/chat_journal/points?wait=true", timeout=30,
                    json={"points": [{"id": int(date.replace("-", "")), "vector": _vec_for(text),
                          "payload": {"date": date, "weekday": wd, "text": text,
                                      "ts": day0 + 86399000, "source": "console-journal"}}]})
        if wr.status_code != 200:
            return 502, {"error": f"日志写入失败: {wr.text[:200]}"}
        print(f"[台] 日志已补账 {date}（{len(text)} 字，GLM-low）", flush=True)
        return 200, {"ok": True, "date": date, "text": text}
    except Exception as e:
        return 500, {"error": str(e)[:300]}


# ==== v1.4.3 脑绑定总闸 + 人设底稿五槽（用户 1002 深夜定稿；写侧一律先抄后撕）====
BINDING_FILE = "/root/work/cloud-config/brain_binding.json"
PERSONA_FILES = {
    "duet":     "/root/work/cloud-config/pure_prompt.txt",
    "ram":      "/root/work/cloud-config/prompt/solo_ram.txt",
    "rem":      "/root/work/cloud-config/prompt/solo_rem.txt",
    "emt":      "/root/work/cloud-config/prompt/solo_emt.txt",
    "trio":     "/root/work/cloud-config/prompt/trio_prompt.txt",
    "duet_ram": "/root/work/cloud-config/prompt/duet_ram.txt",
    "duet_rem": "/root/work/cloud-config/prompt/duet_rem.txt",
}
PERSONA_TRASH = "/root/work/server-backups/persona_trash"


def _persona_backup(tag, path):
    """先抄后撕：旧文件全文抄进 persona_trash/<日期>/，成功返回路径，失败 None（调用方须中止写入）。"""
    try:
        tdir = os.path.join(PERSONA_TRASH, time.strftime("%Y%m%d"))
        os.makedirs(tdir, exist_ok=True)
        fp = os.path.join(tdir, f"{tag}.bak-" + time.strftime("%H%M%S"))
        with open(path, encoding="utf-8") as rf, open(fp, "w", encoding="utf-8") as wf:
            wf.write(rf.read())
        return fp
    except Exception as e:
        print(f"[台] ⚠️ 留底失败 {tag}: {e}", flush=True)
        return None


def _brain_binding_get():
    """v2.1.0：读 tavern 场景展平视图（UI 两控件不变），scenes 全量附带（桥 v4.0.0 三场景结构）。"""
    try:
        cur = json.loads(open(BINDING_FILE, encoding="utf-8").read())
    except Exception:
        cur = {}
    tv = cur.get("tavern") if isinstance(cur, dict) and isinstance(cur.get("tavern"), dict) else cur
    scenes = cur if isinstance(cur, dict) and "tavern" in cur else {}
    return {"provider": str((tv or {}).get("provider") or "ds"),
            "glm_effort": str((tv or {}).get("glm_effort") or "low"),
            "ds_effort": str((tv or {}).get("ds_effort") or "high"),
            "scenes": scenes}


def _brain_binding_set(provider, glm_effort, ds_effort="high"):
    # v2.1.0：值域扩 cli（本地8317国外脑）/local；写侧只动 tavern 槽，pet/service 槽原样保留（防整档覆写踩 v4.0.0 场景结构）
    if provider not in ("glm", "ds", "local", "cli"):
        return 400, {"error": "provider 只准 glm/ds/local/cli"}
    if provider == "glm" and glm_effort not in ("low", "high", "max"):
        return 400, {"error": "glm_effort 只准 low/high/max"}
    if provider == "ds" and ds_effort not in ("low", "high", "max"):
        return 400, {"error": "ds_effort 只准 low/high/max"}
    if os.path.exists(BINDING_FILE) and not _persona_backup("brain_binding", BINDING_FILE):
        return 500, {"error": "旧配置留底失败，已中止写入"}
    try:
        cur = json.loads(open(BINDING_FILE, encoding="utf-8").read())
    except Exception:
        cur = {}
    if not isinstance(cur, dict):
        cur = {}
    cur["tavern"] = {"provider": provider, "glm_effort": glm_effort if provider == "glm" else "low",
                     "ds_effort": ds_effort if provider == "ds" else "high"}
    cur.setdefault("pet", {"provider": "cli", "glm_effort": "low"})     # v4.1.0 用户矩阵默认
    cur.setdefault("service", {"provider": "cli", "glm_effort": "low"})
    try:
        with open(BINDING_FILE, "w", encoding="utf-8") as wf:
            json.dump(cur, wf, ensure_ascii=False, indent=1)
    except Exception as e:
        return 500, {"error": f"写入失败: {str(e)[:200]}"}
    print(f"[台] 脑绑定已切换 tavern={provider}/{glm_effort}（pet/service 槽原样保留）", flush=True)
    return 200, {"ok": True, **cur["tavern"], "scenes": cur}


# ==== v1.7.0 API 钥匙自助换发（v2.1.0 改版：智谱槽退役、云CLI槽上编、OWI#6=云CLI）====
KEY_SLOTS = {
    "zhipu":      {"file": "/root/work/.zhipu_key_cloud", "name": "智谱云钥匙（已退役·桥不再读）",
                   "desc": "v4.1.0 起桥 GLM=云CLI 付费 key（住 CLI 配置内）。此钥匙位仅历史留档，保存不影响任何服务；OWI 同步已废。"},
    "modelscope": {"file": "/root/work/.modelscope_key", "name": "魔搭钥匙（桥 DS 脑·按次计费）",
                   "desc": "DeepSeek 魔搭道（酒馆专职）在用。保存后自动重启桥（约5秒）。"},
    "cli":        {"file": "/root/work/cliproxy/.api_key", "name": "云CLI客户端钥匙（桥GLM/免费道/OWI#6）",
                   "desc": "CLIProxyAPI 网关下游钥匙。上游各家 key 在 CLI 官方管理页维护：http://10.14.14.1:8317/management.html。保存后自动重启桥。"},
    "owi_zhipu":  {"file": None, "name": "OWI 连接#6 指纹（现=云CLI）",
                   "desc": "v2.1.0 起 OWI #6 = http://172.19.0.1:8317/v1（云CLI），与 cli 槽同钥匙；旧「智谱钥匙同步 OWI」已废。"},
}
OWI_DB = "/var/lib/docker/volumes/open-webui/_data/webui.db"
OWI_KEY_IDX = 6   # v2.1.0 起 = http://172.19.0.1:8317/v1（云CLI），不再是 coding 端点
OWL_IDX_FILE = "/root/work/cliproxy/.api_key"  # OWI#6 同步源=云CLI 钥匙（v2.1.0 改）
OWI_IDX_URL = "http://172.19.0.1:8317/v1"


def _owi_key_read():
    import sqlite3
    db = sqlite3.connect(f"file:{OWI_DB}?mode=ro", uri=True)
    raw = db.execute("SELECT value FROM config WHERE key='openai.api_keys'").fetchone()[0]
    db.close()
    return json.loads(raw)[OWI_KEY_IDX]


def _owi_key_write(new_key):
    """停 OWI→直改 db→起 OWI（避免 WAL 锁与内存覆写）；返回 (code, dict)。"""
    import subprocess
    def sh(cmd, t=120):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
    if sh("docker stop open-webui-slim").returncode != 0:
        return 500, {"error": "docker stop 失败"}
    try:
        import sqlite3
        db = sqlite3.connect(OWI_DB, timeout=10)
        raw = db.execute("SELECT value FROM config WHERE key='openai.api_keys'").fetchone()[0]
        keys = json.loads(raw)
        old = keys[OWI_KEY_IDX][-4:] if keys[OWI_KEY_IDX] else "(空)"
        keys[OWI_KEY_IDX] = new_key
        db.execute("UPDATE config SET value=? WHERE key='openai.api_keys'",
                   (json.dumps(keys, ensure_ascii=False),))
        db.commit()
        db.close()
        out = f"OWI#6 钥匙 {old} → {new_key[-4:]}"
        # v2.1.0 防腐蚀：#6 的 base_url 钉到云CLI（历史值若是 coding 端点则矫直）
        try:
            db2 = sqlite3.connect(OWI_DB, timeout=10)
            rawu = db2.execute("SELECT value FROM config WHERE key='openai.api_base_urls'").fetchone()[0]
            urls = json.loads(rawu)
            if len(urls) > OWI_KEY_IDX and urls[OWI_KEY_IDX] != OWI_IDX_URL:
                urls[OWI_KEY_IDX] = OWI_IDX_URL
                db2.execute("UPDATE config SET value=? WHERE key='openai.api_base_urls'",
                            (json.dumps(urls, ensure_ascii=False),))
                db2.commit()
                out += "（url 已钉云CLI）"
            db2.close()
        except Exception:
            pass
    except Exception as e:
        sh("docker start open-webui-slim")
        return 500, {"error": f"db 写入失败（OWI 已拉回）: {str(e)[:150]}"}
    sh("docker start open-webui-slim")
    for _ in range(12):
        time.sleep(5)
        try:
            if httpx.get("http://127.0.0.1:3001/health", timeout=4).status_code == 200:
                return 200, {"ok": True, "msg": out + "；OWI 已重启 healthy"}
        except Exception:
            pass
    return 200, {"ok": True, "msg": out + "；但 OWI health 未就绪，稍后自查 docker ps"}


def _bridge_restart():
    """桥启动时读钥匙，故保存后必须重启（姿势=reboot_bridges.sh 桥行原样）。"""
    import subprocess
    subprocess.run("pkill -f 'tavern-bridge-cloud.py'", shell=True, capture_output=True)
    time.sleep(1.5)
    subprocess.run("cd /root/work && BRIDGE_BIND=172.19.0.1 setsid nohup /root/memvenv/bin/python3 "
                   "/root/work/cloud-config/tavern-bridge-cloud.py >> /root/work/logs/tavern-bridge.log "
                   "2>&1 < /dev/null &", shell=True, capture_output=True)
    for _ in range(10):
        time.sleep(1.5)
        try:
            if httpx.get("http://172.19.0.1:18170/healthz", timeout=3).status_code == 200:
                return True
        except Exception:
            pass
    return False


def _keys_list():
    out = {}
    for slot, meta in KEY_SLOTS.items():
        try:
            val = _owi_key_read() if slot == "owi_zhipu" else open(meta["file"], encoding="utf-8").read().strip()
            out[slot] = {"name": meta["name"], "desc": meta["desc"], "exists": bool(val),
                         "len": len(val), "tail4": val[-4:] if val else ""}
        except Exception:
            out[slot] = {"name": meta["name"], "desc": meta["desc"], "exists": False,
                         "len": 0, "tail4": ""}
    return out


def _keys_reveal(slot):
    meta = KEY_SLOTS.get(slot)
    if not meta:
        return 400, {"error": "slot 只准 " + "/".join(KEY_SLOTS)}
    try:
        val = _owi_key_read() if slot == "owi_zhipu" else open(meta["file"], encoding="utf-8").read().strip()
    except Exception as e:
        return 500, {"error": f"读取失败: {str(e)[:150]}"}
    return 200, {"key": val}


def _keys_save(slot, key, sync_owi):
    meta = KEY_SLOTS.get(slot)
    if not meta:
        return 400, {"error": "slot 只准 " + "/".join(KEY_SLOTS)}
    key = str(key or "").strip()
    if not key or len(key) < 16:
        return 400, {"error": "钥匙像不对（少于16位），别把指纹或半截粘进来"}
    msgs = []
    if slot == "owi_zhipu":
        c, d = _owi_key_write(key)
        msgs.append(d.get("msg") or d.get("error"))
        if c != 200:
            return c, d
    else:
        path = meta["file"]
        old = ""
        try:
            old = open(path, encoding="utf-8").read().strip()
        except Exception:
            pass
        if old == key:
            return 200, {"ok": True, "msg": "与现役钥匙相同，未做任何改动"}
        try:
            if old:  # 旧钥匙就地留底
                bak = f"{path}.bak-" + time.strftime("%Y%m%d-%H%M%S")
                with open(bak, "w", encoding="utf-8") as wf:
                    wf.write(old)
                msgs.append(f"旧钥匙留底 {os.path.basename(bak)}")
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as wf:
                wf.write(key)
            os.replace(tmp, path)
            os.chmod(path, 0o600)
            msgs.append(f"{path} 已更新（尾 {key[-4:]}）")
        except Exception as e:
            return 500, {"error": f"写入失败: {str(e)[:150]}"}
        if not _bridge_restart():
            return 500, {"error": "钥匙已保存，但桥重启未就绪——去「运行小票」看 tavern-bridge.log，或手动跑 reboot_bridges.sh"}
        msgs.append("桥已重启 healthy")
    if slot == "zhipu" and sync_owi:
        c, d = _owi_key_write(key)
        msgs.append(d.get("msg") or d.get("error"))
        if c != 200:
            return 500, {"ok": True, "msg": "；".join(msgs) + "；⚠️ OWI 同步失败（桥侧钥匙已生效）"}
    print(f"[台] 钥匙已换 slot={slot} tail4={key[-4:]} sync_owi={bool(sync_owi)}", flush=True)
    return 200, {"ok": True, "msg": "；".join(msgs)}


# ==== v1.8.0 学习签（题池管理+掌握度视图；题池=learning_points.jsonl 行号=id，与桥 v3.8.0 考官引擎同源）====
EXAM_POINTS_FILE = "/root/work/cloud-config/learning_points.jsonl"
EXAM_STATE_FILE = "/root/work/cloud-config/exam_state.json"
EXAM_TRASH = "/root/work/server-backups/exam_trash"


def _exam_read_state():
    try:
        st = json.loads(open(EXAM_STATE_FILE, encoding="utf-8").read())
        if isinstance(st, dict) and isinstance(st.get("points"), dict):
            return st
    except Exception:
        pass
    return {"points": {}}


def _exam_list():
    """题池+掌握度合并列表：id/topic/text/状态（新/due日期/间隔）。"""
    out = []
    st = _exam_read_state()
    today = time.strftime("%Y-%m-%d")
    try:
        with open(EXAM_POINTS_FILE, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                text = str(d.get("text") or "").strip()
                if not text:
                    continue
                topic = text.split("]")[0].lstrip("[") if text.startswith("[") else "综合"
                ps = st["points"].get(str(i))
                if not ps:
                    status = "新题"
                else:
                    iv = ps.get("interval") or 0
                    due = ps.get("due") or ""
                    status = f"掌握(interval {iv}天)" if iv >= 21 else (f"到期({due})" if due <= today else f"复习中({due})")
                out.append({"id": i, "topic": topic, "text": text, "status": status})
    except Exception:
        pass
    return {"items": out, "total": len(out), "today": today}


def _exam_add(text, topic=None):
    text = str(text or "").strip()
    if len(text) < 5:
        return 400, {"error": "题目太短（<5字）"}
    try:  # 追加前留底
        os.makedirs(EXAM_TRASH, exist_ok=True)
        if os.path.exists(EXAM_POINTS_FILE):
            import shutil as _sh
            _sh.copy2(EXAM_POINTS_FILE, os.path.join(
                EXAM_TRASH, f"learning_points.bak-" + time.strftime("%Y%m%d-%H%M%S")))
        with open(EXAM_POINTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"date": time.strftime("%Y-%m-%d"),
                                "text": f"[{topic or '学习'}] {text}"}, ensure_ascii=False) + "\n")
        print(f"[台] 考官题池 +1（{len(text)}字）", flush=True)
        return 200, {"ok": True, "msg": "已追加题池（行号即 id，姐妹晨报/对话会自动排考）"}
    except Exception as e:
        return 500, {"error": f"写入失败: {str(e)[:150]}"}


def _exam_reset(pid):
    st = _exam_read_state()
    if str(pid) not in st["points"]:
        return 400, {"error": "该题尚无掌握度记录"}
    try:
        st["points"].pop(str(pid))
        tmp = EXAM_STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
        os.replace(tmp, EXAM_STATE_FILE)
        return 200, {"ok": True, "msg": f"题 {pid} 掌握度已重置为新题"}
    except Exception as e:
        return 500, {"error": str(e)[:150]}


# ==== v1.9.0 Token 计量聚合（读近 7 天小票的 usage 字段）====
def _tokens_list():
    days = []
    for i in range(6, -1, -1):
        ts = time.time() - i * 86400
        ymd = time.strftime("%Y%m%d", time.localtime(ts))
        label = time.strftime("%m-%d", time.localtime(ts))
        fp = f"/root/work/logs/turn_receipt-{ymd}.jsonl"
        total = prompt = comp = turns = cached = 0
        by_mode = {}
        try:
            with open(fp, encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    u = d.get("usage") or {}
                    t = u.get("total") or 0
                    if not t:
                        continue
                    total += t; prompt += u.get("prompt", 0); comp += u.get("completion", 0); turns += 1
                    cached += u.get("cached", 0)
                    mode = (d.get("mode") or "?").split("·")[0]
                    by_mode[mode] = by_mode.get(mode, 0) + t
        except FileNotFoundError:
            pass
        days.append({"date": label, "total": total, "prompt": prompt, "completion": comp,
                     "cached": cached, "turns": turns, "by_mode": by_mode})
    return {"days": days}


# ==== v2.0.0 桥参数（bridge_params.json 热读；好感度直调 bond_state.json）====
BP_FILE = "/root/work/cloud-config/bridge_params.json"
BP_DEFAULT = {"bond_daily_cap": 3, "nostalgia_prob": 15, "nostalgia_half": 50,
              "nostalgia_daily_max": 1, "vision_tail": 40, "summary_every": 20,
              "reply_temperature": 0.8, "rp_level": 2, "kb_topk": 3}
BOND_FILE = "/root/work/cloud-config/bond_state.json"
BP_SCHEMA = {  # key: (min, max, 类型, 说明)
    "bond_score":          (0, 100, int, "好感度当前分（0-100；≥70 恋人 / ≥50 亲密 / ≥90 灵魂伴侣）"),
    "bond_daily_cap":      (1, 10, int, "每日好感度变动封顶 ±N（姐妹变心/升温速度）"),
    "nostalgia_prob":      (0, 100, int, "回忆杀触发概率 %（每轮判定）"),
    "nostalgia_half":      (0, 100, int, "回忆杀触发后转「考你一题」的概率 %"),
    "nostalgia_daily_max": (0, 1, int, "回忆杀每日次数：0=关闭 1=每日至多一次"),
    "vision_tail":         (10, 80, int, "对话视野条数（40 条=20 轮；越大记得越远但更贵更慢）"),
    "summary_every":       (10, 50, int, "前情提要浓缩周期（每 N 条消息浓缩一次）"),
    "reply_temperature":   (0.1, 1.5, float, "回复温度（低=稳重 高=放飞）"),
    "rp_level":            (1, 4, int, "演出浓度挡：1 轻度 2 标准 3 加强 4 全沉浸（2=现状零注入；4=现实锚标签换【此刻】）"),
    "kb_topk":             (1, 10, int, "台词库/场景库每轮注入条数（默认 3=历史现状；越大台词味越足但每轮更长）"),
}


def _bp_read():
    try:
        d = json.loads(open(BP_FILE, encoding="utf-8").read())
        if isinstance(d, dict):
            return {**BP_DEFAULT, **d}
    except Exception:
        pass
    return dict(BP_DEFAULT)


def _bp_backup(tag):
    try:
        tdir = "/root/work/server-backups/bridge_params_trash"
        os.makedirs(tdir, exist_ok=True)
        src = BP_FILE if os.path.exists(BP_FILE) else "/dev/null"
        import shutil as _sh
        _sh.copy2(src, os.path.join(tdir, f"{tag}.bak-" + time.strftime("%Y%m%d-%H%M%S"))) if os.path.exists(BP_FILE) else None
        return True
    except Exception:
        return False


def _bparams_get():
    cur = _bp_read()
    return {k: {"value": cur.get(k, BP_DEFAULT[k]), "default": BP_DEFAULT[k],
                "min": v[0], "max": v[1], "type": v[2].__name__, "desc": v[3]}
            for k, v in BP_SCHEMA.items() if k != "bond_score"}


def _bparams_set(key, value):
    if key not in BP_SCHEMA or key == "bond_score":
        return 400, {"error": "key 非法"}
    lo, hi, typ, _ = BP_SCHEMA[key]
    try:
        v = typ(value)
    except (TypeError, ValueError):
        return 400, {"error": "值类型不对"}
    if not (lo <= v <= hi):
        return 400, {"error": f"越界：只准 {lo}~{hi}（防手滑打挂对话）"}
    if not _bp_backup(key):
        return 500, {"error": "留底失败，已中止写入"}
    cur = _bp_read()
    cur[key] = v
    tmp = BP_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=1)
    os.replace(tmp, BP_FILE)
    print(f"[台] 桥参数 {key} = {v}", flush=True)
    return 200, {"ok": True, "msg": f"{key} = {v} 已保存（桥每请求现读，下一句话生效）"}


def _bparams_reset():
    if not _bp_backup("reset"):
        return 500, {"error": "留底失败"}
    try:
        if os.path.exists(BP_FILE):
            os.remove(BP_FILE)
        return 200, {"ok": True, "msg": "已恢复全部默认值（下一句话生效）"}
    except Exception as e:
        return 500, {"error": str(e)[:150]}


def _bond_score_set(value):
    lo, hi, _, _ = BP_SCHEMA["bond_score"]
    try:
        v = int(value)
    except (TypeError, ValueError):
        return 400, {"error": "分数须为整数"}
    if not (lo <= v <= hi):
        return 400, {"error": f"越界：只准 {lo}~{hi}"}
    try:
        st = json.loads(open(BOND_FILE, encoding="utf-8").read())
        old = st.get("score", 75)
        import shutil as _sh
        tdir = "/root/work/server-backups/bridge_params_trash"
        os.makedirs(tdir, exist_ok=True)
        _sh.copy2(BOND_FILE, os.path.join(tdir, f"bond_state.bak-" + time.strftime("%Y%m%d-%H%M%S")))
        st["score"] = v
        tmp = BOND_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
        os.replace(tmp, BOND_FILE)
        print(f"[台] 好感度 {old} → {v}", flush=True)
        return 200, {"ok": True, "msg": f"好感度 {old} → {v} 已写入（下一轮对话生效；旧账本已留底）"}
    except Exception as e:
        return 500, {"error": f"写入失败: {str(e)[:150]}"}


def _persona_list():
    out = {}
    for slot, path in PERSONA_FILES.items():
        try:
            txt = open(path, encoding="utf-8").read()
            out[slot] = {"path": path, "chars": len(txt.strip()), "text": txt}
        except Exception:
            out[slot] = {"path": path, "chars": 0, "text": "", "missing": True}
    return out


def _persona_save(slot, text):
    path = PERSONA_FILES.get(slot)
    if not path:
        return 400, {"error": "槽位只准 " + "/".join(PERSONA_FILES)}
    text = str(text or "").strip()
    if not text:
        return 400, {"error": "底稿正文不能为空"}
    if os.path.exists(path) and not _persona_backup(slot, path):
        return 500, {"error": "旧稿留底失败，已中止写入"}
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as wf:
            wf.write(text + "\n")
    except Exception as e:
        return 500, {"error": f"写入失败: {str(e)[:200]}"}
    print(f"[台] 底稿已保存 {slot}（{len(text)} 字）——下一句生效", flush=True)
    return 200, {"ok": True, "slot": slot, "chars": len(text)}


# ==== v1.4.4 执行小票（桥每轮落 turn_receipt-YYYYMMDD.jsonl，只写不清；本台只读渲染）====
import glob as _glob


def _receipt_list(date=None):
    """执行小票按天列表（v1.4.5 用户定版：按天翻，单天全量，不做数字分页）。
    返回 {dates:[全部有票日期 ISO 新→旧], date:选中日, rows:该天全部轮次元数据}；date 缺省=最新一天。"""
    files = sorted(_glob.glob("/root/work/logs/turn_receipt-*.jsonl"), reverse=True)

    def _iso(fn):
        raw = fn.rsplit("-", 1)[1].replace(".jsonl", "")
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}" if len(raw) == 8 else raw

    dates = [_iso(f) for f in files]
    sel = str(date or "").strip().replace("-", "")
    if len(sel) == 8:
        sel = f"{sel[:4]}-{sel[4:6]}-{sel[6:8]}"
    if not sel or sel not in dates:
        sel = dates[0] if dates else ""
    rows = []
    if sel:
        fp = f"/root/work/logs/turn_receipt-{sel.replace('-', '')}.jsonl"
        try:
            with open(fp, encoding="utf-8") as rf:
                for i, line in enumerate(rf, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    rows.append({"file": fp, "line": i, "ts": d.get("ts"), "mode": d.get("mode"),
                                 "provider": d.get("provider"), "user": (d.get("user_text") or "")[:60],
                                 "total_ms": (d.get("timings") or {}).get("total_ms"),
                                 "ft_ms": (d.get("timings") or {}).get("first_token_ms"),
                                 "err": bool(d.get("error")),
                                 "inj": len(d.get("injections") or []),
                                 "rec": len(d.get("recalls") or [])})
        except Exception:
            pass
        rows.sort(key=lambda x: (x.get("ts") or ""), reverse=True)
    # v1.5.0 双日志合一：统计卡数据源从 mentor-chain.log 改 turn_receipt（随所选日翻动）
    _brains = {}
    for _r in rows:
        _k = _r.get("mode") or "?"
        _brains[_k] = _brains.get(_k, 0) + 1
    _tms = [_r["total_ms"] for _r in rows if isinstance(_r.get("total_ms"), (int, float))]
    _stats = {"rounds": len(rows), "brains": _brains,
              "avg_sec": round(sum(_tms) / len(_tms) / 1000, 1) if _tms else 0,
              "src": "turn_receipt"}
    return {"dates": dates, "date": sel, "rows": rows, "stats": _stats}


def _receipt_detail(file, line):
    safe = os.path.realpath(str(file or ""))
    if not safe.startswith(os.path.realpath("/root/work/logs") + os.sep + "turn_receipt-"):
        return {"error": "非法路径"}
    try:
        with open(safe, encoding="utf-8") as rf:
            for i, l in enumerate(rf, 1):
                if i == int(line or 0):
                    return json.loads(l)
    except Exception as e:
        return {"error": str(e)[:200]}
    return {"error": "行号越界"}

# ==== v2.4.0 想法账本（ideas_ledger：只读浏览+改类目+语义搜+导出；数据=桥 v4.4.5+ 写入） ====
IDEA_COLL = "ideas_ledger"
IDEA_FILE = "/root/work/cloud-config/ideas_ledger.jsonl"
IDEA_CATS_FILE = "/root/work/cloud-config/ideas_categories.json"


def _idea_cats():
    try:
        return json.load(open(IDEA_CATS_FILE, encoding="utf-8"))["cats"]
    except Exception:
        return [{"id": "stock", "name": "股票"}, {"id": "work", "name": "工作"}, {"id": "study", "name": "学习"},
                {"id": "life", "name": "生活"}, {"id": "relation", "name": "关系"}, {"id": "other", "name": "其他"}]


def _ideas_data():
    """全量滚动+版本链重组：chains=[{current, members(旧→新)}]，stats=轻统计。"""
    pts, off = [], None
    while True:
        body = {"limit": 200, "with_payload": True}
        if off is not None:
            body["offset"] = off
        try:
            d = _q.post(f"{QDRANT}/collections/{IDEA_COLL}/points/scroll", json=body).json().get("result", {})
        except Exception:
            break
        pts += d.get("points", [])
        off = d.get("next_page_offset")
        if not off:
            break
    ents = []
    for p in pts:
        pl = dict(p.get("payload") or {})
        pl["id"] = p.get("id")
        if (pl.get("q") or "").strip() and (pl.get("c") or "").strip():
            ents.append(pl)
    ents.sort(key=lambda e: e.get("ts") or 0)
    by_id = {e["id"]: e for e in ents}
    child_of = {}   # old_id -> new_id（取代方向）
    for e in ents:
        for sid in (e.get("supersedes") or []):
            if sid in by_id:
                child_of[sid] = e["id"]
        sb = e.get("superseded_by")
        if sb and sb in by_id and e["id"] not in child_of:
            child_of[e["id"]] = sb
    parent_of = {v: k for k, v in child_of.items()}
    chains = []
    for e in ents:
        if e["id"] in child_of:
            continue   # 非链头（还有更新版挂着）
        seq = [e]
        cur = e
        while cur["id"] in parent_of:
            p = by_id.get(parent_of[cur["id"]])
            if not p:
                break
            seq.insert(0, p)
            cur = p
        chains.append({"current": e["id"], "members": seq})
    chains.sort(key=lambda c: -(c["members"][-1].get("ts") or 0))
    cats = _idea_cats()
    cur_list = [c["members"][-1] for c in chains]
    stats = {"total": len(ents), "chains": len(chains),
             "none": sum(1 for e in cur_list if not e.get("cat")),
             "by_cat": {c["id"]: sum(1 for e in cur_list if e.get("cat") == c["id"]) for c in cats}}
    return {"cats": cats, "entries": sorted(ents, key=lambda e: -(e.get("ts") or 0)), "chains": chains, "stats": stats}


def _ideas_search(q, mode):
    """sem=嵌入席向量查询（0.5 宽阈值取 20，命中映射回链头去重）；kw=子串扫描。"""
    hits = []
    if mode == "sem":
        try:
            v = _vec_for(q)
            if min(v) >= 0:   # v2.4.0b FNV 伪向量守卫（嵌入席僵死时防假命中；与桥 v4.4.6c 同签名判据）
                return {"hits": [], "error": "嵌入席超时，稍后再试语义搜（或先用关键词搜）"}
            r = _q.post(f"{QDRANT}/collections/{IDEA_COLL}/points/query",
                        json={"query": v, "limit": 20, "score_threshold": 0.5, "with_payload": True},
                        timeout=30)
            for p in (r.json().get("result", {}).get("points") or []):
                hits.append({"hit_id": p.get("id"), "score": round(p.get("score", 0), 3)})
        except Exception:
            pass
    else:
        low = q.lower()
        for e in _ideas_data()["entries"]:
            if low in ((e.get("q") or "") + " " + (e.get("c") or "") + " " + (e.get("r") or "")).lower():
                hits.append({"hit_id": e["id"], "score": None})
    data = _ideas_data()
    head_of = {}
    for c in data["chains"]:
        for m in c["members"]:
            head_of[m["id"]] = c["current"]
    seen, out = set(), []
    for h in hits:
        cid = head_of.get(h["hit_id"])
        if cid and cid not in seen:
            seen.add(cid)
            out.append({"hit_id": h["hit_id"], "current_id": cid, "score": h["score"]})
    data["hits"] = out
    return data


def _ideas_retag(pid, cat):
    """v2.4.0 最小纠错：单条改类目（cat='' = 未分类）；Qdrant payload 即时改+jsonl 留审计事件。"""
    if cat and cat not in {c["id"] for c in _idea_cats()}:
        return {"ok": False, "error": "非法类目"}
    try:
        _q.post(f"{QDRANT}/collections/{IDEA_COLL}/points/payload",
                json={"points": [pid], "payload": {"cat": cat or None, "cat_source": "user" if cat else None},
                      "wait": True},
                timeout=30)
    except Exception as e:
        return {"ok": False, "error": str(e)[:150]}
    try:
        with open(IDEA_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"op": "retag", "id": pid, "cat": cat or None, "ts": int(time.time() * 1000)},
                               ensure_ascii=False) + "\n")
    except Exception:
        pass
    return {"ok": True}


def _ideas_export_md():
    data = _ideas_data()
    name_of = {c["id"]: c["name"] for c in data["cats"]}
    lines = ["# 想法账本", "",
             f"> 导出于 {time.strftime('%Y-%m-%d %H:%M')}；共 {data['stats']['total']} 条 / {data['stats']['chains']} 个问题链", ""]
    for c in data["chains"]:
        cur = c["members"][-1]
        lines.append(f"## {cur.get('q', '?')}")
        for m in c["members"]:
            is_cur = m is cur
            cat = (m.get("cat") and name_of.get(m["cat"], "?")) or "未分类"
            src = {"user": "你定", "model": "模型", "inherited": "继承"}.get(m.get("cat_source"), "-")
            lines.append(f"- **{m.get('date', '?')}{'（现行）' if is_cur else '（旧版）'}** 〔{cat}·{src}〕 {m.get('c', '')}"
                         + (f"（理由：{m.get('r')}）" if m.get("r") else ""))
        lines.append("")
    return "\n".join(lines)

# ==== v1.6.0 定时任务页（root crontab 可视化；先备份后写，写失败回滚）====
CRON_BAK_DIR = "/root/work/server-backups"
_CRON_SPECIAL = ("@reboot", "@hourly", "@daily", "@weekly", "@monthly", "@yearly")


def _cron_read_lines():
    r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    return r.stdout.splitlines() if r.returncode == 0 else []


def _cron_backup():
    try:
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        fp = os.path.join(CRON_BAK_DIR, "crontab.bak-" + time.strftime("%Y%m%d-%H%M%S"))
        with open(fp, "w", encoding="utf-8") as f:
            f.write(cur)
        return fp
    except Exception:
        return ""


def _cron_parse(lines):
    items = []
    note = ""
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("#@ "):
            note = s[3:].strip()
            continue
        if not s:
            continue
        if s.startswith("#DISABLED# "):
            body = s[len("#DISABLED# "):]
            enabled = False
        elif s.startswith("#"):
            continue
        else:
            body = s
            enabled = True
        parts = body.split(None, 1)
        if parts and parts[0] in _CRON_SPECIAL or (parts and parts[0].startswith("@")):
            sched, cmd = parts[0], (parts[1] if len(parts) > 1 else "")
        elif len(parts) == 2 and len(body.split()) >= 6:
            f = body.split(None, 5)
            sched, cmd = " ".join(f[:5]), f[5]
        else:
            note = ""
            continue   # 环境变量等非任务行不进列表
        title, _, rem = note.partition("|")
        items.append({"idx": i, "enabled": enabled, "sched": sched, "cmd": cmd.strip(),
                      "title": title.strip() or "未命名任务", "note": rem.strip() or "（无备注）"})
        note = ""
    return items


def _cron_list():
    return {"items": _cron_parse(_cron_read_lines())}


def _cron_write_lines(lines):
    fp = _cron_backup()
    r = subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n", capture_output=True, text=True)
    if r.returncode != 0 and fp:
        try:   # 写失败回滚备份
            subprocess.run(["crontab", "-"], input=open(fp, encoding="utf-8").read(),
                           capture_output=True, text=True)
        except Exception:
            pass
    return r.returncode == 0, (r.stderr or "").strip()[:200], fp


def _cron_valid_sched(s):
    s = s.strip()
    if s in _CRON_SPECIAL:
        return True
    f = s.split()
    if len(f) != 5:
        return False
    pat = re.compile(r"^(\*|\*/\d+|\d+(?:-\d+)?(?:/\d+)?)$")
    for x in f:
        for seg in x.split(","):
            if not pat.match(seg):
                return False
    return True


def _cron_toggle(idx, fp):
    lines = _cron_read_lines()
    if idx < 0 or idx >= len(lines):
        return 400, {"error": "行号越界，请刷新"}
    s = lines[idx].strip()
    if fp and fp[:30] not in lines[idx]:
        return 409, {"error": "crontab 已被其他改动影响，请刷新后重试"}
    if s.startswith("#DISABLED# "):
        lines[idx] = s[len("#DISABLED# "):]
    elif s.startswith("#") or not s:
        return 400, {"error": "该行不是可开关的任务行，请刷新"}
    else:
        lines[idx] = "#DISABLED# " + s
    ok, err, bak = _cron_write_lines(lines)
    if not ok:
        return 500, {"error": "crontab 写入失败(已回滚): " + err}
    return 200, {"ok": True, "bak": bak}


def _cron_settime(idx, sched, fp):
    sched = (sched or "").strip()
    if not _cron_valid_sched(sched):
        return 400, {"error": "计划表达式非法（5 段 cron 如 30 4 * * *，或 @reboot/@daily/@hourly/@weekly/@monthly）"}
    lines = _cron_read_lines()
    if idx < 0 or idx >= len(lines):
        return 400, {"error": "行号越界，请刷新"}
    s = lines[idx].strip()
    body = s[len("#DISABLED# "):] if s.startswith("#DISABLED# ") else s
    if fp and fp[:30] not in body:
        return 409, {"error": "crontab 已被其他改动影响，请刷新后重试"}
    parts = body.split(None, 1)
    if parts and parts[0].startswith("@"):
        new = (sched + " " + (parts[1] if len(parts) > 1 else "")).strip()
    else:
        f = body.split(None, 5)
        if len(f) < 6:
            return 400, {"error": "该行不是标准 5 段 cron 任务，请在 SSH 里改"}
        new = sched + " " + f[5]
    if s.startswith("#DISABLED# "):
        new = "#DISABLED# " + new
    lines[idx] = new
    ok, err, bak = _cron_write_lines(lines)
    if not ok:
        return 500, {"error": "crontab 写入失败(已回滚): " + err}
    return 200, {"ok": True, "bak": bak}


_q = httpx.Client(timeout=30)
_auth_cache = {"raw": None, "ts": 0}
_bruteforce = {}   # v1.4 防爆破 {ip: [连败次数, 最近失败ts]}，成功清零，重启清零


def _auth_pair():
    if _auth_cache["raw"] is None or time.time() - _auth_cache["ts"] > 60:
        try:
            _auth_cache["raw"] = open(AUTH_FILE, encoding="utf-8").read().strip()
        except Exception:
            _auth_cache["raw"] = ":"
        _auth_cache["ts"] = time.time()
    return _auth_cache["raw"]


def _tail_lines(path, n):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.readlines()[-int(n):]
    except Exception as e:
        return [f"(读不到 {path}: {e})"]


def _audit_view(n):
    rows = []
    for ln in _tail_lines(AUDIT_LOG, n):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except Exception:
            rows.append({"ts": "?", "mode": "坏行", "sec": 0, "user": ln[:80]})
    today = time.strftime("%Y-%m-%d")
    td = [r for r in rows if str(r.get("ts", "")).startswith(today)]
    brains = {}
    for r in td:
        brains[r.get("mode", "?")] = brains.get(r.get("mode", "?"), 0) + 1
    secs = [float(r.get("sec") or 0) for r in td if r.get("sec") is not None]
    stats = {
        "today": len(td),
        "brains": brains,
        "avg_sec": round(sum(secs) / len(secs), 1) if secs else 0,
        "log_file": AUDIT_LOG,
    }
    return {"stats": stats, "rows": list(reversed(rows))}


def _payload_text(p):
    if not isinstance(p, dict):
        return str(p)
    if p.get("text"):
        base = str(p["text"])
    else:
        base = json.dumps(p, ensure_ascii=False)
    role = p.get("role")
    ts = p.get("ts") or p.get("time")
    head = f"[{role}] " if role else ""
    stamp = ""
    if ts:
        try:
            stamp = time.strftime("%m-%d %H:%M", time.localtime(int(ts) / 1000)) + " "
        except Exception:
            stamp = ""
    return stamp + head + base


def _scroll_all(coll, max_points=2000):
    """带 offset 翻页拉点，生成器逐页吐，防大集合一次进内存。"""
    offset = None
    got = 0
    while got < max_points:
        body = {"limit": 500, "with_payload": True, "with_vector": False}
        if offset is not None:
            body["offset"] = offset
        r = _q.post(f"{QDRANT}/collections/{coll}/points/scroll", json=body)
        r.raise_for_status()
        d = r.json()["result"]
        pts = d.get("points") or []
        if not pts:
            break
        for p in pts:
            yield p
        got += len(pts)
        offset = d.get("next_page_offset")
        if offset is None:
            break


def _scroll_ids(coll, cap=50000):
    """v2.3.6：全量点 id 升序清单（不带 payload/向量，一次滚动拉完；cap 防御极端大集合）。"""
    ids, cur = [], None
    while len(ids) < cap:
        body = {"limit": 500, "with_payload": False, "with_vector": False}
        if cur is not None:
            body["offset"] = cur
        r = _q.post(f"{QDRANT}/collections/{coll}/points/scroll", timeout=30, json=body)
        r.raise_for_status()
        d = r.json()["result"]
        pts = d.get("points") or []
        if not pts:
            break
        ids.extend(p["id"] for p in pts)
        cur = d.get("next_page_offset")
        if cur is None:
            break
    return ids[:cap]


def _payloads_by_ids(coll, ids):
    """v2.3.6：按 id 批量取 payload（500/批），返回 {id: payload}；已删 id 自然缺席。"""
    out = {}
    for i in range(0, len(ids), 500):
        r = _q.post(f"{QDRANT}/collections/{coll}/points", timeout=30,
                    json={"ids": ids[i:i + 500], "with_payload": True, "with_vector": False})
        r.raise_for_status()
        for p in (r.json().get("result") or []):
            out[p["id"]] = p.get("payload")
    return out


def _memories_offset(v):
    """v2.3.2：URL 游标→Qdrant offset（点 id 整数优先，UUID 原样）。"""
    if v in (None, "", "null"):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return str(v)


def _memories_count(coll, ql):
    """v2.3.2：带关键词的真实命中总数（全扫计数，不带向量；万条亚秒级）。"""
    c = 0
    for p in _scroll_all(coll, max_points=10 ** 9):
        txt = _payload_text(p.get("payload"))
        if ql in txt.lower():
            c += 1
    return c


def _memories_view(coll, q, n, offset=None):
    """v2.3.6 倒序游标分页（用户令：最新在前）：先拉全量 id 升序清单再倒着走，
    offset=倒序清单里的位置游标（整数）；q 过滤/首屏 total 语义与 v2.3.2 一致。"""
    n = min(int(n or 100), 500)
    ql = (q or "").strip().lower()
    desc = _scroll_ids(coll)[::-1]          # 新→旧
    i = 0 if offset in (None, "", "null") else max(0, min(int(offset), len(desc)))
    out = []
    while i < len(desc) and len(out) < n:
        chunk = desc[i:i + 500]
        pl = _payloads_by_ids(coll, chunk)
        for j, pid in enumerate(chunk):
            if pid not in pl:               # 翻页间隙被删的点跳过
                continue
            txt = _payload_text(pl[pid])
            if ql and ql not in txt.lower():
                continue
            out.append({"id": pid, "text": txt[:300]})
            if len(out) >= n:
                i += j + 1                  # 游标=已检到的下一条（块尾未检行不丢）
                break
        else:
            i += len(chunk)
    has_more = i < len(desc)
    total = None
    if offset in (None, "", "null"):        # 首屏才算总数，续批前端持有
        total = len(desc) if not ql else _memories_count(coll, ql)
    return {"coll": coll, "count": len(out), "items": out,
            "next_offset": i if has_more else None,
            "has_more": has_more, "total": total}


def _csv_export(coll, wfile):
    wfile.write(b"\xef\xbb\xbf")  # utf-8-sig BOM，Excel 直开不乱码
    buf = io.StringIO()
    wr = csv.writer(buf)
    wr.writerow(["id", "text"])
    count = 0
    for p in _scroll_all(coll, max_points=10**9):
        wr.writerow([p["id"], _payload_text(p.get("payload"))])
        count += 1
        if count % 200 == 0:  # 每 200 行冲一次缓冲，流式下压内存
            wfile.write(buf.getvalue().encode("utf-8"))
            buf = io.StringIO()
            wr = csv.writer(buf)
    wfile.write(buf.getvalue().encode("utf-8"))
    return count


def _run_export_chats():
    try:
        pr = subprocess.run(["/root/memvenv/bin/python3", EXPORT_SCRIPT],
                            capture_output=True, text=True, timeout=180)
        tail = (pr.stdout or "")[-400:] + (pr.stderr or "")[-200:]
    except Exception as e:
        return {"error": str(e)[:200]}
    files = []
    try:
        for root, _dirs, fs in os.walk(EXPORT_DST):
            for fn in fs:
                fp = os.path.join(root, fn)
                files.append({"name": os.path.relpath(fp, EXPORT_DST),
                              "size": os.path.getsize(fp),
                              "mtime": time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(fp)))})
    except Exception:
        pass
    files.sort(key=lambda x: x["name"])
    return {"returncode": pr.returncode, "script_tail": tail[-500:], "files": files[-50:]}


def _journal_list():
    """v1.3：chat_journal 全量按 ts 倒序（一条=一天）。集合不存在/空=空列表。"""
    r = _q.post(f"{QDRANT}/collections/chat_journal/points/scroll", timeout=30,
                json={"limit": 400, "with_payload": True, "with_vector": False})
    pts = (r.json().get("result") or {}).get("points") or []
    rows = []
    for p in pts:
        pl = p.get("payload") or {}
        rows.append({"date": str(pl.get("date") or ""), "weekday": str(pl.get("weekday") or ""),
                     "text": str(pl.get("text") or ""), "ts": pl.get("ts") or 0})
    rows.sort(key=lambda x: x["ts"], reverse=True)
    return {"count": len(rows), "items": rows}


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("[台]", fmt % args, flush=True)

    def _authed(self):
        pair = _auth_pair()
        if ":" not in pair:
            return False
        ip = self.client_address[0]
        st = _bruteforce.get(ip)
        if st and st[0] >= 5:   # v1.4 防爆破：连错 5 次后延迟递增（2^(n-5) 秒，上限 120s），成功清零
            wait = min(120, 2 ** (st[0] - 5))
            if time.time() - st[1] < wait:
                time.sleep(min(20, wait / 8))
        want = "Basic " + base64.b64encode(pair.encode("utf-8")).decode()
        got = self.headers.get("Authorization", "")
        ok = got == want
        if ok:
            _bruteforce.pop(ip, None)
        else:
            c = (_bruteforce.get(ip, [0, 0]))[0] + 1
            _bruteforce[ip] = [c, time.time()]
            if c % 10 == 0:
                print(f"[台] ⚠️ {ip} 认证失败累计 {c} 次", flush=True)
        return ok

    def _deny(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="tavern-console"')
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _file(self, path, ctype):
        try:
            data = open(path, "rb").read()
        except Exception:
            self._json(404, {"error": "static missing"})
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "max-age=86400")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path, _, qs = self.path.partition("?")
        params = {}
        for kv in qs.split("&"):
            if "=" in kv:
                k, _, v = kv.partition("=")
                params[k] = unquote(v)
        try:
            if path == "/healthz":
                self._json(200, {"status": "ok", "service": "tavern-console"})
                return
            if not self._authed():
                self._deny()
                return
            if path == "/api/expr/list":
                self._json(200, _expr_api_list())
            elif path == "/api/expr/files":
                who = re.sub(r"[^a-z0-9_]", "", params.get("who") or "")[:24]
                emo = re.sub(r"[^a-zA-Z0-9_]", "", params.get("emo") or "")[:40]
                self._json(200, {"who": who, "emo": emo,
                                 "files": _expr_group_files(who, emo) if (who and emo) else []})
            elif path == "/api/expr/preview":
                who = re.sub(r"[^a-z0-9_]", "", params.get("who") or "")[:24]
                emo = re.sub(r"[^a-zA-Z0-9_]", "", params.get("emo") or "")[:40]
                gfn = re.sub(r"[^a-zA-Z0-9_.-]", "", params.get("f") or "")[:80]
                lp = os.path.join(EXPR_ASSETS, who, f"{emo}.png")
                if who and emo and gfn:
                    gp = os.path.join(EXPR_ASSETS, who, emo, gfn)
                    if os.path.isfile(gp):
                        lp = gp
                if not (who and emo and os.path.isfile(lp)):
                    gfiles = _expr_group_files(who, emo) if (who and emo) else []
                    if gfiles:
                        lp = os.path.join(EXPR_ASSETS, who, emo, gfiles[0])
                if not (who and emo and os.path.isfile(lp)):
                    self._json(404, {"error": "正本无此格（容器可能有货：先「从容器补缺」）"})
                    return
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "close")
                self.end_headers()
                with open(lp, "rb") as f:
                    self.wfile.write(f.read())
                self.close_connection = True


            if path == "/" or path == "/index.html":
                self._html()
            elif path == "/review":
                body = _review_page_html().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path == "/api/review/img":
                d = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_-]", "", params.get("d") or "")[:64]
                f = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_.-]", "", params.get("f") or "")[:80]
                fp = os.path.realpath(os.path.join(REVIEW_ROOT, d, f))
                if not (d and f and fp.startswith(os.path.realpath(REVIEW_ROOT) + os.sep)
                        and os.path.isfile(fp)):
                    self._json(404, {"error": "no such file"})
                    return
                self.send_response(200)
                self.send_header("Content-Type",
                                 "image/png" if fp.lower().endswith(".png") else "image/jpeg")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "close")
                self.end_headers()
                with open(fp, "rb") as fh:
                    self.wfile.write(fh.read())
                self.close_connection = True
            elif path == "/static/tabler.min.css":
                self._file(os.path.join(CONSOLE_DIR, "tabler.min.css"), "text/css; charset=utf-8")
            elif path == "/static/tabler.min.js":
                self._file(os.path.join(CONSOLE_DIR, "tabler.min.js"),
                           "application/javascript; charset=utf-8")
            elif path == "/static/chart.umd.js":
                self._file(os.path.join(CONSOLE_DIR, "chart.umd.js"),
                           "application/javascript; charset=utf-8")
            elif path == "/api/audit":
                self._json(200, _audit_view(int(params.get("n") or 200)))
            elif path == "/api/bridge":
                self._json(200, {"lines": [l.rstrip("\n") for l in _tail_lines(BRIDGE_LOG, int(params.get("n") or 100))]})
            elif path == "/api/collections":
                r = _q.get(f"{QDRANT}/collections")
                r.raise_for_status()
                names = [c["name"] for c in r.json()["result"]["collections"]]
                self._json(200, {"collections": names})
            elif path == "/api/ideas/list":
                self._json(200, _ideas_data())
            elif path == "/api/ideas/search":
                self._json(200, _ideas_search(params.get("q") or "", params.get("mode") or "sem"))
            elif path == "/api/ideas/export":
                fmt = params.get("fmt") or "md"
                if fmt == "jsonl":
                    body = open(IDEA_FILE, "rb").read() if os.path.exists(IDEA_FILE) else b""
                    ctype, fname = "application/octet-stream", "ideas_ledger.jsonl"
                else:
                    body = _ideas_export_md().encode("utf-8")
                    ctype, fname = "text/markdown; charset=utf-8", "ideas-ledger.md"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                self.close_connection = True
            elif path == "/api/memories":
                self._json(200, _memories_view(params.get("coll") or "chat_memory",
                                               params.get("q") or "", params.get("n") or 100,
                                               params.get("offset")))
            elif path == "/api/point":
                coll = params.get("coll") or "chat_memory"
                pid = params.get("id") or ""  # v1.0 的 params 是扁平 dict（值=字符串），勿用 parse_qs 的 [0] 惯例
                if str(pid).isdigit():
                    pid = int(pid)
                pl = _point_full(coll, pid)
                self._json(200, {"id": pid, "payload": pl,
                                 "text": pl.get("text") or pl.get("summary") or ""})
            elif path == "/api/palace/taxonomy":
                c, d = _palace("GET", "/taxonomy"); self._json(c, d)
            elif path == "/api/palace/list":
                c, d = _palace("GET", "/list", params={"room": params.get("room"),
                                                       "limit": params.get("limit") or 50,
                                                       "offset": params.get("offset") or 0})
                self._json(c, d)
            elif path == "/api/palace/get":
                c, d = _palace("GET", "/get", params={"id": params.get("id")}); self._json(c, d)
            elif path == "/api/palace/search":
                c, d = _palace("POST", "/recall", body={"query": params.get("q"), "limit": 20})
                self._json(c, d)
            elif path == "/api/ingest/recent":
                self._json(200, _ingest_recent(int(params.get("n") or 100)))
            elif path == "/api/journal/list":
                self._json(200, _journal_list())
            elif path == "/api/gate":
                self._json(200, _gate("GET"))
            elif path == "/api/export/csv":
                coll = params.get("coll") or "chat_memory"
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{coll}-{time.strftime("%Y%m%d-%H%M%S")}.csv"')
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True
                n = _csv_export(coll, self.wfile)
                print(f"[台] CSV 导出 {coll} 共 {n} 行", flush=True)
            else:
                self._json(404, {"error": "not found"})
        except Exception as e:
            try:
                self._json(500, {"error": str(e)[:300]})
            except Exception:
                pass

    def do_POST(self):
        try:
            if not self._authed():
                self._deny()
                return
            n = int(self.headers.get("Content-Length", 0) or 0)
            req = json.loads(self.rfile.read(n) or b"{}")
            if self.path.rstrip("/") == "/api/delete":
                coll = str(req.get("coll") or "")
                single = req.get("ids") is None
                raw_ids = [req.get("id")] if single else req.get("ids")  # v2.3.4 兼容旧单删 {"id":..}
                if not coll or not isinstance(raw_ids, list) or not raw_ids or any(i is None for i in raw_ids):
                    self._json(400, {"error": "coll 与 id/ids 必填"})
                    return
                if len(raw_ids) > 1000:
                    self._json(400, {"error": "一次最多 1000 条，请分批"})
                    return
                pids, trash, missing = [], [], []   # v2.3.4 批量删：逐条先抄后撕，一条留底失败=整批中止
                for raw in raw_ids:
                    pid = int(raw) if isinstance(raw, str) and raw.isdigit() else raw
                    pl = _point_full(coll, pid)   # v1.4.1 先抄后撕
                    if not pl:
                        missing.append(raw)
                        continue
                    fp = _trash_dump(coll, pid, pl)
                    if not fp:
                        self._json(500, {"error": f"留底失败 {pid}，已中止删除（回收站目录不可写？）"})
                        return
                    pids.append(pid)
                    trash.append(fp)
                if not pids:
                    if single:
                        self._json(404, {"error": "点不存在"})
                    else:
                        self._json(200, {"deleted": 0, "missing": missing})
                    return
                r = _q.post(f"{QDRANT}/collections/{coll}/points/delete",
                            json={"points": pids})
                ok = r.status_code == 200
                self._json(200 if ok else 502,
                           {"deleted": len(pids) if ok else 0, "trash": trash, "missing": missing,
                            "qdrant": r.text[:200]})
            elif self.path.rstrip("/") == "/api/update":
                coll = str(req.get("coll") or "")
                pid = req.get("id")
                text = str(req.get("text") or "")
                if not coll or pid is None or not text.strip():
                    self._json(400, {"error": "coll/id/text 必填"})
                    return
                if isinstance(pid, str) and pid.isdigit():
                    pid = int(pid)
                pl = _point_full(coll, pid)
                if not pl:
                    self._json(404, {"error": "点不存在"})
                    return
                key = "summary" if ("summary" in pl and "text" not in pl) else "text"
                pl[key] = text
                if req.get("role"):
                    pl["role"] = str(req["role"])
                r = _q.post(f"{QDRANT}/collections/{coll}/points/payload",
                            json={"payload": pl, "points": [pid]})
                ok = r.status_code == 200
                self._json(200 if ok else 502, {"updated": ok, "qdrant": r.text[:200]})
            elif self.path.rstrip("/") == "/api/add":
                coll = str(req.get("coll") or "chat_memory")
                text = str(req.get("text") or "").strip()
                if not text:
                    self._json(400, {"error": "text 必填"})
                    return
                pid = int(time.time() * 1000)
                sid = str(req.get("sessionId") or "st-live")
                if coll == "chat_summary":
                    pl = {"sessionId": sid, "summary": text, "ts": pid,
                          "source": "console-manual", "up_to": 0}
                elif coll == "chat_memory":
                    pl = {"sessionId": sid, "role": str(req.get("role") or "user"),
                          "text": text, "ts": pid}
                else:
                    pl = {"text": text, "ts": pid}
                r = _q.put(f"{QDRANT}/collections/{coll}/points?wait=true",
                           json={"points": [{"id": pid, "vector": _vec_for(text), "payload": pl}]})
                ok = r.status_code == 200
                self._json(200 if ok else 502, {"added": ok, "id": pid, "qdrant": r.text[:200]})
            elif self.path.rstrip("/") == "/api/palace/add":
                c, d = _palace("POST", "/add", body=req); self._json(c, d)
            elif self.path.rstrip("/") == "/api/palace/update":
                c, d = _palace("POST", "/update", body=req); self._json(c, d)
            elif self.path.rstrip("/") == "/api/palace/delete":
                c, d = _palace("POST", "/delete", body=req); self._json(c, d)
            elif self.path.rstrip("/") == "/api/journal/update":
                date = str(req.get("date") or "").strip()
                text = str(req.get("text") or "").strip()
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", date) or not text:
                    self._json(400, {"error": "date/text 必填（date=YYYY-MM-DD）"})
                    return
                pid = int(date.replace("-", ""))
                if not _point_full("chat_journal", pid):
                    self._json(404, {"error": "该日期没有日志条"})
                    return
                r1 = _q.post(f"{QDRANT}/collections/chat_journal/points/payload",
                             json={"payload": {"text": text}, "points": [pid]})
                r2 = _q.put(f"{QDRANT}/collections/chat_journal/points/vectors?wait=true",
                            json={"points": [{"id": pid, "vector": _vec_for(text)}]})
                ok = r1.status_code == 200 and r2.status_code == 200
                self._json(200 if ok else 502, {"updated": ok,
                           "qdrant": r1.text[:120] + " | " + r2.text[:120]})
            elif self.path.rstrip("/") == "/api/journal/delete":
                date = str(req.get("date") or "").strip()
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
                    self._json(400, {"error": "date 须为 YYYY-MM-DD"})
                    return
                pid = int(date.replace("-", ""))
                pl = _point_full("chat_journal", pid)   # v1.4.1 先抄后撕
                if not pl:
                    self._json(404, {"error": "该日期没有日志条"})
                    return
                fp = _trash_dump("chat_journal", pid, pl)
                if not fp:
                    self._json(500, {"error": "留底失败，已中止删除"})
                    return
                r = _q.post(f"{QDRANT}/collections/chat_journal/points/delete",
                            json={"points": [pid]})
                ok = r.status_code == 200
                self._json(200 if ok else 502, {"deleted": ok, "trash": fp, "qdrant": r.text[:200]})
            elif self.path.rstrip("/") == "/api/bridge_healthz":
                try:
                    br = httpx.get(BRIDGE + "/healthz", timeout=5)
                    self._json(br.status_code, br.json())
                except Exception as e:
                    self._json(502, {"error": f"桥不可达: {str(e)[:150]}"})
            elif self.path.rstrip("/") == "/api/receipt/list":
                self._json(200, _receipt_list(req.get("date")))
            elif self.path.rstrip("/") == "/api/receipt/detail":
                self._json(200, _receipt_detail(req.get("file"), req.get("line")))
            elif self.path.rstrip("/") == "/api/brain/get":
                self._json(200, _brain_binding_get())
            elif self.path.rstrip("/") == "/api/brain/binding":
                c, d = _brain_binding_set(str(req.get("provider") or ""), str(req.get("glm_effort") or ""),
                                          str(req.get("ds_effort") or "high"))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/ideas/retag":
                try:
                    pid = int(req.get("id"))
                except Exception:
                    self._json(400, {"error": "bad id"})
                    return
                self._json(200, _ideas_retag(pid, str(req.get("cat") or "")[:32]))
            elif self.path.rstrip("/") == "/api/persona/list":
                self._json(200, _persona_list())
            elif self.path.rstrip("/") == "/api/persona/save":
                c, d = _persona_save(str(req.get("slot") or ""), req.get("text"))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/journal/generate":
                date = str(req.get("date") or "").strip()
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", date) or date >= time.strftime("%Y-%m-%d"):
                    self._json(400, {"error": "date 须为 YYYY-MM-DD 且早于今天"})
                    return
                c, d = _journal_generate(date)   # v1.4.2 本台自带浓缩（桥 /v1/journal/generate 已废）
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/ingest/submit":
                ids = req.get("ids") or []
                if not ids:
                    self._json(400, {"error": "ids 必填（先勾选对话）"})
                    return
                self._json(200, _ingest_submit(ids))
            elif self.path.rstrip("/") == "/api/cron/list":
                self._json(200, _cron_list())
            elif self.path.rstrip("/") == "/api/cron/toggle":
                try:
                    cidx = int(req.get("idx"))
                except (TypeError, ValueError):
                    self._json(400, {"error": "idx 必填"})
                    return
                c, d = _cron_toggle(cidx, str(req.get("fp") or ""))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/cron/settime":
                try:
                    cidx = int(req.get("idx"))
                except (TypeError, ValueError):
                    self._json(400, {"error": "idx 必填"})
                    return
                c, d = _cron_settime(cidx, str(req.get("sched") or ""), str(req.get("fp") or ""))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/keys/list":
                self._json(200, _keys_list())
            elif self.path.rstrip("/") == "/api/keys/reveal":
                c, d = _keys_reveal(str(req.get("slot") or ""))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/keys/save":
                c, d = _keys_save(str(req.get("slot") or ""), str(req.get("key") or ""), req.get("sync_owi"))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/exam/list":
                self._json(200, _exam_list())
            elif self.path.rstrip("/") == "/api/exam/add":
                c, d = _exam_add(str(req.get("text") or ""), str(req.get("topic") or ""))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/bparams/get":
                self._json(200, _bparams_get())
            elif self.path.rstrip("/") == "/api/balance/ping":
                # v2.1.0 余额红绿灯（手动按钮；转发桥 /balance/ping，桥侧 max_tokens=1 实弹）
                try:
                    r = httpx.get(BRIDGE + "/balance/ping", timeout=45)
                    self._json(200, r.json())
                except Exception as e:
                    self._json(200, {"state": "yellow", "error": f"桥不可达: {str(e)[:120]}"})
            elif self.path.rstrip("/") == "/api/brain/probe":
                # v2.1.0 手动探活（转发桥 /brain/probe）
                try:
                    r = httpx.post(BRIDGE + "/brain/probe", timeout=20)
                    self._json(200, r.json())
                except Exception as e:
                    self._json(502, {"error": f"桥不可达: {str(e)[:120]}"})
            elif self.path.rstrip("/") == "/api/bparams/set":
                c, d = _bparams_set(str(req.get("key") or ""), req.get("value"))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/bparams/reset":
                c, d = _bparams_reset()
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/affection":
                # v2.1.0 好感度当前值（用户令「调参控件旁显示当前值」）：转发桥 GET /affection
                try:
                    r = httpx.get(BRIDGE + "/affection", timeout=8)
                    self._json(200, r.json())
                except Exception as e:
                    self._json(502, {"error": f"桥不可达: {str(e)[:120]}"})
            elif self.path.rstrip("/") == "/api/bondscore/set":
                c, d = _bond_score_set(req.get("score"))
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/tokens/list":
                self._json(200, _tokens_list())
            elif self.path.rstrip("/") == "/api/exam/reset":
                try:
                    pid = int(req.get("id"))
                except (TypeError, ValueError):
                    self._json(400, {"error": "id 必填"})
                    return
                c, d = _exam_reset(pid)
                self._json(c, d)
            elif self.path.rstrip("/") == "/api/export/chats":
                self._json(200, _run_export_chats())
            # ==== v2.1.0 表情柜 ====
            elif self.path.rstrip("/") == "/api/expr/upload":
                who = re.sub(r"[^a-z0-9_]", "", str(req.get("who") or ""))[:24]
                emo = re.sub(r"[^a-zA-Z0-9_]", "", str(req.get("emo") or ""))[:40]
                b64 = str(req.get("data_b64") or "")
                if not (who and emo and b64):
                    self._json(400, {"error": "who/emo/图数据必填"})
                    return
                import base64 as _b64
                try:
                    raw = _b64.b64decode(b64)
                except Exception:
                    self._json(400, {"error": "图数据解码失败"})
                    return
                if len(raw) < 100 or len(raw) > 15 * 1024 * 1024 or not raw[:8].startswith(b"\x89PNG"):
                    self._json(400, {"error": "仅支持 PNG（100B~15MB）"})
                    return
                gdir = os.path.join(EXPR_ASSETS, who, emo)
                os.makedirs(gdir, exist_ok=True)
                fname = f"{time.strftime('%H%M%S')}{int(time.time() * 1000) % 1000:03d}.png"
                lp = os.path.join(gdir, fname)
                with open(lp, "wb") as f:
                    f.write(raw)
                ok, out = _expr_push_group(who, emo)
                self._json(200 if ok else 502, {"local_saved": lp, "remote_pushed": ok,
                                                "grp_n": len(_expr_group_files(who, emo)), "docker": out})
            elif self.path.rstrip("/") == "/api/expr/delete":
                who = re.sub(r"[^a-z0-9_]", "", str(req.get("who") or ""))[:24]
                emo = re.sub(r"[^a-zA-Z0-9_]", "", str(req.get("emo") or ""))[:40]
                if not (who and emo):
                    self._json(400, {"error": "who/emo 必填"})
                    return
                gfn = re.sub(r"[^a-zA-Z0-9_.-]", "", str(req.get("f") or ""))[:80]
                if gfn:
                    gfp = os.path.join(EXPR_ASSETS, who, emo, gfn)
                    if not os.path.isfile(gfp):
                        self._json(404, {"error": "组内无此图"})
                        return
                    tdir = os.path.join(EXPR_BAK, time.strftime("%Y%m%d-%H%M%S"), who, emo)
                    os.makedirs(tdir, exist_ok=True)
                    import shutil as _sh
                    _sh.copy2(gfp, os.path.join(tdir, gfn))
                    os.remove(gfp)
                    rok, rout = _expr_docker("exec", EXPR_CTR, "rm", "-f", f"{EXPR_CTR_DIR}/{who}/{emo}/{gfn}")
                    self._json(200, {"deleted": True, "file": gfn, "backup_dir": tdir, "remote_rm": bool(rok)})
                    return
                lp = os.path.join(EXPR_ASSETS, who, f"{emo}.png")
                gd = os.path.join(EXPR_ASSETS, who, emo)
                import shutil as _sh
                bak_sides, tdir = _expr_backup_one(who, emo)
                if os.path.isdir(gd):
                    try:
                        _sh.copytree(gd, os.path.join(tdir, emo + "_group"), dirs_exist_ok=True)
                        bak_sides = bak_sides + ["group"]
                    except Exception:
                        pass
                if os.path.exists(lp) and "local" not in bak_sides:
                    self._json(500, {"error": "正本留底失败，已中止删除"})
                    return
                if os.path.exists(lp):
                    os.remove(lp)
                if os.path.isdir(gd):
                    _sh.rmtree(gd)
                rok, rout = _expr_docker("exec", EXPR_CTR, "rm", "-f", f"{EXPR_CTR_DIR}/{who}/{emo}.png")
                rok2, rout2 = _expr_docker("exec", EXPR_CTR, "rm", "-rf", f"{EXPR_CTR_DIR}/{who}/{emo}")
                self._json(200, {"deleted": True, "backup_dir": tdir, "backup_sides": bak_sides,
                                 "remote_rm": bool(rok and rok2)})
            elif self.path.rstrip("/") == "/api/expr/sync":
                """正本→容器全量同步（expr_into_owi.sh 内置版；容器重建丢图后的一键恢复）。"""
                who = re.sub(r"[^a-z0-9_]", "", str(req.get("who") or ""))[:24]
                whos = [who] if who else _expr_who_dirs()
                done = {}
                for w in whos:
                    adir = os.path.join(EXPR_ASSETS, w)
                    if not os.path.isdir(adir):
                        continue
                    _expr_docker("exec", EXPR_CTR, "mkdir", "-p", f"{EXPR_CTR_DIR}/{w}")
                    ok, out = _expr_docker("cp", adir + "/.", f"{EXPR_CTR}:{EXPR_CTR_DIR}/{w}/")
                    done[w] = ok
                self._json(200, {"synced": done})
            elif self.path.rstrip("/") == "/api/expr/pull":
                """容器→正本补缺（只补正本没有的格子，不覆盖正本已有）。"""
                who = re.sub(r"[^a-z0-9_]", "", str(req.get("who") or ""))[:24]
                if not who:
                    self._json(400, {"error": "who 必填"})
                    return
                adir = os.path.join(EXPR_ASSETS, who)
                os.makedirs(adir, exist_ok=True)
                tmp = f"/tmp/expr_pull_{who}_{int(time.time())}"
                ok, out = _expr_docker("cp", f"{EXPR_CTR}:{EXPR_CTR_DIR}/{who}/.", tmp)
                if not ok:
                    self._json(404, {"error": f"容器无此角色目录：{out[:150]}"})
                    return
                pulled = []
                for f in os.listdir(tmp):
                    if not f.lower().endswith(".png"):
                        continue
                    dst = os.path.join(adir, f)
                    if not os.path.exists(dst):
                        import shutil
                        shutil.copy2(os.path.join(tmp, f), dst)
                        pulled.append(f)
                import shutil as _sh
                _sh.rmtree(tmp, ignore_errors=True)
                self._json(200, {"pulled": pulled})
            elif self.path.rstrip("/") == "/api/expr/addrole":
                who = re.sub(r"[^a-z0-9_]", "", str(req.get("who") or ""))[:24]
                if len(who) < 2:
                    self._json(400, {"error": "角色名（小写字母数字）至少 2 字符"})
                    return
                os.makedirs(os.path.join(EXPR_ASSETS, who), exist_ok=True)
                rok, rout = _expr_docker("exec", EXPR_CTR, "mkdir", "-p", f"{EXPR_CTR_DIR}/{who}")
                self._json(200, {"who": who, "local": True, "remote": rok})
            elif self.path.rstrip("/") == "/api/gate":
                patch = {k: bool(req[k]) for k in ("tts", "img") if k in req}
                self._json(200, _gate("POST", patch))

            else:
                self._json(404, {"error": "not found"})
        except Exception as e:
            try:
                self._json(500, {"error": str(e)[:300]})
            except Exception:
                pass

    def _html(self):
        html = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


PAGE = """<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>雷姆拉姆小屋 · 管理台</title>
<link rel="stylesheet" href="/static/tabler.min.css">
<style>pre.log{max-height:420px;overflow:auto;font-size:12px;background:#1a1e2c;color:#d6deeb;padding:12px;border-radius:6px}
.tabpane{display:none}.tabpane.active{display:block}
/* ==== v2.3.2 记忆库：限高内滚+粘性表头+回顶 ==== */
body.theme-dark{color-scheme:dark}
#mem-card{position:relative}
#pane-mem .table-responsive{max-height:calc(100vh - 296px);overflow:auto;outline:none;overscroll-behavior:contain;scrollbar-color:#66708a #d9dee7;scrollbar-width:thin}
body.theme-dark #pane-mem .table-responsive{scrollbar-color:#8a94b8 #202840}
#mem-table thead th{position:sticky;top:0;z-index:1;background:#fff;box-shadow:inset 0 -1px 0 rgba(0,0,0,.08)}
body.theme-dark #mem-table thead th{background:#1a2032;box-shadow:inset 0 -1px 0 #2a3350}
#mem-top{position:absolute;right:14px;bottom:14px;width:44px;height:44px;border-radius:50%;font-size:18px;z-index:2;box-shadow:0 2px 10px rgba(0,0,0,.35)}
/* ==== v1.6.1 夜间模式（手搓覆盖，Tabler 旧版无全套暗色）==== */
body.theme-dark{background:#131722;color:#d6deeb}
body.theme-dark .navbar{background:#161c2c;border-color:#262e47}
body.theme-dark .card{background:#1c2233;border-color:#2a3350;box-shadow:0 1px 2px rgba(0,0,0,.4);color:#d6deeb}
body.theme-dark .card-header{border-color:#2a3350}
body.theme-dark .card-body{color:#d6deeb}
body.theme-dark .card-title,body.theme-dark h1,body.theme-dark h3,body.theme-dark h4,body.theme-dark .h1,body.theme-dark h5,body.theme-dark b{color:#e2e8f5}
body.theme-dark .subheader{color:#8b94ab}
body.theme-dark .table{color:#d6deeb;--tblr-table-color:#d6deeb}
body.theme-dark .table thead th{color:#a8b1c7;border-color:#2a3350;background:#1a2032}
body.theme-dark .table td,body.theme-dark .table th{border-color:#262e47}
body.theme-dark .table-hover tbody tr:hover{background:#202840}
body.theme-dark .text-muted{color:#8b94ab!important}
body.theme-dark code{background:#232b44;color:#9fb6e8}
body.theme-dark .form-control,body.theme-dark .form-select{background:#161c2c;border-color:#2a3350;color:#d6deeb}
body.theme-dark .form-control::placeholder{color:#5d6a85}
body.theme-dark .btn-outline-primary{color:#7ba3e8;border-color:#3a4a72}
body.theme-dark .btn-outline-danger{color:#e87b88;border-color:#723a44}
body.theme-dark .btn-outline-success{color:#7be8a0;border-color:#3a7248}
body.theme-dark .btn-outline-secondary{color:#aab2c5;border-color:#3a4258}
body.theme-dark .btn-secondary{background:#2a3350;border-color:#2a3350;color:#d6deeb}
body.theme-dark .btn-outline-primary:hover,body.theme-dark .btn-outline-danger:hover,body.theme-dark .btn-outline-success:hover{color:#131722}
body.theme-dark .nav-pills .nav-link{color:#a8b1c7}
body.theme-dark .nav-pills .nav-link.active{background:#3b5bdb;color:#fff}
body.theme-dark a{color:#7ba3e8}
body.theme-dark .badge.bg-blue-lt{background:rgba(90,140,220,.18);color:#8ab4f8}
body.theme-dark .badge.bg-green-lt,body.theme-dark .badge.bg-success-lt{background:rgba(47,194,113,.16);color:#7be8a0}
body.theme-dark .badge.bg-red-lt{background:rgba(223,74,105,.16);color:#ff8ca3}
body.theme-dark .badge.bg-cyan-lt,body.theme-dark .badge.bg-azure-lt{background:rgba(67,181,220,.16);color:#7bd0e8}
body.theme-dark .badge.bg-secondary-lt{background:rgba(160,170,190,.16);color:#aab2c5}
body.theme-dark div[style*="background:#fff"]{background:#1c2233!important;color:#d6deeb}
body.theme-dark div[style*="background:#fff"] .text-muted{color:#8b94ab!important}
body.theme-dark tr[style*="#fff5f5"]{background:#3a2326!important}
body.theme-dark textarea.form-control{background:#161c2c;color:#d6deeb}
</style>
</head><body class="theme-light">
<script>try{if(localStorage.getItem('console-theme')==='dark'){document.body.classList.remove('theme-light');document.body.classList.add('theme-dark')}}catch(e){}</script>
<div class="page">
<header class="navbar navbar-expand-md d-print-none">
 <div class="container-xl">
  <h1 class="navbar-brand mb-0 h3">🧶 雷姆拉姆小屋 · 管理台</h1>
  <span class="badge bg-blue-lt ms-2" id="bridge-ver">统一管线 …</span>
  <button class="btn btn-sm ms-2" id="theme-btn" onclick="themeToggle()" title="白天/夜间模式切换">🌙</button>
 </div>
</header>
<div class="container-xl pt-3">
<ul class="nav nav-pills mb-3" id="tabs">
 <li class="nav-item"><a class="nav-link active" data-t="audit" href="#">运行小票</a></li>
 <li class="nav-item"><a class="nav-link" data-t="mem" href="#">记忆库</a></li>
 <li class="nav-item"><a class="nav-link" data-t="palace" href="#">记忆宫(云)</a></li>
 <li class="nav-item"><a class="nav-link" data-t="ingest" href="#">入库</a></li>
 <li class="nav-item"><a class="nav-link" data-t="brain" href="#">脑绑定</a></li>
 <li class="nav-item"><a class="nav-link" data-t="keys" href="#">API 钥匙</a></li>
 <li class="nav-item"><a class="nav-link" data-t="exam" href="#">学习</a></li>
 <li class="nav-item"><a class="nav-link" data-t="tokens" href="#">Token</a></li>
 <li class="nav-item"><a class="nav-link" data-t="bparams" href="#">桥参数</a></li>
 <li class="nav-item"><a class="nav-link" data-t="persona" href="#">人设底稿</a></li>
 <li class="nav-item"><a class="nav-link" data-t="cron" href="#">定时任务</a></li>
 <li class="nav-item"><a class="nav-link" data-t="export" href="#">导出</a></li>
 <li class="nav-item"><a class="nav-link" data-t="help" href="#">说明</a></li>
 <li class="nav-item"><a class="nav-link" data-t="expr" href="#">表情柜</a></li>
<li class="nav-item"><a class="nav-link" data-t="gate" href="#">资源总闸</a></li>
<li class="nav-item"><a class="nav-link" data-t="ideas" href="#">🧠 想法账本</a></li>
</ul>

<div class="tabpane active" id="pane-audit">
 <div class="row mb-3" id="stat-cards"></div>
 <div class="mb-2" id="rc-datebar"></div>
 <div class="card"><div class="card-header"><h3 class="card-title">运行小票（每轮一条：谁接的、捞了什么、注入了什么、首字/总耗时、写回了什么；点行看全文）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="receiptLoad()">刷新</button></div></div>
  <div class="table-responsive"><table class="table table-vcenter card-table" id="rc-table">
   <thead><tr><th>时间</th><th>模式</th><th>脑</th><th>用户话</th><th>注入块</th><th>召回源</th><th>首字ms</th><th>总耗时ms</th><th></th></tr></thead><tbody></tbody>
  </table></div></div>
 <div class="card mt-2" id="rc-detail-card" style="display:none"><div class="card-header"><h3 class="card-title" id="rc-d-title"></h3></div>
  <div class="card-body" id="rc-detail" style="font-size:12px"></div></div>
 <div class="card mt-3"><div class="card-header"><h3 class="card-title">桥运行日志（尾 100 行，bridge.log 人读流水）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="loadBridge()">刷新</button></div></div>
  <div class="card-body"><pre class="log" id="bridge-log">加载中…</pre></div></div>
</div>

<div class="tabpane" id="pane-mem">
 <div class="card mb-2"><div class="card-body py-2">
   <div class="row g-2 align-items-center">
    <div class="col-auto"><span class="badge bg-cyan-lt">新增一条记忆</span></div>
    <div class="col-auto"><input id="add-sid" class="form-control form-control-sm" value="st-live" style="width:120px" title="sessionId"></div>
    <div class="col-auto"><select id="add-role" class="form-select form-select-sm"><option value="user">user（用户）</option><option value="assistant">assistant（姐妹）</option></select></div>
    <div class="col"><input id="add-text" class="form-control form-control-sm" placeholder="内容正文（选 chat_summary 集合时=写入新前情摘要）" onkeydown="if(event.key=='Enter')addPoint()"></div>
    <div class="col-auto"><button class="btn btn-sm btn-success" onclick="addPoint()">➕ 加入</button></div>
   </div>
 </div></div>
 <div id="edit-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:99">
  <div style="background:#fff;max-width:760px;margin:8vh auto;padding:16px;border-radius:8px">
   <h5>✏️ 修改记忆 <span id="edit-id" class="text-muted" style="font-size:12px"></span></h5>
   <textarea id="edit-text" class="form-control" style="height:220px"></textarea>
   <div class="mt-2 text-end"><button class="btn btn-secondary me-1" onclick="closeEdit()">取消</button>
   <button class="btn btn-primary" onclick="saveEdit()">保存</button></div>
  </div>
 </div>
 <div class="card" id="mem-card"><div class="card-header row g-2">
   <div class="col-auto"><select id="coll" class="form-select" onchange="memSelReset()"></select></div>
   <div class="col-auto"><input id="q" class="form-control" placeholder="关键词过滤"></div>
   <div class="col-auto"><button class="btn btn-primary" onclick="loadMem()">查</button></div>
   <div class="col-auto"><button class="btn btn-outline-danger" id="mem-batch-del" onclick="memBatchDel()" disabled title="勾选行后点此批量删除；删前自动逐条留底">🗑 删除选中(<span id="mem-sel-n">0</span>)</button></div>
   <div class="col-auto"><span class="text-muted" id="mem-count"></span></div>
  </div>
  <div class="table-responsive" id="mem-wrap" tabindex="0" title="滚动到底自动续载；Home 回顶 / End 到底"><table class="table table-vcenter card-table" id="mem-table">
   <thead><tr><th style="width:36px"><input type="checkbox" id="mem-sel-all" title="全选已载入行" onclick="memSelAll(this)"></th><th style="width:90px">ID</th><th>内容</th><th style="width:70px">操作</th></tr></thead><tbody></tbody>
  </table></div>
  <button id="mem-top" class="btn btn-primary" type="button" aria-label="回到顶部" title="回到顶部" onclick="memTop()" style="display:none">↑</button></div></div>
</div>

<div class="tabpane" id="pane-palace">
 <div class="card mb-2"><div class="card-body py-2"><div class="row g-2 align-items-center">
  <div class="col-auto"><select id="pal-room" class="form-select form-select-sm" onchange="palLoad()"></select></div>
  <div class="col"><input id="pal-q" class="form-control form-control-sm" placeholder="语义搜索云端记忆宫（酒馆入库的那些）…" onkeydown="if(event.key=='Enter')palSearch()"></div>
  <div class="col-auto"><button class="btn btn-sm btn-primary" onclick="palSearch()">搜</button></div>
  <div class="col-auto"><button class="btn btn-sm" onclick="palLoad()">全部</button></div>
  <div class="col-auto"><button class="btn btn-sm btn-success" onclick="palAdd()">➕ 入宫一条</button></div>
 </div></div></div>
 <div class="card"><div class="card-body" id="pal-list" style="max-height:62vh;overflow:auto">加载中…</div></div>
</div>
<div id="pal-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:99">
 <div style="background:#fff;max-width:760px;margin:8vh auto;padding:16px;border-radius:8px">
  <h5>🏛 云宫抽屉 <span id="pal-id" class="text-muted" style="font-size:12px"></span></h5>
  <textarea id="pal-text" class="form-control" style="height:240px"></textarea>
  <div class="mt-2 text-end"><button class="btn btn-secondary me-1" onclick="document.getElementById('pal-modal').style.display='none'">取消</button>
  <button class="btn btn-danger me-1" onclick="palDelete()">删除</button>
  <button class="btn btn-primary" onclick="palSave()">保存</button></div>
 </div>
</div>

<div class="tabpane" id="pane-ingest">
 <div class="card mb-2"><div class="card-body py-2"><div class="row g-2 align-items-center">
  <div class="col-auto"><span class="badge bg-azure-lt">入库工作台</span></div>
  <div class="col-auto"><select id="ig-n" class="form-select form-select-sm"><option>50</option><option selected>100</option><option>200</option></select></div>
  <div class="col-auto"><button class="btn btn-sm btn-primary" id="ig-btn-load" onclick="igLoad()">加载对话</button></div>
  <div class="col-auto"><button class="btn btn-sm" onclick="igToggle(true)">全选</button></div>
  <div class="col-auto"><button class="btn btn-sm" onclick="igToggle(false)">清空</button></div>
  <div class="col"><span class="text-muted" style="font-size:12px">勾选要记的对话 → 点入库，书记员提炼成记忆条收进记忆宫（约30-120秒），失败可重点一次</span></div>
  <div class="col-auto"><button class="btn btn-sm btn-success" id="ig-btn-go" onclick="igSubmit()">📥 入库所勾</button></div>
 </div></div></div>
 <div class="card"><div class="card-body" id="ig-list" style="max-height:52vh;overflow:auto">点「加载对话」开始</div></div>
 <div class="card mt-2"><div class="card-body text-muted" id="ig-result">回执显示在这</div></div>
</div>

<div class="tabpane" id="pane-cron">
 <div class="card"><div class="card-header"><h3 class="card-title">定时任务（root crontab：开关=停用/启用，改时间即时生效；每次改动前自动备份到 server-backups/crontab.bak-*）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="cronLoad()">刷新</button></div></div>
  <div class="table-responsive"><table class="table table-vcenter card-table" id="cron-table">
   <thead><tr><th>状态</th><th>标题</th><th>备注（干嘛用的）</th><th>计划</th><th>命令</th><th>操作</th></tr></thead><tbody></tbody>
  </table></div></div>
 <div class="card mt-2"><div class="card-body text-muted" style="font-size:12px">新增任务：SSH 往 crontab 加两行——第一行 <code>#@ 标题 | 备注说明</code>，第二行标准 cron 行，本页即带备注显示。命令本体不提供网页编辑（防误操作），启停与改时间用上面按钮。</div></div>
</div>

<div class="tabpane" id="pane-brain">
 <div class="card"><div class="card-header"><h3 class="card-title">脑绑定总闸（两控件，改完下一句生效）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="brainLoad()">刷新</button></div></div>
  <div class="card-body">
   <p class="text-muted" style="font-size:12px">总闸决定「酒馆」线（含旧名与单人底稿线）由哪家脑驱动；三人两棒同跟（双人接力 1018 已停用）。计费属性：GLM=按量付费·DeepSeek=魔搭按次·local/cli=免费。桌宠/服务场景默认本地国外脑（cli），本页只切酒馆槽（场景槽见 bb-out 展示）。</p>
   <div class="row g-2 align-items-center">
    <div class="col-auto"><label class="form-label mb-0">脑</label>
     <select id="bb-provider" class="form-select form-select-sm" onchange="brainForm()">
      <option value="ds">DeepSeek·魔搭（酒馆专职·按次）</option><option value="glm">GLM-5.3·按量付费</option><option value="cli">本地国外脑·免费（Groq 经 EasyTier）</option><option value="local">本地模型·免费（18080）</option></select></div>
    <div class="col-auto"><label class="form-label mb-0" id="bb-effort-label">GLM 档位</label>
     <select id="bb-effort" class="form-select form-select-sm">
      <option value="low">low（快）</option><option value="high">high</option><option value="max">max</option></select></div>
    <div class="col-auto"><button class="btn btn-sm btn-primary" onclick="brainSave()">保存切换</button></div>
   </div>
   <div id="bb-out" class="mt-2 text-muted" style="font-size:12px"></div>
  </div></div>
 <div class="card"><div class="card-header"><h3 class="card-title">云CLI 与本地脑状态（手动按钮，页面零自动轮询）</h3>
   <div class="card-actions"><a class="btn btn-sm" href="http://10.14.14.1:8317/management.html" target="_blank">CLI 管理页↗</a></div></div>
  <div class="card-body">
   <div class="row g-2 align-items-center">
    <div class="col-auto"><button class="btn btn-sm" onclick="balancePing()">余额红绿灯（5.3 一发）</button></div>
    <div class="col-auto"><button class="btn btn-sm" onclick="brainProbe()">手动探活（本地脑/cli 脑）</button></div>
   </div>
   <div id="cli-status-out" class="mt-2 text-muted" style="font-size:12px">绿=付费余额正常 / 红=1113 余额不足（去充值）/ 黄=其他异常。探活不发模型调用。</div>
  </div></div>
</div>

<div class="tabpane" id="pane-keys">
 <div class="card"><div class="card-header"><h3 class="card-title">API 钥匙自助换发（换完钥匙来这里粘贴保存即可）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="keysLoad()">刷新指纹</button></div></div>
  <div class="card-body">
   <p class="text-muted" style="font-size:12px">明文存服务器原位（chmod 600，只有你能看）；👁 点开显示明文。保存后自动重启对应服务生效，旧钥匙就地留底 <code>.bak-时间戳</code>。</p>
   <div id="keys-cards"></div>
  </div></div>
</div>

<div class="tabpane" id="pane-exam">
 <div class="card"><div class="card-header"><h3 class="card-title">姐妹考官 · 题池管理（题=learning_points.jsonl，桥 v3.8.0 引擎按间隔重复自动排考；晨报每天 08:00 随口带一题）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="examLoad()">刷新</button></div></div>
  <div class="card-body">
   <div class="row g-2 mb-2">
    <div class="col-auto"><select id="exam-topic" class="form-select form-select-sm">
      <option value="学习">[学习]</option><option value="学习·Java">[学习·Java]</option><option value="学习·Qdrant">[学习·Qdrant]</option>
      <option value="学习·英语">[学习·英语]</option><option value="学习·炒股纪律">[学习·炒股纪律]</option></select></div>
    <div class="col"><input id="exam-new" class="form-control form-control-sm" placeholder="输入知识点（一句话），姐妹会把它变成问题来考你"></div>
    <div class="col-auto"><button class="btn btn-sm btn-primary" onclick="examAdd()">加题</button></div>
   </div>
   <div id="exam-stats" class="text-muted mb-1" style="font-size:12px"></div>
   <div class="table-responsive" style="max-height:420px;overflow:auto"><table class="table table-vcenter card-table" id="exam-table">
    <thead><tr><th>id</th><th>topic</th><th>知识点</th><th>状态</th><th></th></tr></thead><tbody></tbody></table></div>
   <div id="exam-out" class="text-muted mt-1" style="font-size:12px"></div>
  </div></div>
</div>

<div class="tabpane" id="pane-gate">
  <div class="card"><div class="card-body">
    <div class="d-flex justify-content-between align-items-center mb-1">
      <h1 class="card-title mb-0">本机资源总闸</h1>
      <button class="btn btn-sm btn-outline-secondary" onclick="gateLoad()">刷新</button>
    </div>
    <p class="text-secondary mb-1">云端直控本机（EasyTier→proxy :9233 v4.3）。治「生图/聊天互挤 8G 显存」。</p>
    <div id="gate-status">加载中…</div>
  </div></div>
</div>
<div class="tabpane" id="pane-ideas">
 <div class="card"><div class="card-header"><h3 class="card-title">🧠 想法账本（你的结论 decision journal）</h3>
   <div class="card-actions">
     <button class="btn btn-sm" onclick="ideasLoad()">刷新</button>
     <a class="btn btn-sm" href="/api/ideas/export?fmt=md">导出 MD</a>
     <a class="btn btn-sm" href="/api/ideas/export?fmt=jsonl">导出 JSONL</a>
   </div></div>
  <div class="card-body">
   <div class="row g-2 mb-2">
    <div class="col"><input id="ideas-q" class="form-control form-control-sm" placeholder="搜想法（语义=按意思翻，关键词=按字面翻）" onkeydown="if(event.key==='Enter')ideasSearch()"></div>
    <div class="col-auto"><select id="ideas-mode" class="form-select form-select-sm"><option value="sem">语义</option><option value="kw">关键词</option></select></div>
    <div class="col-auto"><button class="btn btn-sm btn-primary" onclick="ideasSearch()">搜</button></div>
    <div class="col-auto"><button class="btn btn-sm" onclick="ideasClear()">清</button></div>
   </div>
   <div class="row g-3">
    <div class="col-3"><div class="card p-2"><div id="ideas-cats"></div></div></div>
    <div class="col-9">
      <div id="ideas-stats" class="text-muted mb-2" style="font-size:12px"></div>
      <div id="ideas-list" style="max-height:calc(100vh - 320px);overflow:auto"></div>
    </div>
   </div>
   <p class="text-muted mt-2" style="font-size:12px">来源徽标：你定=口述｜模型=AI 从五类挑｜继承=同题接替沿用｜未分类=待归口。「其他」只有你能定（AI 禁选）。卡片点开看版本链+改类目，改完即时生效并留审计。</p>
  </div></div>
</div>

<div class="tabpane" id="pane-tokens">
 <div class="card"><div class="card-header"><h3 class="card-title">Token 消耗（桥 v3.8.1 起小票自带 usage；数据源=近 7 天执行小票）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="tokLoad()">刷新</button></div></div>
  <div class="card-body">
   <div id="tok-cards" class="row g-2 mb-2"></div>
   <canvas id="tok-chart" height="90"></canvas>
   <div class="table-responsive mt-2"><table class="table table-vcenter card-table" id="tok-mode-table">
    <thead><tr><th>今日模式分布</th><th>tokens</th></tr></thead><tbody></tbody></table></div>
   <div id="tok-out" class="text-muted mt-1" style="font-size:12px"></div>
  </div></div>
</div>

<div class="tabpane" id="pane-bparams">
 <div class="card"><div class="card-header"><h3 class="card-title">桥参数（每请求热读：保存后下一句话生效；改前自动留底）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="bpLoad()">刷新</button>
   <button class="btn btn-sm btn-outline-warning" onclick="bpReset()">恢复全部默认</button></div></div>
  <div class="card-body">
   <div class="card mb-2"><div class="card-body py-2">
    <b>好感度当前分</b> <span id="bp-score-now" class="text-muted" style="font-size:12px"></span>
    <div class="input-group input-group-sm mt-1">
     <input type="number" id="bp-score" class="form-control" placeholder="0-100" min="0" max="100">
     <button class="btn btn-primary" onclick="bpScoreSave()">改分（双重确认）</button>
    </div>
    <div id="bp-score-out" class="text-muted mt-1" style="font-size:12px"></div>
   </div></div>
   <div id="bp-cards"></div>
  </div></div>
</div>

<div class="tabpane" id="pane-persona">
 <div class="card"><div class="card-header"><h3 class="card-title">人设底稿（保存=下一句生效，旧稿自动留底 persona_trash）</h3>
   <div class="card-actions"><button class="btn btn-sm" onclick="personaLoad()">刷新</button></div></div>
  <div class="card-body">
   <ul class="nav nav-pills mb-2" id="ptabs">
    <li class="nav-item"><a class="nav-link active" data-p="duet" href="#">双人场景</a></li>
    <li class="nav-item"><a class="nav-link" data-p="ram" href="#">拉姆单线</a></li>
    <li class="nav-item"><a class="nav-link" data-p="rem" href="#">蕾姆单线</a></li>
    <li class="nav-item"><a class="nav-link" data-p="emt" href="#">艾米莉亚</a></li>
    <li class="nav-item"><a class="nav-link" data-p="trio" href="#">三人同场</a></li>
   </ul>
   <textarea id="persona-text" class="form-control" rows="16" style="font-size:12px;font-family:monospace"></textarea>
   <div class="row mt-2 g-2 align-items-center">
    <div class="col"><span id="persona-info" class="text-muted" style="font-size:12px"></span></div>
    <div class="col-auto"><button class="btn btn-sm btn-primary" onclick="personaSave()">保存当前稿</button></div>
   </div>
  </div></div>
</div>


<div class="tabpane" id="pane-expr">
 <div class="card mb-2"><div class="card-body py-2"><div class="row g-2 align-items-center">
  <div class="col-auto"><span class="badge bg-purple-lt">表情柜 v2.1.0</span> <span class="text-muted" style="font-size:12px">正本=/root/work/expr_assets（容器重建不丢）·容器副本=桥取图生效层·改动先备份 _backup/</span></div>
  <div class="col-auto"><button class="btn btn-sm btn-primary" onclick="exprSync()">⬆ 全部同步到容器</button></div>
  <div class="col-auto"><button class="btn btn-sm" onclick="exprPullCur()">⬇ 从容器补缺（当前角色）</button></div>
  <div class="col-auto"><input id="expr-newrole" class="form-control form-control-sm" placeholder="新角色名(小写)" style="width:130px"><button class="btn btn-sm btn-success ms-1" onclick="exprAddRole()">➕ 新角色</button></div>
  <div class="col-auto"><span class="text-muted" style="font-size:12px">🟢双有 🟡仅正本 🔴缺格</span></div>
 </div></div></div>
 <ul class="nav nav-pills mb-2" id="expr-tabs"></ul>
 <div class="card"><div class="card-body"><div class="row g-2" id="expr-grid" style="row-gap:14px">加载中…</div></div></div>
 <div id="expr-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:99" onclick="if(event.target===this)exprCloseBig()">
  <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:#fff;padding:12px;border-radius:8px;text-align:center">
   <h6 id="expr-big-title"></h6>
   <img id="expr-big-img" style="max-width:70vw;max-height:60vh">
   <div class="mt-2"><button class="btn btn-sm" onclick="exprCloseBig()">关闭</button></div>
  </div>
 </div>
 <input type="file" id="expr-file" accept="image/png" style="display:none" onchange="exprFilePicked()">
</div>

<div class="tabpane" id="pane-export">
 <div class="card"><div class="card-header"><h3 class="card-title">导出</h3></div><div class="card-body">
  <div class="row g-3">
   <div class="col-md-6"><div class="subheader">对话记忆 CSV</div>
    <div class="input-group mb-2"><select id="csv-coll" class="form-select"></select>
     <button class="btn btn-primary" onclick="csvExport()">下载 CSV</button></div>
    <div class="text-muted">流式导出整张集合（id+内容），utf-8 带 BOM，Excel 直开。</div></div>
   <div class="col-md-6"><div class="subheader">ST 存档导出（OWI→TXT/JSON）</div>
    <button class="btn btn-primary mb-2" id="btn-stexport" onclick="runChatsExport()">跑导出脚本</button>
    <div class="text-muted" id="stexport-note">调 export_chats_20260925.py，产物在 /root/work/st_exports。</div>
    <div id="stexport-files" class="mt-2" style="max-height:260px;overflow:auto"></div></div>
  </div>
 </div></div>
</div>

<div class="tabpane" id="pane-help">
 <div class="card"><div class="card-header"><h3 class="card-title">使用说明</h3></div><div class="card-body">
  <p><b>入库工作台（v1.4）：</b>「入库」签 → 加载对话 → 勾选要记的 → 点入库 → 页面直接显示回执。书记员只提炼你勾的内容，失败重点一次。这是记忆入库的唯一入口（桥内口令已摘除）。</p>
  <p><b>本台管什么：</b>运行小票（谁接的、多快、捞了什么——审计与小票已合一，统计随所选日翻动）、记忆库浏览/新增/修改/删除、导出。</p>
  <p><b>定时任务（v1.6.0）：</b>root crontab 可视化——启停开关、改计划时间即时生效；每条任务的标题/备注写在 crontab 的 <code>#@ 标题 | 备注</code> 注释行里；每次改动前自动备份到 server-backups/crontab.bak-*，写失败自动回滚。</p>
  <p><b>API 钥匙（v1.7.0）：</b>你在平台重新生成钥匙后，来这里粘贴保存即可。智谱/魔搭保存后自动重启桥（约5秒断连）；智谱可勾选同步 OWI 网页模型。旧钥匙就地留底 <code>.bak-时间戳</code>。明文只住服务器文件（chmod 600），👁 小眼睛点开看、合上清空。</p>
  <p><b>记忆治理（向量库全景）：</b>开 SSH 隧道后访问 Qdrant 官方 Dashboard——
  <code>ssh -i C:\\Users\\yourname\\.zcode\\keys\\cloud_ed25519 -L 15679:127.0.0.1:5679 -L 16333:127.0.0.1:6333 root@SERVER_IP -N</code><br>
  本台地址 <code>http://127.0.0.1:15679</code>；Qdrant 记忆治理 <code>http://127.0.0.1:16333/dashboard</code>（可看/可改全部分量集合，慎用写操作）。</p>
  <p><b>下拉入口：</b>酒馆（总入口，脑由「脑绑定」页两控件定，GLM/DS 切换）/ 酒馆三人（三姐妹一次生成）/ ram / rem / emt 三单人线；原生 GLM low/high/max 预设直连不走桥。酒馆双人接力已停用（1018 用户令，等 token 自由再开）。</p>
  <p><b>记忆宫召回：</b>每轮自动检索「主人」翅膀的记忆抽屉注入顶部（≥0.55 相关度过筛）。入库唯一入口=「入库」工作台签（勾选对话→书记员提炼→页面回执）；聊天里说「入库」只是普通话题，不触发任何动作。</p>
  <p><b>往日日志：</b>每天对话自动浓缩成带日期的日志页（chat_journal 集合）；每轮语义召回 top2 注入
  【往日日志】块，配合前情提要日期头，姐妹能自然说出"昨天/上周三"。日志签可翻/改/删/手动补账（正本是对话记忆，日志删了可重生成）。</p>
 </div></div>
</div>

</div></div>
<script src="/static/tabler.min.js"></script>
<script src="/static/chart.umd.js"></script>
<script>
const esc = s => (s??'').toString().replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
// ==== v1.6.1 夜间模式切换 ====
function themeToggle(){
  const b = document.body, dark = b.classList.toggle('theme-dark');
  b.classList.toggle('theme-light', !dark);
  try{ localStorage.setItem('console-theme', dark ? 'dark' : 'light'); }catch(e){}
  document.getElementById('theme-btn').textContent = dark ? '☀️' : '🌙';
}
try{ if(document.body.classList.contains('theme-dark')) document.getElementById('theme-btn').textContent = '☀️'; }catch(e){}
document.querySelectorAll('#tabs a').forEach(a => a.onclick = e => {
  e.preventDefault();
  document.querySelectorAll('#tabs a').forEach(x => x.classList.remove('active'));
  document.querySelectorAll('.tabpane').forEach(x => x.classList.remove('active'));
  a.classList.add('active');
  document.getElementById('pane-' + a.dataset.t).classList.add('active');
  if(a.dataset.t==='expr')exprLoad(EXPR_WHO);
  if(a.dataset.t==='gate')gateLoad();
  if(a.dataset.t==='ideas')ideasLoad();
});
// ==== v2.3.0 资源总闸 JS ====
var gateLast=null;
function gateRender(g){
  var el=document.getElementById('gate-status');if(!el)return;
  if(!g||g.ok===false){el.innerHTML='<span class="text-danger">本机总闸不在线（proxy 9233 未跑或 EasyTier 断）</span>';return;}
  gateLast=g;
  function btn(k){var on=g[k];return ' <button class="btn btn-sm '+(on?'btn-danger':'btn-success')+'" data-gk="'+k+'">'+(on?'关掉':'打开')+'</button>';}
  el.innerHTML='<div class="mb-1">🎙️ 本地语音引擎（cosyvoice 9235/9233·硬闸·关=聊天不再拉起引擎）：'+(g.tts?'🟢 开':'🔴 关')+btn('tts')+'</div>'
    +'<div class="mb-1">🎨 本地生图（ComfyUI·软闸·管 AI 开工检查）：'+(g.img?'🟢 开':'🔴 关')+btn('img')+'</div>'
    +'<div class="text-secondary">GPU 显存 '+(g.gpu||'?')+' ｜ 状态更新 '+(g.updated||'-')+'</div>'
    +'<div class="text-secondary">关语音后酒馆点喇叭报「语音总闸已关闭」=预期，文字聊天不受影响；生图闸管 AI（skill 开工必查）管不住第三方直连 8188。</div>';
}
function gateLoad(){
  fetch('/api/gate').then(function(r){return r.json();}).then(gateRender)
    .catch(function(e){var el=document.getElementById('gate-status');if(el)el.innerHTML='<span class="text-danger">加载失败: '+e+'</span>';});
}
function gateToggle(k){
  var p={};p[k]=!(gateLast&&gateLast[k]);
  fetch('/api/gate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)})
    .then(function(r){return r.json();}).then(gateRender);
}
document.getElementById('gate-status').addEventListener('click',function(ev){
  var b=ev.target.closest('button[data-gk]');if(b)gateToggle(b.dataset.gk);});

// ==== v2.4.0 想法账本 JS ====
var ideasData=null, ideasFilter='__all';
function ideasCatName(id){ if(!ideasData)return ''; var c=ideasData.cats.find(function(x){return x.id===id}); return c?c.name:(id||''); }
function ideasSrc(s){ return s==='user'?'你定':(s==='model'?'模型':(s==='inherited'?'继承':'未分类')); }
function ideasBadges(e){
  var cat=e.cat?('［'+ideasCatName(e.cat)+'·'+ideasSrc(e.cat_source)+'］'):'［未分类］';
  return '<span class="badge '+(e.cat?'bg-blue-lt':'bg-secondary-lt')+'">'+cat+'</span> '
   +(e.versions>1?'<span class="badge bg-purple-lt">第'+e.versions+'版</span> ':'')
   +'<span class="badge bg-green-lt">现行</span>';
}
function ideasCard(ch, hitInfo){
  var cur=ch.members[ch.members.length-1];
  var versions=ch.members.map(function(m,idx){
      var isCur=idx===ch.members.length-1;
      return '<div class="mb-2" style="font-size:13px;'+(isCur?'':'opacity:.75')+'"><b>'+esc(m.date||'?')+(isCur?'（现行）':'（旧版·已被取代）')+'</b> ［'+(m.cat?ideasCatName(m.cat):'未分类')+'·'+ideasSrc(m.cat_source)+'］<br>'+esc(m.c)+(m.r?'<br><span class="text-muted">理由：'+esc(m.r)+'</span>':'')+'</div>';
     }).join('');
  var det='<div id="ideas-det-'+cur.id+'" style="display:none" class="mt-2 ps-2 border-start">'+versions
   + '<div class="row g-1 align-items-center"><div class="col-auto"><select id="ideas-rt-'+cur.id+'" class="form-select form-select-sm">'
   + '<option value="">未分类</option>'+ideasData.cats.map(function(c){return '<option value="'+c.id+'"'+(cur.cat===c.id?' selected':'')+'>'+esc(c.name)+'</option>';}).join('')
   + '</select></div><div class="col-auto"><button class="btn btn-sm btn-primary" onclick="ideasRetag('+cur.id+')">改类目</button></div></div></div>';
  var hit=hitInfo?(' <span class="badge bg-orange-lt">命中'+(hitInfo.score?(' '+hitInfo.score):'')+(hitInfo.old?'·旧版':'')+'</span>'):'';
  return '<div class="card p-2 mb-2"><div style="cursor:pointer" onclick="var d=document.getElementById(\\'ideas-det-'+cur.id+'\\');d.style.display=(d.style.display===\\'none\\'?\\'\\':\\'none\\')"><b>'+esc(cur.q)+'</b>'+hit+'<div class="mt-1">'+ideasBadges(cur)+' <span class="text-muted" style="font-size:12px">'+(cur.date||'')+'</span></div></div>'+det+'</div>';
}
function ideasRender(hits){
  var el=document.getElementById('ideas-list'); if(!el||!ideasData)return;
  if(hits){ el.innerHTML=hits.length?hits.map(function(h){return ideasCard(h.chain,h);}).join(''):'<p class="text-muted">没翻到——换几个词试试语义搜，或者直接去酒馆问姐妹。</p>'; return; }
  var chains=ideasData.chains.filter(function(c){var cur=c.members[c.members.length-1];
    if(ideasFilter==='__all')return true; if(ideasFilter==='__none')return !cur.cat; return cur.cat===ideasFilter;});
  el.innerHTML=chains.length?chains.map(function(c){return ideasCard(c,null);}).join(''):'<p class="text-muted">这里还没有想法——去酒馆聊出结论后说「存想法」。</p>';
}
function ideasRenderNav(){
  var cur_cats=ideasData.chains.map(function(c){return c.members[c.members.length-1];});
  function n(f){return cur_cats.filter(f).length;}
  var html='<div style="cursor:pointer" class="mb-1 '+(ideasFilter==='__all'?'text-primary fw-bold':'')+'" onclick="ideasSetFilter(\\'__all\\')">全部（'+ideasData.chains.length+'）</div>'
   +'<div style="cursor:pointer" class="mb-1 '+(ideasFilter==='__none'?'text-primary fw-bold':'')+'" onclick="ideasSetFilter(\\'__none\\')">🔍 未分类（'+n(function(e){return !e.cat;})+'）</div>'
   +ideasData.cats.map(function(c){return '<div style="cursor:pointer" class="mb-1 '+(ideasFilter===c.id?'text-primary fw-bold':'')+'" onclick="ideasSetFilter(\\''+c.id+'\\')">'+esc(c.name)+'（'+n(function(e){return e.cat===c.id;})+'）</div>';}).join('');
  document.getElementById('ideas-cats').innerHTML=html;
  document.getElementById('ideas-stats').textContent='共 '+ideasData.stats.total+' 条想法 · '+ideasData.stats.chains+' 个问题链 · 未分类 '+ideasData.stats.none+' 条';
}
function ideasSetFilter(f){ideasFilter=f;ideasRenderNav();ideasRender(null);}
function ideasLoad(){
  fetch('/api/ideas/list').then(function(r){return r.json();}).then(function(d){ideasData=d;ideasRenderNav();ideasRender(null);})
   .catch(function(e){document.getElementById('ideas-list').innerHTML='<span class="text-danger">加载失败：'+e+'</span>';});
}
function ideasSearch(){
  var q=document.getElementById('ideas-q').value.trim(); if(!q){ideasClear();return;}
  var mode=document.getElementById('ideas-mode').value;
  fetch('/api/ideas/search?q='+encodeURIComponent(q)+'&mode='+mode).then(function(r){return r.json();})
   .then(function(d){
     if(d.error){document.getElementById('ideas-list').innerHTML='<span class="text-danger">'+esc(d.error)+'</span>';return;}
     ideasData=d; ideasRenderNav();
     var byCur={}; d.chains.forEach(function(c){byCur[c.current]=c;});
     var hits=d.hits.map(function(h){return {chain:byCur[h.current_id],score:h.score,old:(h.hit_id!==h.current_id)};})
                   .filter(function(x){return x.chain;});
     ideasRender(hits);
   });
}
function ideasClear(){document.getElementById('ideas-q').value='';if(ideasData)ideasRender(null);}
function ideasRetag(id){
  var sel=document.getElementById('ideas-rt-'+id); if(!sel)return;
  fetch('/api/ideas/retag',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id,cat:sel.value})})
   .then(function(r){return r.json();}).then(function(d){ if(d.ok)ideasLoad(); else alert(d.error||'改类目失败'); });
}

// ==== v1.4.3 脑绑定 + 人设底稿 ====
let personaSlot = 'duet', personaData = {};
document.querySelectorAll('#ptabs .nav-link[data-p]').forEach(a => a.onclick = e => {
  e.preventDefault();
  document.querySelectorAll('#ptabs .nav-link').forEach(x => x.classList.remove('active'));
  a.classList.add('active');
  personaSlot = a.dataset.p;
  personaFill();
});
function personaFill(){
  const d = personaData[personaSlot] || {};
  document.getElementById('persona-text').value = d.text || '';
  document.getElementById('persona-info').textContent = (d.path || '') + ' · ' + (d.chars || 0) + ' 字' + (d.missing ? ' · 文件不存在' : '') + (d.locked ? ' · 等建线' : '');
}
async function personaLoad(){
  try{
    const r = await fetch('/api/persona/list', {method:'POST'});
    personaData = await r.json();
    personaFill();
  }catch(e){ document.getElementById('persona-info').textContent = '加载失败：' + e; }
}
async function personaSave(){
  const text = document.getElementById('persona-text').value;
  if(!text.trim()) return alert('底稿正文不能为空');
  if(!confirm('保存「' + personaSlot + '」底稿？旧稿自动留底，保存后下一句生效。')) return;
  try{
    const r = await fetch('/api/persona/save', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({slot: personaSlot, text})});
    const d = await r.json();
    if(d.ok){ alert('已保存（' + d.chars + ' 字），下一句生效'); personaLoad(); }
    else alert('失败：' + (d.error || r.status));
  }catch(e){ alert('保存失败：' + e); }
}
const PROV_LABEL = {glm:'GLM-5.3·按量付费', ds:'DeepSeek·魔搭', local:'本地模型', cli:'本地国外脑', glmfree:'GLM-4.7·免费娱乐档'};
async function brainLoad(){
  try{
    const r = await fetch('/api/brain/get', {method:'POST'});
    const d = await r.json();
    document.getElementById('bb-provider').value = d.provider || 'glm';
    document.getElementById('bb-effort').value = (d.provider === 'ds') ? (d.ds_effort || 'high') : (d.glm_effort || 'low');
    brainForm();
    const sc = d.scenes && d.scenes.pet ? ('；桌宠=' + (d.scenes.pet.provider||'?') + ' 服务=' + (d.scenes.service?d.scenes.service.provider:'?')) : '';
    document.getElementById('bb-out').textContent = '当前绑定（tavern）：' + (PROV_LABEL[d.provider]||d.provider) + '，档位 ' + ((d.provider==='ds') ? (d.ds_effort||'high') : (d.glm_effort||'-')) + sc;
  }catch(e){ document.getElementById('bb-out').textContent = '读取失败：' + e; }
}
function brainForm(){
  const p = document.getElementById('bb-provider').value;
  document.getElementById('bb-effort').disabled = (p !== 'glm' && p !== 'ds');
  document.getElementById('bb-effort-label').textContent = (p === 'ds') ? 'DeepSeek 档位' : 'GLM 档位';
}
async function brainSave(){
  const provider = document.getElementById('bb-provider').value;
  const effort = document.getElementById('bb-effort').value;
  if(!confirm('把酒馆槽切到 ' + (PROV_LABEL[provider]||provider) + ((provider==='glm'||provider==='ds') ? ' '+effort : '') + '？下一句消息生效。')) return;
  try{
    const r = await fetch('/api/brain/binding', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({provider, glm_effort: effort, ds_effort: effort})});
    const d = await r.json();
    if(d.ok){ alert('已切换：' + (PROV_LABEL[provider]||provider)); brainLoad(); }
    else alert('失败：' + (d.error || r.status));
  }catch(e){ alert('切换失败：' + e); }
}
// v2.1.0 云CLI 状态卡：余额红绿灯 + 手动探活（按钮触发，零自动轮询——按次计费渠道禁探活）
async function balancePing(){
  const out = document.getElementById('cli-status-out');
  out.textContent = 'ping 中……（发一发 max_tokens=1 的 5.3）';
  try{
    const d = await fetch('/api/balance/ping', {method:'POST'}).then(r=>r.json());
    const icon = {green:'🟢 余额正常', red:'🔴 1113 余额不足（需充值）', yellow:'🟡 异常'}[d.state] || d.state;
    out.textContent = icon + '　HTTP=' + d.http + '　耗时=' + d.ms + 'ms' + (d.error ? '　' + d.error : '');
  }catch(e){ out.textContent = '🟡 探测失败：' + e; }
}
async function brainProbe(){
  const out = document.getElementById('cli-status-out');
  out.textContent = '探活中……（2s 超时×2 路）';
  try{
    const d = await fetch('/api/brain/probe', {method:'POST'}).then(r=>r.json());
    out.textContent = 'cli脑(Groq)=' + (d.foreign.alive ? '🟢活' : '🔴死') + '　本地模型(18080)=' + (d.local.alive ? '🟢活' : '🔴死（pet/service 若配 local 会降级）');
  }catch(e){ out.textContent = '🟡 探活失败：' + e; }
}
// v1.4.7 浏览器兼容两刀：①URL 带凭据登录后立刻 location.replace 洗净（Chrome 禁止从含凭据的
// URL 环境发 fetch；replaceState 不够，必须真实导航；同 origin basicAuth 有会话缓存不会二次弹窗）；
// ②桥版本徽章从桥 healthz 动态取（旧版写死会过期）。
if (location.username) {
  location.replace(location.origin + location.pathname);
} else {
fetch('/api/bridge_healthz', {method: 'POST', credentials: 'same-origin'}).then(r => r.json()).then(d => {
  if (d && d.pipeline) document.getElementById('bridge-ver').textContent = '统一管线 ' + d.pipeline.replace('unified-', 'v');
}).catch(() => { document.getElementById('bridge-ver').textContent = '统一管线（版本获取失败）'; });
}
brainLoad();
personaLoad();
async function receiptLoad(date){
  try{
    const r = await fetch('/api/receipt/list', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({date: date || null})});
    const d = await r.json();
    const dates = d.dates || [], cur = d.date || '', rows = d.rows || [];
    const idx = dates.indexOf(cur);
    const bar = document.getElementById('rc-datebar');
    if(bar){
      bar.innerHTML =
        `<button class="btn btn-sm" ${idx < 0 || idx >= dates.length - 1 ? 'disabled' : ''} onclick="receiptLoad('${dates[idx + 1] || ''}')">← 前一天</button>
         <span class="mx-2"><b>${esc(cur || '无票')}</b> · ${rows.length} 轮</span>
         <button class="btn btn-sm" ${idx <= 0 ? 'disabled' : ''} onclick="receiptLoad('${dates[idx - 1] || ''}')">后一天 →</button>`
        + (dates.length > 1 ? ` <select class="form-select form-select-sm d-inline-block w-auto" onchange="receiptLoad(this.value)">${dates.map(x => `<option ${x === cur ? 'selected' : ''}>${x}</option>`).join('')}</select>` : '');
    }
    const st = d.stats || {};   // v1.5.0 统计卡（源=turn_receipt，随所选日）
    const brainBadges = Object.entries(st.brains || {}).map(([k, v]) =>
      `<span class="badge bg-green-lt me-1">${esc(k)} ×${v}</span>`).join('') || '<span class="text-muted">暂无</span>';
    document.getElementById('stat-cards').innerHTML = `
     <div class="col-sm-4"><div class="card"><div class="card-body py-3"><div class="subheader">轮次（${esc(cur || '无票')}）</div><div class="h1 m-0">${st.rounds ?? 0}</div></div></div></div>
     <div class="col-sm-4"><div class="card"><div class="card-body py-3"><div class="subheader">各脑分布</div><div class="mt-1">${brainBadges}</div></div></div></div>
     <div class="col-sm-4"><div class="card"><div class="card-body py-3"><div class="subheader">平均耗时</div><div class="h1 m-0">${st.avg_sec ?? 0}<small class="text-muted">s</small></div></div></div></div>`;
    document.querySelector('#rc-table tbody').innerHTML = rows.map(x =>
      `<tr style="cursor:pointer${x.err ? ';background:#fff5f5' : ''}" onclick="receiptShow('${x.file}','${x.line}')">
       <td>${esc(x.ts)}</td><td>${esc(x.mode || '')}</td><td>${esc(x.provider || '')}</td>
       <td>${esc(x.user || '')}</td><td>${x.inj}</td><td>${x.rec}</td><td>${x.ft_ms ?? '-'}</td><td>${x.total_ms ?? '-'}</td>
       <td>${x.err ? '<span class="badge bg-red-lt">错</span>' : ''}</td></tr>`).join('')
      || `<tr><td colspan="9" class="text-muted">${cur ? '这一天没有小票' : '还没有小票（发一句话就有了）'}</td></tr>`;
  }catch(e){ console.error(e); }
}
async function receiptShow(file, line){
  try{
    const r = await fetch('/api/receipt/detail', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({file, line: Number(line)})});
    const d = await r.json();
    if(d.error){ alert('读取失败：' + d.error); return; }
    document.getElementById('rc-detail-card').style.display = 'block';
    document.getElementById('rc-d-title').textContent = '小票详情 · ' + (d.ts || '') + ' · ' + (d.mode || '');
    let h = `<p><b>用户话：</b>${esc(d.user_text || '')}</p>`;
    h += `<p><b>脑：</b>${esc(d.provider || '')} · 首字 ${(d.timings || {}).first_token_ms ?? '-'}ms · 总耗时 ${(d.timings || {}).total_ms ?? '?'}ms</p>`;
    if((d.recalls || []).length){
      h += '<h4>捞了什么（召回，含分数）</h4>';
      (d.recalls || []).forEach(rc => {
        h += `<p><b>${esc(rc.source)}</b></p><ul>` + (rc.hits || []).map(x =>
          `<li>[${x.score ?? '-'}] ${esc((x.text || '').slice(0, 160))}</li>`).join('') + '</ul>';
      });
    } else h += '<p class="text-muted">召回：无</p>';
    if((d.injections || []).length){
      h += '<h4>注入了什么（按序，全文截前800字）</h4><ol>' + (d.injections || []).map(x =>
        `<li><b>${esc(x.name)}</b>（${x.chars}字）<pre style="white-space:pre-wrap">${esc((x.text_full || '').slice(0, 800))}</pre></li>`).join('') + '</ol>';
    } else h += '<p class="text-muted">注入：无</p>';
    h += `<p><b>写回：</b>${esc(JSON.stringify(d.writes || {}))} · <b>表情标签：</b>${(d.expr || {}).tags ?? '-'}</p>`;
    if(d.error) h += `<p class="text-danger"><b>错误：</b>${esc(d.error)}</p>`;
    document.getElementById('rc-detail').innerHTML = h;
    document.getElementById('rc-detail-card').scrollIntoView();
  }catch(e){ alert('加载失败：' + e); }
}
receiptLoad();

// ==== v1.6.0 定时任务页 ====
let _cronItems = [];
async function cronLoad(){
  try{
    const r = await fetch('/api/cron/list', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'});
    const d = await r.json();
    _cronItems = d.items || [];
    document.querySelector('#cron-table tbody').innerHTML = _cronItems.map(x => `
     <tr style="${x.enabled ? '' : 'opacity:.45'}">
      <td>${x.enabled ? '<span class="badge bg-success-lt">运行中</span>' : '<span class="badge bg-secondary-lt">已停用</span>'}</td>
      <td><b>${esc(x.title)}</b></td>
      <td class="text-muted" style="max-width:340px">${esc(x.note)}</td>
      <td><code>${esc(x.sched)}</code></td>
      <td class="text-muted" style="font-size:11px;max-width:300px;word-break:break-all">${esc(x.cmd.slice(0,110))}${x.cmd.length>110?'…':''}</td>
      <td class="text-nowrap">
       <button class="btn btn-sm ${x.enabled ? 'btn-outline-danger' : 'btn-outline-success'}" onclick="cronToggle(${x.idx})">${x.enabled ? '停用' : '启用'}</button>
       <button class="btn btn-sm btn-outline-primary" onclick="cronTime(${x.idx})">改时间</button>
      </td>
     </tr>`).join('') || '<tr><td colspan="6" class="text-muted">crontab 为空</td></tr>';
  }catch(e){ console.error(e); }
}
function cronToggle(idx){
  const it = _cronItems.find(i => i.idx === idx);
  if(!it || !confirm(`确定${it.enabled ? '停用' : '启用'}「${it.title}」吗？改动前自动备份。`)) return;
  fetch('/api/cron/toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({idx, fp: it.cmd})})
    .then(r => r.json()).then(d => { d.ok ? cronLoad() : alert('失败：' + (d.error || '?')); });
}
function cronTime(idx){
  const it = _cronItems.find(i => i.idx === idx);
  if(!it) return;
  const ns = prompt('输入新的计划表达式（5 段 cron 如 30 4 * * *，或 @reboot/@daily/@hourly/@weekly/@monthly）', it.sched);
  if(ns === null) return;
  fetch('/api/cron/settime', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({idx, sched: ns, fp: it.cmd})})
    .then(r => r.json()).then(d => { d.ok ? cronLoad() : alert('失败：' + (d.error || '?')); });
}
cronLoad();
// ==== v1.7.0 API 钥匙自助换发 ====
const KEY_DESC = {
  zhipu:      '酒馆/桌宠对话脑在用。保存后<b>自动重启桥（约5秒对话断连）</b>，勾选可同步 OWI 网页模型（再花约50秒）。',
  modelscope: 'DeepSeek 魔搭道在用。保存后自动重启桥（约5秒）。',
  owi_zhipu:  '只在 OWI 网页直选 glm-5.3-flash / 标题生成时用；桥/桌宠不走它。保存=<b>重启 OWI 约50秒</b>（网页与桌宠短暂断连）。'
};
async function keysLoad(){
  const d = await fetch('/api/keys/list', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'}).then(r=>r.json());
  const box = document.getElementById('keys-cards');
  box.innerHTML = Object.entries(d).map(([slot, k]) => `
   <div class="card mb-2"><div class="card-body py-2">
    <div class="d-flex justify-content-between align-items-center">
     <b>${esc(k.name)}</b>
     <span class="text-muted" style="font-size:12px">${k.exists ? '现役尾4位 <code>'+esc(k.tail4)+'</code>（'+k.len+' 位）' : '<span class="text-danger">未配置</span>'}</span>
    </div>
    <div class="text-muted mb-1" style="font-size:12px">${KEY_DESC[slot] || esc(k.desc)}</div>
    <div class="input-group">
     <input type="password" class="form-control form-control-sm" id="key-in-${slot}" placeholder="粘贴新钥匙；点眼睛查看现役明文" autocomplete="off">
     <button class="btn btn-sm" id="key-eye-${slot}" onclick="keyEye('${slot}')" title="显示/隐藏明文">👁</button>
     <button class="btn btn-sm btn-primary" onclick="keySave('${slot}')">保存</button>
    </div>
    <div id="key-out-${slot}" class="text-muted mt-1" style="font-size:12px"></div>
   </div></div>`).join('');
}
let KEY_PLAIN = {};
async function keyEye(slot){
  const inp = document.getElementById('key-in-' + slot);
  const eye = document.getElementById('key-eye-' + slot);
  if (inp.type === 'password'){
    if (!inp.value){
      if (!KEY_PLAIN[slot]){
        const d = await fetch('/api/keys/reveal', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({slot})}).then(r=>r.json());
        if (d.key === undefined){ alert('读取失败：' + (d.error || '?')); return; }
        KEY_PLAIN[slot] = d.key;
      }
      inp.value = KEY_PLAIN[slot];
    }
    inp.type = 'text'; eye.textContent = '🙈';
  } else {
    inp.type = 'password'; eye.textContent = '👁';
    inp.value = '';  // 合上眼睛即清空明文，只留指纹提示
  }
}
async function keySave(slot){
  const key = document.getElementById('key-in-' + slot).value.trim();
  if (!key){ alert('先粘贴新钥匙（或点眼睛查看现役的）'); return; }
  let sync = false;
  if (slot === 'zhipu')
    alert('智谱槽已退役（桥 v4.1.0 GLM 走云CLI付费key）。保存只会留档，不再影响桥，也不会同步 OWI。');
  else if (slot === 'modelscope' || slot === 'cli')
    sync = confirm('保存会重启桥（约5秒断连）。确定继续？');
  if (slot === 'zhipu' && !confirm('确认仍要留档保存？')) return;
  if (!confirm('确认保存并生效？')) return;
  document.getElementById('key-out-' + slot).textContent = '保存中……（重启服务请稍候）';
  const d = await fetch('/api/keys/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({slot, key, sync_owi: sync})}).then(r=>r.json());
  document.getElementById('key-out-' + slot).innerHTML = d.ok ? ('✅ ' + esc(d.msg || '已保存')) : ('❌ ' + esc(d.error || '?'));
  if (d.ok){ KEY_PLAIN[slot] = key; keysLoad(); }
}
keysLoad();
// ==== v1.8.0 学习签（题池+掌握度）====
async function examLoad(){
  const d = await fetch('/api/exam/list', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'}).then(r=>r.json());
  const tb = document.querySelector('#exam-table tbody');
  tb.innerHTML = (d.items || []).map(it => `
   <tr><td>${it.id}</td><td style="font-size:12px">${esc(it.topic)}</td>
   <td style="font-size:12px">${esc(it.text.length > 80 ? it.text.slice(0,80)+'…' : it.text)}</td>
   <td style="font-size:12px">${esc(it.status)}</td>
   <td><button class="btn btn-sm" onclick="examReset(${it.id})">重置</button></td></tr>`).join('');
  const items = d.items || [];
  const st = {新:0, 到期:0, 复习中:0, 掌握:0};
  items.forEach(it => {
    if (it.status === '新题') st['新']++;
    else if (it.status.startsWith('到期')) st['到期']++;
    else if (it.status.startsWith('掌握')) st['掌握']++;
    else st['复习中']++;
  });
  document.getElementById('exam-stats').textContent =
    `共 ${d.total} 题 | 新题 ${st['新']} | 今日到期 ${st['到期']} | 复习中 ${st['复习中']} | 已掌握 ${st['掌握']}（间隔≥21天）`;
}
async function examAdd(){
  const text = document.getElementById('exam-new').value.trim();
  if (!text){ alert('先输入知识点'); return; }
  const topic = document.getElementById('exam-topic').value;
  const d = await fetch('/api/exam/add', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text, topic})}).then(r=>r.json());
  document.getElementById('exam-out').innerHTML = d.ok ? '✅ ' + esc(d.msg) : '❌ ' + esc(d.error || '?');
  if (d.ok){ document.getElementById('exam-new').value = ''; examLoad(); }
}
// ==== v1.9.0 Token 计量页 ====
let _tokChart = null;
async function tokLoad(){
  const d = await fetch('/api/tokens/list', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'}).then(r=>r.json());
  const days = d.days || [];
  const today = days[days.length-1] || {};
  const week = days.reduce((a,x)=>a+(x.total||0),0);
  const ndays = days.filter(x=>x.total>0).length || 1;
  const hit = today.prompt ? Math.round((today.cached||0)/today.prompt*100) : 0;
  document.getElementById('tok-cards').innerHTML = [
    ['今日消耗', (today.total||0).toLocaleString()], ['今日轮次', (today.turns||0)],
    ['缓存命中率', hit + '%（省 ' + (hit*0.75).toFixed(0) + '% 输入费）'], ['近 7 天合计', week.toLocaleString()]
  ].map(([t,v]) => `<div class="col"><div class="card"><div class="card-body py-2"><div class="subheader" style="font-size:12px">${t}</div><h4>${v}</h4></div></div></div>`).join('');
  const tb = document.querySelector('#tok-mode-table tbody');
  const bm = today.by_mode || {};
  tb.innerHTML = Object.entries(bm).sort((a,b)=>b[1]-a[1]).map(([m,v]) =>
    `<tr><td>${esc(m)}</td><td>${v.toLocaleString()}</td></tr>`).join('') || '<tr><td colspan=2 class="text-muted">今日暂无 usage 数据（桥 v3.8.1 部署前的轮次不计量）</td></tr>';
  const ctx = document.getElementById('tok-chart');
  if (_tokChart) _tokChart.destroy();
  _tokChart = new Chart(ctx, {
    type: 'bar',
    data: { labels: days.map(x=>x.date),
      datasets: [
        {label:'输入', data: days.map(x=>x.prompt), backgroundColor:'#206bc4'},
        {label:'输出', data: days.map(x=>x.completion), backgroundColor:'#2fb344'}
      ]},
    options: { responsive:true, scales:{ x:{ stacked:true }, y:{ stacked:true, ticks:{ callback:v=>(v/1000)+'k' } } } }
  });
}
tokLoad();
bpLoad();
// ==== v2.0.0 桥参数 ====
async function bpLoad(){
  const d = await fetch('/api/bparams/get', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'}).then(r=>r.json());
  const box = document.getElementById('bp-cards');
  box.innerHTML = Object.entries(d).map(([k, v]) => {
   const LV = ['轻度','标准','加强','全沉浸'];
   const ctrl = (k === 'rp_level') ? `
    <input type="range" min="1" max="4" step="1" value="${v.value}" id="bp-in-${k}" class="form-range mt-1" style="max-width:300px"
     oninput="document.getElementById('bp-lv-${k}').textContent=['轻度','标准','加强','全沉浸'][this.value-1]">
    <div class="d-flex justify-content-between text-muted" style="max-width:300px;font-size:11px"><span>轻度</span><span>标准</span><span>加强</span><span>全沉浸</span></div>
    <div class="mt-1"><span id="bp-lv-${k}" class="badge bg-primary">${LV[v.value-1]||'?'}</span>
     <button class="btn btn-primary btn-sm ms-2" onclick="bpSave('${k}')">保存</button></div>` : `
    <div class="input-group input-group-sm mt-1">
     <input type="number" step="0.1" id="bp-in-${k}" class="form-control" placeholder="${v.min} ~ ${v.max}">
     <button class="btn btn-primary" onclick="bpSave('${k}')">保存</button>
    </div>`;
   return `
   <div class="card mb-2"><div class="card-body py-2">
    <div class="d-flex justify-content-between"><b style="font-size:13px">${esc(v.desc)}</b>
    <span class="text-muted" style="font-size:12px">现值 <code>${v.value}</code>（默认 ${v.default}）</span></div>
    ${ctrl}
    <div id="bp-out-${k}" class="text-muted mt-1" style="font-size:12px"></div>
   </div></div>`;}).join('');
  // v2.1.0 好感度当前分上屏（用户令：调参控件旁必须显示当前值——bp-score-now 占位此前从没被喂过）
  try{
    const a = await fetch('/api/affection', {method:'POST'}).then(r=>r.json());
    const el = document.getElementById('bp-score-now');
    if (el) el.textContent = '当前 ' + a.score + ' 分（' + (a.level || '?') + ' · 相识 ' + (a.days ?? '?') + ' 天）';
  }catch(e){
    const el = document.getElementById('bp-score-now');
    if (el) el.textContent = '（读取失败）';
  }
}
async function bpSave(key){
  const v = document.getElementById('bp-in-' + key).value;
  if (v === ''){ alert('先填值'); return; }
  const d = await fetch('/api/bparams/set', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key, value: v})}).then(r=>r.json());
  document.getElementById('bp-out-' + key).innerHTML = d.ok ? '✅ ' + esc(d.msg) : '❌ ' + esc(d.error || '?');
  if (d.ok) bpLoad();
}
async function bpScoreSave(){
  const v = document.getElementById('bp-score').value;
  if (v === ''){ alert('先填分数'); return; }
  if (!confirm('确认把好感度改为 ' + v + '？\\n这会直接改变姐妹与你的关系档位。')) return;
  if (!confirm('再次确认：旧账本会自动留底，但当前分立即生效。确定？')) return;
  const d = await fetch('/api/bondscore/set', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({score: v})}).then(r=>r.json());
  document.getElementById('bp-score-out').innerHTML = d.ok ? '✅ ' + esc(d.msg) : '❌ ' + esc(d.error || '?');
  if (d.ok) bpLoad();
}
async function bpReset(){
  if (!confirm('恢复全部桥参数为默认值？（当前自定义会留底）')) return;
  const d = await fetch('/api/bparams/reset', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'}).then(r=>r.json());
  alert(d.ok ? d.msg : ('失败：' + (d.error || '?')));
  bpLoad();
}
bpLoad();
async function examReset(id){
  if (!confirm('重置题 ' + id + ' 的掌握度？')) return;
  await fetch('/api/exam/reset', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id})});
  examLoad();
}
examLoad();

async function loadBridge(){
  const r = await fetch('/api/bridge?n=100'); const d = await r.json();
  document.getElementById('bridge-log').textContent = d.lines.join('\\n') || '(空)';
}
async function loadColls(){
  const r = await fetch('/api/collections'); const d = await r.json();
  const LAB = {
    chat_memory:'聊天记忆（自动入库）',
    chat_summary:'前情摘要（剧情浓缩）',
    chat_journal:'往日日志（一天一条）',
    dual_dialogues:'双人对话库（自动回忆）',
    remram_lines:'场景库（原著台词）',
    ram_dialogues:'拉姆单人台词库',
    rem_dialogues:'雷姆单人台词库',
    emilia_dialogues:'艾米莉亚单人台词库',
    trio_dialogues:'三人剧本对话库'
  };
  const opts = (d.collections||[]).map(c => {
    const lab = LAB[c];
    return `<option value="${esc(c)}">${esc(c)}${lab ? ' - ' + esc(lab) : ''}</option>`;
  }).join('');
  document.getElementById('coll').innerHTML = opts;
  document.getElementById('csv-coll').innerHTML = opts;
}
let memNext=null, memHasMore=false, memTotal=null, memLoading=false, memLoadedN=0;
function memRow(it, coll){
  return `<tr><td><input type="checkbox" class="mem-sel" data-id="${esc(it.id)}" onchange="memSelSync()"></td><td class="text-muted text-nowrap">${esc(it.id)}</td><td style="white-space:pre-wrap">${esc(it.text)}</td>
   <td><button class="btn btn-sm btn-outline-primary" onclick="editPoint('${esc(coll)}','${esc(it.id)}')">改</button>
   <button class="btn btn-sm btn-outline-danger" onclick="delPoint('${esc(coll)}','${esc(it.id)}')">删</button></td></tr>`;
}
function memCountLabel(){
  const el = document.getElementById('mem-count');
  const t = memTotal != null ? ` / 共 ${memTotal} 条` : '';
  el.textContent = memHasMore ? `已载入 ${memLoadedN}${t} · 往下滚续载` : (memTotal != null ? `已全部载入 ${memLoadedN}${t}` : `共 ${memLoadedN} 条`);
}
const memSel = new Set();
function memSelSync(){
  document.querySelectorAll('#mem-table .mem-sel').forEach(c => {
    if (c.checked) memSel.add(c.dataset.id); else memSel.delete(c.dataset.id);
  });
  memSelUI();
}
function memSelUI(){
  document.getElementById('mem-sel-n').textContent = memSel.size;
  document.getElementById('mem-batch-del').disabled = memSel.size === 0;
  const boxes = document.querySelectorAll('#mem-table .mem-sel');
  document.getElementById('mem-sel-all').checked = boxes.length > 0 && [...boxes].every(c => c.checked);
}
function memSelAll(master){
  document.querySelectorAll('#mem-table .mem-sel').forEach(c => c.checked = master.checked);
  memSelSync();
}
function memSelReset(){
  memSel.clear();
  const all = document.getElementById('mem-sel-all');
  if (all) all.checked = false;
  document.getElementById('mem-sel-n').textContent = '0';
  document.getElementById('mem-batch-del').disabled = true;
}
async function memBatchDel(){
  const coll = document.getElementById('coll').value;
  const n = memSel.size;
  if (!n) return;
  if(!confirm(`确定删除 ${coll} 里选中的 ${n} 条吗？此操作不可恢复（删前自动逐条留底到服务器回收站）。`)) return;
  const ids = [...memSel].map(id => isNaN(+id)? id : +id);
  const r = await fetch('/api/delete', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({coll, ids})});
  const d = await r.json();
  if (d.error){ alert('删除失败：' + d.error); return; }
  memSelReset();
  const miss = (d.missing && d.missing.length) ? `，另有 ${d.missing.length} 条本就不存在` : '';
  alert(`已删除 ${d.deleted} 条${miss}`);
  loadMem();
}
async function loadMem(append){
  const wrap = document.getElementById('mem-wrap');
  if (memLoading) return;
  if (append){ if (!memHasMore) return; }
  else { memNext = null; memTotal = null; memLoadedN = 0; memSelReset(); }
  memLoading = true;
  const coll = document.getElementById('coll').value;
  const q = document.getElementById('q').value;
  const off = (append && memNext != null) ? `&offset=${encodeURIComponent(memNext)}` : '';
  const r = await fetch(`/api/memories?coll=${encodeURIComponent(coll)}&q=${encodeURIComponent(q)}&n=200${off}`);
  const d = await r.json();
  memLoading = false;
  if (d.error || !d.items){ document.getElementById('mem-count').textContent = '加载失败：' + (d.error || '?'); return; }
  const rows = d.items.map(x => memRow(x, coll)).join('');
  const tb = document.querySelector('#mem-table tbody');
  if (append) tb.insertAdjacentHTML('beforeend', rows);
  else tb.innerHTML = rows || '<tr><td colspan=4 class="text-muted">无命中</td></tr>';
  memLoadedN += d.items.length;
  memNext = d.next_offset; memHasMore = !!d.has_more;
  if (d.total != null) memTotal = d.total;
  memCountLabel();
  if (append && memHasMore && wrap.scrollHeight <= wrap.clientHeight + 60) loadMem(true); // 容器未填满继续补批，保证可滚
}
function memTop(){ document.getElementById('mem-wrap').scrollTo({top:0,behavior:'smooth'}); }
(function(){
  const w = document.getElementById('mem-wrap');
  if (!w) return;
  const btn = document.getElementById('mem-top');
  w.addEventListener('scroll', () => {
    if (w.scrollTop > 400) btn.style.display = 'block';
    else if (w.scrollTop < 200) btn.style.display = 'none';
    if (memHasMore && !memLoading && w.scrollTop + w.clientHeight >= w.scrollHeight - 300) loadMem(true);
  });
  w.addEventListener('keydown', e => {
    if (e.key === 'Home'){ e.preventDefault(); memTop(); }
    if (e.key === 'End'){ e.preventDefault(); w.scrollTop = w.scrollHeight; }
  });
})();
let editColl=null, editId=null;
async function editPoint(coll,id){
  editColl=coll; editId=id;
  const r = await fetch('/api/point?coll='+encodeURIComponent(coll)+'&id='+encodeURIComponent(id));
  const d = await r.json();
  if(d.error){ alert(d.error); return; }
  document.getElementById('edit-text').value = d.text || '';
  document.getElementById('edit-id').textContent = id;
  document.getElementById('edit-modal').style.display='block';
}
function closeEdit(){ document.getElementById('edit-modal').style.display='none'; }
async function saveEdit(){
  const text = document.getElementById('edit-text').value;
  const r = await fetch('/api/update',{method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({coll:editColl, id: isNaN(+editId)? editId : +editId, text})});
  const d = await r.json();
  if(d.updated){ closeEdit(); loadMem(); } else { alert('保存失败：'+(d.error||d.qdrant||'?')); }
}
async function addPoint(){
  const coll = document.getElementById('coll').value;
  const text = document.getElementById('add-text').value.trim();
  if(!text) return alert('先写内容');
  const r = await fetch('/api/add',{method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({coll, sessionId: document.getElementById('add-sid').value,
      role: document.getElementById('add-role').value, text})});
  const d = await r.json();
  if(d.added){ document.getElementById('add-text').value=''; alert('已加入，点ID='+d.id); loadMem(); }
  else alert('加入失败：'+(d.error||d.qdrant||'?'));
}
async function delPoint(coll, id){
  if(!confirm(`确定删除 ${coll} 里的点 ${id} 吗？此操作不可恢复。`)) return;
  const r = await fetch('/api/delete', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({coll, id: isNaN(+id)? id : +id})});
  const d = await r.json();
  if(d.deleted){ alert('已删除'); loadMem(); } else { alert('删除失败：' + (d.error || d.qdrant || '?')); }
}
let palId=null;
async function palTax(){
  const d = await(await fetch('/api/palace/taxonomy')).json();
  const rooms = [];
  for(const w in (d||{})){ for(const r in d[w]) rooms.push(r); }
  document.getElementById('pal-room').innerHTML = '<option value="">全部房间</option>' +
    rooms.map(r => `<option>${esc(r)}</option>`).join('');
}
function palRender(items, withId){
  const el = document.getElementById('pal-list');
  // v1.4.8 分数过筛：带分数的条目挂徽章；<0.30 的滤掉（人眼线宽放，过滤只在显示层）
  const list = (items || []).filter(it => typeof it.score !== 'number' || it.score >= 0.30);
  if (!list.length) { el.innerHTML = '<div class="text-muted">（没有相关度 ≥0.30 的结果——语义搜索宁缺毋滥）</div>'; return; }
  el.innerHTML = list.map(it => {
    const body = esc(it.text || it.content_preview || '').slice(0, 260);
    const meta = esc(it.room || '') + (it.title ? ' · ' + esc(it.title) : '');
    const score = typeof it.score === 'number'
      ? `<span class="badge bg-${it.score >= 0.5 ? 'green' : it.score >= 0.4 ? 'yellow' : 'gray'}-lt me-1">${it.score}</span>`
      : '';
    const rid = it.drawer_id || it.id || '';
    const head = rid
      ? `<div class="card mb-2 p-2" style="cursor:pointer" onclick="palOpen('${esc(rid)}')"><div class="text-muted" style="font-size:12px">${score}${meta}</div><div style="white-space:pre-wrap">${body}</div></div>`
      : `<div class="card mb-2 p-2"><div class="text-muted" style="font-size:12px">${score}${meta}（搜索结果只读）</div><div style="white-space:pre-wrap">${body}</div></div>`;
    return head;
  }).join('') || '<div class="text-muted">空空如也</div>';
}
async function palLoad(){
  const room = document.getElementById('pal-room').value;
  const d = await(await fetch('/api/palace/list?limit=50' + (room?'&room='+encodeURIComponent(room):''))).json();
  if(d.error){ document.getElementById('pal-list').textContent = d.error; return; }
  palRender(d.drawers || [], true);
}
async function palSearch(){
  const q = document.getElementById('pal-q').value.trim();
  if(!q) return palLoad();
  const d = await(await fetch('/api/palace/search?q='+encodeURIComponent(q))).json();
  if(d.error){ document.getElementById('pal-list').textContent = d.error; return; }
  palRender(d.items || [], false);
}
async function palOpen(id){
  palId = id;
  const d = await(await fetch('/api/palace/get?id='+encodeURIComponent(id))).json();
  document.getElementById('pal-id').textContent = id;
  document.getElementById('pal-text').value = (d && d.content) ? d.content : JSON.stringify(d, null, 1);
  document.getElementById('pal-modal').style.display='block';
}
async function palSave(){
  const text = document.getElementById('pal-text').value;
  const d = await(await fetch('/api/palace/update',{method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({id: palId, content: text})})).json();
  if(d.success || d.updated){ document.getElementById('pal-modal').style.display='none'; palLoad(); }
  else alert('保存失败：'+(d.error||JSON.stringify(d).slice(0,120)));
}
async function palDelete(){
  if(!confirm('删除这条云宫记忆？（宫桥会先自动备份全文到服务器 palace_trash 再删）')) return;
  const d = await(await fetch('/api/palace/delete',{method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({id: palId})})).json();
  if(d.deleted){ document.getElementById('pal-modal').style.display='none'; palLoad(); palTax(); }
  else alert('失败：'+(d.error||JSON.stringify(d).slice(0,120)));
}
async function palAdd(){
  const room = prompt('入哪个房间？（默认 生活）', document.getElementById('pal-room').value || '生活');
  if(room===null) return;
  const title = prompt('一句话标题：'); if(title===null) return;
  const text = prompt('正文：'); if(!text) return;
  const d = await(await fetch('/api/palace/add',{method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({room, title, text})})).json();
  if(d.success || d.drawer_id){ alert('已入宫'); palLoad(); palTax(); }
  else alert('失败：'+(d.error||JSON.stringify(d).slice(0,120)));
}
let igLoaded = false;
async function igLoad(){
  const n = document.getElementById('ig-n').value;
  const b = document.getElementById('ig-btn-load'); b.disabled = true; b.textContent = '加载中…';
  try{
    const d = await (await fetch('/api/ingest/recent?n=' + n)).json();
    const items = d.items || [];
    document.getElementById('ig-list').innerHTML = items.map(it => `
      <label class="d-block mb-1" style="cursor:pointer;border-bottom:1px solid #eee;padding:2px 0">
       <input type="checkbox" class="ig-cb" value="${it.id}">
       <span class="badge ${it.role === 'user' ? 'bg-blue-lt' : 'bg-pink-lt'}">${it.role === 'user' ? '主人' : '姐妹'}</span>
       <span class="text-muted" style="font-size:12px">${esc(it.stamp)}</span>
       <span style="white-space:pre-wrap">${esc(it.text)}</span></label>`).join('')
      || '<div class="text-muted">空空如也</div>';
    igLoaded = true;
  } finally { b.disabled = false; b.textContent = '加载对话'; }
}
function igToggle(all){
  document.querySelectorAll('.ig-cb').forEach(cb => cb.checked = all);
}
async function igSubmit(){
  const ids = Array.from(document.querySelectorAll('.ig-cb:checked')).map(cb => +cb.value);
  if(!ids.length) return alert('先勾选要入库的对话');
  if(!confirm('把勾选的 ' + ids.length + ' 条提交书记员提炼入库？（约30-120秒，别关页面）')) return;
  const b = document.getElementById('ig-btn-go'); b.disabled = true; b.textContent = '入库中…（30-120s）';
  const out = document.getElementById('ig-result');
  out.className = 'card-body'; out.textContent = '书记员提炼中…';
  try{
    const r = await fetch('/api/ingest/submit', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ids})});
    const d = await r.json();
    if(d.error){ out.textContent = '📖 ' + d.error; out.className = 'card-body text-warning'; }
    else{
      const t = (d.titles && d.titles.length) ? '：' + d.titles.join('、') : '';
      let s = '📖 已入宫 ' + d.added + ' 条' + t;
      if(d.dup) s += '（重复跳过 ' + d.dup + '）';
      if(d.failed) s += '（失败 ' + d.failed + '）';
      out.textContent = s; out.className = 'card-body text-success';
    }
  }catch(e){ out.textContent = '📖 入库失败：' + e; out.className = 'card-body text-danger'; }
  finally{ b.disabled = false; b.textContent = '📥 入库所勾'; }
}
function csvExport(){
  const coll = document.getElementById('csv-coll').value;
  location.href = '/api/export/csv?coll=' + encodeURIComponent(coll);
}
async function runChatsExport(){
  const b = document.getElementById('btn-stexport');
  b.disabled = true; b.textContent = '跑着呢…';
  try{
    const r = await fetch('/api/export/chats', {method:'POST'});
    const d = await r.json();
    document.getElementById('stexport-note').textContent = d.error ? ('失败：'+d.error)
      : `完成（returncode=${d.returncode}）。${(d.files||[]).length} 个产物：`;
    document.getElementById('stexport-files').innerHTML = (d.files||[]).map(f =>
      `<div class="text-muted">${esc(f.mtime)} · ${esc(f.name)} · ${f.size}B</div>`).join('');
  } finally { b.disabled = false; b.textContent = '跑导出脚本'; }
}
// ==== v2.1.0 表情柜（正本⇄容器双列；改动先备份）====
let EXPR_DATA = null, EXPR_WHO = null, EXPR_PENDING = null;
const EMO_ZH = {admiration:'赞赏',amusement:'逗乐',anger:'愤怒',annoyance:'烦躁',approval:'认可',
  caring:'关心',confusion:'困惑',curiosity:'好奇',desire:'渴望',disappointment:'失望',
  disapproval:'不认同',disgust:'厌恶',embarrassment:'尴尬',excitement:'兴奋',fear:'恐惧',
  gratitude:'感激',grief:'悲恸',joy:'开心',love:'爱意',nervousness:'紧张',neutral:'平静',
  optimism:'乐观',pride:'骄傲',realization:'顿悟',relief:'如释重负',remorse:'悔恨',
  sadness:'难过',surprise:'惊讶'};   // v2.3.5 表情柜中文注解；未登记情绪回退裸名
async function exprLoad(who){
  const d = await fetch('/api/expr/list').then(r=>r.json());
  EXPR_DATA = d;
  const tabs = document.getElementById('expr-tabs');
  if (!who) who = (d.roles[0] || {}).who || null;
  EXPR_WHO = who;
  tabs.innerHTML = (d.roles || []).map(r =>
    `<li class="nav-item"><a class="nav-link ${r.who===who?'active':''}" href="#" onclick="exprLoad('${r.who}');return false">${r.who} <span class="badge bg-green-lt">${r.std_cover}/28</span></a></li>`).join('');
  const role = (d.roles || []).find(r => r.who === who);
  const grid = document.getElementById('expr-grid');
  if (!role){ grid.innerHTML = '<span class="text-muted">无角色目录（右上「新角色」建一个）</span>'; return; }
  grid.innerHTML = role.grid.map(g => {
    const dot = (g.local && g.remote) ? '🟢' : (g.local ? '🟡' : '🔴');
    const n = g.grp_n || (g.local ? 1 : 0);
    return `<div class="col-6 col-md-3 col-lg-2">
     <div style="border:1px solid #e2e5f0;border-radius:6px;padding:8px 6px;cursor:pointer" onclick="exprOpen('${g.emo}')" title="点开管理这一组的图">
      <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px"><span><b>${g.emo}</b>${EMO_ZH[g.emo] ? ' <span class="text-muted">' + EMO_ZH[g.emo] + '</span>' : ''}</span><span>${dot}</span></div>
      <div style="margin-top:6px;font-size:12px">${g.local ? `<span class="badge bg-blue-lt">×${n}</span>` : '<span class="text-muted">空格</span>'}</div>
     </div></div>`;
  }).join('');
}
function exprBig(emo, src){ document.getElementById('expr-big-title').textContent = EXPR_WHO+' · '+emo+(EMO_ZH[emo] ? '（'+EMO_ZH[emo]+'）' : ''); document.getElementById('expr-big-img').src = src; document.getElementById('expr-modal').style.display='block'; }
function exprCloseBig(){ document.getElementById('expr-modal').style.display='none'; }
async function exprOpen(emo){
  const who = EXPR_WHO;
  if (!who) return;
  const d = await fetch('/api/expr/files?who='+who+'&emo='+emo).then(r=>r.json());
  const files = d.files || [];
  let box = document.getElementById('expr-group-panel');
  if (!box){
    box = document.createElement('div');
    box.id = 'expr-group-panel';
    box.style.cssText = 'position:fixed;inset:0;background:rgba(20,22,30,.62);z-index:9999;display:flex;align-items:center;justify-content:center';
    box.onclick = (e)=>{ if (e.target===box) exprCloseGroup(); };
    document.body.appendChild(box);
  }
  const tiles = files.map(f =>
    `<div style="text-align:center">
      <img src="/api/expr/preview?who=${who}&emo=${emo}&f=${f}&t=${Date.now()}" style="width:170px;height:250px;object-fit:contain;background:#f6f7fb;border-radius:6px;cursor:zoom-in" onclick="window.open(this.src)">
      <div style="font-size:11px;margin-top:3px">${f} <a href="#" style="color:#c33;text-decoration:none" onclick="exprDelOne('${emo}','${f}');return false">删</a></div>
    </div>`).join('')
    || '<span style="color:#889">这组还没图，点「加图」塞一张</span>';
  box.innerHTML = `<div style="background:#fff;border-radius:10px;padding:16px;max-width:92vw;max-height:86vh;overflow:auto">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:10px">
      <b style="font-size:14px">${who} · ${emo}${EMO_ZH[emo] ? '（' + EMO_ZH[emo] + '）' : ''} · 共 ${files.length} 张（聊天随机抽=从这个组抽；点图看原图）</b>
      <span style="display:flex;gap:6px">
       <button class="btn btn-sm btn-primary" onclick="exprPick('${who}','${emo}')">加图</button>
       ${files.length?`<button class="btn btn-sm btn-outline-danger" onclick="exprDel('${who}','${emo}')">清空整组</button>`:''}
       <button class="btn btn-sm btn-outline-secondary" onclick="exprCloseGroup()">关</button>
      </span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:12px">${tiles}</div>
  </div>`;
}
function exprCloseGroup(){ const b = document.getElementById('expr-group-panel'); if (b) b.remove(); }
async function exprDelOne(emo, f){
  if (!confirm('删这张：'+f+'？（先备份 _backup/ 再删）')) return;
  const r = await fetch('/api/expr/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({who: EXPR_WHO, emo: emo, f: f})}).then(x=>x.json());
  if (r.error) alert('删除失败：'+r.error); else exprOpen(emo);
}
function exprPick(who, emo){ EXPR_PENDING = {who, emo}; document.getElementById('expr-file').value=''; document.getElementById('expr-file').click(); }
function exprFilePicked(){
  const f = document.getElementById('expr-file').files[0];
  if (!f || !EXPR_PENDING) return;
  const rd = new FileReader();
  rd.onload = async () => {
    const b64 = rd.result.split(',')[1];
    const r = await fetch('/api/expr/upload', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({who: EXPR_PENDING.who, emo: EXPR_PENDING.emo, data_b64: b64})}).then(x=>x.json());
    if (r.error) alert('上传失败：'+r.error);
    else { exprLoad(EXPR_PENDING.who); if (document.getElementById('expr-group-panel')) exprOpen(EXPR_PENDING.emo); }
  };
  rd.readAsDataURL(f);
}
async function exprDel(who, emo){
  if (!confirm(`删除 ${who} · ${emo} 整组（单图+组图，先备份到 _backup/ 再删）？`)) return;
  const r = await fetch('/api/expr/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({who, emo})}).then(x=>x.json());
  if (r.error) alert('删除失败：'+r.error); else { exprCloseGroup(); exprLoad(who); }
}
async function exprSync(){
  if (!confirm(`把正本全部角色全量 docker cp 到容器？（容器重建丢图后的一键恢复；同名覆盖生效层）`)) return;
  const r = await fetch('/api/expr/sync', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'}).then(x=>x.json());
  alert(r.error ? '失败：'+r.error : '已同步：'+JSON.stringify(r.synced));
  exprLoad(EXPR_WHO);
}
async function exprPullCur(){
  if (!EXPR_WHO) return;
  const r = await fetch('/api/expr/pull', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({who: EXPR_WHO})}).then(x=>x.json());
  alert(r.error ? '失败：'+r.error : '补回 '+((r.pulled||[]).length)+' 格：'+(r.pulled||[]).join(', '));
  exprLoad(EXPR_WHO);
}
async function exprAddRole(){
  const who = (document.getElementById('expr-newrole').value||'').trim().toLowerCase();
  if (!who) return alert('先填角色名');
  const r = await fetch('/api/expr/addrole', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({who})}).then(x=>x.json());
  if (r.error) return alert('失败：'+r.error);
  document.getElementById('expr-newrole').value='';
  exprLoad(who);
}

loadBridge(); loadColls(); palTax(); palLoad();
</script>
</body></html>
"""

if __name__ == "__main__":
    import threading
    pub = http.server.ThreadingHTTPServer(("0.0.0.0", 5879), H)     # v1.4 公网口（basicAuth+防爆破）
    loc = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H)   # 本地隧道口（开隧道.bat 15679 兼容）
    threading.Thread(target=loc.serve_forever, daemon=True).start()
    print(f"管理台 v1.6.1 已起（v1.6.1=夜/昼主题切换：导航栏🌙钮+localStorage记忆+防白闪+手搓暗色覆盖块；v1.6.0=定时任务签：crontab 可视化+启停开关+改计划时间+#@备注行，先备份后写写失败回滚；v1.5.0=双日志合一） 公网 0.0.0.0:5879 + 本地 127.0.0.1:{PORT}（basicAuth+防爆破连败延迟）", flush=True)
    pub.serve_forever()
