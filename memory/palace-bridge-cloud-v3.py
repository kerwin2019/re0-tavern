# -*- coding: utf-8 -*-
"""记忆宫桥 v3 :9236 — MemPalace 读写双口 + 云宫管理口（0926 晚，用户令"把你说的那个写完"）。
v3.1.3（1003 云宫换嵌 qwen3-emb 随行件，PLAN-20261003）：recall 扩池 60→300 恒定
（1,942 抽屉=池 60 只见 3% 的视野病；同尺后 300=真 top300，纯 Python 余弦毫秒级）；
预热线程 range(30) 配套。原生排序 vs 重打分名次对比跑一两周，凭数据再议瘦身/全量。
内部：spawn 官方 mempalace-mcp（stdio MCP），走正规工具通道。
外部（v2 原有，零改动）：
      POST /ingest {items:[{room,title,text}]} → {added,dup,failed,titles}
      POST /recall {query, limit=3}             → {items:[{room,title,text}]}（只读）
外部（v3 新增管理口，wing 固定「主人」）：
      GET  /taxonomy                            → {taxonomy:{room:count}}
      GET  /list?room=&limit=&offset=            → {drawers:[{drawer_id,room,content_preview,...}],total}
      GET  /get?id=                              → 抽屉全文
      POST /add {room,title,text,added_by?}      → add_drawer（title 织进正文头）
      POST /update {id,content}                  → update_drawer
      POST /delete {id}                          → 删前全文备份进 /root/work/server-backups/palace_trash/<日期>/ 才删
      GET  /healthz
纪律：只服务本机 127.0.0.1；召回只读不写入；管理口删除必先落备份。
"""
import http.server
import json
import os
import queue
import re
import subprocess
import threading
import time
from datetime import datetime

import shutil as _sh

import httpx  # v3.1 分数重打分用（嵌入席）
EXE = _sh.which("mempalace-mcp") or "/usr/local/bin/mempalace-mcp"
PORT = 9236
WING = "主人"
SRC = "tavern-chat-cloud/" + time.strftime("%Y-%m")
TRASH = "/root/work/server-backups/palace_trash"

_lock = threading.Lock()
_proc = None
_rq = None
_ADD = "mempalace_add_drawer"
_SEARCH = None
_TOOLS = {}


def _reader(proc, q):
    for line in proc.stdout:
        try:
            q.put(json.loads(line))
        except Exception:
            pass


def _rpc(method, params, msg_id=None, timeout=120):
    msg = {"jsonrpc": "2.0", "method": method, "params": params}
    if msg_id is not None:
        msg["id"] = msg_id
    _proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
    _proc.stdin.flush()
    if msg_id is None:
        return None
    end = time.time() + timeout
    while time.time() < end:
        try:
            obj = _rq.get(timeout=3)
        except queue.Empty:
            continue
        if obj.get("id") == msg_id:
            if "error" in obj:
                raise RuntimeError(str(obj["error"])[:200])
            return obj["result"]
    raise TimeoutError(method)


def _child():
    """拿活的 MCP 子进程；死了就重开。v3：全工具名注册进 _TOOLS。"""
    global _proc, _rq, _ADD, _SEARCH, _TOOLS
    _proc = subprocess.Popen([EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
                             )
    _rq = queue.Queue()
    threading.Thread(target=_reader, args=(_proc, _rq), daemon=True).start()
    _rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                        "clientInfo": {"name": "tavern-ingest", "version": "1.0"}}, msg_id=1)
    _proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    _proc.stdin.flush()
    tools = _rpc("tools/list", {}, msg_id=2)["tools"]
    _TOOLS = {}
    for t in tools:
        n = t["name"]
        if "add_drawer" in n:
            _TOOLS["add"] = n
            _ADD = n
        elif "list_drawer" in n:
            _TOOLS["list"] = n
        elif "get_drawer" in n and "get_drawers" not in n:
            _TOOLS["get"] = n
        elif "update_drawer" in n:
            _TOOLS["update"] = n
        elif "delete_drawer" in n and "delete_drawers" not in n:
            _TOOLS["delete"] = n
        elif "taxonomy" in n:
            _TOOLS["taxonomy"] = n
        elif "search" in n:
            _TOOLS["search"] = n
            _SEARCH = n


