# REFERENCE-20261006-拉姆28情绪提示词表（WAI17 + ram LoRA 量产配方·红瞳版）

> 用途：拉姆表情差分 28 张的**现役量产配方**（与 REFERENCE-20261006-艾米莉亚表同构，姐妹一条流水线）。
> 引擎线变更：0927 正本（REFERENCE-20260927）=Anima 线，**保留作备选引擎**；1004 大裁决后量产主力=WAI17+LoRA（T8 112/112 零失败实证）。
> **瞳色终审（1006 用户令）=红瞳**：ram_rezero_illu_v1 训练集自带 red eyes 合令；1003 蓝瞳修正案已判废。

## 定稿配方（A 线=量产主力，20-24s/张）

- 底模：**WAI-illustrious-SDXL_v17**（CheckpointLoaderSimple）
- LoRA：**ram_rezero_illu_v1.safetensors**（57MB），weight **1.0**（LoraLoaderModelOnly），**触发词 `r4m`**（训练集自带 red eyes=红瞳合规）
  - 备选：Rem.safetensors（114MB nochekaiser 拉姆版）——⚠️文件名叫 Rem 实为拉姆 LoRA，勿与蕾姆混用；触发词体系仿 nochekaiser（`ram (re:zero)` 系，用前对 API trainedWords）
- 采样：euler_ancestral / normal / **28 步 / CFG 5.5** / **832×1216**
- 景别锁：**cowboy shot + eye-level + straight-on**（禁 full body/特写）
- 身份锁：正向 `pink hair, red eyes`；**负面永久 `blue hair, blue eyes`**（防串蕾姆）
- 女仆装 tag：`maid, maid headdress, white apron, black dress, black thighhighs, short hair, hair covering one eye`（拉姆短发遮右眼）
- 杂志字负面打击组：`(magazine scan, scan artifacts, subtitles, watermark, page number, printed text:1.3)`
- 画风负面补：`vector line, uniform black outline, big round eyes, cartoon, game sprite, 3d render, ai painting style`

### 拼装顺序

```
[质量头 masterpiece, best quality, amazing quality, very aesthetic, absurdres, newest]
+ [触发词 r4m + 女仆装 tag 全套]
+ [身份锁正向 pink hair, red eyes]
+ [情绪描述（见下表）]
+ [cowboy shot framed from the thighs up, eye-level shot, straight-on angle]
+ [simple white background, modern high-quality anime illustration, clean detailed rendering]
```

## 28 情绪描述表（拉姆人格定调：毒舌姐姐/淡定从容/嘴硬心软；搬 0927 定稿描述，人格未变）

| 情绪 | 描述（英文，接在触发词后） |
|---|---|
| neutral | calm composed expression, slight confident smile, looking at viewer, standing tall |
| admiration | impressed admiring look, sparkle in the eyes, clapping hands slowly, genuinely amazed |
| amusement | amused smirk, giggle with closed eyes, hand covering mouth, clearly entertained |
| anger | angry glaring expression, furrowed brows, open mouth scolding, puffed cheeks, arms crossed |
| annoyance | annoyed ticked-off expression, slight frown, looking away with half-lidded eyes, sighing |
| approval | approving nod with closed eyes and a satisfied smile, arms folded, dignified |
| caring | gentle caring expression, warm soft smile, leaning slightly toward the viewer |
| confusion | confused puzzled expression, head tilted to one side, one eyebrow raised |
| curiosity | curious interested look, leaning in to peek, wide attentive eyes |
| desire | covetous playful gaze, reaching one hand out, half-lidded scheming eyes, small grin |
| disappointment | disappointed deep sigh, closed eyes, shaking head slightly, downcast |
| disapproval | stern disapproving frown, hands on hips, looking down at the viewer |
| disgust | disgusted grossed-out expression, covering mouth with one hand, recoiling slightly |
| embarrassment | heavily blushing embarrassed expression, looking away, covering part of face with one hand |
| excitement | excited sparkling eyes, open mouth happy grin, energized posture |
| fear | frightened trembling expression, teary wide eyes, shrinking back slightly |
| gratitude | grateful teary-eyed smile, hands clasped together, bowing head slightly |
| grief | grieving sorrowful expression, tears welling in downcast eyes, clutching chest |
| joy | joyful bright open-mouth smile, sparkling eyes, radiant happy expression |
| love | loving dreamy expression, hands on cheeks, blushing with heartwarming smile |
| nervousness | nervous uneasy expression, sweat drop on cheek, fidgeting with fingers |
| optimism | hopeful optimistic smile, bright eyes looking slightly upward, confident pose |
| pride | proud smug grin, hands on hips, chin raised, self-satisfied expression |
| realization | sudden realization, eyes widened, hand raised to mouth, stunned expression |
| relief | relieved soft smile, exhaling with closed eyes, hand on chest, relaxed shoulders |
| remorse | remorseful apologetic expression, guilty downcast eyes, hands clasped tightly |
| sadness | sad sorrowful expression, teary eyes, downturned mouth, holding own sleeve |
| surprise | surprised, wide eyes, open mouth, hands raised to cheeks, startled expression |

> ⚠️ 拉姆极口嫌体正直：love/joy 类在整批挑图时注意别选成"艾米莉亚式的甜"——她的基准是 smug/淡然，甜要收敛。

## 后处理管线（同 emt 表）

1. 精修二段（整批时上）：RealESRGAN_x4plus_anime_6B 4x → 缩 1248×1872 → img2img denoise 0.3 / 12 步
2. rembg(isnet-anime) 抠透明（`D:\AI\rembg-env`）→ 深绿底 (20,60,20) 质检 → `_qc` 质检照与成品分离
3. 命名=`情绪名.png`，上云 OWI `/expr/ram/`（雷姆套同构目录）
4. 上云后桥映射：`_EXPR_WHO["拉姆"]="ram"`（核对现役值再动）

## 通用坑锁

- 红瞳是终审令——出蓝瞳/粉瞳直接弃（负面锁 blue eyes 已带，pink eyes 靠 LoRA 红瞳压制）
- Anima joy 构图漂脸部特写前科（老引擎）；A 线景别锁已带
- **挑图必须用户目审**（emt 159 张全灭前科）
- 蕾姆参考图缺货维持挂账（等用户供图）

## 关联

emt 姊妹表=REFERENCE-20261006；老 Anima 配方=REFERENCE-20260927（备选引擎+红瞳翻案注记）；T8 实证=OPS-20261005d；挂账入口=TODO-20261006-06待办文档.md
