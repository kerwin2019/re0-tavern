# -*- coding: utf-8 -*-
r"""
gsv-openai-proxy.py v3（2026-10-20 晚，OWI 前端切分管线解剖修复版）
v1（2026-10-18）: OpenAI /v1/audio/speech 兼容壳，坐 GSV api_v2 :9880 上，监听
10.14.14.2:9234（只绑 EasyTier 网卡，禁 0.0.0.0），voice 映射热读，mp3=ffmpeg 转码。
v2（1020 午）: 洗文本+按行分角色+长段句切 concat+单段失败隔离。
v3（1020 晚·实锤修复）: 真凶=OWI 前端 TTS 管线（拿真实消息对拍，五块 225/153/162/102/79
分毫不差）：①其 Qi 洗 markdown 把 ![拉姆 disapproval](url) 洗成裸 alt 文字内联句中
（=用户听到的图片标志真身；v2 行锚 LABEL_LINE 拦不住行中）；②其 punctuation 切分只按
英文 .!?+空白 或 换行 断句，再按「<50字或<4词就往前一块粘」合并，把「艾米莉亚：」前缀
切离正文/粘进块中行首错位（v2 行首锚 PREFIX_RE 全数脱靶→投票并列落 rem=艾米莉亚被
雷姆念真身）。修四刀：①INLINE_LABEL 内联剥「名字+空格+英文词」（alt 残字行中行首通杀）；
②PREFIX_ANY 全文任意位置认「名字：」锚切分段路由（前缀保留在朗读文本里=本尊自己报名）；
③前缀全无三级兜底：名字投票(≥2 且 2 倍优势)→继承上一请求说话人(120s 窗)→rem；
④日志逐段带声线+文字头（用户令：哪把嗓子读了哪句一眼可查）。
选型注（1020 用户令「查现成轮子」）：md→朗读文本语义对齐 pipecat MarkdownTextFilter
（docs.pipecat.ai，图片整删/链接留字）与 mdit_plain（markdown-it 官方纯文本渲染器）；
「名字: 台词」行解析制先例=multivoice / Script-to-Voice-Generator-EdgeTTS / HX-SayBook；
但「聊天 UI 无状态切块流」的跨请求说话人继承无现成轮子，自研三级兜底（DeepSeek 复核挂账）。
v3.1（1020 晚·并发实验判负存档+流式立项否决）：①用户拍板流式不做（酒馆=外偶发场景压不出
收益+课堂线已有流式+OWI 更新覆盖自改件前科）；②块内 ThreadPool 4 工人并发实测全笔变慢
（4段 11.1→15.8s、3段 7.3→11.1s、2段 5.8→8.7s）=GSV 单卡推理串行本质，并发=GPU 争抢
纯亏，串行即本机物理最优（数据存档防再试）。
v3.2（1020 晚·微调三刀，用户听后细单）：①报名前缀剥声（「拉姆：」等锚只管路由不再朗读，
用户令「人名不要念出」；句中人名=角色第三人称自称属对白本体，保留——要全剥一行可改）；
②符号全折算逗号级停顿（用户令「遇符号都算断句算作逗号」：括号/引号/破折号/省略号/冒号
分号等→中文逗号=GSV 短停顿，句号级停顿太长弃用；。！？、保留原位）。实锤=OWI 前端只按
英文 .!? 断句、GSV 读括号内容且不给停顿→「（坐在窗边看他）我算了一下」连读怪腔真身；
③chunk 硬切 80 改软换行：优先落在最近停顿标点，找不到才硬切（实锤=80 硬切把
「艾米莉亚：（把书往旁边放」拦腰斩断、「我算了一下」甩进下一笔请求=怪断句真凶之二）。
延迟定谳（1020 晚 19:30 实测日志）：首笔音频≈LLM 出字+整块串行合成（187 字 3 段 11.5s）；
GPU 空闲无后台缓存任务，OWI 语音缓存只对同文字重播命中（新回复永 miss）=非流式管线
结构性下限，非故障。
v3.3（1020 晚·符号折算改类目制，用户令「不能遇一个改一个」）：v3.2 逐符号枚举扩集废止，
改 Unicode 大类默认拒绝制——字母/数字（任意文字）放行，标点 P* 与符号 S* 两大类一律折算
中文逗号=短停顿，控制/格式符丢弃；白名单只留 GSV 认得的句读「，。！？、」，ASCII !?→全角。
业界正典（1020 联网取证）：SSML <break>=W3C 停顿标准（GSV api_v2 不吃 SSML，中文逗号即
本管等效物）；ChatTTS 标点类→[uv_break] 停顿令牌；echogarden「isolated dash 转 comma 确保
断句」「VITS 系无标点不给停顿」；Amazon TN 按 Unicode 类切分——类目映射=通行做法。
小数点回填（数字，数字{1~2}位且后继非数字→点）；锚提取之后跑不变（冒号是路由锚）。
v3.4（1020 晚·机读残字闸，用户实听报障「2110333057 被念出来」）：酒馆生图回复尾贴
![gid](/gen/gid.png)，OWI 洗文本把 alt 内联=整条请求只剩「211033-3057」类图片 ID，念成
「二一零三三，三零五七」。修两处：①根治=桥侧 gen 图 alt 不再带 gid（![](/gen/…png)，
OWI 洗完=零残字）；②兜底=sanitize 后全文无字母类字符（Unicode L*，数字/标点不算）即判
机读残字→SKIP 400 不合成（与 empty-clean 同语义同响应）。表情图 alt「拉姆 anger」v3
INLINE_LABEL 已剥不在靶；纯数字对白在角色扮演场景属病态，闸误杀风险接受存档。
监听 10.14.14.2:9234（只绑 EasyTier 网卡，禁 0.0.0.0——桥域血案家法）。
v3.5（1020 晚·内心音，用户拍板「低音中间档=像角色内心音一样」）：括号动作描写（（）/()）
不再全音量本音直念——split_quiet 切出 quiet 段，同角色本音合成后 ffmpeg volume 压低
（QUIET_VOLUME=0.5 即 −6dB，会诊锚定 −4~−6dB 浅端起步耳测加深），段内边界 normalize 后
补逗号停顿（normalize 剥尾逗号，顺序勿倒）；
duck 失败回退原响度不炸单。引擎侧查证（1020 联网）：本机 api_v2.py 源码+官方文档双证无
emotion/whisper/音量参数，GSV 不吃 SSML；社区「情绪控制」通行解=参考音频切换制（api.py
fork 的 emotion 接口本质=预设参考音频夹），情绪跟着参考音频走、零样本原生参数控制不存在
（RVC-Boss issue #2448 实锤文本提示不可靠）。引擎级「软声」变体=每角色加低语参考音频
（aux_ref 音色融合道）留作后续可选项；响度数值等 DeepSeek 会诊（有声书/配音工业内心独白
响度差）+耳测微调。
v3.6（1021 晨·内心音真混响，用户三档实听选中档）：quiet 段压低后挂卷积混响（顺序=
用户铁律「先压低再加效果器」）。合成 IR=预延迟 3ms+早反射 7/13/21ms+0.28s 指数衰减
噪声尾+单极点低通，L2 能量归一（REVERB_WET=0.18 直接=湿/干幅度比），输出带 0.45s
尾音余量段防段边界截断（会诊实锤 Audacity 手册坑）。aecho 判负存档（1020 用户「像
浴室」：梳状滤波物理上非混响）；不走 ffmpeg afir（每段起进程+IR 文件管理重），自写
numpy FFT 卷积（GSV runtime 自带 numpy），实测 3.4s clip 12~31ms/段。前夜 demo 血案
存档：IR 归一误用 L1 范数湿声 −47dB 全灭（用户实听「没听到混响」定谳）——效果器
验收必须实测湿声电平（干声残差法），只测耗时=半验。
v3.7（1021 午·chunk 上限 80→50+掉字检测闸，用户报「大概率找不到工作」这句没语音）：OWI 缓存
音频 ASR 定谳=句子真丢了；追凶三回合：①同片回放完好→非「必掉」；②50 字片仍稳定掉头 4 字
（「可能砍半」）→③定谳=GSV 输出按 (文本,声线,seed) **完全确定性**，seed=42 下某些文本+声线
组合生成坏音频且钉死复现（10:57 案=ram 声线掉尾、AI 回放=rem 声线完好，故一度误判偶发；
与 v3 时代 138→90 截断同病）。修两刀：①片上限 50 降暴露面；②掉字检测闸 audio_suspicious=
估时(4.6 字/秒+每停顿 0.3s，实测校准)对实际时长，<82% 判可疑→seed=43 重合成一条取更长
（坏骰重掷），自动愈合不再静默。掉字检测=ASR 字数法（时长法判死存档见函数注）。
v3.8（1021 晚·chunk 上限回摆 50→80，用户拍板「第二种吧，不然听着难受」）：50 字短片
韵律碎片化判负。会诊背书：官方教程 50 字只是保守线，社区 #1256 实证 80~110 字跑全书
流畅；掉尾本质=AR 长度泛化路径级缺陷，任何长度风险非零，靠短片压制治标。暴露面回升
由 ASR 字数闸兜底（v3.7 已在役），垫逗号偏方不动。
v3.8b（1021 晚·回放实弹即中一案：80 字逗号切点把「不是人，」落成片2 裸开头被吞——
垫逗号降概率非免疫，字数闸数学盲区=≤5% 丢失落在健康带 0.954 内）。补两刀：①片头闸
head_suspicious=片头 4s ASR 首字缺席即报警（专抓计数闸盲区，误报仅良性重骰）；②切点
两级优先=句末标点（。！？）先于停顿标点（句界切=整句出声治碎片化，新片头=新句主谓流
远离裸短句高危位）。重试逻辑升级：重骰过闸直接取（不再唯时长论）。
v3.8c（1022 晨·声线串台单，用户耳验抓到：重播拉姆独白出了雷姆声）：236 字独白唯一
一提「这一点拉姆不哄你」过不了旧投票线（≥2 才认），直播时对=蹭上条锚点消息的 120s
继承，单独重播继承冷了落默认 rem。放宽投票=≥1 且无对手即认（拉姆/蕾姆惯用第三人称
自指，无锚独白里自指远多于跨提），投票胜出回写 _LAST_SPEAKER 独白链后续跟着走。
v3.9（1022·认显式声线字段，B 方案最后一刀）：桥决议器（v4.4.0）查锚点账本后带 voice
字段转发=查表确定的声线，优先于投票/继承/默认（hint 校验须在声线表内，narrator_default
拒收防裸转发绕过启发式）。锚点段照旧按「名字：」路由——桥管这条消息，锚点管这段话，
两层不打架。失配时决议器剥字段裸转发，本壳行为与 v3.8c 完全一致（零退化）。
v3.9.2（1105 晚·可观测性四刀，1105 语音「停在半路」案复盘令）：三方日志对账实锤=片头/字数
两闸对 ASR 同音字（她→他/顿→蹲/拆→查/话锋→画风衣）精确比对误报风暴，几乎每片重骰，单笔
19.6~57.3s 超出 OWI 等待窗=截断真身。本版只加观测不加判：①REQ #id 进场行，闸线/重骰线/
每片耗时行全带 #id+片序（并发请求行交错不可读案）；②重骰判决三态（kept/keep-original/
fail）不再静默——旧标签 AUDIO-SHORT retry 实为两闸共用一驳，按触发原因改标；③OK 行带
head_rr/short_rr 重骰计数；④CLIENT-ABORT=响应写出失败显式记账（OWI 半路放弃=合成白烧，
此前零日志难定谳）。业界正典（1105 联网四路取证）：TTS→ASR round-trip CER 闸=canonical
loop（rodwoods.dev round-trip CER / inworld open-tts-eval / NVIDIA Riva tts-evaluate /
FutureAGI TTSAccuracy 95% 门），但 WER/CER 须读作 TTS+ASR 联合信号（inworld 官注）、
极短句 ASR 分歧应隔离复核非硬判（ttsproof ASR-uncertainty quarantine）——片头闸同音
宽容（pypinyin 拼音串编辑距离）=下一刀候选，待用户拍板。
v3.9.3（1105 深夜·片头闸同音宽容=方案 X，用户拍板「搞X」）：v3.9.2 复盘定谳误报主因=ASR
回读惯把同音字写成别字（她→他/顿→蹲/话锋→画风衣/蕾→雷/可→克）而闸拿精确子串比对必炸。
业界正典（1105 四路取证）=比对前双方规范化到口语形态（ttsproof equivalence-aware）——中文
的口语形态就是无调拼音。落地=期望首字与回读前 6 字各转无调音节（pypinyin lazy_pinyin，
GSV runtime 新装，清华镜像）比音节：同音放行；音节真缺（「用户」吞头案）仍重骰；拆/查
这类不同音的真误读照抓（chai≠cha）。pypinyin 缺席=自动退回旧精确比对（fail-open 同款，
闸语义不升不降）。字数闸不动（数 CJK 个数天然抗同音）。
日志: gsv-openai-proxy.log（同目录）。
"""
import json
import os
import re
import time
import base64
import itertools
import unicodedata
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gsv-openai-voices.json")
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gsv-openai-proxy.log")
GSV = "http://127.0.0.1:9880/tts"
FFMPEG = r"D:\AI\GPT-SoVITS-v2pro-20261006\runtime\ffmpeg.exe"
BIND = ("10.14.14.2", 9234)
REQ_SEQ = itertools.count(1)   # v3.9.2 请求号：并发请求日志行交错可读性

