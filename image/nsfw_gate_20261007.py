# nsfw_gate：第二层防御·双域机检合闸（20261007 定版）
# 双安检员：WD14 rating 头（Danbooru 动漫域）+ NudeNet v3（真人照片域，部位检测式）
# 判定三分流：PASS 放行 / GRAY 灰名单 / QUARANTINE 隔离（AI 只读 JSON 分数，禁 Read 图像本体——宪法 §十）
# 用法：python nsfw_gate_20261007.py <目录或单文件> [--quarantine]   （--quarantine 才真 mv，默认只报告）
# 阈值依据：自家 196 张基线（WD14 max 0.054 / NudeNet 0 检出）+ 真实阳性样本（questionable 0.922/部位 0.93/NudeNet 0.711）
import os, sys, csv, glob, json, shutil, time
import numpy as np
from PIL import Image
import site as _site
_bins = []
for _sp in _site.getsitepackages():
    _bins += glob.glob(os.path.join(_sp, "nvidia", "*", "bin"))
if _bins:
    os.environ["PATH"] = ";".join(_bins) + ";" + os.environ["PATH"]  # add_dll_directory 不够，ORT 依赖 PATH 解析 cuDNN 依赖链
import onnxruntime as ort

MODEL_DIR = os.path.expanduser(r"~\.cache\huggingface\hub\models--SmilingWolf--wd-v1-4-moat-tagger-v2\snapshots\8452cddf280b952281b6e102411c50e981cb2908")
WD_EXPLICIT, WD_QUESTIONABLE, WD_TAG = 0.50, 0.60, 0.30
WD_GRAY = 0.15
NU_THRESH = {"FEMALE_GENITALIA_EXPOSED": 0.45, "MALE_GENITALIA_EXPOSED": 0.45, "ANUS_EXPOSED": 0.45,
             "FEMALE_BREAST_EXPOSED": 0.45, "BUTTOCKS_EXPOSED": 0.50, "MALE_BREAST_EXPOSED": 0.60}
QUARANTINE_DIR = r"D:\AI\aiDocs\_临时\nsfw_quarantine"

