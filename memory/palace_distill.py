# -*- coding: utf-8 -*-
"""
palace_distill.py — 记忆宫蒸馏器 v1.0（1113，Mem0 式蒸馏索引配套）
================================================================
把 wing「主人」的原始记忆抽屉（对话实录生切片/记录）经 GLM 蒸馏成独立事实短句，
写入同宫新 wing「记忆蒸馏」——模糊查询的语义锚点层（库里没有蒸馏答案条目=含糊回答的
深层根因，1113 诊断）。召回侧：宫桥 v3.2.3 /recall 可选 wing 参数，酒馆桥深忆链路专线
打蒸馏翼；普通召回（wing=主人）零影响。

用法（云机 /root/memvenv/bin/python3）:
  python3 palace_distill.py --limit 8 --dry     # 试跑看蒸馏质量不写库
  python3 palace_distill.py --limit 30          # 小批实写
  python3 palace_distill.py                     # 全量断点续跑
  python3 palace_distill.py --rooms 交易,心理    # 只蒸指定房间

断点续跑：state 文件记 done_ids（含 NONE 跳过者——跳过也是终态，防反复白烧 token）。
增量 cron：每天 04:30 跑一次，新抽屉自动补蒸。
"""
import json
import re
import sys
import time
import threading
import urllib.request
import urllib.error
from queue import Queue

PALACE = "http://127.0.0.1:9236"
GLM_URL = "http://127.0.0.1:8317/v1/chat/completions"
KEY_PATH = "/root/work/cliproxy/.api_key"
STATE_PATH = "/root/work/cloud-config/palace_distill_state.json"
SRC_WING = "主人"
FACT_WING = "记忆蒸馏"
FACT_ROOM = "记忆蒸馏"
ADDED_BY = "zcode-distill"

DISTILL_PROMPT = """你是记忆蒸馏器。输入是主人的一段生活记忆原文（对话切片/日记/记录）。
把它蒸馏成独立的事实短句，每句一行，供日后语义检索使用。规则：
1. 每句=一个完整事实，尽量带时间（原文有就带），含事件+结果/情绪/驱动因
2. 保留全部具体细节：数字、金额、日期、人名、书名、方法名，禁止空话套话
3. 若原文是纯任务输出/数据计算/代码/行情点位/寒暄（没有任何关于主人的生活事实），只输出：NONE
4. 最多 6 句；只输出事实句本身，不要编号、不要解释、不要引号
5. 用「主人」指代用户本人；事实句要自带主题词，能不靠上下文被独立检索命中

原文：
<<<
{content}
>>>
"""


def _post_json(url, body, timeout=90, key=None):
    req = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers={"Content-Type": "application/json",
                                          **({"Authorization": f"Bearer {key}"} if key else {})},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _get_json(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def glm_key():
    with open(KEY_PATH, encoding="utf-8") as f:
        return f.read().strip()


def glm_distill(content, key):
    """单抽屉蒸馏。返回事实短句列表（空列表=NONE/失败）。429 退避重试一次。"""
    msgs = [{"role": "user", "content": DISTILL_PROMPT.replace("{content}", content)}]
    body = {"model": "glm-5.3-flash", "thinking": {"type": "enabled"},
            "reasoning_effort": "low", "max_tokens": 350, "temperature": 0.2, "messages": msgs}
    for attempt in range(2):
        try:
            d = _post_json(GLM_URL, body, timeout=90, key=key)
            t = (d["choices"][0]["message"].get("content") or "").strip()
            if not t or t.upper().startswith("NONE"):
                return []
            lines = []
            for ln in t.splitlines():
                ln = ln.strip().strip("-•*").strip()
                if not ln or ln.upper().startswith("NONE"):
                    continue
                ln = re.sub(r"^\d+[.、)．]\s*", "", ln)   # 剥「1. 」类编号
                if 8 <= len(ln) <= 120:
                    lines.append(ln)
            return lines[:6]
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(25)
                continue
            print(f"[distill] GLM 失败 http={e.code}", flush=True)
            return []
        except Exception as e:
            if attempt == 0:
                time.sleep(6)
                continue
            print(f"[distill] GLM 异常: {str(e)[:80]}", flush=True)
            return []
    return []


def orig_title_of(content):
    m = re.match(r"\s*【(.+?)】", content or "")
    return m.group(1) if m else ""


def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"done_ids": [], "written": 0, "none": 0}


