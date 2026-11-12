# 生图三姐妹·定档包（20261007）

> 地位：三姐妹表情图生产线的**自包含定档包**——配方、原图、样张、脚本、云上 SOP 全在里面。
> 下次开工：先读 `image-gen` skill（路标）→ 按需翻本包；skill 里史料不全时，**答案在本包**。
> 组包人：ZCode（20261007 终极任务令）；对标件=`cosyvoice\assets\拉姆声卡-定档包-20261006\`。

## 包结构

```
00_README.md                          ← 本文件
01_定档配方/
  配方总表.md                         ← ★第一读：三引擎参数+提示词模板+双封条+触发词弹药表+执行参数
  wf_illustrious_v3.json              ← Illustrious 量产工作流（可直 POST，示例 ram_noch_s4×neutral）
  wf_anima_v1.json                    ← Anima 工作流（无监工裸跑，示例 rem×neutral）
  wf_pony_v1.json                     ← Pony 工作流（score_9 体系，示例 rem×smile）
  skeleton_v2.png                     ← 监工骨架源图（ComfyUI input 用同名文件）
02_量产原图/                           ← 云上表情柜在役正本的本地留底（7 套×28=196 张）
  emt_noch_28/ emt_263_28/ emt_s3_28/ ram_illu_28/ ram_nochs4_28/ rem_anima_28/ rem_set2_28/
  （emt 三套=柜上每格 3 张的来源；rem_set2=用户桌面淘图套；文件名=款_情绪）
03_试货样张/                           ← 挑补丁的历史档案（判活判负的证据）
  全家试货13款/                        ← 20261007 全家试货（每款 smile+neutral 两张，含判负款证据）
  蕾姆试货双批_原版/ 蕾姆试货双批_封条/  ← NSFW 封条无损验证对照批（36 张）
  拉姆海选12/                          ← 20261006 拉姆海选卷
04_脚本/                              ← 在役脚本快照（正本在 D:\AI\scripts 与 llama\script，此处为定档时点快照）
  mass28_final3_20261007.py           ← ★量产骨架：submit/wait + 三引擎 build 函数 + 28 情绪词表三套
  final3_collage_20261007.py          ← 拼图全览（脚本可跑但 AI 禁 Read 产物）
  rem_trial18_nsfw_20261007.py        ← 试货骨架（Illustrious 7 款+Anima+Pony 对照）+ 各款触发词 ROSTER
  lora_trial24_20261007.py / anima_trial_20261007.py
  bridge_emtfix / bridge_group / console_group / console_grid / console_underscore_20261007.py ← 云端补丁五件
05_云上管线/
  上云SOP与柜桥架构.md                 ← ★推云三步+验收三连+改码家法+服务定位+补丁回滚表
```

## 三十秒复现路径

1. 探活 ComfyUI：`GET http://127.0.0.1:8188/system_stats`（挂了=portable `run_nvidia_gpu.bat`，25-40s）
2. 显存让路：35B 文本模型与生图互斥（用户令 35B 不开）；语音链可共存
3. 照抄 `01_定档配方\配方总表.md` §二 模板 → 填触发词（§三 弹药表）→ 填情绪词（§四）→ 单张试水 → 放全量（§五 节奏）
4. 批量循环抄 `04_脚本\mass28_final3_20261007.py`
5. 上云抄 `05_云上管线\上云SOP与柜桥架构.md` §二 三步 → §三 验收

## 红线（违反=白干）

- **AI 禁目验自产图**（宪法 §十）：成图/拼图一律不 Read，视觉审阅 100% 归用户
- 判负图不删（都是证据）；删除=回收站
- 改配方先试水 1 张；改云上代码先备份后补丁文件流

## 数字对账（20261007 定档时点）

- 量产原图 196（7×28，零缺格）；试货样张 73；包体积 ~220MB
- 云上柜：emt ×3 / ram ×2 / rem ×2（rem=Anima 款+桌面套），旧款备份 `expr_assets/_backup/20261007b-oldtiers/`