def _mcp_alive():
    return _proc is not None and _proc.poll() is None


def _ensure():
    if not _mcp_alive():
        _child()


def _tool(name_key, arguments, timeout=90):
    """v3 通用工具调用（带锁保活），返回挖净的文本再尽量转 JSON。"""
    with _lock:
        _ensure()
        res = _rpc("tools/call", {"name": _TOOLS[name_key], "arguments": arguments},
                   msg_id=int(time.time() * 1000) % 100000, timeout=timeout)

    def dig(obj):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):
            return "\n".join(dig(x) for x in obj if x)
        if isinstance(obj, dict):
            if "text" in obj and isinstance(obj["text"], str):
                return obj["text"]
            for k in ("content", "result", "data", "items", "points"):
                if k in obj:
                    return dig(obj[k])
            return json.dumps(obj, ensure_ascii=False)
        return str(obj)

    raw = dig(res)
    try:
        return json.loads(raw)
    except Exception:
        return raw


def ingest(items):
    """items: [{room,title,text}] → 逐条 add_drawer，返回统计。（v2 原样零改动）"""
    global _ADD
    ok, dup, fail, titles = 0, 0, 0, []
    with _lock:
        try:
            if not _mcp_alive():
                _child()
        except Exception as e:
            return {"added": 0, "dup": 0, "failed": len(items), "titles": [], "error": f"MCP 子进程失败: {e}"}
        for i, it in enumerate(items):
            room = str(it.get("room") or "生活").strip() or "生活"
            title = str(it.get("title") or "未命名").strip()
            text = str(it.get("text") or "").strip()
            if not text:
                fail += 1
                continue
            content = f"【{title}】\n\n{text}"
            try:
                res = _rpc("tools/call", {"name": _ADD, "arguments": {
                    "wing": WING, "room": room, "content": content,
                    "added_by": "tavern-入库", "source_file": f"{SRC}#{title[:40]}"}},
                    msg_id=100 + i, timeout=120)
                txt = json.dumps(res, ensure_ascii=False)
                if "duplicate" in txt.lower() or "已存在" in txt:
                    dup += 1
                else:
                    ok += 1
                    titles.append(f"{room}·{title}")
            except Exception as e:
                fail += 1
                titles.append(f"(失败){room}·{title}: {str(e)[:60]}")
    return {"added": ok, "dup": dup, "failed": fail, "titles": titles}


def _dig_text(obj):
    """从 MCP results 里尽力挖出正文字符串（结构未知，多层防御）。"""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "\n".join(_dig_text(x) for x in obj if x)
    if isinstance(obj, dict):
        for k in ("text", "content", "raw", "result"):
            if k in obj and obj[k]:
                return _dig_text(obj[k])
        return json.dumps(obj, ensure_ascii=False)
    return str(obj)


ZEMB_SEAT = os.environ.get("ZEMB_SEAT", "http://172.19.0.1:18300/v1/embeddings")
RECALL_MIN_SCORE = float(os.environ.get("RECALL_MIN_SCORE", "0"))   # 0=只打分不滤（过滤权在桥/台）


_EMB_CACHE = {}   # v3.1.1 向量记忆缓存 {键: 向量}——wing 抽屉总量小，预热后每次召回只嵌查询句
_EMB_CACHE_STORE = "/root/work/cloud-config/.palace_emb_cache.json"   # v3.2.0 落盘位（重启不空窗）
_EMB_DIRTY = {"n": 0, "last": 0.0}   # v3.2.0 攒写标记（新向量数/上次落盘时刻）
_FILLQ = set()        # v3.2.0 后台补嵌队列（去重；rescore 的全部 miss 都有机会入缓存，不再 0 分排尾永不翻身）
_FILL_LOCK = threading.Lock()


