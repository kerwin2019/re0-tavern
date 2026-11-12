# 酒馆接入 CosyVoice3 语音链路 — 调试记录与操作手册（2026-09-17）

> 目标（用户令）：酒馆问答 → 调用 CosyVoice3 生成语音 → 酒馆播放。调通链路用微型文字桩，真 LLM API 用户回家自配。

## 一、资产盘点（知识库 + 实地核验）

| 资产 | 位置 | 状态 |
|---|---|---|
| CosyVoice3（真三代）+ OpenAI 兼容适配器 | **WSL2 Ubuntu-22.04** `~/Projects/CosyVoice/cosyvoice_api_server.py`，conda 环境 `cosyvoice3` | ✅ 本日拉起，`:9233` |
| 音色 | `spk2info.pt` 持久注册 7 个雷姆变体：rem/remzh/remreal/remv2/remg/remtrim/remv3（干声 lmfin.wav 重建） | ✅ 在册 |
| 酒馆 SillyTavern 1.19.0 | `D:\AI\SillyTavern\SillyTavern-1.19.0`，:8000 | ✅ 本日安装点火 |
| 微型文字桩 Qwen3-0.6B-Q8_0（610M） | `D:\AI\models\tiny\`，官方 b10964 引擎 :8090 | ✅ 本日代理下载（639MB/23s）点火 |
| Windows 二代整合包 | `D:\AI\cosyvoice3-0529`（cosyvoice_final 环境，rem.pt） | 未动，留作兜底 |

## 二、链路拓扑

```
浏览器 :8000 酒馆
  ├─ 文字: Chat Completion → 自定义OAI → http://127.0.0.1:8090/v1 (Qwen3-0.6B 桩)
  └─ 语音: TTS → OpenAI Compatible → POST http://127.0.0.1:9233/v1/audio/speech
            (酒馆后端代理转发, 请求体 {model,input,voice,response_format,speed})
            → 适配器返回 WAV (RIFF, 24kHz) → 酒馆 <audio> 播放
```

- 适配器忽略 response_format=mp3 恒返 WAV——浏览器嗅探字节照播，**实测 200 ✓**（3.8s/句）
- 酒馆内置 CosyVoice 提供商（v3ucn 形状 GET /speakers + POST /{text,speaker}）与咱适配器**不匹配**，勿选；要选 **OpenAI Compatible** 提供商
- 适配器 `/v1/voices` 需 token（"invalid console token"），酒馆此路径手填音色名不受影响

## 三、酒馆 UI 配置（5 步）

1. API 连接（插头图标）→ API: **聊天补全** → 来源: **自定义(兼容 OpenAI)** → 端点 `http://127.0.0.1:8090/v1`，密钥随意 → 连接，模型列表出桩名即通
2. 扩展(积木图标) → TTS → TTS Provider: **OpenAI Compatible**
3. Provider Endpoint: `http://127.0.0.1:9233/v1/audio/speech`
4. Model: `cosyvoice3`；Available Voices: `rem`（想要别的变体就填 remv2 等，逗号分隔）
5. TTS 面板勾 **自动播放**；消息按句切分朗读（原生支持，即用户定调的"伪流式"）

## 四、三个服务的启动命令（开机后按序）

```powershell
# 1) TTS (WSL2, 模型加载约40s)
wsl -d Ubuntu-22.04 -- bash -c 'source ~/miniconda3/etc/profile.d/conda.sh && conda activate cosyvoice3 && cd ~/Projects/CosyVoice && export PYTHONPATH=third_party/Matcha-TTS:$PYTHONPATH DS_SKIP_CUDA_CHECK=1 && setsid nohup python cosyvoice_api_server.py >/tmp/cosyvoice-api.log 2>&1 </dev/null & sleep 3; pgrep -af cosyvoice_api_server'

# 2) 文字桩
D:\AI\llama\official-b10964\llama-server.exe -m D:\AI\models\tiny\Qwen3-0.6B-Q8_0.gguf --port 8090 -ngl 99 -c 8192 --host 127.0.0.1 --no-webui

# 3) 酒馆
D:\AI\SillyTavern\SillyTavern-1.19.0\Start.bat   # http://127.0.0.1:8000
```

## 五、注意事项

- **显存单链路纪律**：CosyVoice3 FP16 吃 4.5-6G——TTS 调试时 llama-swap 的 35B 席必须先卸（`GET http://127.0.0.1:18080/unload`）；回家换真 API 时同理，CosyVoice 与 35B 座不能同时驻留
- 语音合成单句 3.8-5.4s（0.5B FP16）；长回复自动按句排队播，属设计内伪流式
- WSL 后台服务用 `setsid nohup` 拉起才不会被 wsl 会话退出带走（裸 nohup+& 已踩坑一次）
- 微型桩 Qwen3-0.6B 自带思考模式：max_tokens 太小会全烧在思考里（建议 ≥400）
- 用户回家后把酒馆文字源从 8090 换成真 API 即可，TTS 侧零改动

## 六、⏳ 待办（用户裁决「回家再说」）：装 Horae 记忆插件

**2026-09-17 已完成核验**（GitHub 原仓库实查，非转述）：

- 仓库 `SenriYuki/SillyTavern-Horae`（v1.15.1，188 星）：真实存在，功能清单与宣传文档逐条相符（时间线时间锚/服装锁/物品栏唯一ID/情绪关系网络/场景记忆/RPG 模块化开关/自动摘要&隐藏+本地向量召回/辅助 API 串行队列）；要求酒馆 ≥1.13.0，本机 1.19.0 满足；**最后推送 2026-06-07（约 3 个半月未更）**，开放 issue 无致命伤（#10 AI 分析空数据、#14 往图像生成掺信息算小毛病）
- **安装三步**：酒馆扩展面板（积木图标）→ Install Extension 贴 `https://github.com/SenriYuki/SillyTavern-Horae.git` → 刷新页面（配套正则自动注入）
- ⚠️ **本机最大坑——辅助 API 必须与主聊天同席**：五席在 llama-swap 互斥组里，辅助 API 若指别的席 → 换装赶人 → KV 全失重爬（0916 同病）。指 18080 时 model 名必须和主聊天席位一致，串行排队正好把后台分析挤同一常驻模型
- 向量记忆走浏览器 Web Worker（bge/e5 各 30-60MB 一次性下载进浏览器缓存），不占显存、不碰 docrag 的 D:\AI\models\bge，与 CosyVoice 互不影响
- **主模型前提**：账本标签靠主模型输出——8090 的 0.6B 桩带不动，须先换真 API/真席位再正式用
- **首配建议**（原文档建议+本机化）：只开核心记忆（时间线/服装/物品/情绪关系），RPG 模块全关，只挂这一个记忆插件（多记忆插件互踩）；自动摘要&隐藏对本地 4060 反而是加速项（旧文压缩 → prefill 变快，向量召回补细节）

## §六 追记（2026-09-17 晚）：Horae 已装入酒馆

git clone --depth 1 到 `D:\AI\SillyTavern\SillyTavern-1.19.0\public\scripts\extensions\third-party\SillyTavern-Horae`（manifest.json 验证在位）——用户刷新酒馆页面即生效，配套正则首次加载自动注入。配置环节（核心记忆开/RPG 全关/辅助 API 同席）等真 API 配好后按本档上文执行。
