# REFERENCE-cosyvoice坑册与排查速查-20260917

> ⭐ cosyvoice.cpp 新体系唯一排查入口。**所有结论均已本机实测验证，遇同类症状先查此档，禁止重新联网搜索/重新试错。**
> 主案卷：[OPS-20260917c-TTS加速落地](OPS-20260917c-TTS加速落地-cosyvoicecpp全链路.md) · [OPS-20260917b-调研与平台裁定](OPS-20260917b-TTS加速方案调研-cosyvoicecpp与LightTTS深挖.md)
> 老域（python 版 CosyVoice3 时代）：`aiDocs\cosyVoice3\`（历史档+部署手册，新体系勿混用）

## 一、运行架构快照（恢复用）

```
酒馆(:8000, node server.js, 目录 D:\AI\SillyTavern\SillyTavern-1.19.0)
  → 后端转发 /api/openai/custom/generate-voice（key 读 secrets.json 的 api_key_custom）
    → 记录代理 :9233（python cosyvoice-proxy-20260917b.py v3.1：剥 emoji + **句级分片 ≤80 字/片 + 片间静音无损拼接** + 强制 stream=false + 记 input 全文 + 音频存档 audio-capture\）
      → 真 server :9235（cosyvoice-server.exe --api --verbose，无 --stream）
        → 模型 Q8_0 (900M) + 雷姆音色 rem.gguf（预编码，零 ONNX 前端开销）
旧 WSL2 python 适配器（原 :9233）已停用退役；tiny 桩 :8090 已无必要（真 API 已接），可停。
```

**启动顺序**：**首选桌面一键** `重启语音服务.bat`（= 杀旧+起 server 9235+起代理 9233+healthz 体检，10 秒；跑大模型前点一下=显存归零重起）。手动等价：`cmd /c D:\AI\aiDocs\cosyvoice\script\cosyvoice-restart-chain-20260917.bat`。验证：`curl http://127.0.0.1:9233/healthz` 应返回 `{"status":"ok","voices":["rem"]}`。⚠️ 管理员权限拉起的实例普通权限杀不掉：bat 会明示"关黑窗再点一次"，照做即自洽。