def _emb_load():
    """v3.2.0 启动装载落盘缓存：搜宫后 rescore 只欠查询句一次嵌入≈1.8s（旧版重启全冷=首批 10 条 miss≈16s）。
    值统一 array('f')（1024×4B=4KB/条，全池 2k 条≈8MB）；坏档静默弃用照旧预热。"""
    import base64
    from array import array as _arr
    try:
        with open(_EMB_CACHE_STORE, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get("model") != "qwen3-emb":
            print(f"[palace] 落盘缓存模型不符({d.get('model')})，弃用照旧预热", flush=True)
            return
        for k, s in (d.get("vec") or {}).items():
            a = _arr("f")
            a.frombytes(base64.b64decode(s))
            if len(a) == 1024:
                _EMB_CACHE[k] = a
        print(f"[palace] 落盘缓存装载 {len(_EMB_CACHE)} 条", flush=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[palace] 落盘缓存装载失败(弃用): {e}", flush=True)


def _emb_save():
    """v3.2.0 缓存落盘（原子写 tmp+rename；攒写节流：新向量 <48 条且距上次 <120s 就不动盘）。
    「q:」查询句键不入盘（一次性，入盘只膨胀文件）。"""
    import base64
    now = time.time()
    if _EMB_DIRTY["n"] < 48 and now - _EMB_DIRTY["last"] < 120:
        return
    try:
        blob = {}
        for k, v in _EMB_CACHE.items():
            if k.startswith("q:"):
                continue
            try:
                blob[k] = base64.b64encode(v.tobytes()).decode("ascii")
            except Exception:
                continue
        tmp = _EMB_CACHE_STORE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"v": 1, "model": "qwen3-emb", "n": len(blob), "vec": blob}, f, ensure_ascii=False)
        os.replace(tmp, _EMB_CACHE_STORE)
        _EMB_DIRTY["n"] = 0
        _EMB_DIRTY["last"] = now
        print(f"[palace] 缓存落盘 {len(blob)} 条", flush=True)
    except Exception as e:
        print(f"[palace] 缓存落盘失败(不影响服务): {e}", flush=True)


def _filler():
    """v3.2.0 后台补嵌线程：把 rescore 捞到的全部 miss 渐次嵌入（批 16，批间 1.5s 错峰不让席）。
    补齐后 live rescore 只欠查询句一次嵌入。失败退避（丢批的 key 下次 miss 自然重入队）。"""
    from array import array as _arr
    while True:
        time.sleep(1.5)
        try:
            with _FILL_LOCK:
                batch = list(_FILLQ)[:16]
                for k in batch:
                    _FILLQ.discard(k)
            if not batch:
                continue
            r = httpx.post(ZEMB_SEAT, timeout=120,
                           json={"model": "qwen3-emb", "input": [k[2:] for k in batch]})
            r.raise_for_status()
            for k, d in zip(batch, r.json()["data"]):
                _EMB_CACHE[k] = _arr("f", d["embedding"])
                _EMB_DIRTY["n"] += 1
            _emb_save()
        except Exception:
            time.sleep(4)


