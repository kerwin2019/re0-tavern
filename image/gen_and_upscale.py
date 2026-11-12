# -*- coding: utf-8 -*-
"""Z-Image Turbo generate -> purge VRAM -> SeedVR2 upscale, one-click driver.

Usage (run with ComfyUI portable python):
  python gen_and_upscale.py --prompt "a cat"              # generate 768 then upscale to 1080
  python gen_and_upscale.py --upscale-only --input X.png  # upscale an existing image (copied into ComfyUI/input)
Requires ComfyUI already running at --url (default http://127.0.0.1:8188).
"""
import argparse
import json
import shutil
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GEN_WF = ROOT / "_dl" / "zimage_api_workflow.json"
UP_WF = ROOT / "_dl" / "seedvr2" / "upscale_api_workflow.json"
LTX_WF = ROOT / "_dl" / "ltx23" / "ltx23_i2v_api.json"
OUT_DIR = ROOT / "ComfyUI_windows_portable" / "ComfyUI" / "output"
IN_DIR = ROOT / "ComfyUI_windows_portable" / "ComfyUI" / "input"


def http_json(url, payload=None, timeout=30):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def vram_gb(url):
    try:
        s = http_json(url + "/system_stats")
        d = s["devices"][0]
        return d.get("vram_free", 0) / 1e9, d.get("vram_total", 0) / 1e9
    except Exception:
        return -1, -1


def run_prompt(url, workflow, tag):
    free, total = vram_gb(url)
    print("[%s] VRAM before: %.2fG free / %.2fG total" % (tag, free, total))
    t0 = time.time()
    pid = http_json(url + "/prompt", {"prompt": workflow})["prompt_id"]
    while True:
        time.sleep(2)
        h = http_json(url + "/history/" + pid)
        if pid not in h:
            continue
        status = h[pid].get("status", {})
        if status.get("status_str") in ("success", "error"):
            break
    dt = time.time() - t0
    if status["status_str"] == "error":
        msgs = [m for m in status.get("messages", []) if m[0] == "execution_error"]
        print("[%s] FAILED after %.1fs: %s" % (tag, dt, json.dumps(msgs)[:2000]))
        sys.exit(1)
    images = []
    for node_out in h[pid]["outputs"].values():
        images += node_out.get("images", [])
    free2, _ = vram_gb(url)
    print("[%s] done in %.1fs, VRAM after: %.2fG free, outputs: %s"
          % (tag, dt, free2, ", ".join(i["filename"] for i in images)))
    return images


def purge(url):
    print("[purge] freeing models + memory via /free ...")
    try:
        # /free returns 200 with an EMPTY body in ComfyUI 0.36 - do not json-parse
        req = urllib.request.Request(url + "/free",
                                     data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=30)
    except Exception as e:
        print("[purge] /free call failed (continuing):", e)


def run_video(url, image_name, vprompt, vsize, vframes):
    wf = json.loads(LTX_WF.read_text(encoding="utf-8"))
    wf["1"]["inputs"]["image"] = image_name
    wf["2"]["inputs"]["width"] = vsize
    wf["2"]["inputs"]["height"] = vsize
    base = vsize // 2
    wf["20"]["inputs"]["width"] = base
    wf["20"]["inputs"]["height"] = base
    wf["20"]["inputs"]["length"] = vframes
    wf["21"]["inputs"]["frames_number"] = vframes
    wf["5"]["inputs"]["text"] = vprompt
    run_prompt(url, wf, "video")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", default="a majestic mountain lake at sunrise, golden light, ultra detailed")
    ap.add_argument("--upscale-only", action="store_true")
    ap.add_argument("--input", default="", help="image path for --upscale-only / --video-only")
    ap.add_argument("--resolution", type=int, default=1080, help="SeedVR2 target shortest edge")
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument("--vprompt", default="", help="video prompt; enables the LTX-2.3 stage after upscale")
    ap.add_argument("--video-only", action="store_true", help="skip gen+upscale, run LTX-2.3 I2V directly")
    ap.add_argument("--vsize", type=int, default=512, help="LTX output video width/height (square)")
    ap.add_argument("--vframes", type=int, default=49, help="LTX frame count, must be 8n+1")
    ap.add_argument("--url", default="http://127.0.0.1:8188")
    args = ap.parse_args()

    up_wf = json.loads(UP_WF.read_text(encoding="utf-8"))
    up_wf["4"]["inputs"]["resolution"] = args.resolution

    if args.video_only:
        p = Path(args.input)
        if not p.exists():
            print("input not found: %s" % p)
            sys.exit(1)
        shutil.copy2(p, IN_DIR / p.name)
        purge(args.url)
        run_video(args.url, p.name, args.vprompt, args.vsize, args.vframes)
        print("All done. Output folder:", OUT_DIR)
        return

    if not args.upscale_only:
        gen_wf = json.loads(GEN_WF.read_text(encoding="utf-8"))
        # zimage_api_workflow.json: node 4 = positive CLIPTextEncode, 5 = negative
        gen_wf["4"]["inputs"]["text"] = args.prompt
        gen_wf["5"]["inputs"]["text"] = ""
        for nid, node in gen_wf.items():
            if node["class_type"] == "KSampler":
                node["inputs"]["seed"] = args.seed
        imgs = run_prompt(args.url, gen_wf, "generate")
        src = OUT_DIR / imgs[0]["filename"]
        dst = IN_DIR / imgs[0]["filename"]
        shutil.copy2(src, dst)
        up_wf["1"]["inputs"]["image"] = imgs[0]["filename"]
    else:
        p = Path(args.input)
        if not p.exists():
            print("input not found: %s" % p)
            sys.exit(1)
        dst = IN_DIR / p.name
        shutil.copy2(p, dst)
        up_wf["1"]["inputs"]["image"] = p.name

    purge(args.url)
    imgs = run_prompt(args.url, up_wf, "upscale")

    if args.vprompt:
        up_name = imgs[0]["filename"]
        shutil.copy2(OUT_DIR / up_name, IN_DIR / up_name)
        purge(args.url)
        run_video(args.url, up_name, args.vprompt, args.vsize, args.vframes)
    print("All done. Output folder:", OUT_DIR)


if __name__ == "__main__":
    main()