**资产地图**：
| 路径 | 内容 |
|---|---|
| `D:\AI\cosyvoice.cpp\` | 源码 + build\bin（自编 CLI/DLL/ggml-cuda） |
| `D:\AI\cosyvoice-selfbuild\` | **线上运行目录**（预编译 server.exe + 自编 DLL 混合包） |
| `D:\AI\cosyvoice-prebuilt\` | 预编译 v0.1.3 原包（弃用备用，DLL 有行为异常勿回退） |
| `D:\AI\models\cosyvoice3-gguf\` | Q8_0.gguf / rem.gguf / frontend-onnx\ / server.log / proxy.log / audio-capture\ |
| `D:\AI\models\faster-whisper-small\` | ASR 耳朵模型（手动下载自 hf-mirror） |

## 二、症状 → 原因 → 修法速查（全部实测实锤）

### 酒馆侧语音

| 症状 | 根因 | 修法 |
|---|---|---|
| 报 `Model not found: tts-1` | server 校验 model 名 | 酒馆 TTS 面板 Model 填 `cosyvoice3-2512` |
| 报 `unsupported_format` 400 | 酒馆前端硬编码 mp3，miniaudio 版 server 只出 wav | 已 patch（openai-compatible.js response_format→wav），升级酒馆重焊 |
| **直连 API（绕过酒馆）也报 `unsupported_format` 400** | **server 对缺省 response_format 默认按 mp3 拒绝**（2026-09-18 ComfyUI 对口型战役实测补记） | 请求体显式带 `"response_format":"wav"`；代理层不补这个字段 |
| 语音只播一小段/不出声/截断 | server `--stream` 的 WAV 头 RIFF size 是占位符 0x7FFFFFFB，浏览器按假头截断 | server **禁用 --stream**（酒馆后端本来就全量聚合，流式零收益）；已固化进启动脚本 |
| 一条回复被拆几段音频连播 | "按段朗读（流式播放时）"= periodic tick，LLM 生成中按段落提前合成 | **这是特性非 bug**（首句 4 秒开口 vs 全量 20-30 秒）；不喜欢就取消勾选 |
| 单条音频拖长 2-3 倍、失控长音（35字→293s） | **emoji 进文本归一化出怪 token**（实测 35 字带😊：19.6s→43s，极端 293s） | 代理层 emoji 正则剥离已常驻（酒馆更新冲不走）；proxy.log 的 `[emoji-stripped]` 标记即工作证据 |
| 念出 Horae 记忆卡内容 | Horae 把 `<horae>`/`<horaeevent>` 块拼进 mes | TTS 排队源头剥离（index.js patch）+ 面板勾"跳过标签块" |
| 发新消息把旧回复重读一遍 | ST 重渲染旧消息重发 RENDERED 事件 × 内建去重只记"上一条"哈希 | per-message 去重 patch（index.js，**摘除实测必复发**，已固化重打） |
| 完全不朗读 | voiceMap（角色→音色映射）为空 | 酒馆 TTS 面板角色下拉配好音色并保存；或 evaluate 设 `extension_settings.tts.voiceMap` |
| 思考文本混进正文被念 | GLM 思考走 reasoning_content 字段 | 酒馆 Reasoning Template 选 **Auto**（实测拆分正常） |

### 编译（cosyvoice.cpp / ggml）

| 症状 | 根因 | 修法 |
|---|---|---|
| `pip 装不上/递归依赖冲突`类 pip 装包失败 | Py3.13 轮子缺失（历史问题） | ctranslate2 ≥4.6 已有 cp313 win 轮子，直接 `pip install faster-whisper`（纯新增 2 包零冲突，2026-09-17 实测） |
| `STL1002: Unexpected compiler version, expected CUDA 12.4 or newer` | CUDA 12.0 太老，MSVC 14.44 STL 头文件硬性 static_assert，`-allow-unsupported-compiler` 绕不过 | **升级 CUDA ≥12.4**（本机已装 12.9.1，`D:\AI\cuda_12.9.1_installer.exe` 留存；静默装 `-s` 自动跳过旧驱动） |
| VS 生成器 `No CMAKE_C_COMPILER` | vswhere 默认不枚举 BuildTools（须 `-products *`），CMake 内部调用不带 | **弃用 VS 生成器**，用 vcvars64 + Ninja（脚本已固化） |
| `Could not find nvcc in CUDAToolkit_ROOT` | 路径漏写 `v` 前缀（实际目录 `CUDA\v12.9`） | 核对真实目录名 |
| CUDA 编译器检测咬旧 nvcc | 旧会话 `CUDA_PATH` 环境变量仍指 v12.0 | `-DCMAKE_CUDA_COMPILER` 显式钉 `...\v12.9\bin\nvcc.exe` |
| `httplib.ixx C1001 内部编译器错误` | MSVC 19.44 + C++20 modules + cpp-httplib 的 ICE，关 LTO 无效 | **绕过**：预编译 v0.1.3 的 server.exe + 自编 DLL 混用（C ABI 兼容实测通过）；不修编译器 |
| 编译出的语音异常（赛博声/语速 10 字/秒） | 预编译 ggml CUDA DLL 行为异常（issue #15 实锤+用户人耳确认） | **必须用自编 ggml-cuda.dll**，勿回退预编译 DLL |

### 环境与工具

| 症状/需求 | 结论 |
|---|---|
| exe 静默无输出、退出码 -1073741515（0xC0000135） | 缺依赖 DLL。**dumpbin /dependents 逐层查**（vcvars64 环境）；本机 System32 无 VC 运行库，从 BuildTools Redist 目录拷 |
| cosyvoice.cpp 运行依赖全家 | ggml/ggml-base/ggml-cpu(借 b10964)+ggml-cuda+cublas/cudart(借)+**icuuc78/icuin78/icudt78**（ICU 78.3 Win64 MSVC2022 包）+**libomp**+MSVCP140/VCRUNTIME140_1（BuildTools Redist） |
| bat 脚本报 `'端口' is not recognized` 类乱命令 | bat 内中文注释被 GBK 代码页咬碎——**bat 必须纯 ASCII** |
| 命令行传中文参数乱码（EXITCODE=123/参数错） | cmd/bat GBK 读 UTF-8 花掉——**用 pwsh 传参**（原生 UTF-8） |
| python/asr 从 HF 下模型 401（cas-server.xethub.hf.co） | hf-xet 走 Xet 通道被拒 | `HF_HUB_DISABLE_XET=1` + `HF_ENDPOINT=https://hf-mirror.com`，或手动从 hf-mirror 下模型目录（ASR small 模型清单：model.bin/config.json/tokenizer.json/vocabulary.txt → `D:\AI\models\faster-whisper-small\`） |
| 酒馆 TTS 面板没有"测试"按钮 | 触发方式 = 发消息自动生成，或每条消息上的播放图标（三个点→铅笔→小喇叭） |

### 智谱 GLM-5.3-Flash（聊天 API）

| 项 | 结论 |
|---|---|
| 端点/模型 | `https://open.bigmodel.cn/api/paas/v4/` + `glm-5.3-flash`（全小写） |
| 思考模式 | **关不掉**（官方文档实锤：thinking.type 仅支持 enabled）；力度用顶层 `reasoning_effort`：none/minimal/low→low，medium/high→high，xhigh/max→max |
| 酒馆附加参数 | `reasoning_effort: low`（角色扮演轻思考）；官方建议 `thinking.clear_thinking: false` 可选 |
| 提示词后处理 | 保持"未选择"（GLM 吃标准格式） |

