# OPS-20260917c — TTS 加速落地：cosyvoice.cpp 全链路调通（Windows 原生）

> 上游：[OPS-20260917b-TTS加速方案调研](OPS-20260917b-TTS加速方案调研-cosyvoicecpp与LightTTS深挖.md)（调研+平台裁定）→ 本档（落地实施）
> 结论先行：**Windows 原生 cosyvoice-server(预编译 v0.1.3 + 借用 CUDA DLL) 已上线 ：9233，雷姆音色零前端开销，RTF 0.22-0.47，首包 0.42s，显存增量仅 ~855 MiB，酒馆端到端 200 全通。**

## 一、最终架构

```
酒馆 UI(:8000) → ST后端 /api/openai/custom/generate-voice（纯转发）
  → cosyvoice-server.exe (:9233, Windows 原生, CUDA, API+stream 模式)
    → Q8_0 GGUF 模型 (D:\AI\models\cosyvoice3-gguf\CosyVoice3-2512_Q8_0.gguf, 900MiB)
    → voice "rem" = 预编码 rem.gguf (127KB, 跳过 ONNX 前端)
WSL2 python 适配器（旧 :9233，FP16，RTF 1.07）已停用 = 显存释放 4.5G
```

## 二、实测数据（RTX 4060 Laptop 8G，预编译包 + b10964 借用 ggml-cuda.dll）

| 项 | python 版（旧） | cosyvoice.cpp（新） | 提升 |
|---|---|---|---|
| RTF（CLI 长句 39字） | 1.07 | **0.22**（849ms/3.8s 音频） | ~5× |
| RTF（server 非流式 33字） | 1.07 | 0.47（2.60s/5.48s） | ~2.3× |
| 首包（stream:true） | 无（伪流式等整句） | **0.42s**（23 chunk 增量） | 真·流式 |
| 显存增量 | 4.5-6G | **~855 MiB**（总 2494 − 基线 1639） | 常驻可行 |
| 前端开销 | 每次请求 2.5s | **0（rem.gguf 复用，prompt_prepare 0.41ms）** | 免除 |
| model_load（冷启） | 数十秒 | 851ms | — |

audio 输出：pcm_f32le 24000Hz mono。CLI 默认采样参数（temp 1.0 / top_k 25 / top_p 0.8），KV cache 默认 k=q8_0,v=q4_0，flash attention 双开。

## 三、依赖链全套清单（D:\AI\cosyvoice-prebuilt\，预编译包补齐记录）

