# REFERENCE-20261007-生图三姐妹生产完全手册

> 地位：三姐妹表情图生产线的**方法正本**（对标 REFERENCE-20261006-角色语音生产完全手册）。
> 数据与配方住在定档包：`D:\AI\aiDocs\llama\assets\生图三姐妹-定档包-20261007\`；本手册管方法、坑册、判决与索引。
> 成册背景：20261006e~1007 三姐妹量产+引擎扩张战役收官（全程账=OPS-20261007-生图三姐妹量产与引擎扩张战役.md）；用户终极任务令「下次开工直接照抄，不反复试」。

## 0. 一图流（下次开工照此走）

```
image-gen skill 触发 → 读本手册 §1 定档卡 → 探活/让显存 → 照抄配方总表（试水1张→全量）
→ 非视觉核验+拼图+目审夹 → 用户目审 → 上云三步+验收三连 → 柜里随机抽自当生效
```

## 1. 定档卡（20261007 用户目审收官态）

| 项 | 定档 |
|---|---|
| 引擎三件 | Illustrious/WAI17（主力，有监工）｜Anima-Base v1.0（qwen 编码，无监工裸跑）｜Pony V6XL（score_9 体系，监工兼容） |
| 监工骨架 | xinsir ControlNetXL OpenPose，strength 0.7 / start 0.0 / end 0.7，骨架源=skeleton_v2.png（1536×2304 原尺寸提取+PIL 裁） |
| 量产配方 v3 | 试货配方+NSFW 封条+场景封条+白底正词（参数全表=定档包 01\配方总表.md） |
| 种子 | 20261006（全役统一，横向可比） |
| 柜上在役款 | emt=noch/2-63/s3 三款×28｜ram=illu/noch_s4 两款×28｜rem=Anima1918762+桌面套两款×28 |
| 情绪词表 | 拉姆=毒舌版｜emt=温和+冰晶｜rem=emt 剥冰晶（三表正本=mass28_final3 脚本） |
| 换弹规则 | 每格一叠图随机抽（桥 v2.2）；淘图/新款往格里塞即可，画风不论 |

## 2. 机制铁事实（照抄可用，来历见 §4 坑册）

1. **DWPose 脸盲**：bbox_detector="None"（跳过检测）+ pose_estimator=torchscript；骨架必须从 1536×2304 原尺寸提取后 PIL 裁
2. **LoadImage 按文件名缓存**：换内容必须换文件名
3. **服装组词必挂**：civitai 触发词分特征组/服装组/替换装组，只挂特征组=衣服自由发挥；但服装组会引场景背景 → 场景封条治
4. **`1girl, solo` 免疫场景病**（emt_s3 实证）；无此词的款必须挂场景封条
5. **LoRA 门派铁律**：触发词只认同门派底模；Illustrious/SDXL 一门，Pony 一门（跨族=鬼图），Anima 一门（结构不通监工），文件名带门派标（illu/pony/anima 前缀防呆，原带标不动）
6. **rezero_pack（19-in-1）**：权重 0.8 才是人有衣服穿；v2 词系=`rezerochar+角色名`
7. **Anima 三件套**：UNETLoader weight_dtype="default" 必填｜CLIPLoader type=qwen_image｜采样器 er_sde（euler_a 不存在是 Pony 的坑，Anima 用 er_sde）
8. **产物真目录**：`D:\AI\ComfyUI\output\`（portable 内层 output 是空壳）
9. **双封条**：NSFW 四连（nsfw,nude,topless,nipples,explicit）+ 场景五连（indoors,scenery,detailed background,window,door）——只加不删
10. **API 骨架**：POST /prompt → 轮询 /history/<id> 到 completed；批量循环 try/except 单张不断批

## 3. 三本 SOP（细账在定档包）

- **量产 SOP**：定档包 `01_定档配方\配方总表.md` §二模板→§三触发词→§四情绪词→§五执行节奏
- **上云 SOP**：定档包 `05_云上管线\上云SOP与柜桥架构.md`（备份→scp→docker cp 三步+验收三连）
- **改云码家法**：同上 §四（备份/补丁文件流/杀启分条/node --check 本地验）
- **挑新 LoRA SOP**：试货骨架=`llama\script\lora_trial24_20261007.py`（每款 smile/neutral 两张+触发词 ROSTER），样张判活判负归用户目审；卡拉取=`civitai_*_survey_20261007.py`（模型卡入 `lora-cards-*`）；验身=SHA256 对卡

## 4. 坑册（判负路勿重试）

| # | 坑 | 判词 |
|---|---|---|
| 1 | 服装组词引场景背景（nochekaiser 首烤 28 张全木门） | 场景封条治本；试水 1 张验背景是铁律 |
| 2 | rezero_pack 1.0 权重=金发陌生女 | 0.8+丰富词表复活 |
| 3 | ram_il169 / ram_locon / rem_locon | 单词款崩坏/LoCon 词无效——判负封存，勿再试 |
| 4 | Anima/Pony 28 套装 | 用户目审「不怎么样」正式出局（1007）——单张试货可以，量产线不走 |
| 5 | UNETLoader 400 / KSampler 400 | weight_dtype 缺 / euler_a 不存在（Pony 用 euler_ancestral） |
| 6 | 残留 ComfyUI 进程占 8188 | 杀到 netstat 无 LISTEN；版本看启动日志非 system_stats |
| 7 | 2 颗标错 id 的下载 | SHA256 对弹药卡验身是收货铁规 |
| 8 | ssh 内联 python 引号炸 | 补丁一律本地 Write→scp→远端跑 |
| 9 | output 双目录 | 真目录=D:\AI\ComfyUI\output |
| 10 | emt 占位图案（桥内旧令） | 条件失效的占位代码要主动清点撤销 |

## 5. 索引（什么东西在哪）

- 定档包（配方/原图/样张/脚本/云上SOP）：`llama\assets\生图三姐妹-定档包-20261007\`
- 在役脚本正本：`llama\script\`（mass28_final3 / final3_collage / trial 三件 / 云端补丁五件）
- 弹药卡：`llama\data\lora-cards-20261006\`（emt 系）+ `lora-cards-20261007\`（ram/rem 系+改名账）
- LoRA 库：`...\ComfyUI\models\loras\`（29 件门派防呆命名）；监工模型：`models\controlnet\controlnetxlCNXL_xinsirOpenpose.safetensors`
- 目审夹：`USER-REVIEW-TMP\`（20261006e 系列 + 20261007 系列 + 收官三连目审）
- 云端：桥/台=/root/work/cloud-config/；正本=/root/work/expr_assets/；备份=server-backups/+expr_assets/_backup/
- 过程账：OPS-20261007-生图三姐妹量产与引擎扩张战役.md（§七续战=本册同日账）；判决终审=MASTER §5