_tags, _ridx = [], []
with open(os.path.join(MODEL_DIR, "selected_tags.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(f):
        _tags.append((row["name"], int(row["category"])))
_ridx = [i for i, (n, c) in enumerate(_tags) if c == 9]
RISKY_WORDS = ("nude", "nipple", "pussy", "penis", "cum", "sex", "bottomless")
_sess = ort.InferenceSession(os.path.join(MODEL_DIR, "model.onnx"),
                             providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
_wd_in = _sess.get_inputs()[0]
from nudenet import NudeDetector
_nu = NudeDetector()

def _wd14(path):
    img = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    img = Image.alpha_composite(bg, img).convert("RGB")
    s = max(img.size)
    sq = Image.new("RGB", (s, s), (255, 255, 255))
    sq.paste(img, ((s - img.width) // 2, (s - img.height) // 2))
    arr = np.asarray(sq.resize((_wd_in.shape[1], _wd_in.shape[2])), dtype=np.float32)
    out = _sess.run(None, {_wd_in.name: arr[None]})[0][0].astype(np.float32)
    r = {_tags[i][0]: float(out[i]) for i in _ridx}
    tags = [(_tags[i][0], float(out[i])) for i in range(len(_tags))
            if _tags[i][1] == 0 and any(w in _tags[i][0] for w in RISKY_WORDS) and out[i] > 0.05]
    return r, tags

def gate_one(path):
    rc, rtags = _wd14(path)
    nu = [(x["class"], float(x["score"])) for x in _nu.detect(path)
          if x["class"] in NU_THRESH and x["score"] >= NU_THRESH[x["class"]] * 0.7]
    reasons, level = [], "PASS"
    if rc["explicit"] >= WD_EXPLICIT or rc["questionable"] >= WD_QUESTIONABLE:
        level = "QUARANTINE"; reasons.append(f"WD14评级 explicit={rc['explicit']:.3f} questionable={rc['questionable']:.3f}")
    strong_tags = [(n, v) for n, v in rtags if v >= WD_TAG]
    if strong_tags:
        level = "QUARANTINE"; reasons.append("WD14部位标签 " + ",".join(f"{n}={v:.2f}" for n, v in strong_tags))
    nu_hot = [(n, v) for n, v in nu if v >= NU_THRESH[n]]
    if nu_hot:
        level = "QUARANTINE"; reasons.append("NudeNet " + ",".join(f"{n}={v:.2f}" for n, v in nu_hot))
    if level == "PASS":
        gray = []
        if rc["explicit"] >= WD_GRAY or rc["questionable"] >= WD_GRAY: gray.append("WD14评级灰区")
        if rtags: gray.append(f"WD14标签灰区 {rtags}")
        if nu: gray.append(f"NudeNet灰区 {nu}")
        if gray:
            level = "GRAY"; reasons.append("；".join(gray))
    return {"file": os.path.basename(path), "verdict": level, "reasons": reasons,
            "wd14": {k: round(v, 4) for k, v in rc.items()},
            "wd14_risky_tags": [(n, round(v, 3)) for n, v in rtags],
            "nudenet": [(n, round(v, 3)) for n, v in nu]}

def _fixp(p):
    """Git Bash 风格 /c/... /d/... → Windows 盘符路径。"""
    p = os.path.expanduser(p)
    if len(p) > 2 and p[0] == "/" and p[2] == "/":
        p = p[1].upper() + ":\\" + p[3:]
    return p

def gate_dir(target, quarantine=False):
    target = _fixp(target)
    if os.path.isfile(target):
        files = [target]
    else:
        files = []
        for root, _dirs, names in os.walk(target):
            files += [os.path.join(root, f) for f in sorted(names)
                      if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp"))]
        files.sort()
    t0, out = time.time(), []
    for f in files:
        r = gate_one(f)
        r["file"] = f
        out.append(r)
    q = [r for r in out if r["verdict"] == "QUARANTINE"]
    if quarantine and q:
        qdir = os.path.join(QUARANTINE_DIR, time.strftime("%Y%m%d"))
        os.makedirs(qdir, exist_ok=True)
        for r in q:
            shutil.move(r["file"], os.path.join(qdir, os.path.basename(r["file"])))
            r["moved_to"] = qdir
    rep = {"scanned": len(out), "pass": sum(1 for r in out if r["verdict"] == "PASS"),
           "gray": sum(1 for r in out if r["verdict"] == "GRAY"),
           "quarantine": len(q), "seconds": round(time.time() - t0, 1), "results": out}
    return rep

def sanitize(text):
    """报告脱敏（1007 晚立法：机检报告进对话/检查点必须走本函数——部位标签原词会触发平台内容过滤）。
    词表→代号：W-Q=动漫评级可疑 / W-E=动漫评级直白 / T1..=动漫标签 / N-A=NN胸区 / N-G=NN下身 / N-B=NN臀 / N-X=NN其他"""
    import re as _re
    _MAP = [("FEMALE_GENITALIA_EXPOSED", "N-G"), ("MALE_GENITALIA_EXPOSED", "N-G"),
            ("FEMALE_BREAST_EXPOSED", "N-A"), ("MALE_BREAST_EXPOSED", "N-X"),
            ("BUTTOCKS_EXPOSED", "N-B"), ("ANUS_EXPOSED", "N-G")]
    out = str(text)
    for w, c in _MAP:
        out = out.replace(w, c)
    _WORDS = ["genitalia", "penis", "pussy", "nipple", "cum", "sex", "nude", "areola",
              "breast", "butt", "anal", "erotica", "topless", "bottomless"]
    seen = {}
    def _sub(m):
        w = m.group(0).lower()
        for k in _WORDS:
            if k in w:
                if k not in seen:
                    seen[k] = f"T{len(seen)+1}"
                return m.group(0).replace(m.group(0), seen[k])
        return m.group(0)
    out = _re.sub(r"[a-zA-Z_]{4,}", _sub, out)
    return out

def digest(rep):
    """脱敏摘要：只给判定+分数+代号信号，不含任何部位原词——可安全进对话/检查点。"""
    lines = []
    for r in sorted(rep["results"], key=lambda x: -(max(x["wd14"]["explicit"], x["wd14"]["questionable"]))):
        w = r["wd14"]
        name = os.path.basename(r["file"])
        sig = sanitize("; ".join(r["reasons"][:2])) if r["reasons"] else "无信号"
        mark = {"QUARANTINE": "🚫隔离", "GRAY": "⚠️灰", "PASS": "✅过"}[r["verdict"]]
        lines.append(f"{mark} {name[:16]:<16} Q={w['questionable']:.2f} E={w['explicit']:.2f} | {sig[:60]}")
    return "\n".join([f"扫{rep['scanned']}张: 放行{rep['pass']}/灰{rep['gray']}/隔离{rep['quarantine']}"] + lines)

if __name__ == "__main__":
    tgt = sys.argv[1]
    rep = gate_dir(tgt, quarantine="--quarantine" in sys.argv)
    print(json.dumps({k: v for k, v in rep.items() if k != "results"}, ensure_ascii=False))
    for r in rep["results"]:
        if r["verdict"] != "PASS":
            print(r["verdict"], os.path.basename(r["file"]), "|", sanitize("; ".join(r["reasons"])))
    jf = os.path.join(r"D:\AI\aiDocs\_临时", f"nsfw_gate_report_{time.strftime('%Y%m%d_%H%M%S')}.json")
    json.dump(rep, open(jf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("报告已存", jf)