预编译 zip 只带 exe + onnxruntime.dll，其余全靠本机凑齐（dumpbin /dependents 逐层查缺）：
1. **ggml.dll / ggml-base.dll / ggml-cpu-*.dll** ← 借 `D:\AI\llama\official-b10964\`（官方 llama.cpp 构建，版本兼容实跑通过）
2. **ggml-cuda.dll + cublas64_12.dll + cublasLt64_12.dll + cudart64_12.dll** ← 同上（CUDA 模式）
3. **icuuc78.dll / icuin78.dll / icudt78.dll 等 5 件** ← [ICU 78.3 Win64 MSVC2022](https://github.com/unicode-org/icu/releases/download/release-78.3/icu4c-78.3-Win64-MSVC2022.zip)（release notes 里"Windows 自备 ICU"就是它；版本必须 78，dumpbin 读出的）
4. **libomp.dll** ← b10964 目录（ggml-base.dll 依赖 OpenMP 运行库）
5. **MSVCP140 / MSVCP140_1 / VCRUNTIME140 / VCRUNTIME140_1** ← BuildTools 自带 Redist（`C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Redist\MSVC\14.44.35112\x64\Microsoft.VC143.CRT\`；⚠️ 系统 System32 无 VC redist，llama-server 是静态链接所以以前没暴露）
6. 0xC0000135 (STATUS_DLL_NOT_FOUND) 静默无输出 = 缺上列 DLL 的通用症状；**dumpbin 递归查依赖是最快定位法**

模型与音色（D:\AI\models\cosyvoice3-gguf\）：
- `CosyVoice3-2512_Q8_0.gguf`（943,933,536 B）← [HF Lourdle 仓库](https://huggingface.co/Lourdle/Fun-CosyVoice3-0.5B-2512-GGUF)（代理下载）
- `frontend-onnx/speech_tokenizer_v3.onnx`（969MB）+ `campplus.onnx`（28MB）← 同上（预编码一次性用）
- `frontend-onnx/rem_16k_mono.wav` ← 干声 `D:\AI\models\Fun-CosyVoice3-0.5B\rem\dryVocal\lmfin_16k.wav` 经 ffmpeg 转 16k/mono/s16（原件是 s32/stereo， cosyvoice 前端要 mono s16）
- `rem.gguf`（127,328 B）= 雷姆音色包，参考文本「虽然平时看起来很锐利，但握紧的时候却能感觉到，这就是男生的手。」，预编码命令见启动脚本同目录 encode 流程（pwsh 调 cosyvoice-cli --frontend-only）

## 四、酒馆侧两处 patch（升级酒馆会丢，重装后按本节重焊）

依据：[cosyvoice.cpp TOOLS.md](https://github.com/Lourdle/cosyvoice.cpp/blob/main/docs/TOOLS.md) 格式支持表（miniaudio 版仅 wav/pcm，mp3 需 FFmpeg build）+ 酒馆本地源码实读。

1. `public/scripts/extensions/tts/openai-compatible.js` fetchTtsGeneration：`response_format: 'mp3'` → `'wav'`（前端硬编码 mp3，cosyvoice-server 收 mp3 报 400 unsupported_format 实测实锤）
2. `src/endpoints/openai.js` custom/generate-voice 路由：`Content-Type` 硬编码 `audio/mpeg` → 透传上游 `result.headers.get('content-type') ?? 'audio/mpeg'`（真接 OpenAI mp3 时同样正确，普适改进）
3. `public/scripts/extensions/tts/index.js` processAndQueueTtsMessage：clone 后剥 `<horae>`/`<horaeevent>` 块再入队（Horae 把记忆块拼进 mes，TTS 会照念 68 秒小抄实锤；内建 skip_tags 开关不可靠，源头剥覆盖全部路径）
4. `public/scripts/extensions/tts/index.js` onMessageEvent：加 per-message 去重（`readHashes` Map 按 `${chatId}:${messageId}` 登记，hash 相同即 return）——【2026-09-17 晚实验定案】用户提议摘除验证 → 原版立即复现"念出全部旧对话"（20:13 实测）→ **缝隙实锤，补丁必要，已重打**。机理：ST 重渲染旧消息重发 RENDERED 事件 × 内建去重只记"上一条"哈希。酒馆更新后按本条重焊；重焊代码 = hashNew 计算后插 readHashes 查查登记块（本档历史含完整代码）。另：官方"按段朗读（流式播放时）"= periodic tick 机制（`tts_periodic_auto_generation`，生成中按段落提前合成），是碎片语音出处，用户未勾已排除
5. `public/scripts/extensions/tts/openai-compatible.js` fetchTtsGeneration：发送前剥 emoji/符号区段（`[\u{1F000}-\u{1FAFF}\u{1F1E6}-\u{1F1FF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{2190}-\u{21FF}\u{FE0F}\u{200D}]`）——**emoji 拖长实锤**：同 35 字文本无 emoji 19.6s / 带 😊 43s，叠加采样随机可失控至 293s（server 日志 id=13/14）；GLM 回复高频带 emoji，必剥

端到端实测（模拟浏览器带 CSRF+cookie）：`POST /api/openai/custom/generate-voice` → **200 audio/wav**，2.37s 返回 4.0s 雷姆语音。酒馆 TTS provider 配置要点（UI 侧）：provider=OpenAI Compatible，endpoint=`http://127.0.0.1:9233/v1/audio/speech`（填完整路径），voices 手填 `rem`，model 随意（server 忽略）。**酒馆 UI 需强刷（Ctrl+F5）加载新前端 js**。

## 五、服务管理

- 启动：`cmd /c D:\AI\aiDocs\cosyVoice3\脚本\cosyvoice-server-start-20260917.bat`（或 pwsh Start-Process 隐藏窗；进程名 cosyvoice-server.exe）
- 日志：`D:\AI\models\cosyvoice3-gguf\server.log`
- ⚠️ 启动脚本 bat 必须纯 ASCII 注释——UTF-8 中文在 GBK 代码页 cmd 下被咬碎成乱命令（今日踩坑，报 `'端口' is not recognized`）
- ⚠️ 必须 `--api` 参数，否则默认 WebUI 模式
- 与 35B 席显存互斥关系解除：TTS 855MiB + tiny桩，8G 卡共存余量充裕；LLM 全 GPU 深窗（7G+）时仍需协调，账见 [OPS-20260917b §6.4](OPS-20260917b-TTS加速方案调研-cosyvoicecpp与LightTTS深挖.md)

## 六、CUDA 12.9.1 自编译（已完成，线上已切换自编 DLL 混合包）

- 动因：CUDA 12.0 + MSVC 14.44 不兼容（STL 头文件 static_assert「expected CUDA 12.4 or newer」，`-allow-unsupported-compiler` 绕不过头文件检查，实测实锤）；且 issue #15 预编译 CUDA DLL 噪声/行为异常风险
- **CUDA 12.9.1 静默安装完成**（`cuda_12.9.1_576.57_windows.exe -s`，驱动 610.47 > 576.57 自动跳过驱动；v12.0 并存保留）
- configure 三个坑（脚本 `cosyVoice3\脚本\cosyvoice-cpp-configure-cuda-20260917.bat` 已固化）：
  1. VS 生成器对 BuildTools 实例失明（vswhere 需 `-products *`，CMake 内部不带）→ **必须 vcvars64 + Ninja**
  2. `-DCUDAToolkit_ROOT` 路径漏写 `v` 前缀（实际目录 `CUDA\v12.9`）→ Toolkit not found
  3. 旧会话 `CUDA_PATH` 环境变量仍指 v12.0，CMake 编译器检测咬旧 nvcc → **必须显式 `-DCMAKE_CUDA_COMPILER=...\v12.9\bin\nvcc.exe`**
  4. 成功组合：vcvars64 + Ninja + `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 -DCMAKE_CUDA_FLAGS="-allow-unsupported-compiler" -DGGML_CCACHE=OFF`，全量编译 ~10 分钟
- **server 编译未解**：`tools/server/httplib.ixx(79) C1001 内部编译器错误`（MSVC 19.44 + C++20 modules + cpp-httplib 组合 ICE，`-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF` 无效）。绕过 = **预编译 v0.1.3 的 cosyvoice-server.exe + 自编 cosyvoice.dll/ggml 全家 DLL 混合包**——C ABI 兼容实跑通过（`D:\AI\cosyvoice-selfbuild\`）
- **A/B 对照实锤 issue #15 不止噪声**：同句同 seed（39 字），预编译 DLL 版 3.76s 音频（10.4 字/秒异常赶拍）vs 自编 DLL 版 10.76s（3.6 字/秒自然语速）；RTF 相近（0.50/0.56）→ 旧 ggml CUDA 采样行为异常，已弃用。对照音频留档：`D:\AI\models\cosyvoice3-gguf\A-B-prebuilt-dll.wav` / `B-selfbuild-dll.wav`（音质人耳终审用）

## 七、终态（2026-09-17 晚更新：诊断代理部署 + ASR 审听耳朵上岗 + 稳定运行确认）

- **链路**：酒馆 → **记录代理 v2**（:9233，[脚本/cosyvoice-proxy-logger-20260917.py](../脚本/cosyvoice-proxy-logger-20260917.py)：①emoji/符号剥离（过滤职责自酒馆前端补丁迁入，酒馆侧该补丁保持摘除）②input 全文记录至 proxy.log ③**每份合成音频自动存档** `audio-capture\`）→ 真 server（:9235，`--verbose` → server.log）
- **ASR 审听耳朵**（2026-09-17 晚上岗）：faster-whisper 1.2.1（系统 Python，纯新增 2 包零冲突；用户旧日"装不上"= ctranslate2 缺 Py3.13 轮子，4.6+ 已解）+ small 模型本地目录 `D:\AI\models\faster-whisper-small\`（用户手动从 hf-mirror 下载；**注意模型下载须 `HF_HUB_DISABLE_XET=1`，Xet 通道 401**）。转写脚本 [脚本/asr-transcribe-20260917.py](../脚本/asr-transcribe-20260917.py)：22s 音频 4.3s 转写，内容与原稿吻合（一字精度差属 small 模型正常）。用途：怀疑念错时拿 audio-capture 存档转写对账，用户不必人肉反复听
- **稳定运行确认**：补丁全集（wav/MIME/horae 剥离/dedupe/emoji 剥离-代理层）生效后连续多轮单条正确合成，无复读、无拼接、无失控
- **已知观察**：语速偏慢（~2 字/秒，正常 3.6）——不致命，用户裁决暂不处理；嫌慢可在酒馆 TTS 面板把 Speed 从 1 调至 ~1.15 直接补偿；根治线索 = 自编 ggml 时加 `-DGGML_CUDA_FA_QUANTS="q8_0-q4_0"` 重编译
- **未结案 → 已破案（2026-09-17 深夜）**：「全量重读/三份合一」真相 = 三事叠加的听感：①每轮回复正常朗读（一问一答一条，代理日志证实无拼接大请求）②**emoji 拖长 2-3 倍**（无过滤期实测 67字→60.4s、109字→110.9s，即 1 字/秒；过滤后回落 3-5 字/秒）③新建聊天时 greeting 开场白也被自动朗读（20:44:32 的 28 字实锤）——多轮拖长连播 = "全量重读"体感。**根治 = 代理层 emoji 剥离（已常驻）**；greeting 朗读为 ST 设计行为未动。browser-use 复现记录：新浏览器实例实测三轮对话三条请求一一对应，语速正常
- **ASR 耳道备注**：audio-capture 存档实证（emoji 过滤前后同规模文本时长对比 60.4s/110.9s → 34.4s/124.2s）已在档
- 与 35B 席显存互斥关系解除：TTS ~1.2G + tiny桩，8G 卡共存空间充裕；LLM 全 GPU 深窗（7G+）时仍需协调，账见 [OPS-20260917b §6.4](OPS-20260917b-TTS加速方案调研-cosyvoicecpp与LightTTS深挖.md)

## 八、已知遗留

1. **音质人耳验收 ✅ 已完成（2026-09-17 晚）**：用户亲耳 A/B——预编译 DLL 版"赛博机器人声"（⚠️注意归因：是旧预编译 ggml CUDA DLL 行为异常，**不是**升级 CUDA 12.9 所致，勿记反）；自编版"声音很稳"通过
2. ~~server --stream 流式~~ **已撤（同晚实锤）**：流式 WAV 的 RIFF 头 size 是占位符 `0x7FFFFFFB`（≈2GB），浏览器 audio 按头解析导致截断/只播一小段/不出声；而 ST 后端 `arrayBuffer()` 本来就全量聚合后才发浏览器，**流式在此链路零收益纯坑** → 启动脚本已去 `--stream`，非流式实测 `header_declared == actual` 完全一致。真流式的收益需浏览器增量播放改造（低优先）
3. **TTS 念 Horae 记忆块**：Horae 把记忆数据以 `<horae>`/`<horaeevent>` 标签拼进 message.mes，TTS 照念 → 解法 = 酒馆 TTS 面板勾"**跳过标签块里的内容**"（skip_tags 正则剥所有标签块）+ 顺手勾"跳过代码块"
4. **请求积压暴涨教训**：server `--concurrency 1` 串行；skip_tags 未勾时段落越积越长，实测耗时 38s→158s→168s→400s 排队。进度窗（`Get-Content server.log -Wait` 实时滚动）可一眼判断 start/done/耗时；积压时重启 server 秒清
5. **自编 ggml 的 FlashAttention 向量核缺失警告**：`no FlashAttention vector kernel compiled for K/V types q8_0-q4_0, converting to f16 (slow)`——下次重编译加 `-DGGML_CUDA_FA_QUANTS="q8_0-q4_0"` 可消（速度小损失，非致命）
6. cosyvoice-server 无 GET /v1/voices（酒馆 voices 是 UI 手填，不受影响）
7. WSL2 内 cosyvoice_api_server.py 已停用未删除（回滚路径：WSL `setsid nohup python cosyvoice_api_server.py`，但端口 9233 与新服务冲突，二选一）