PREFIX_ANY = re.compile(
    r"(拉姆|[蕾雷]姆|艾米莉亚|艾米|emilia|ram|rem)\s*[:：]", re.IGNORECASE)
PREFIX_MAP = {
    "拉姆": "ram", "蕾姆": "rem", "雷姆": "rem", "艾米莉亚": "emt", "艾米": "emt",
    "ram": "ram", "rem": "rem", "emt": "emt", "emilia": "emt",
}
NAME_COUNTS = [
    ("rem", re.compile(r"[蕾雷]姆")),
    ("ram", re.compile(r"拉姆")),
    ("emt", re.compile(r"艾米莉亚|艾米|emilia", re.IGNORECASE)),
]
# 裸 alt 标签（1020 案实锤：OWI 前端把 ![拉姆 disapproval](url) 洗成内联文字"拉姆 disapproval"
# 粘在句中，行锚正则拦不住；此处按「名字+空格+一个英文词」内联通杀，只吃一词防误吞正文）
INLINE_LABEL = re.compile(r"(拉姆|[蕾雷]姆|艾米莉亚|艾米)\s+[a-zA-Z][a-zA-Z0-9_]*")

# v3.5 内心音（1020 用户拍板）：括号动作描写=同角色本音压低念（有声书内心独白手法）。
# 引擎无原生情绪/音量参数（v3.5 头注查证账），压低=ffmpeg 后处理。
QUIET_VOLUME = "0.5"   # 线性倍率 = -6dB（会诊锚定区间 −4~−6dB 的浅端，从浅起步耳测加深）
ParenQ = re.compile(r"（[^（）]*）|\([^()]*\)")

