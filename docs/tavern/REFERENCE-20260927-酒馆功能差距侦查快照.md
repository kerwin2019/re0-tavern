# 酒馆功能差距盘点·外部侦查快照（2026-09-27 晨）

> 用途：用户问"咱们和酒馆还差什么、有什么创意可借鉴"。本档只存侦查快照与来源，判断落 TODO 档。
> 搜索道：Firecrawl（中档）四发；外部软件纪律=只采信官方文档站与一手帖。

## 一、ST 官方扩展面（docs.sillytavern.app 实勘）
- 内置：Chat Translation / Image Captioning / Image Generation(SD) / **Expression Images（表情差分立绘）** / Summarize / **TTS（ElevenLabs/Silero/XTTS/AllTalk 等）** / Token Counter
- 可装扩展：**Live2d** / VRM(3D) / RVC(变声) / **Weather** / **Idle** / Group Greetings / Group SendAs / RSS / Prompt Inspector / Quick Persona / WebLLM / D&D Dice / Chess / Screen Share / Silence Player / Variable Viewer / Emoji Picker
- 第三方：expressions-plus（Tyranomaster）——go-emotions 本地分类（distilbert ~100MB ONNX）+范围规则+表情套装（chibi/full 子目录）

## 二、表情差分机制（实勘 docs+expressions-plus README）
- classify 模块=小情感分类模型跑在 ST 服务器旁，吃 AI 最新回复 → 输出最可能的一个情绪标签 → 前端换对应 sprite 图（28 表情包：admiration/amusement/anger/...）
- 来源：Local（本地小模型）/ LLM（让大模型顺带判）/ WebLLM 三种 classify 源
- expressions-plus 增强：情绪区间规则（如 5-10% 命中 smirk.png）、表情套装切换（chibi/full）

## 三、VN 模式（docs 实勘）
- User Settings 开 Visual Novel Mode → 聊天布局变成立绘在侧的视觉小说样式；sprite 获取=官方 sprite 包或 LoRA+SD 自制

## 四、群聊机制（docs 实勘）
- 多角色卡同聊；**Auto-mode=按回复顺序自动轮转发言（5 秒间隔）**；@点名触发；"Reply Only When Mentioned"曾是需要的功能请求

## 五、陪伴类产品 2026 创意面（多源互证）
- **Dippy AI**：proactive memory——"别的应用等你打开，它先发消息、引用你提过的事"（=咱们的关怀钩子 v3.5.5 已同款，方向验证）
- **Nomi AI**：persistent memory 关系向 + **多角色群聊**（multi-companion group chats 是差异化卖点）
- **Kindroid**：多层记忆（backstories/persistent memories/**searchable journal entries 可检索日志**）+语音通话+**AI 自拍**（生成形象照片）
- **Replika**：关系模式记忆/3D 形象/AR/语音通话
- **FictionLab**：长记忆+**scenario 带 timestamps and scheduling（时间戳与日程的场景）**
- **Moemate**：voice cloning+动画形象+图生成+web search+screen perception
- 业界趋势总结（GemPages/Vellum 榜单一致口径）：原生语音、图像回复、持久记忆、proactive 行为是 2026 主航道

## 来源
- docs.sillytavern.app/extensions + /expression-images + /visual-novel + /groupchats
- github.com/Tyranomaster/expressions-plus；tavernsprite.com 表情包 28 文件列表
- vellum.ai/best-character-ai-alternatives；biz4group.com；gempages.net；swfte.com/dippy-ai；reddit r/CharacterAIrunaways