def _rescore(query, items, want, qvec=None):
    """v3.1 分数重打分：嵌入席（qwen3-emb，与酒馆台词库同款模型=分数线统一语义）对 query 与
    候选重算余弦，按分重排。v3.1.1=文本向量记忆缓存（CPU 席批量嵌入实测 >15s 会超时降级，
    缓存后预热一次、之后每召回只嵌查询句）；嵌入席不可用=原序返回不打分（绝不卡召回）。
    v3.1.5-obs 纯观测：分段时间打点（嵌几条/嵌入耗时/余弦耗时），零行为变更。
    v3.2.0 qvec=桥侧传入的查询句向量（list len1024）：有效则免嵌查询句（CPU 席省 ≈1.8s/轮）。"""
    _t0 = time.time()
    try:
        keys = ["q:" + query] + ["t:" + (it.get("text") or "")[:256] for it in items]
        _allmiss = [k for k in keys if k not in _EMB_CACHE and not k.startswith("q:")]
        _qvec_ok = False
        if qvec and len(qvec) == 1024:
            try:
                from array import array as _qa
                _EMB_CACHE[keys[0]] = _qa("f", [float(x) for x in qvec])   # v3.2.0 桥侧向量直挂（查询句不落盘）
                _qvec_ok = True
            except Exception:
                _qvec_ok = False
        _live_cap = 0 if _qvec_ok else 2   # v3.2.0c 桥模式(qvec)=零 live 嵌入：暖区 recall 只欠搜宫 2.3s（1019 终测 live-2 嵌的全是 filler 未铺到的新鲜抽屉，白付 2.9s/轮）；新鲜度交 filler 分钟级补齐。无 qvec 的Caller 保 2 条
        todo = _allmiss[:_live_cap]
        if not _qvec_ok:
            todo = ["q:" + query] + todo
        for _k in _allmiss[10:]:   # v3.2.0 其余 miss 全数交后台补嵌（旧版=0 分排尾永不翻身）
            _FILLQ.add(_k)
        _t1 = time.time()
        if todo:
            r = httpx.post(ZEMB_SEAT, timeout=40,
                           json={"model": "qwen3-emb", "input": [k[2:] for k in todo]})
            r.raise_for_status()
            from array import array as _arr
            for k, d in zip(todo, r.json()["data"]):
                _EMB_CACHE[k] = _arr("f", d["embedding"])   # v3.2.0 统一 array 存储（4KB/条）
                if not k.startswith("q:"):
                    _EMB_DIRTY["n"] += 1
            _emb_save()
        import math
        qv = _EMB_CACHE.get(keys[0])
        if qv is None:
            raise RuntimeError("query embedding missing (embed request short?)")
        _t2 = time.time()

        def _cos(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a)) or 1e-9
            nb = math.sqrt(sum(y * y for y in b)) or 1e-9
            return dot / (na * nb)

        for it, k in zip(items, keys[1:]):
            _v = _EMB_CACHE.get(k)
            it["score"] = round(_cos(qv, _v), 3) if _v else 0.0   # v3.1.3 池300后缓存可能未铺满：miss 打 0 分排尾（预热补齐后恢复），不再 KeyError 整体降级
        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        if RECALL_MIN_SCORE > 0:
            items = [it for it in items if it["score"] >= RECALL_MIN_SCORE]
        print(f"[palace][obs] rescore: 池{len(items)} miss嵌{len(todo)} 嵌入{int((_t2 - _t1) * 1000)}ms 余弦排序{int((time.time() - _t2) * 1000)}ms 段总{int((time.time() - _t0) * 1000)}ms 缓存存量{len(_EMB_CACHE)}", flush=True)
        return items[:int(want)]
    except Exception as e:
        print(f"[palace] 重打分失败（降级原序）: {e} [obs]段总{int((time.time() - _t0) * 1000)}ms", flush=True)
        return items[:int(want)]


def recall(query, limit=3, qvec=None):
    """只读召回：search 工具语义搜「主人」wing 的记忆抽屉。（v2 原样零改动；v3.2.0 收 qvec 透传重打分）"""
    global _SEARCH
    q = str(query or "").strip()
    if not q:
        return {"items": [], "error": "query 为空"}
    _tA = time.time()   # v3.1.5-obs 纯观测打点
    with _lock:
        try:
            if not _mcp_alive():
                _child()
        except Exception as e:
            return {"items": [], "error": f"MCP 子进程失败: {e}"}
        if not _SEARCH:
            return {"items": [], "error": "mempalace-mcp 无搜索工具"}
        try:
            res = _rpc("tools/call", {"name": _SEARCH, "arguments": {
                "query": q, "wing": WING, "limit": 300}}, msg_id=900, timeout=60)   # v3.1.3 池恒 300（1,942 抽屉时代 60 只见 3%；同尺 qwen3-emb 后 300=真 top300）
        except Exception as e:
            return {"items": [], "error": str(e)[:150]}
    _tB = time.time()
    raw = _dig_text(res)
    items = []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            for d in data:
                if isinstance(d, dict):
                    items.append({"room": str(d.get("room") or d.get("wing") or ""),
                                  "drawer_id": str(d.get("drawer_id") or d.get("id") or ""),
                                  "title": str(d.get("title") or d.get("name") or ""),
                                  "text": str(d.get("content") or d.get("text") or "")[:400]})
        elif isinstance(data, dict):
            for d in (data.get("results") or data.get("drawers") or data.get("items") or []):
                if isinstance(d, dict):
                    items.append({"room": str(d.get("room") or d.get("wing") or ""),
                                  "drawer_id": str(d.get("drawer_id") or d.get("id") or ""),
                                  "title": str(d.get("title") or d.get("name") or ""),
                                  "text": str(d.get("content") or d.get("text") or "")[:400]})
    except Exception:
        pass
    if not items and raw.strip():
        items = [{"room": "", "title": "", "text": raw[:600]}]
    items = [it for it in items if len((it.get("text") or "").strip()) >= 10]
    items = _rescore(q, items, int(limit), qvec)   # v3.1 重打分+重排（v3.2.0 桥侧向量直挂）
    _tC = time.time()
    print(f"[palace][obs] recall: lock+search={int((_tB - _tA) * 1000)}ms 拆包+rescore={int((_tC - _tB) * 1000)}ms 总={int((_tC - _tA) * 1000)}ms 返回{len(items)}", flush=True)
    return {"items": items, "raw_head": raw[:400]}