# 跨请求说话人继承（无状态 HTTP 的土记忆）：OWI 前端把一条消息按标点切成多笔请求先后送来，
# 后续块可能整块无前缀（前缀被切进上一块），120s 窗内沿用上一笔的说话人
_LAST_SPEAKER = [0.0, "rem"]
_INHERIT_WINDOW = 120.0

# 符号→停顿（v3.3 类目制，1020 用户令「不能遇一个改一个」）：默认拒绝——白名单外
# 的标点 P*/符号 S* 一律折算中文逗号=GSV 短停顿（句号级停顿太长弃用），控制/格式符丢弃。
# 必须在 plan_segments 之后跑（冒号是路由锚，先跑会拆锚）。
_PAUSE_KEEP = set("，。！？、")
_ASCII_PAUSE_MAP = {"!": "！", "?": "？", "'": "", "’": ""}


def normalize_pause(text):
    out = []
    for ch in text:
        if ch in _PAUSE_KEEP:
            out.append(ch)
            continue
        if ch in _ASCII_PAUSE_MAP:
            out.append(_ASCII_PAUSE_MAP[ch])
            continue
        cat = unicodedata.category(ch)
        if cat[0] in "LN":        # 字母/数字（任意文字、全半角）
            out.append(ch)
        elif ch in "\r\n":        # 换行=停顿
            out.append("，")
        elif cat == "Zs":         # 空格保留
            out.append(" ")
        elif cat[0] in "PS":      # 标点/符号（括号引号破折号省略号冒号分号货币数学表情…全落此）
            out.append("，")
        # 其余（控制/格式/私有区）直接丢
    text = "".join(out)
    text = re.sub(r" *([，。！？]) *", r"\1", text)          # 停顿标点吸附相邻空格
    text = re.sub(r"(\d)，(\d{1,2})(?!\d)", r"\1.\2", text)  # 小数点回填（3，5→3.5；千分位 1，000 不动）
    text = re.sub(r"，{2,}", "，", text)
    text = re.sub(r"，(?=[。！？])", "", text)    # 句末标点前的逗号让位
    text = re.sub(r"(?<=[。！？])，+", "", text)  # 句末标点后的逗号让位
    return text.strip("， \n")