def save_state(st):
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False)
    import os
    os.replace(tmp, STATE_PATH)


def main():
    args = sys.argv[1:]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 0
    dry = "--dry" in args
    rooms = None
    if "--rooms" in args:
        rooms = [x.strip() for x in args[args.index("--rooms") + 1].split(",") if x.strip()]

    tax = _get_json(f"{PALACE}/taxonomy")
    wing_rooms = tax.get(SRC_WING) or {}
    use_rooms = rooms or list(wing_rooms.keys())
    print(f"[distill] 房间: {use_rooms}（共 {sum(wing_rooms.get(r, 0) for r in use_rooms)} 抽屉）", flush=True)

    # 1) 列全抽屉 id（分页拉取；只拿 id，全文靠 /get）
    ids = []
    for room in use_rooms:
        off, n = 0, 50
        while True:
            d = _get_json(f"{PALACE}/list?room=" + urllib.request.quote(room) + f"&limit={n}&offset={off}")
            batch = d.get("drawers") or []
            ids += [(it.get("drawer_id") or "", room) for it in batch if it.get("drawer_id")]
            if len(batch) < n:
                break
            off += n
    st = load_state()
    done = set(st.get("done_ids") or [])
    todo = [(i, r) for i, r in ids if i not in done]
    if limit:
        todo = todo[:limit]
    print(f"[distill] 总 {len(ids)} · 已蒸 {len(done)} · 待蒸 {len(todo)}{' · DRY' if dry else ''}", flush=True)
    if not todo:
        print("[distill] 无待蒸，收工", flush=True)
        return

    key = glm_key()
    q = Queue()
    for x in todo:
        q.put(x)
    lock = threading.Lock()
    stat = {"done": 0, "written": 0, "none": 0, "fail": 0}

    def worker():
        while True:
            try:
                did, room = q.get_nowait()
            except Exception:
                return
            try:
                full = _get_json(f"{PALACE}/get?id=" + urllib.request.quote(did))
                content = str(full.get("content") or full.get("text") or "")
                if len(content.strip()) < 30:
                    with lock:
                        stat["none"] += 1
                        if not dry:
                            st["done_ids"].append(did)
                    continue
                facts = glm_distill(content[:3000], key)
                if dry:
                    with lock:
                        stat["done"] += 1
                        print(f"[dry] [{room}] {(orig_title_of(content) or did[-12:])[:40]} → {len(facts)} 句", flush=True)
                        for ln in facts:
                            print(f"    · {ln}", flush=True)
                    q.task_done()
                    continue
                if not facts:
                    with lock:
                        stat["none"] += 1
                        st["done_ids"].append(did)
                    continue
                ot = orig_title_of(content)
                title = f"蒸馏·{room}·{ot[:36]}" if ot else f"蒸馏·{room}·{did[-10:]}"
                _post_json(f"{PALACE}/add", {
                    "wing": FACT_WING, "room": FACT_ROOM, "title": title,
                    "text": "\n".join(facts), "added_by": ADDED_BY}, timeout=120)
                with lock:
                    stat["written"] += 1
                    stat["done"] += 1
                    st["written"] = st.get("written", 0) + 1
                    st["done_ids"].append(did)
                    if stat["done"] % 30 == 0:
                        save_state(st)
                        print(f"[distill] 进度 {stat['done']}/{len(todo)} · 成写 {stat['written']} · NONE {stat['none']}", flush=True)
            except Exception as e:
                with lock:
                    stat["fail"] += 1
                    print(f"[distill] 抽屉失败 {did[:40]}: {str(e)[:80]}", flush=True)
            finally:
                q.task_done()

    ts0 = time.time()
    ths = [threading.Thread(target=worker, daemon=True) for _ in range(3)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    if not dry:
        save_state(st)
    _min = int((time.time() - ts0) / 60)
    print(f"[distill] 收工 {stat['done']}/{len(todo)} · 成写 {stat['written']} · NONE {stat['none']} · 失败 {stat['fail']} · 用时 {_min} 分钟"
          f"{' · DRY 未写库' if dry else ''}", flush=True)


if __name__ == "__main__":
    main()