## 三、显存账（独显 8G，核显管桌面）

- TTS 常驻基线 ~900M；**长跑累积**：CUDA VMM 保留缓冲不归还（大请求峰值后），实测十余轮后 cosyvoice 进程涨至 ~4.5G——**非泄漏，重启即全额归还**（10 秒起来）
- **VMM 高水位机理（2026-09-17 源码级实锤，勿再当泄漏排查）**：官方定性 = 故意设计，[llama.cpp#4712](https://github.com/ggml-org/llama.cpp/issues/4712) 维护者明确"计算缓冲保留峰值复用防重分配"，该 Issue 关闭时**没有**加"用完即还"开关；ggml-cuda.cu 的 VMM 池 `free()` 只回退指针不归还物理显存，进程退出才释放。服务端已内置长文本分块（`--max-llm-len` 预算控制单 chunk LLM 图上限），累积大头 = 池峰值 + 常驻调度缓冲 + 整段音频 PCM 拼装缓冲（随总音频时长线性涨）。保留量 TTS 自己复用不受损，**受害者只有同卡邻居**
- **缓解三板斧（按推荐序）**：① 代理层（:9233）加单请求文本上限（如 500 字，超长切片分次发）→ 峰值封顶；② 跑大模型前/定时重启 cosyvoice-server → 全额归还；③ 实验项 `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1`（启动 bat 加一行，ggml 运行时读，免重编译）→ cudaMalloc 托管内存，显存吃紧时驱动可把 TTS 闲置页挪去内存，代价是再合成变慢，未实测。Windows WDDM 本身在显存不足时会降级闲置页（#4712 里有述），但不可控不能依赖
- **①+② 已落地并二改（2026-09-17 深夜，OPS-20260917d），现行 = v3.1 句级分片**（规则出自老伪流式档 `cosyVoice3\集成\长文本朗读流水线方案调研.md` + Deepgram 句边界共识）：句末标点切、短句合并 ≤80 字/片、逗号级软切、片间 0.12s 静音。**实测账（基线 855 MiB）**：68 字→1389；**1800 字→29 片全 ≤80→1443 MiB（RTF 0.118 几乎零损耗）**；对照 v3 的 500 字片时代 = 1813-1917。**最坏情况峰值 ~1.44G，正式进入"LLM 6G + 语音 1.5G"预算**；NVIDIA `CUDA - Sysmem Fallback Policy`（控制面板按程序设 cosyvoice-server.exe，[官方说明](https://nvidia.custhelp.com/app/answers/detail/a_id/5490/~/system-memory-fallback-for-stable-diffusion)）降级为额外保险。**Windows 消费卡无进程级显存硬上限**（MIG 是数据中心卡功能），"圈死"= 入口句级分片 + 一键重启
- 突击腾显存：重启 cosyvoice-server（启动脚本）+ 停 tiny 桩（:8090，真 API 时代已无必要）→ 立得 ~5G
- 现存音频/日志增长点：`audio-capture\` 每份几 MB，定期清理

## 四、诊断工具箱（不用重新发明）

1. **代理日志** `proxy.log`：每次请求的时间/来源/input 全文/emoji 剥离标记/耗时/音频字节数——"雷姆念了什么、念多久"全部有案
2. **server 详细日志** `server.log`（--verbose）：REQ start/done/details
3. **音频存档** `audio-capture\`：每份合成自动留档 → `python aiDocs\cosyvoice\script\asr-transcribe-20260917.py <wav>` 转写对账（small 模型 22s 音频 4.3s 转写）
4. **DLL 缺失定位**：`dumpbin /dependents <dll>`（vcvars64 环境）递归查依赖
5. **酒馆后端转发日志**：openai.js 已加 `[TTS-DIAG]` 行（input 长度+开头 150 字），st-stdout.log 可查
6. **显存**：`nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader`（管理员权限可看进程明细）

## 五、酒馆补丁重焊清单（酒馆升级后必做，源码级改动共 5 处）

1. `public/scripts/extensions/tts/openai-compatible.js`：response_format 'mp3'→'wav'
2. `src/endpoints/openai.js` custom/generate-voice：Content-Type 透传上游 + `[TTS-DIAG]` 日志行
3. `public/scripts/extensions/tts/index.js` processAndQueueTtsMessage：剥 `<horae>`/`<horaeevent>` 块
4. `public/scripts/extensions/tts/index.js` onMessageEvent：per-message 去重（readHashes Map，**摘除必复发已实验定案**）
5. ~~emoji 剥离（前端）~~ **已迁代理层**，不再打酒馆侧

改完浏览器必须 **Ctrl+F5**（前端 js）+ 重启 node（后端 js）。