def log(msg):
    from datetime import datetime
    line = f"{datetime.now():%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_voices():
    with open(CONF, encoding="utf-8") as f:
        return json.load(f)


def sanitize(text):
    """剔除一切不该出声的东西：markdown 图片(alt一起没)/裸 alt 残字/表情标记/链接留字/裸URL。"""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)      # markdown 图片整删（直连未过 OWI 洗的防御层）
    text = INLINE_LABEL.sub(" ", text)                      # 裸 alt 残字「拉姆 disapproval」行中行首通杀
    text = re.sub(r"\[\[[^\]]*\]\]", " ", text)            # [[表情:caring]]
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)   # 链接留文字
    text = re.sub(r"https?://\S+", " ", text)              # 裸 URL
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fallback_voice(text, hint=None):
    """无前缀文本三级兜底：显式声线(桥决议器 v3.9)→名字投票(≥1 且严格占优)→继承→rem。
    v3.9 hint=桥决议器查锚点账本得出的确定声线，查表≠猜测，优先于一切启发式。
    名字投票(1021 放宽，用户耳验抓到声线串台)：旧线 ≥2 漏掉「独白只自指一次」的文本——
    案发 236 字独白唯一一提「这一点拉姆不哄你」被落 rem（直播时对=蹭上条锚点消息
    的继承；单独重播继承窗 120s 冷了就露馅）。拉姆/蕾姆话术惯用第三人称自指
    （「拉姆不哄你」「蕾姆也说两句」），无锚独白里自指远多于跨提，故 ≥1 且无对手
    即认。投票胜出回写 _LAST_SPEAKER，独白后续无锚块跟着走。
    风险账：无锚旁白偶然提到某姐妹一次会跟跑其声线（旁白多走锚点或多提，罕见）。"""
    if hint:
        _LAST_SPEAKER[0] = time.time()
        _LAST_SPEAKER[1] = hint
        return hint
    counts = {k: len(rx.findall(text)) for k, rx in NAME_COUNTS}
    best = max(counts, key=counts.get)
    others = max((v for k, v in counts.items() if k != best), default=0)
    if counts[best] >= 1 and counts[best] > others:
        _LAST_SPEAKER[0] = time.time()
        _LAST_SPEAKER[1] = best
        return best
    if time.time() - _LAST_SPEAKER[0] <= _INHERIT_WINDOW:
        return _LAST_SPEAKER[1]
    return "rem"


def plan_segments(text, hint=None):
    """「名字：」锚切分路由（全文任意位置，前缀一并保留朗读）；无锚整段走兜底(hint 优先)；同声线相邻合并。"""
    ms = list(PREFIX_ANY.finditer(text))
    segs = []
    if not ms:
        segs.append([fallback_voice(text, hint), text.strip()])
    else:
        head = text[:ms[0].start()].strip()
        if head:
            segs.append([fallback_voice(head, hint), head])
        for i, m in enumerate(ms):
            k = PREFIX_MAP.get(m.group(1).lower()) or PREFIX_MAP.get(m.group(1)) or "rem"
            end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
            # v3.2 锚只管路由不出声（用户令「人名不要念出」）：朗读正文从冒号后起
            body = text[m.end():end].strip()
            if body:
                segs.append([k, body])
    merged = []
    for k, s in segs:
        if not s:
            continue
        if merged and merged[-1][0] == k:
            merged[-1][1] += s
        else:
            merged.append([k, s])
    if merged:
        _LAST_SPEAKER[0] = time.time()
        _LAST_SPEAKER[1] = merged[-1][0]
    return [(k, s.strip()) for k, s in merged if s.strip()]