# ==== v3 管理口实现 ====

def api_taxonomy():
    t = _tool("taxonomy", {})
    if isinstance(t, dict) and "taxonomy" in t:
        return t["taxonomy"]
    return t


def api_list(room=None, limit=50, offset=0):
    args = {"wing": WING, "limit": int(limit), "offset": int(offset)}
    if room:
        args["room"] = room
    return _tool("list", args)


def api_get(did):
    return _tool("get", {"drawer_id": did})


def api_add(room, title, text, added_by="console-web"):
    content = f"【{title}】\n\n{text}" if title else text
    return _tool("add", {"wing": WING, "room": room or "生活", "content": content,
                         "added_by": added_by, "source_file": f"{SRC}#console-{title[:30]}"}, timeout=120)


def api_update(did, content, room=None):
    args = {"drawer_id": did, "content": content}
    if room:
        args["room"] = room
    return _tool("update", args, timeout=120)


def api_delete(did):
    """删前全文备份进 server-backups/palace_trash/<日期>/ 才删（回收站纪律）。"""
    full = api_get(did)
    day = datetime.now().strftime("%Y%m%d")
    safe = re.sub(r"[^0-9A-Za-z_-]", "_", did)[:80]
    folder = os.path.join(TRASH, day)
    os.makedirs(folder, exist_ok=True)
    fp = os.path.join(folder, f"mempalace_{safe}.md")
    with open(fp, "w", encoding="utf-8") as f:
        f.write(json.dumps(full, ensure_ascii=False, indent=1) if not isinstance(full, str) else full)
    r = _tool("delete", {"drawer_id": did})
    return {"deleted": r, "backup": fp}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[宫桥]", fmt % args, flush=True)

    def _send(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path, _, qs = self.path.partition("?")
        from urllib.parse import parse_qs
        p = {k: v[0] for k, v in parse_qs(qs).items()}
        try:
            if path.rstrip("/") in ("/healthz", "/"):
                self._send(200, {"status": "ok", "service": "mempalace-ingest-bridge",
                                 "recall": True, "manage": True, "embedder": _EMBEDDER_OK,
                                 "version": "v3.2.2"})
            elif path == "/taxonomy":
                self._send(200, api_taxonomy())
            elif path == "/list":
                self._send(200, api_list(p.get("room"), int(p.get("limit") or 50), int(p.get("offset") or 0)))
            elif path == "/get":
                self._send(200, api_get(p.get("id") or ""))
            else:
                self._send(404, {"error": "not found"})
        except Exception as e:
            self._send(500, {"error": str(e)[:250]})

    def do_POST(self):
        path = self.path.rstrip("/")
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
            req = json.loads(self.rfile.read(n) or b"{}")
            if path == "/ingest":
                items = (req.get("items") or [])[:8]  # 单次至多 8 条，防垃圾洪泛
                if not items:
                    self._send(400, {"error": "items 为空"})
                    return
                self._send(200, ingest(items))
            elif path == "/recall":
                self._send(200, recall(req.get("query"), req.get("limit") or 3, req.get("query_vector")))
            elif path == "/add":
                self._send(200, api_add(str(req.get("room") or ""), str(req.get("title") or ""),
                                        str(req.get("text") or ""), str(req.get("added_by") or "console-web")))
            elif path == "/update":
                self._send(200, api_update(str(req.get("id") or ""), str(req.get("content") or ""),
                                           req.get("room")))
            elif path == "/delete":
                self._send(200, api_delete(str(req.get("id") or "")))
            else:
                self._send(404, {"error": "not found"})
        except Exception as e:
            self._send(500, {"error": str(e)[:200]})


_EMBEDDER_OK = None   # v3.2.2 启动自检三态：None=未检 True=过 False=挂（healthz 暴露，错了必响）


def _embedder_selfcheck():
    """v3.2.2 启动自检（血案 1009/1019 治标刀），两层探针：
    L1 env 直判：MEMPALACE_EMBEDDING_MODEL != openai-compat = 必挂（身份闸的根，秒判不等待）；
    L2 行为探针：30s 后真打一发召回，返回项文本剥空白后含 "error" = 身份拒（1019 签名；
       注意错误 JSON 是 pretty-print 带换行缩进，禁用紧凑格式 startswith 判——负测 1020 实锤过盲区）。"""
    global _EMBEDDER_OK
    if os.environ.get("MEMPALACE_EMBEDDING_MODEL") != "openai-compat":
        _EMBEDDER_OK = False
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        print("!! [自检][爆红][L1] env 直判：MEMPALACE_EMBEDDING_MODEL 缺失或不符——", flush=True)
        print("!!   宫桥启动漏带三项嵌入 env，MemPalace 必拒搜。", flush=True)
        print("!! 唯一正道：重启只准跑 /root/work/cloud-config/restart-palace.sh", flush=True)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        return
    time.sleep(30)
    try:
        r = recall("[自检]嵌入器探针", 1)
        items = (r or {}).get("items") or []
        bad = (not items) or any(
            str((it or {}).get("text", "")).lstrip().startswith("{")
            and '"error"' in str((it or {}).get("text", ""))[:200]
            for it in items)
        if bad:
            _EMBEDDER_OK = False
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
            print("!! [自检][爆红][L2] 行为探针不过：召回返回 error（嵌入器身份被拒，", flush=True)
            print("!!   或嵌入席 172.19.0.1:18300 不可达）。", flush=True)
            print("!! 唯一正道：重启只准跑 /root/work/cloud-config/restart-palace.sh", flush=True)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        else:
            _EMBEDDER_OK = True
            print("[自检] 嵌入器 OK：env 正确+真召回无 identity 拒绝", flush=True)
    except Exception as e:
        _EMBEDDER_OK = False
        print(f"!! [自检][爆红][L2] 嵌入器自检异常：{str(e)[:200]}", flush=True)


if __name__ == "__main__":
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"记忆宫桥 v3.2.2 已起 :{PORT} → wing={WING}（/ingest+/recall 原样 + /taxonomy /list /get /add /update /delete 管理口，删前自动备份；v3.2.2=启动自检（30s 真召回,error 即横幅爆红+healthz 报 embedder:false,治哑错）+唯一启动件 restart-palace.sh 配套,1020 漏 env 血案治标）；v3.2.1=管理口钉单数工具（MemPalace3.11 单/复数分家,解析器循环后写盖前写,get/delete 曾误中批量版→点开/删除坏,1020 修）；v3.2.0=向量缓存落盘+全量miss后台补嵌（首字三刀刀1，配合桥 v4.2.9）；v3.1.3=池恒300+预热30；v3.1.4=recall 透传 drawer_id）", flush=True)
    _emb_load()   # v3.2.0 重启不空窗
    threading.Thread(target=_filler, daemon=True).start()   # v3.2.0 后台补嵌
    threading.Thread(target=_embedder_selfcheck, daemon=True).start()   # v3.2.2 启动自检（错了必响）

    def _prewarm():
        """v3.1.2 预热线程：启动后台分轮把全池文本嵌入缓存（每轮 rescore 内限 10 条），
        避免首条真实召回撞上冷缓存大批嵌入超时降级。失败静默，绝不影响主服务。"""
        time.sleep(6)
        for i in range(30):
            try:
                n0 = len(_EMB_CACHE)
                recall(f"预热轮{i}", 50)
                if len(_EMB_CACHE) == n0:
                    break   # 一轮零新增=全池已缓存
                time.sleep(2)
            except Exception:
                time.sleep(3)

    threading.Thread(target=_prewarm, daemon=True).start()
    srv.serve_forever()