def chunk(text, limit=80):
    """长段软换行：上限 80=v3.8（1021 晚回摆，用户拍板）：50 短片只用半天即判碎
    （「不然听着难受」=韵律碎片化）；社区 #1256 实证 80~110 字跑全书流畅。掉尾风险
    （77 字片曾静默掉 14 字）不靠短片压制——AR 长度泛化缺陷任何长度风险非零，兜底=
    ASR 字数闸+片头闸（head_suspicious），垫逗号偏方照旧。
    切点两级优先（v3.8b）：先倒扫句末标点（。！？），找不到才退回停顿标点——句界切
    =天然韵律单元（治 50 字碎片化的正是「整句出声」），且新片开头=新句主谓流，远离
    「逗号后裸短句落片头」高危位（1021 实锤：逗号切点让「不是人，」成片2 开头被吞）。"""
    if len(text) <= limit:
        return [text]
    pauses = set("，。！？、；!?;…")
    strong = set("。！？!?")
    out = []
    while len(text) > limit:
        cut = limit
        for i in range(limit, limit // 2, -1):
            if text[i - 1] in strong:
                cut = i
                break
        else:
            for i in range(limit, limit // 2, -1):
                if text[i - 1] in pauses:
                    cut = i
                    break
        out.append(text[:cut])
        text = text[cut:]
    if text.strip():
        out.append(text)
    return [p for p in out if p.strip()]


def split_quiet(text):
    """v3.5 内心音切分：括号动作描写切出为 quiet 段（括号自身剥掉），其余为普通段。
    未闭合括号不切（当普通文本交给类目折算成停顿）；嵌套括号只吃最内层（外层壳折算停顿）。"""
    runs = []
    pos = 0
    for m in ParenQ.finditer(text):
        if m.start() > pos:
            runs.append([text[pos:m.start()], False])
        inner = m.group(0)[1:-1].strip()
        if inner:
            runs.append([inner, True])
        pos = m.end()
    if pos < len(text):
        runs.append([text[pos:], False])
    return [(t, q) for t, q in runs if t.strip()]


def duck_wav(wav):
    """v3.5 内心音：段级压低（ffmpeg volume，会诊配方 v1=纯 volume 不加滤波/混响），
    失败回退原响度不炸单。段间相对响度锚定（测对白段 LUFS 再算增益）留作耳测后升级项。"""
    import subprocess, tempfile
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            tf.write(wav)
            p = tf.name
        out = p + ".q.wav"
        subprocess.run([FFMPEG, "-y", "-i", p, "-af", f"volume={QUIET_VOLUME}",
                        "-c:a", "pcm_s16le", out], check=True, capture_output=True, timeout=60)
        with open(out, "rb") as f:
            wav = f.read()
        os.remove(out)
        os.remove(p)
        return wav
    except Exception as e:
        log(f"duck fail -> full volume: {e!r}")
        return wav


# v3.6 内心音真混响（1021 用户三档实听选中档）：quiet 段 duck 后挂卷积混响。
# IR 按 sr 缓存（GSV 固定 48k，只造一次）；L2 归一后 wet 直接=湿/干幅度比。
REVERB_WET = 0.18    # 浅档（1022 用户耳审判中档太大，降 18）
SILENT_MP3_B64 = (   # 0.1s 24000Hz mono 静音 mp3（ffmpeg anullsrc，908B）——空片静音闸用
    "SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYzLjEuMTAwAAAAAAAAAAAAAAD/84TAAAAAAAAAAAAASW5mbwAAAA8AAAAHAAADYABV"
    "VVVVVVVVVVVVVVVVVXFxcXFxcXFxcXFxcXFxjo6Ojo6Ojo6Ojo6Ojo6qqqqqqqqqqqqqqqqqqqrHx8fHx8fHx8fHx8fHx+Pj4+Pj"
    "4+Pj4+Pj4+Pj//////////////////8AAAAATGF2YzYzLjEuAAAAAAAAAAAAAAAAJAQgAAAAAAAAA2CZUAveAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAD/80TEAAAAA0gAAAAATEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1FMy7/80TEUwAAA0gAAAAAMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1FMy7/80TEpgAAA0gAAAAAMTAwVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1FMy7/"
    "80TErAAAA0gAAAAAMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVMQU1FMy7/80TErAAAA0gAAAAAMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/80TErAAAA0gAAAAAVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/80TErAAAA0gAAAAA"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVU="
)
REVERB_TAIL = 0.45   # 输出尾音余量段（秒），防段边界截断（会诊实锤坑）
_IR_CACHE = {}


def _synth_ir(sr):
    import numpy as np
    n = int(sr * REVERB_TAIL)
    t = np.arange(n) / sr
    ir = np.random.default_rng(42).standard_normal(n)
    ir *= np.exp(-t / 0.28)           # 扩散尾（衰减常数 0.28s，耳审定档随 wet 一起出）
    ir[: int(sr * 0.003)] = 0         # 3ms 预延迟（干声先行）
    for d_ms, g in ((7, 0.35), (13, 0.25), (21, 0.18)):   # 早反射
        ir[int(sr * d_ms / 1000)] += g
    out = np.empty_like(ir)
    acc = 0.0
    for i in range(n):                # 单极点低通去颗粒感（一次性成本，造完即缓存）
        acc += 0.5 * (ir[i] - acc)
        out[i] = acc
    fade = int(sr * 0.02)
    out[-fade:] *= np.linspace(1, 0, fade)   # IR 尾淡出防截断咔哒
    out /= np.sqrt((out * out).sum())        # L2 能量归一（L1 血案见头注 v3.6）
    return out


def reverb_wav(wav):
    """v3.6 quiet 段混响：干声全量+湿声 REVERB_WET，FFT 卷积合成 IR，输出带尾音余量。
    只吃 pcm_s16le wav（duck_wav 出品）；失败回退压低件不炸单。"""
    import io, wave
    try:
        import numpy as np
        with wave.open(io.BytesIO(wav), "rb") as w:
            sr, ch = w.getframerate(), w.getnchannels()
            if w.getsampwidth() != 2:
                return wav
            x = np.frombuffer(w.readframes(w.getnframes()),
                              dtype=np.int16).astype(np.float64) / 32768.0
        x = x.reshape(-1, ch)
        ir = _IR_CACHE.get(sr)
        if ir is None:
            ir = _IR_CACHE[sr] = _synth_ir(sr)
            log(f"reverb IR ready sr={sr} n={len(ir)}")
        n = len(x) + len(ir) - 1
        nfft = 1 << (n - 1).bit_length()
        Y = np.fft.irfft(np.fft.rfft(x, nfft, axis=0)
                         * np.fft.rfft(ir, nfft)[:, None], nfft, axis=0)
        out_len = len(x) + int(sr * REVERB_TAIL)
        y = np.zeros((out_len, ch))
        y[: len(x)] = x
        y += REVERB_WET * Y[:out_len]
        peak = np.abs(y).max()
        if peak > 0.99:
            y /= peak / 0.99
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(ch)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((y * 32767).astype(np.int16).tobytes())
        return buf.getvalue()
    except Exception as e:
        log(f"reverb fail -> ducked only: {e!r}")
        return wav


def gsv_tts(text, ref, seed=42):
    # v3.7 吞开头短句偏方（1021 实锤：裸开头「短句+逗号」被 GSV 系统性吞掉——「可能砍半，」
    # 六个种子全灭、前缀「，」后 3/3 种子全活；与社区已知吞首字病同款）。前缀只加停顿符
    # 零 CJK，不碰切分/路由/掉字闸的账。
    payload = {
        "text": "，" + text, "text_lang": "zh",
        "ref_audio_path": ref["refAudioPath"],
        "prompt_text": ref["promptText"], "prompt_lang": "ja",
        "text_split_method": "cut0", "media_type": "wav",
        "streaming_mode": False, "speed_factor": 1.0, "seed": seed,
        "temperature": 1.0, "top_k": 15, "top_p": 1.0,
    }
    greq = urllib.request.Request(
        GSV, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    with urllib.request.urlopen(greq, timeout=120) as resp:
        return resp.read()


def wav_duration(wav):
    import io, wave
    try:
        with wave.open(io.BytesIO(wav), "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return 0.0


_ASR = [None]   # 懒加载单例（SenseVoiceSmall，GSV runtime 自带 funasr）


def _asr_model():
    if _ASR[0] is None:
        from funasr import AutoModel
        _ASR[0] = AutoModel(model="iic/SenseVoiceSmall", trust_remote_code=True,
                            device="cpu", disable_update=True)
    return _ASR[0]


def audio_suspicious(wav, text, tag=""):
    """v3.7 掉字闸（1021 实锤两案：77 字片掉尾 14 字/49 字片掉头 4 字，按
    (文本,声线,seed) 确定性复现）。⭐时长法判死存档：健康语速散布 ±10% 盖过小掉字
    （0.82/0.85 两版阈值一个漏坏件一个误报好件，真数据双杀）。改 ASR 字数法：
    转写 CJK 字数 vs 输入 CJK 字数，<93% 判可疑——同音字不改字数=天然抗 ASR 噪声。
    阈值 0.93 由真件定标：两坏案 0.78/0.907，健康件 0.954；误报代价=重合成一次取
    更长（~4s，无害）。fail-open：ASR 链路任何异常=放行不拦。"""
    import re, io, tempfile, subprocess, contextlib
    try:
        cjk = lambda s: len(re.sub(r"[^\u4e00-\u9fff]", "", s))
        n = cjk(text)
        if n < 8:
            return False
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            tf.write(wav)
            p = tf.name
        out16 = p + ".16k.wav"
        subprocess.run([FFMPEG, "-y", "-i", p, "-ar", "16000", "-ac", "1", out16],
                       check=True, capture_output=True, timeout=60)
        res = _asr_model().generate(input=out16, language="zh", use_itn=False)
        spoken = cjk(re.sub(r"<\|[^|]*\|>", "", res[0]["text"]))
        ratio = spoken / float(n)
        bad = ratio < 0.93
        if bad:
            log(f"{tag}AUDIO-SHORT suspicious: cjk in={n} spoken={spoken} ratio={ratio:.2f}")
        return bad
    except Exception as e:
        log(f"audio guard fail-open: {e!r}")
        return False
    finally:
        with contextlib.suppress(Exception):
            os.remove(p)
        with contextlib.suppress(Exception):
            os.remove(out16)


_PY = [None, True]   # v3.9.3 lazy_pinyin 单例 + 可用旗（库缺席退精确比对，fail-open 同款）


def _pinyin_fn():
    if not _PY[1]:
        return None
    if _PY[0] is None:
        try:
            from pypinyin import lazy_pinyin
            _PY[0] = lazy_pinyin
        except Exception as e:
            _PY[1] = False
            log(f"pypinyin unavailable -> head gate exact-match fallback: {e!r}")
            return None
    return _PY[0]


def _head_missing(head, asr_text):
    """v3.9.3 同音宽容比对（1105 误报风暴案，用户拍板方案 X）：ASR 回读惯把同音字写成
    别字（她→他/顿→蹲/话锋→画风衣/蕾→雷/可→克），精确子串比对必炸。正典=比对前双方
    规范化到口语形态（ttsproof equivalence-aware）——中文的口语形态就是无调拼音。期望首字
    与回读前 6 字各转音节，音节缺席才判真吞字；「拆/查」这类不同音的真误读照抓。"""
    fn = _pinyin_fn()
    if fn is None:
        return head not in asr_text
    head_py = fn(head)
    asr_py = fn(asr_text[:6])
    if not head_py or not asr_py:
        return head not in asr_text
    return head_py[0] not in asr_py


def head_suspicious(wav, text, tag=""):
    """v3.8b 片头闸（1021 实锤：80 字逗号切点让「不是人，」落成片2 裸开头被吞——
    垫逗号偏方降概率非免疫；字数闸数学盲区=≤5% 丢失落在健康带 0.954 内抓不到）。
    片头 4s ASR，首 CJK 字缺席才报警（首字被吞=音频里真没有；ASR 首词误听时有发生
    →误报代价仅重骰一次，良性偏严划算）。极短片（无 CJK）放行。fail-open 同款。"""
    import re, tempfile, subprocess, contextlib
    try:
        heads = re.findall(r"[\u4e00-\u9fff]", text)[:2]
        if not heads:
            return False
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            tf.write(wav)
            p = tf.name
        out16 = p + ".head.wav"
        subprocess.run([FFMPEG, "-y", "-t", "4", "-i", p, "-ar", "16000", "-ac", "1",
                        out16], check=True, capture_output=True, timeout=60)
        res = _asr_model().generate(input=out16, language="zh", use_itn=False)
        t = re.sub(r"<\|[^|]*\|>", "", res[0]["text"])
        bad = _head_missing(heads[0], t)   # v3.9.3 拼音层同音宽容（方案 X）
        if bad:
            log(f"{tag}HEAD-DROP suspicious: head=「{heads[0]}{''.join(heads[1:])}」 asr4s={t[:24]!r}")
        return bad
    except Exception as e:
        log(f"head guard fail-open: {e!r}")
        return False
    finally:
        with contextlib.suppress(Exception):
            os.remove(p)
        with contextlib.suppress(Exception):
            os.remove(out16)


def concat_wavs(wavs):
    """多段 wav 用 ffmpeg concat 拼一条；失败回退第一段。"""
    if len(wavs) == 1:
        return wavs[0]
    import subprocess, tempfile, glob
    tmp = tempfile.mkdtemp(prefix="gsvseg_")
    try:
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for i, w in enumerate(wavs):
                p = os.path.join(tmp, f"seg{i}.wav")
                with open(p, "wb") as g:
                    g.write(w)
                f.write(f"file '{p}'\n")
        out = os.path.join(tmp, "out.wav")
        subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", out], check=True, capture_output=True, timeout=60)
        with open(out, "rb") as f:
            return f.read()
    except Exception as e:
        log(f"concat fail -> first seg only: {e!r}")
        return wavs[0]
    finally:
        for p in glob.glob(os.path.join(tmp, "*")):
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(tmp)
        except OSError:
            pass


def transcode(audio, fmt):
    """GSV 只出 wav；要别的格式 ffmpeg 本地转（v1 同款）。"""
    if fmt in ("wav", "pcm"):
        return audio, "audio/wav"
    import subprocess, tempfile
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            tf.write(audio)
            wav_path = tf.name
        mp3_path = wav_path + ".mp3"
        subprocess.run([FFMPEG, "-y", "-i", wav_path, "-codec:a", "libmp3lame",
                        "-q:a", "4", mp3_path], check=True, capture_output=True, timeout=60)
        with open(mp3_path, "rb") as f:
            audio = f.read()
        os.remove(mp3_path)
        os.remove(wav_path)
        return audio, "audio/mpeg"
    except Exception as e:
        log(f"ffmpeg transcode fail -> fallback wav: {e!r}")
        return audio, "audio/wav"


def _seg_head(p):
    return p[:12].replace("\n", "/").replace("\r", "")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/health", "/v1/models"):
            body = json.dumps({"status": "ok", "voices": sorted(load_voices().keys())}).encode()
            self._send(200, body)
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        if not self.path.startswith("/v1/audio/speech"):
            self._send(404, b'{"error":"not found"}')
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(length) or b"{}")
        except Exception as e:
            self._send(400, json.dumps({"error": f"bad json: {e}"}).encode())
            return
        raw = (req.get("input") or "").strip()
        if not raw:
            self._send(400, b'{"error":"input is required"}')
            return
        want = str(req.get("response_format") or "mp3").lower()
        t0 = time.time()
        rid = next(REQ_SEQ)   # v3.9.2 并发请求日志行交错可读性（1105 截断案复盘令）
        log(f"REQ #{rid} chars={len(raw)} want={want} voice={str(req.get('voice') or '-')[:24]}")
        voices = load_voices()
        hint = str(req.get("voice") or "").strip().lower()   # v3.9 桥决议器显式声线
        if hint not in voices or hint == "narrator_default":
            hint = None
        clean = sanitize(raw)
        if not clean or not any(unicodedata.category(c)[0] == "L" for c in clean):
            # v3.9.1 空片静音闸（1022 用户报 OWI 报 External:400）：纯标点/机器码片不合成，
            # 但回 200+0.1s 静音 mp3——OWI 前端对 4xx 弹红字报错，播静音=用户无感。日志照记可观察。
            log(f"#{rid} SKIP machine-only -> SILENT chars={len(clean)}「{_seg_head(clean or '')}」")
            self._send(200, base64.b64decode(SILENT_MP3_B64), ctype="audio/mpeg")
            return
        segs = plan_segments(clean, hint)
        wavs, fails, plan = [], 0, []
        head_rr = short_rr = 0   # v3.9.2 重骰计数进 OK 行
        for key, seg_text in segs:
            ref = voices.get(key) or voices.get("narrator_default") or voices["rem"]
            runs = split_quiet(seg_text)  # v3.5 内心音切分（先绑定，len(runs) 边界停顿要用）
            for i, (run_text, quiet) in enumerate(runs):
                t = normalize_pause(run_text)  # v3.3 符号类目折算（锚提取后才跑）
                if not t:
                    continue
                if i < len(runs) - 1:
                    t += "，"  # v3.5 段内边界停顿（normalize 剥尾逗号，归一化后补回）
                for piece in chunk(t):
                    plan.append((key, piece, quiet))
                    ptag = f"#{rid} P{len(plan)}"   # v3.9.2 片级可观测
                    try:
                        pi_t0 = time.time()
                        wav = gsv_tts(piece, ref)
                        reasons = []
                        if audio_suspicious(wav, piece, tag=ptag):
                            reasons.append("short")
                        elif head_suspicious(wav, piece, tag=ptag):
                            reasons.append("head")
                        if reasons:
                            if reasons[0] == "head":
                                head_rr += 1
                            else:
                                short_rr += 1
                            try:
                                wav2 = gsv_tts(piece, ref, seed=43)
                                bad2 = audio_suspicious(wav2, piece, tag=ptag) or head_suspicious(wav2, piece, tag=ptag)
                                if not bad2 or wav_duration(wav2) > wav_duration(wav):
                                    wav = wav2
                                    log(f"{ptag} retry seed=43 kept {'+'.join(reasons)}"
                                        + ("" if not bad2 else " (longer)"))
                                else:
                                    log(f"{ptag} retry seed=43 keep-original {'+'.join(reasons)}"
                                        + " (still bad, not longer)")
                            except Exception as e2:
                                log(f"{ptag} retry fail keep-original: {e2!r}")
                        if quiet:
                            wav = duck_wav(wav)
                            wav = reverb_wav(wav)  # v3.6 先压低后混响（用户铁律）
                        wavs.append(wav)
                        log(f"{ptag}[{key}{'·q' if quiet else ''}] {time.time() - pi_t0:.1f}s ok")
                    except Exception as e:
                        fails += 1
                        log(f"{ptag} GSV FAIL voice={key} err={e!r}")
        # v3.1 并发实验判负存档（1020）：ThreadPoolExecutor 4 工人实测全笔变慢
        # （4段 11.1→15.8s，3段 7.3→11.1s，2段 5.8→8.7s）=GSV 单卡推理串行本质，
        # 并发=GPU 争抢+线程开销纯亏。串行即本机物理最优，勿再试并发。
        if not wavs:
            self._send(502, json.dumps({"error": "gsv upstream: all segments failed"}).encode())
            return
        audio, ctype = transcode(concat_wavs(wavs), want)
        plan_desc = " + ".join(
            f"{k}:{len(p)}{'·q' if q else ''}「{_seg_head(p)}」" for k, p, q in plan)
        log(f"OK #{rid} want={want} sent={ctype} chars={len(raw)} stripped={len(raw) - len(clean)} "
            f"plan=[{plan_desc}] segs={len(plan)} fail={fails} head_rr={head_rr} short_rr={short_rr} "
            f"bytes={len(audio)} t={time.time() - t0:.1f}s")
        try:
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(audio)))
            self.end_headers()
            self.wfile.write(audio)
        except Exception as e:
            # v3.9.2 客户端半路放弃（OWI 等待窗）=整笔合成白烧，显式记账
            log(f"#{rid} CLIENT-ABORT sent-fail bytes={len(audio)} "
                f"t={time.time() - t0:.1f}s err={e!r}")


if __name__ == "__main__":
    log(f"gsv-openai-proxy v3.9.3 start on {BIND}")
    ThreadingHTTPServer(BIND, Handler).serve_forever()
