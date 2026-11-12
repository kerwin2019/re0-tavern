# -*- coding: utf-8 -*-
"""
v4.4.9（1113 晨·重画令牌，用户醒后令「对图不满意想重新生成/演示要新鲜图」）：新增「重画日记」口
（_diary_redraw_hit：「重画日记」「日记 重画」等去首尾+内部空格（全半角）后恰为四字才命中，精确制
同「日记」口），命中= _comic_payload(force=True)：跳过当日幂等重新 文案→入队→覆盖 comic_state
（此后打「日记」秒回的就是新图）；prompt 尾附「换不同取材角度避免与上一版雷同」；队列 item 带
seed_base=时间派生（comic_diary 默认种子=日期基数，同日重画不换种子=构图雷同「重画了个寂寞」），
PC 轮询器透传 --seed-base。旧图不删照在墙上。「日记」口与幂等语义零变化。
v4.4.8（1113 深夜·日记令牌改接四格漫画线，用户语义裁决「日记=四格漫画+评分那套，不是睡前插画」）：
触发口原样（_diary_token_hit 只认「日记」二字），但命中后改走 _comic_payload()：当天聊天(_today_msgs)
→文案员提示词（四格漫画线-定档-20261015 正本移植）→GLM(max_tokens 2048, effort low)→容错 JSON 解析
（剥```json栏/找边界/单引号修/失败重试 1 次/解析后值内英文双引号扫地出门）→comic_state.json 当日幂等
→_comic_enqueue()（who=comic kind=comic，scene=台词 JSON 全量，不走 [:500] 截断）。回复=照 v4.4.7 模式：
注入 COMIC_SKILL_BLOCK（角色口吻 1~2 句，禁复述台词）+流尾/非流式收口 _comic_markdown()——三姐妹台词+
随缘评分 markdown 秒级可见，随后 _gen_wait_markdown(gid, timeout=300) 等四格整图嵌回（产图 3-4 分钟
>默认 150，timeout 抬 300）。下游：PC 轮询器 v3 认 kind=="comic"→comic_diary.py 产 完整四格.png→
genupload 同口上墙。v4.4.7 插画接线六处（两管线×检测/tail/收口）全部改接，DIARY_SKILL_BLOCK/
DIARY_FAIL_BLOCK_TMPL/_diary_markdown/DIARY_WHO_CN 退役删除；_diary_token_hit 保留复用；v3.7.9 睡前
插画线回归 21:00 cron 专用（_diary_trigger + /diary/* + crontab 全保留零改动）。
v4.4.7（1113 凌晨·日记令牌上聊天线，用户令「能不能只打日记两个字」）：触发=去首尾空格后整条消息
恰好是「日记」二字（_diary_token_hit 单口；「写日记」「日记？」等部分含「日记」的一概不触发=普通
回话）。三人线+统一管线两检出点（任务调用/裸测关），命中即调 _diary_trigger()（v3.7.9 原口，当日
幂等）：成功=注入 DIARY_SKILL_BLOCK（角色口吻 1~2 句告知写好了，禁复述内容）+回复尾 _diary_markdown
追加日记全文引用块+插画——当日首次=同自拍等图 ≤150s（_gen_wait_markdown 原语）；同日重复触发=不再等
直出 URL（GEN_STORE 内存态重启失忆，防吊满 150s）；失败（今日对话<30 字/GLM 空回）=注入
DIARY_FAIL_BLOCK_TMPL 角色口吻转告（禁提系统术语）。图链与自拍完全同链：genqueue→PC 轮询器→ComfyUI
→genupload 上墙（v3.7.9 T12 骨架零改动）。_diary_trigger 重复分支补 gen_id 字段。
v4.4.6（1024·想法账本分类，用户令「开工吧」；调研+DeepSeek 会诊定案）：①词表=6 类稳定 ID
（stock/work/study/life/relation/other，显示名住 ideas_categories.json 可改不动历史数据）；②<idea>
第四段=分类（可选）：用户口述（含别名映射）优先 source=user，模型从五实质类挑 source=model，
「其他」=用户专属词模型禁选，口述不在闭集/拿不准=未分类（cat=null 系统态，不是「其他」）；③同题
取代时新条目默认继承旧条目实质类目（source=inherited），用户口述覆盖继承，旧条是未分类/其他不继承；
④分类搭主回复便车零额外调用（按次计费无感）。配套 console v2.4.0 浏览页。
v4.4.5（1024·想法账本 MVP，用户令「开工吧」；调研=decision journal+AI resurfacing 成熟模式，会诊
DeepSeek 3863 字审后分档施工）：用户结论的 decision journal——存=用户明示「存想法」→模型末行输出
<idea>问题|结论|理由</idea>（照 <gen> 先例：_IdeaFilter 流式剥行屏显不可见+流尾 idea_store 入库）；
取=注入族新增「想法账本」路（每轮用户向量 vs 账本 active 条目，强命中≥0.60 才注入复述提醒块，
弱命中零注入）；版本=同题≥0.88 新结论自动取代旧条（旧条翻 superseded 不删，新条记 supersedes 链
与 versions 计数，注入时只给最新+旧版计数）；存储=jsonl 真源（/root/work/cloud-config/
ideas_ledger.jsonl）+Qdrant ideas_ledger 集合镜像（懒建照 _ensure_journal_coll 家法）。接线=三人线+
统一管线两处（duet 停用不接）；任务调用/裸测不注入。二三期（候选池/反馈令牌/加权回忆杀）观察后再议。
v4.4.4（1023·DeepSeek 会诊补刀，审阅件=aiDocs/_临时/bridge-lenfree-20261023/deepseek-review-request.md）：
①认真块第5条升级=禁思考中估算字数/篇幅预算+显式否定「精炼/简洁/收束/差不多够了」+历史免责（旧短回复
=旧规则残留非本轮长度示范）+优先级（本条>人设长度习惯）+完成度导向（风险点/步骤/替代方案/复盘/下一
步说完说透）+「不另启深度分析模式等自动分支」（手动认真块=唯一指令源，防双开抢注意力）；②ds
16384→32768（会诊疑点实锤：探针 completion_tokens=91 vs 可见回复24字=思考计入 completion 共享预算，
思考放开后16384余量存疑；32768 探针 200 接受，按次计费抬满无成本）；③「收尾凝练刻薄」去「凝练」
（会诊抓的漏网压缩词）。未采纳：User角色注入（会诊复核同意现有末位system等效且生产验证）、自动模式
改名（优先级条款已覆盖，观察后再议）、记忆块元标签+历史压缩（观察期后再议）、日常软描述（会诊同判
不加）。
v4.4.3（1023·篇幅解缚三刀，用户裁定「酒馆线废除一切字数规矩，长度交给模型自己；只有认真模式
才注入系统块且必须篇幅全开」）：①trio_prompt 减法=删尽话短/行数/句数类硬规矩（拉姆习惯话短、
蕾姆不超5行、三句内收尾、两三句展开边界），根因=字数规矩被模型内化成自掐（思考实录「篇幅有限
要精炼」「大概700-900字」，用户明说放开后仍自划1500-2500）；②认真块加第5条=篇幅完全放开+
思考放最深（块仍置底紧贴 user 生成位，v4.3.5 机制不动）；③防截断抬档=ds 8192→16384（魔搭
max_tokens=16384 探针 200 实证）、glm low 2048→8192 / high 8192→16384、duet 2048→8192、
zhipu_stream_relay 默认 2048→8192（三调用方全显式传参=死默认顺手抬）。薄人设方案用户否决。
v4.4.0（1022·语音决议器，用户拍板 B 方案「桥认得角色，OWI 不认得」）：OWI 的 TTS 引擎 URL 改指
桥新增 /v1/audio/speech 端点=薄决议器（只查表不猜）。桥转播回复的三个写回咽喉（duet/统一/三人，
流式非流式全汇）顺手把「规整全文+锚点位置图」记进滚动账本（20 条）；碎片请求来了做规整子串定位，
命中最优重叠锚点段→带显式 voice 字段转发本地壳；失配剥 voice 裸转发（壳退回锚点/投票启发式）。
壳侧同步认 voice 字段（v3.9）。OWI 前端/后端/壳零改动；OWI 后端注入的 config voice=rem 在失配时
一并剥掉，保启发式语义。设计裁定=DeepSeek 会诊 1022（第四条路边界：账本=UI 无关数据，决议器=
独立查表层，换 UI 迁「决议器+壳+GSV」三件套）。
v4.3.5（1021 晨·认真模式按钮，用户开工令「提交后咱们搞那个认真模式的扩展功能吧」）：OWI Filter
Function（self.toggle=True=输入条内联 chip，官方 docs 实证）当按钮——滤镜 inlet 只在末条 user 尾
打标 [[SERIOUS_MODE]]；装配权留桥（[自拍] 同哲学=提示词单点管理）：do_POST 入口单点剥标置旗
（先剥再取 user=召回/写回/装配全下游零污染），trio 装配块【认真模式】置底=紧贴 user 消息生成位
（用户令「放到最下层」）：问答质量优先+不必过分遵守扮演提示词+拉姆毒舌禁令+出场权重 7:2:1
（放大拉姆/降蕾姆/削艾米莉亚=傻白甜分戏）+表情标签照常；统一管线（单人线）同块去权重句。
认真轮思考档拉满 B["effort"]="max"（glm 档 max_tokens 跟 16384 惯例；ds 本就 8192；local/cli
上游不收参自动忽略）=「要认真思考」走 v4.3.1 修好的 effort 管线不只是嘴上说说。任务调用
（X-OpenWebUI-Task）不注入不提档（防后台任务误触发）；注入经 _add_inj 进小票=验收凭据。
v4.3.4/v4.3.3（1020 深夜·头注补记，正文见 EXPR_TAG_RE 与 _gen_wait_markdown 行注）：
v4.3.4=标签突变形（![拉姆表情:x]）双形正则通吃+EXPR_RULE 负例警示；v4.3.3=gen 图 alt 摘 gid
（OWI 洗文本内联 alt 致图片 ID 被语音念出，1020 实听报障）。
v4.3.2（1020 深夜·表情指令提示词加固一层，用户令「加固一层吧，不然六张图怪怪的」）：按 1020 深夜
DeepSeek 会诊配方（双写=尾部约束衰减+近因+注意力稀释的结构病，提示词层软减频、桥级去重=硬保证）
双刀：①EXPR_RULE 尾加多人场格式骨架 few-shot 正例（会诊引证：精确格式 few-shot ~99% 遵从 vs
裸指令 ~80%，负例再加 ~5%）；②EXPR_REASSERT 尾加【输出终点契约】=末标签即全文最后一字+英文
no 短语收束（近因位放收束指令；中文「不要」易被忽略、英文 no 短语更稳）。桥级 v4.3.1 去重不动
（100% 兜底不变），本层只降模型双写频率、省一层剥标签噪音进前情提要。
v4.3.1（1020 晚·去重闸门修正+ds 流式档位补线，用户报「还是 6 个表情图」+「三人线思考太单薄」）：①v4.3.0 去重判据 default_who is None 站错岗——三人线流式 expr_who=""（v3.7.2 老语义：空串=开过滤器且无主语兜底），"" is None 恒假→去重在三人线从未生效，模型双写结尾标签照插=3真+3重（20:15 小票+OWI 库 6 图实证；前一笔 3 图纯因模型当日没双写）。修=expr_substitute/_ExprFilter.feed/flush 三处判空改 not default_who（None 与 "" 同属多人场；单人场带名字串不去重、保留情绪演变，语义不变）。②v4.1.6 ds 档位接线漏了 zhipu_stream_relay 非 GLM 分支——reasoning_effort 只进了 _up_once 与两处内联体，三人线流式走 relay 永远裸奔上游默认档=思考单薄真凶（魔搭探针实证：同题 effort=max 思维链 1382 字 vs 裸 306 字；小票 reasoning=0=魔搭 usage 不报数的假账，非真没思考）。修=非 GLM 分支 url==MS_URL 且 reasoning 非空时带 reasoning_effort；local/foreign/CLI 上游不碰（参数兼容未验）。
v4.3.0（1020·多人场表情同人去重，用户报「每个人的图片都变成了两份」）：v4.2.1 教会模型分段段末各带标签后，模型常在段末之外再把三人标签重写一遍在回复末尾（双写），两处都被 expr 管线原位换图=同一角色图出两份。修=多人场（default_who=None）同人首图定档——expr_substitute/_ExprFilter.feed/_ExprFilter.flush 三处同一 seen 集，后续同角色标签只剥不插；单人场（default_who 有值）不去重，保留情绪演变。段中插图行为零改动（用户令「我挺喜欢对话中间的」）；兜底 expr_fallback_tail 零改动（有标签本来就不补）。
v4.2.9b（1019 深夜·首字三刀加固，观测驱动两补）：①_vec_for single-flight——注入族四路并行同刻全 miss 时只发一次真席请求（Event 等待，其余拿缓存），防 3 路重复嵌同句挤占 4 核 CPU 席；②宫召回传向量——palace_recall_block 加 vec 形参，桥把 _vec_for(bare) 的向量随 /recall 的 query_vector 传宫，宫侧重打分免再嵌查询句（观测实锤：搜宫内部混合检索已嵌一遍查询句，重打分再嵌=每轮白付 1.8s）。
v4.2.9（1019 深夜·首字延迟三刀施工，施工单=PLAN-20261019-酒馆首字延迟三刀施工单）：用户报首字 13.4~22s（小票实测），分锅=魔搭 TTFB 0.5~0.8s 无罪、记忆宫 /recall 13.5s 主犯、桥向量席 2.3s/次×每轮 3~4 次重复从犯（全在喊魔搭之前串行跑完）。三刀：①_VEC_CACHE 同轮同文向量缓存（key=原文 cap 32 仅进程内存；三处召回块签名零改动，首轮算完其余字典命中；FNV 伪向量不缓存=失败不钉死）；②_recall_family 注入族并行器（四路 IO 等待型线程池并发、按传入序原样合并保 _add_inj 顺序、各块自带 fail-open；工人线程挂主线程 _RX 小票账本共享防召回命中随 thread-local 蒸发）；③[precall] 一行计时日志（路数/耗时/各块字数）供验收对数。三条装配线（duet/trio/solo）各换一行；solo 守卫语义保留（单人模式记忆库/场景库连查询一起跳）。
v4.2.8（1019 深夜·裸触发「生图」收编，用户令「能不能不打那个符号」）：用户嫌 [自拍][角色] 要切英文输入法打括号。新触发=消息以「生图」开头（^\\s*生图）即自拍模式，角色名=紧随其后的固定花名册前缀（艾米莉亚|蕾姆|雷姆|拉姆+英文别名 rem/ram/emt/emilia，re.I），无分隔符也认=前缀匹配不靠标点；没紧跟→全文找第一个花名册词兜底；生图开头但全不中→不触发当普通回话（用户令「搞错了是我的问题」）。旧括号令牌保留双轨。两检出点（三人/统一管线）收口换 _gen_token_hit() 单口；技能块触发语同步改。
v4.2.7（1019 深夜·零行为变更，化石标注防再坑）：BRAINS[酒馆三人] 静态行加 ⚠️注——运行时 trio 脑=scene_brain("tavern") 每请求现读 brain_binding.json（v4.0.0 起如此，当晚小票 6/6 provider=remram-trio-deepseek 实证为 deepseek）；AI 曾误读静态行向用户错报「三人走 GLM 烧摘要专户」，本版仅加标注。
v4.2.6（1019 晚·「你自己验是好使的，我验就是不好使」定谳+宽容解析救场，6b=who 终审补丁）：用户 UI 实测连挂 vs 我方 API 非流式全通。Playwright 进 OWI 亲测复现 2/2 必挂 + 2×2 分决实验（同消息同三人脑 stream=False 有行 / stream=True 无行）+ 非流式全文落盘抓到真身=模型把生成行写成 <gen>场景…</gen>，「角色名|」整段漏掉（口头玩笑类消息下高发）。旧代码只认严格式的死法：非流式=畸形行原样透传不排队；流式=_GenFilter 从 <gen 起整段扣留、正则永不中、流末静默丢弃（用户只见回话无图无提示）。修七刀：①_gen_parse 双式解析（严格式优先，无名字段 who=None 交 _gen_who 终审）；②_GenFilter 换 _gen_parse；③relay 流末 gen_filter.flush() 放行扣留区（可解析=捕获剥除，不可解析=可见化，杜绝静默吞文）；④三人/单人非流式收口换 _gen_parse；⑤流式写回剥行补 ANY_RE；⑥技能块加格式硬性军规一行；⑦6b=_gen_who(nm, token_name) who 终审——首验实锤回退分支裸用 gen_hit_name 把中文「拉姆」塞进队列、轮询器 ROUTE_MAP 只认 ram/rem/emt=静默跳过 150s 超时。验=非流式+流式+UI 活体三路全绿（队列 who=ram/上墙 1.4MB/流内带图 markdown/UI 出图 212942-2975）。
v4.2.5（1019·场景描述改中文制，用户令「第二套」Qwen 全量接管自拍线）：selfie_server v2.0 三酒馆路由 illu→Qwen-2.1 参考锚定（风火雷电特效 Illu 判死终审），技能块 <gen> 内容从英文 danbooru 标签改为中文自然语言场景描述（40~150 字，Qwen3VL 直吃中文）+动态效果可见化中文菜谱（风=半透明风刃/斩击轨迹线/发丝裙摆翻飞；火=火舌火星；雷=电弧闪电；冰雪=冰晶寒气，依据=1019 二会诊官方手办透明特效件先例）+禁外貌词/禁英文标签。GEN_LINE_RE(.+?) 语言无关零改动，scene 500 上限够用。考据与定版提示词=OPS-20261019-风魔法特效引擎战役§七。
v4.2.4（1019·风标签军规修正，DeepSeek 会诊+danbooru 论坛实据）：v4.2.3 军规里 cloth fluttering 未验真、clothes lift 在 danbooru 语义=掀衣走光语境（论坛原话「specifically for a nsfw context」）会给自拍图带跑偏偏置，换 verified 的 wind_lift（正式蕴含 wind_lift->wind，专指风吹衣物）+floating hair（hair_blowing 别名）。会诊同时定谳：纯提示词路线画不出风=路径级死亡（Illustrious 底模对风先验缺失，Aerokinesis LoRA 作者原话佐证），破局=特效 LoRA（Aerokinesis/Wind Lift 候选，下载撞登录墙待用户）或混合管线（Illu 底图+特效区局部重绘）。
v4.2.3（1019·蕾姆写法收编+效果标签军规，用户 15 时实测漏两件）：①用户按屏显字打令牌——三人稿段标签是「蕾姆：」，用户单人线发 [自拍][蕾姆] 而 GEN_TOKEN_RE 只认「雷姆」→不触发=普通回话（病根不是令牌词也不是模型）。修=GEN_TOKEN_RE/GEN_LINE_RE 加蕾姆位、GEN_NAME_WHO 蕾姆→rem、技能块角色名行注明两写法等同。②风魔法轮模型标签其实齐全（gen_queue 145500-0178 实据：wind magic/gust of wind/hair blowing/skirt fluttering），Illu 不认自造合成词画不出风→技能块加效果标签军规：动态效果必须用 danbooru 现成效果词（wind/floating hair/cloth fluttering/clothes lift）。引擎之争（illu vs qwen2.1）另出 A/B 实测交用户目审。
v4.2.2（1019·三人线接自拍令牌，用户 14:41 实测漏）：v4.2.0 只接了统一管线（酒馆+单人线），用户群聊日常走的是酒馆三人脑——[自拍][拉姆] 在三人线被当普通聊天。修=①技能块拆 _gen_skill_block(step1) 两版：单人/群聊版原文不动，三人场版第一步改「三人各自按人设回应，每人一段各带表情标签，生成指令只画被点名者」；②_trio 注入 GEN_SKILL_BLOCK_TRIO（条件注入零 token 增量同款）；③流式 _GenFilter+流尾入队闭包+写回剥行；非流式发前解析剥行入队等图。机制与统一管线逐件同构。
v4.2.1（1019·三人线表情补课，用户报「早安只有拉姆有表情图」）：旧账非自拍刀引入——①EXPR_RULE/EXPR_REASSERT 只教了拉姆/蕾姆标签格式，艾米莉亚从未被教（v3.7.7 给 emt 上柜 28 图+解析映射时指令没跟上）；②REASSERT 写死「标签放整条回复最后」→三人线模型只在末尾放一个标签，前两段裸奔；改=两人指令补齐艾米莉亚+改「多人场各段段末各带各的标签，单人场放回复最后」；③expr_fallback_tail 无标签兜底补 emt 分支（同源缺口）。trio_prompt.txt 零表情指令无双头冲突；emt 28 图在柜实测。④三人流式分支二次 expr_finish 收口删除（memory 存档 6 图 vs 屏显 3 图实锤，多叠兜底 neutral 进前情提要）。
v4.2.0（1019·自拍接酒馆施工单）：自拍改显式令牌制——①触发=用户消息 [自拍][角色名]（GEN_RE 关键词自动触发退役=误触根除，常量留作历史）；②命中才条件注入 GEN_SKILL_BLOCK 技能块（决策6 平时零 token），模型按人设回话+末行输出 <gen>角色名|英文tags</gen>（模型管画面，桥/PC 管身份）；③新 _GenFilter 流式剥 <gen> 行（姿势照抄 _ExprFilter 扣留区；流末没等到完整标签=原样放行降级可见），非流式发前正则剥行；④scene 字段 80→500（决策7 模型标签串超 80）；⑤GEN_WHO_REF 参考图门槛退役（rem 可自拍，身份改 PC 侧 Illu LoRA 三路由 ram2/rem1/emt3 管）；⑥_gen_wait_markdown fail/timeout 改回人话提示句（决策8 原 None=静默无感）。入队延后到回复解析（<gen> 行才是场景真身）；决策5 无行=不入队不生成。配套 PC 侧 selfie_server v1.9 三路由+poller v2。施工单=D:/AI/aiDocs/_临时/PLAN-20261019-自拍接酒馆施工单.md，验收后同步 /root/core/bridge+云仓。
v4.1.9（1018）：接力停用+死代码清扫（用户令「接力不太想要了直接禁用，等token自由再说」+「双人/单人提示词改完立刻生效」排查）——①DISABLED_BRAINS={"酒馆双人接力"}：/v1/models 不再下发（下拉消失），do_POST 拦截改人话 400；复活=从集合摘名，两棒代码零删。②FAST_SYS/FAST_PROMPT_FILE 死代码删除（v3.4.13 启动载入后全库零消费者；主线真身=pure_prompt.txt 统一管线现读，production_prompt.txt 同为化石；1018 曾误判二人稿=production_prompt.txt，本刀防再误）。在役四份提示词（pure主线/solo三份/trio/duet）本就现读即改即生效，无需改码。运行件直改，验收后同步 /root/core/bridge。
v4.1.8（1018）：两刀小补（用户令「先把这两个改了」）——①断连降噪：新增 QuietServer 覆写 handle_error，ConnectionReset/BrokenPipe/ConnectionAborted/Timeout 降为一行摘要（日志 337 条全栈 traceback 刷屏案；全是手机切后台掐线写回复所致，无实害）；②DS 流式 token 计量：zhipu_stream_relay 非 GLM 分支补 stream_options.include_usage（魔搭 1018 实测末块带 usage 且解析器 v3.8.1 本就通吃；1010 切 DS 后小票 usage 恒全 0 案；条件限定 url∈(MS_URL,ZHIPU)，local/foreign 未验不发）。运行件直改，验收后同步 /root/core/bridge。
v4.1.7（1012）：第三绑定 172.19.0.1:18170（docker OWI 口，OWI 容器拉 /v1/models 专用）——1011 下午重启桥丢 BRIDGE_BIND 环境变量→该口无人听→OWI 拉不到模型清单→酒馆下拉框全空；三绑定=127.0.0.1(管理台)/10.14.14.1(EasyTier)/172.19.0.1(docker OWI)，第三绑定 try/except 网段重建只告警不崩桥；版本号从误标 v4.1.6 改正（v4.1.6=1009 ds 思考档位已占用）。
v4.1.5（1011）：摘要字数双保险（用户令：只调提示词，禁二次压缩=二次付费）——①长度令牌挪到提示词末尾（位置偏差：尾部权重最高）+句子数锚（8~12 句，模型数不了字但数得了句）+替换策略（已了结旧账留一句带过、承诺/未完话题必保）；②本地句界裁剪保险丝（>500 字零成本裁到 500 内，绝不二次调用，句界异常才硬截）。中期单旧摘要召回经讨论否决（与日志/记忆宫内容重叠+摘要帧间雷同检索质量差）。
v4.1.4（1008 深夜·PLAN-20261008 S1）：新 glmfree 档 + pet/service 默认切换。
  - CLI_MODELS 加 free47=glm-4.7-flash（智谱免费家族，走云CLI）；scene_brain 加 glmfree 分支
    （label=remram-glmfree）。_SCENE_DEFAULT pet/service→glmfree（用户裁决：桌宠是娱乐的，
    真有事上酒馆）；brain_binding.json 现值同步改 glmfree，"cli" 值域保留可切回。
  - glmfree 关思维链：4.7-flash 默认 thinking（实弹 59s 才回话），no_think 贯穿
    zhipu_stream_relay/_up_once 全部调用点，payload 加 thinking=disabled（实弹 reasoning_tokens=0 秒回）。
v4.1.0（1007 深夜·am9 结案施工=PLAN-20261007 六步③）：coding 端点退役 + cli 档上编。
  - GLM 全走云 CLI（CLIProxyAPI v8 @127.0.0.1:8317 标准端点）：ZHIPU/ZKEY 常量换指，
    七处调用点零改动；5.3-flash=按量付费 key（只住 CLI 配置），coding 订阅额度零依赖。
  - 新增 cli 档（provider="cli"）：本地 8317 国外脑（groq-120b，经 EasyTier 10.14.14.2，
    python 不直连 Groq 的 CF 1010 纪律），2s 探活先例同 local；死→降级书生 intern-latest
    （clideg 档，云CLI免费道）+WARNING+_FOREIGN_FALLBACK 黄标。
  - pet/service 默认 provider 改 cli（v4.1.0 用户矩阵）；tavern 维持 ds（魔搭专职）。
  - 1113 语义改「付费余额不足」，落 _PAID_1113 戳（管理台余额红绿灯数据源）。
  - 摘要 prompt 搭车寒暄负面指令（用户令原话入稿）。
v3.7.7（1005 午前，T10-part-1）：艾米莉亚表情专属槽——_EXPR_WHO 艾米莉亚 rem→emt，
  配合 OWI 容器新静态目录 /expr/emt/（T8 A线 28 情绪差分 docker cp 上云；容器层易失，
  重建容器需重推=本地 output/T8_20261005/A_emt 常备）。拉姆/蕾姆换装等用户目验后再动。
v4.0.0（1007 夜战·用户矩阵定稿施工=PATCH-FINAL 六针）：分场景脑手术——酒馆/桌宠/服务三脑硬隔离。
  - 针1 brain_binding.json 三场景结构 {"tavern":{provider,glm_effort},"pet":...,"service":...}；
    旧单选两键零感知迁移（tavern 继承旧值，pet/service 默认 glm-low）；ds 禁入 pet/service（落回 glm+WARNING）。
  - 针2 glm_effort max 档 max_tokens=16384（low=2048/high=8192 不变）；duet 已跟总闸（v3.5.9.1），
    trio 解绑 glm 硬编码改跟 tavern 场景（ds=_ds_once 单段烧 1）。
  - 针3 本地脑 provider="local"：upstream=LOCAL_UPSTREAM(10.14.14.2:18080 llama-swap) model=qwen36-256k-moe35；
    scene_brain 选 local 前先探活（2s 超时），死→回退 GLM+WARNING+_FALLBACK_TS（管理台状态牌黄）；
    usage.model 透传 llama-swap 真席名。
  - 针4 桌宠剥离：BRAINS 新增「桌宠」(binding=pet)「服务」(binding=service) 两入口（/v1/models 自动出现）；
    OLV 对话链 conf.yaml model '酒馆'→'桌宠'（本地件，晨报同管线随桌宠脑）。
  - 针5 摘要钉死 GLM high（maybe_summarize effort low→high、max_tokens 768→4096，上游常量 ZHIPU 不动）。
  - v4.1.6（1009）ds 路径接思考档位：brain_binding.tavern.ds_effort(low/high/max,默认high=上游默认)→
    scene_brain effort→_up_once/两处内联请求体带 reasoning_effort（DeepSeek 官方：V4.1-Flash 思维默认开、effort 默认 high、三档 low/high/max）。
  - 针6 回退显式化：本地探活失败/请求异常回退 GLM 均落 WARNING 日志；四脑点名验收=裸测 usage.model 对照。
v3.7.9（1005 午后，T12 角色日记每日一图 v1）：GET /diary/today 读当日日记；POST /diary/trigger 幂等提炼
  （当日 chat_memory→GLM 第一人称小日记→_gen_enqueue 生图入队，PC 轮询器/ComfyUI 在线才出图 fail-open）。
  云端 crontab 21:00 触发（#@ 每日日记图）。rem 无参考图不参与轮换（ram/emt 按星期奇偶）。
v3.7.6（1004 深夜夜战，用户令「桥上只有系统提示词」裸测模式 + PLAN M4 中版考官）：
  - 裸测模式：用户消息带 [裸测] 前缀 → _bare_run 短路——pmsg 只有系统提示词（OWI 模型层底稿/
    SOLO 标记底稿/纯净底稿文件三源照旧）+ 用户消息（前缀剥掉），现实锚/关怀/前情提要/往日日志/
    记忆库/场景库/记忆宫/台词参考/时光羁绊/表情规则/历史消息/SOLO重申 全部不注入，
    写回（chat_memory/摘要/日志）与好感度 tick 全跳过 = 测试零记忆污染；审计小票照记（mode 带 ·bare）。
  - 考你一题（回忆杀学习池分抽）：考题池 /root/work/cloud-config/learning_points.jsonl
    （M4 学习线写入，{"date","text"} 行，text 带 [学习· 前缀）；15% 回忆杀触发时若有学习卡
    → 50% 概率改抽考题卡注入【考你一题】块（考他知识点、先不给答案），否则照旧旧事回忆；
    每日≤1 次闸共用 last_nostalgia；文件缺/空=None fail-open。小票 bond 增 exam 字段。
v3.7.5（1004 时光与羁绊三件套，用户放权令「别碰GPU」；纯CPU零嵌入零GPU调用）：
  - 好感度账本：纯规则 tick（重复纠缠同一话题=-1 / 带来新内容或长文=+1，每日±3 封顶，
    0-100 夹取），初始 75=恋人档（用户令一步到位），状态持久化 bond_state.json；
  - 相识第 N 天：chat_memory 最早点 ts 首算后缓存在账本，注入【时光与羁绊】块
    （恋人关系+羁绊热度+趋势+行为反馈规则），随 _add_inj 进小票；
  - 回忆杀：每日至多一次、15% 概率从 chat_journal 随机抽一天旧账（排除今昨两天）
    注入【回忆杀】块——她主动想起过去的某一天；概率闸在前，滚动查询只在触发时发生；
  - GET /affection 查账口（分数/档位/相识天数/近期流水，供管理台日后画曲线）；
  - 小票增顶层 bond 字段（score/delta/nostalgia）；任务调用（X-OpenWebUI-Task）不记tick不注入。
v3.7.4（1004 ①桶施工，用户令「把①②的干了吧」；方案定稿=HANDOFF-20261003b §四.A1）：
  - first_token_ms 埋点：zhipu_stream_relay/_duet_relay_one 收到首个 content chunk 时记
    t_first 进线程隔离收集器 _rx()，三处小票 timings.first_token_ms 落真值；
    非流式/限额话留 null（429 限额话不算首字）；思维链 chunk 不算（content 才算）。
  - /v1/models 自 v3.7.0 起已列全三脑（本版零改动，旧工单 todo-7ix 后半件=OWI 侧刷新缓存）。
v3.7.3（1003 复审后续三件之二三，用户令「都去做吧」）：
  - duet 补执行小票：注入区 _add_inj 逐块收集+尾部 _receipt_write（此前主路径/_trio 有票、
    _duet 从未有——同类管线不一致，OPS-20261003 §八观察项①）。
  - duet 第一棒末位重申 DUET_RAM_REASSERT（v3.5.5 家法：场控只挂顶部会被 40 条双人 few-shot
    淹，GLM 中段/末位 system 实测服管；实弹验收抓到第一棒越界代言蕾姆双段）。
v3.7.2（1003 压缩后净眼复审修复，正本=aiDocs/llama/md/OPS-20261003-压缩后净眼复审-桥台宫桥三件.md）：
  - P0-1 接力入口复活：v3.7.0 改名只改了 BRAINS 键，DUET_BRAIN 常量漏改→拦截恒 False，
    「酒馆双人接力」一直静默落总入口（healthz duet=旧名实证）；常量对齐+改名时 rg 旧名零残留入家法。
  - P0-2 duet 第二棒占位显式索引：v3.5.8.1 尾部追加 EXPR_REASSERT 后负索引 p2[-2] 错位——
    覆盖的是 DUET_REM_TURN 场控、空 assistant 残留、拉姆原话被标成蕾姆说的；改 append 后记绝对索引。
  - P1 三人流式三连：①流式分支 SSE 已发完不再 _send（原双响应畸形）②收集器清零挪到召回前
    （原在召回后，三人小票 recalls 恒空）+injections 逐块对齐主路径③流式 expr_who 传空串开
    表情过滤器（原 None=标签原样上屏）。
  - 复审漏项补齐：_trio 只挂 EXPR_REASSERT 没挂 EXPR_RULE（模型没有 28 情绪枚举可参照）。
  - 乙批：限额话不进姐妹记忆——写回前剥系统提示语（_clean_for_memory），剥完为空不写 assistant 点。
v3.7.0（1002 晚，用户七入口定版）：emt 单人线+酒馆三人模式+同台改名「酒馆双人接力」。
  - emt 单人线：OWI emt 模型 system=[SOLO_EMT]→桥读 prompt/solo_emt.txt（底稿 v1 用户扫过目）；
    台词接线 emilia_dialogues（who 按文本前缀启发式补标，标注失败条目不进检索）；
    表情暂用蕾姆图占位（用户令，专属差分生成后再换）。
  - 酒馆三人（新入口）：三姐妹一次生成三段（用户令：单次调用，接受互动质量换快与省）；
    底稿=prompt/trio_prompt.txt 独立稿（用户令「隔离，适合微调，二期再拼装」）。
  - 酒馆双人同台→酒馆双人接力（用户改名；旧名零兜底=落总入口，用户令不增加复杂度）。
v3.5.9.0（1002 深夜五批施工）：脑绑定总闸+台词库接线+SOLO 短标记+补账口摘除。
  - 脑绑定总闸（用户两控件定稿）：BRAINS 只留「酒馆」总入口+「酒馆双人同台」；旧三名
    （酒馆glm-5.3-flash-low/high、酒馆deepseek-v4.1 及 v3.5.0 老三名）全部 _ALIASES 并入「酒馆」。
    「酒馆」的脑=每请求现读 /root/work/cloud-config/brain_binding.json（provider=glm/ds，
    glm_effort=low/high/max；坏配置回退 glm-low+告警限频 5 分钟），管理台 v1.4.3「脑绑定」页改。
    双人同台两棒同跟总闸：glm=照旧真流式（档位跟配置）；ds=两次 _ds_once 整段伪流接力。
  - 台词库接线（批2）：solo 时按角色查 ram_dialogues/rem_dialogues 语义 top3（≥0.55，who 过滤
    本角色线），【原著台词参考】叙事式注入当腔调佐料；失败/不命中静默，绝不卡对话。ram 库 1,147 点
    已本地重嵌归一 Qwen3-Emb（原 bge-m3 两派相似度不可比，NIGHT-20261002-ram-reembed.py）。
  - SOLO 短标记（批4）：OWI 模型层 system 只留 [SOLO_RAM]/[SOLO_REM]，桥读到标记→读
    /root/work/cloud-config/prompt/solo_ram.txt|solo_rem.txt 当底稿（底稿迁管理台「人设底稿」页）；
    传全文=旧路径照旧（兼容不破坏）。
  - /v1/journal/generate 手动补账口摘除（批1b）：管理台 v1.4.2 起自带浓缩，桥删口删方法；
    _journal_glm/_journal_write_day/_condense_day 浓缩机器保留（maybe_journal 自动补账还用）。
v3.5.8.1（0927 午）：表情上线首日修复——模型不打标签，三刀加固。
  - 病灶（用户实弹"早安/带伞"两条零图）：EXPR_RULE 埋在 4,678 字底稿中间，历史 40 条零标签
    few-shot 把它淹了（v3.5.5 雷姆串场同病）；且双人线默认无兜底=模型一忘就裸奔。
  - 修：①EXPR_REASSERT 末位重申（紧贴 user 的中段 system，GLM 实测服管）挂统一管线+duet 两路；
    ②expr_fallback_tail 双线兜底：无标签时单人补自己 neutral、双人按文中出场姐妹各补 neutral；
    ③流式/非流式/duet 三处兜底统一走该函数。
v3.5.8（0927 夜）：表情差分上 OWI——对话结束姐妹能"发表情"。
  - 图源=OWI 容器静态目录 /app/build/expr/<ram|rem>/<情绪>.png（56 张已 docker cp；同源相对路径
    /expr/... 公网 :3000 与隧道 :13001 通吃，零安全组改动。容器重建丢图：宿主机正本
    /root/work/expr_assets/，恢复=expr_into_owi.sh 重新 docker cp）。
  - 管线：system 末尾追加表情规则（28 情绪英文枚举+中文对照）→ 模型台词后自带
    [[拉姆表情:xxx]]/[[蕾姆表情:xxx]] → 桥剥标签原位换成 markdown 图；单人/双人/双人同台三线全挂。
  - 流式=_ExprFilter 扣留缓冲状态机（疑似标签前缀先扣留，完整标签→图；换行/闭括号=普通文本放行）；
    非流式=正则替换。无标签→补 neutral 兜底（单人线按底稿关键词 detect_solo_who 判说话人；
    双人线无主语标签只剥不插、不打兜底）。限额兜底话不打表情。
  - 任务调用（X-OpenWebUI-Task）表情规则与过滤器全程关闭，标题/标签零污染。
v3.5.7（0927 晨）：双人同台（姐妹轮转）——拉姆真说完，雷姆对着她刚说的话真接。
  - 新下拉项「酒馆双人同台」（label=remram-duet）：一次用户消息 → 两次普通聊天调用串行。
    与导演链的本质区别：没有思考中间层（导演=要点JSON→包装台词，时间花在非对话的思考上），
    这里第一次调用的产物就是拉姆的原话本身（一半是回复一半是雷姆的输入），时间全花在说话上。
  - 底稿=服务器文件 /root/work/cloud-config/prompt/duet_ram.txt + duet_rem.txt（现读即改即生效，
    拉姆版=单人稿 v1 镜改，蕾姆版=双人稿雷姆段改写；分析类话题分工=拉姆开刀/蕾姆收场）。
  - 每次调用各自的场控指令（只准自己台词动作、禁代对方开口）；雷姆的上下文里塞进拉姆刚说的
    原话（user 后紧跟 assistant+轮到你 system，GLM 中段 system 实测有效）；共享注入算一次两姐妹用。
  - 输出拼接=「拉姆：…\n\n蕾姆：…」；流式=两段真流式接力（各自 reasoning+content 增量照发）；
    写回=一次 user+combined assistant 对（与双人线同构，下游摘要/日志/召回零改动）；审计 mode=酒馆双人同台。
  - 429：拉姆段挂=整轮直说限额；雷姆段挂=拉姆段照出+限额话收尾。
v3.5.6（0927 晨）：可检索日志（Kindroid journal 同款+升级）+ 时间戳锚（PLAN-20260927）。
  - 新集合 chat_journal：一条=一天 {date:"2026-09-26", weekday:"周六", text:"X月X日 周X：正文≤300字",
    ts=当日23:59}；向量=日志正文嵌入；point id=YYYYMMDD（幂等：重跑/手动补账覆盖写）。
  - 触发 maybe_journal()（事件驱动，不做定时器）：每轮写回后查"今天之前还有没有没记日志的日子"
    →后台线程逐日 GLM-low 浓缩（≥2 条消息才算一天，一次最多补 7 天；首次上线自动补齐 0925 起的账）。
  - 注入 journal_block()：语义召回 top2 ≥0.55 →【往日日志】块（Kindroid 是关键词触发，咱用嵌入席
    语义召回=升级版）；双人/单人两线都挂（日期=中性记忆非人设）；注入位=前情提要之后、记忆宫召回之前。
  - 时间锚三点定轴：前情提要头带（截至 X 月 X 日，latest_summary_full 拆出 ts）+ 日志块日期头 +
    现实锚今天日期 →"上周三聊的方案"由模型自己算（Mem0/Letta 通行做法，arXiv 2601.07468）。
  - 手动补账口：POST /v1/journal/generate {date}（管理台 v1.3「日志」签代理；幂等覆盖写）。
v3.5.5（0926 深夜）：关怀钩子（方案甲）+ 单人模式强化。
  - 病灶1（用户报：拉姆单人线蕾姆也出声）：根因=全局历史 40 条双人 few-shot（日志实锤单人底稿
    3654 字在场仍出两段），与格式锁无关（锁在 production_prompt.txt，单人线根本没加载它）。
    修法=solo 时 system 顶加 SOLO_DIRECTIVE（"场内只有你"，通用措辞，将来雷姆/艾米莉亚单人线同用）；
    首版实战修正：旁白动作描写也算出场一并禁 + fetch_history 之后、user 之前加 SOLO_REASSERT 末位重申
    （GLM 对话中间插 system 消息 0926 curl 实测有效）；配套把拉姆底稿里"可以自然提到蕾姆"的邀请句删除。
  - 功能：关怀钩子 checkin_directive()——距上条用户消息 ≥1h（用户拍板 3600s）→ 回复开头先问
    未了结事进展，天气/节日顺口提；数据=chat_memory 最新 user 点 ts（写回在 _send 之后，
    本函数运行时最新 user 点=上一条消息，gap 口径天然正确）；只读 scroll，无历史/失败=静默跳过。
  - 乙方案（定时推送/OWI Automations）判死勿再提：Automations execute_automation 每次新建聊天
    （L407 chat_id=str(uuid4())），不能续旧线 + 任务提示词进历史=污染记忆。
v3.5.4（0926 晚）：现实锚天气升级（用户令"姐妹只知道时间不知道天气"）。
  - 实弹勘误：open-meteo 服务器直连一直是通的，天气位其实在线但只有"现在几度"，
    没有今明预报 → 姐妹说不出"带伞/明天降温"。
  - WEATHER_URL 加 daily 预报（今明两天 weather_code+max/min，一次调用同取，配额不变）；
    锚天气位升级="北京 现在25°C 今雷雨 21~27°C 明雷雨 21~26°C"（纯数据不带指令，话让姐妹自己说）。
  - 节日位加"明天是X节"。缓存 1h/负缓存 5min 照旧（1 万次/天限额富余）。
v3.5.3（0926）：单人线（B 方案=OWI 自定义模型当角色卡）。
  - 用户在 OWI Workspace 建 ram/rem 自定义模型（base=酒馆glm-5.3-flash-low），系统提示词=单人底稿
    （拉姆 v1 由 AI 从 4,678 双人底稿改写，用户可在 OWI 模型编辑页随时改，改完下一条消息即生效）。
  - 桥判定：非任务调用且请求带非空 system（OWI 会把自定义模型的系统提示词随第一条 system 送达）
    → 单人模式：底稿换成传入 system，摘掉双人库(dual_dialogues)与场景库(remram_lines)注入，
    其余管线原样（现实锚/前情提要/记忆宫召回/40条历史/写回/入宫）。
  - 无 system = 双人线原样（pure_prompt.txt）；审计 mode 加 ·solo 后缀。
v3.5.2（0926）：图片透传——GLM-5.3-Flash 原生多模态（智谱官方文档实锤+coding 端点实测 200 认色）。
  - user content 为数组时抽取 text+image_url 项原样透传给智谱脑（DS 脑魔搭不收图维持拍平）；
    拍平文本照旧供日志/召回/写回/审计，纯图无字记 "[用户发了一张图片]"。
  - 配套=OWI 侧需给酒馆脑标 vision 能力（否则 OWI 把图降级成 <attached_files> 文字占位，桥收不到图）。
v3.5.1（0926）：用户令两刀（杂活分离战役）。
  ① 三脑 id 加「酒馆」前缀：酒馆glm-5.3-flash-low / 酒馆glm-5.3-flash-high / 酒馆deepseek-v4.1
    （用户定名式：前缀+底层模型名+思考等级，一眼看懂用的哪个脑；中文仅作 id 透传，OWI/协议层当普通字符串）。
    旧三名进 _ALIASES 继续认（旧对话/缓存下拉发旧 id 不落兜底）。
  ② X-OpenWebUI-Task 保险丝：OWI 后台任务（标题/标签/追问）请求带此官方头 → 跳过
    chat_memory 写回/摘要计数/入宫，审计照记（mode 带 ·task 后缀）。防任务模型误设回酒馆脑再污染历史库。
    （正解=OWI 任务模型指到智谱原生连接，任务根本不过桥；保险丝是双层防线。）
v3.4.13（0926）：用户令两钉。①格式锁挪进 production_prompt.txt（改格式=改文件，不再动代码）；②召回阈值统一 0.55（台词参考 0.5/回忆 0.58 → 0.55，用户拍板容忍轻微污染）。v3.4.12（0926）：讨论定版三刀。
  ① 历史对齐：快速档 chat_memory 视野 12条(6轮)→40条(20轮)，与纯净档 40条 一致
  ② dialog_archive.jsonl 服务端存档拆除——OWI 本就服务端落库，桥不再记第二本（冗余）
  ③ 429 退避/重试全拆——配额制 API 限流=真没量，重试无意义；单用户无并发踩踏；
    一发定胜负：1113→QUOTA_DEAD_MSG，其余 429→RATE_LIMIT_MSG / MS_LIMIT_MSG
v3.4.11（0926）：用户令三刀。
  ① 小话轻路由拆除（深度档不再自动判"晚安类小话"改走快速档——模式用户手动选）
  ② 深想 180s 同句去重拆除（同句重发照常进链）
  ③ 兜底话退役：429/额度干涸不再装拉姆嗓子说"脑子转不动"，改直说限额
    （QUOTA_DEAD_MSG=智谱 1113 烧干 / RATE_LIMIT_MSG=智谱限流 / MS_LIMIT_MSG=魔搭限流）
v3.4.10（0926）：纯净速——纯净管线换 DeepSeek-V4.1-Flash 大脑（魔搭免费道）。
  - 用户新病：纯净档 GLM high 思考憋 20-60s 首字，太慢。
  - 新下拉项「纯净速」= 与纯净完全同管线（4678 原件+现实锚+前情+回忆+40条历史），
    唯一变量=大脑换成魔搭 deepseek-ai/DeepSeek-V4.1-Flash（实测 TTFT 1.2s，思考走
    reasoning_content 流式=兼容 v3.4.9 转发；enable_thinking 参数可关，本版默认开）。
  - 魔搭纪律：429 不退避不重试（防封号），秒回兜底；魔粒计费约 1/次。
  - 纯净(GLM) 原样保留，下拉双项可 A/B 对照。
v3.4.9（0925 深夜）：OWI 接桥第二针——思维链照发。
  - 纯浄档(high reasoning)思考期 30-40s 桥侧静默 → OWI 空存回复（快速档 2s 正常落库，
    模式相关性实锤）。修法=reasoning_content 增量照发给 OWI（其原生渲染思考框），
    静默期消失，第 1 秒即有数据流。
v3.4.8（0925 晚）：OWI 接桥专针。
  - /v1/models 换新 ID：纯净/快速（旧 remram-导演链/remram-快聊 是三模改名前的古董）。
  - 聊天按 model 名路由：model=纯净→pure、快速→fast、深度→deep；
    不认识的名字（含 ST 现状）回退模式旗，ST 行为零变化。
v3.4.7（0925 中秋）：批次四·流式修复第三刀（终）。
  - 链式 httpx.stream(...).__enter__() 的 CM 无引用→GC 即回收→内部 with 退出→
    流被关（'Attempted to read or stream content, but the stream has been closed'）。
  - 修法：CM 存变量保引用（cm = httpx.stream(...); r = cm.__enter__()）。
v3.4.6（0925 中秋）：批次四·流式修复第二刀。
  - httpx Response 不支持 with 协议（'Response' object does not support the context
    manager protocol）——with r: 改 try/finally + r.close()
v3.4.5（0925 中秋）：批次四·流式修复。
  - 治潜伏雷：流式中继 httpx.stream() 的 CM 没 __enter__ 接收，r.status_code 必炸
    （'_GeneratorContextManager' object has no attribute 'status_code'，v3.4.0 起带病，
    ST 一直非流式所以从没炸到人——批4 冒烟实测抓出）
  - 修法：httpx.stream(...).__enter__() 直接拿 Response；429 体读/关响应用 r.read()/r.close()
v3.4.4（0925 中秋）：批次五·小件 + 摘要限长。
  - __模式查询__ 标记：秒回"当前模式：X"（配 QR [模式] 钮），不进链不进记忆
  - 429 快速失败：响应体含 1113/无可用资源包（窗口额度干涸）→ 不退避秒回兜底，纯/快/流式三路都加
  - 摘要 prompt 加"严格不超过 300 字"+ max_tokens 768（治 08:25 观察到的 866/1085 字超标）
  - 深度按钮下架（Default.json 移除；__深想__ 标记与导演链保留）
v3.4.3（0925 中秋）：批次三·知识库隐形召回（pure 专属）。
  - 每轮 embed(user)（自家席，复用写侧 _vec_for）→ dual_dialogues top3 ≥0.58
  - 命中才在 system 顶部追加【若有似无的回忆】块（化进语气/禁照抄/禁提资料三禁令）
  - 检索失败/不命中/伪向量低分 = 静默空串，干净不带；remram_lines 场景库不接（阈值松了塞垃圾）
v3.4.2（0925 中秋）：批次二·记忆闭环（写侧优先）。
  - 写侧 A：pure/fast 每轮把 {role,text,ts,sessionId} 写 Qdrant chat_memory
    （id/ts=毫秒时间戳照旧档；向量=自家席嵌入，失败退化 FNV 伪向量，绝不断对话）
  - 写侧 B（丢稿保险）：每轮整档 append /root/work/exports/dialog_archive.jsonl
  - 读侧：pure 的 system 顶部（现实锚之后）插【前情提要】= chat_summary 里 ts 最新一条
  - 摘要：每 20 轮后台线程用 GLM low 出一段 150-300 字叙事前情写 chat_summary
    （vector [0,0] 维度不动）；旧档无 ts 不参与读侧
v3.4.1（0925 中秋）：批次一·现实锚。
  - pure/fast 的 system 顶部插一行【现实世界】YYYY-MM-DD HH:MM 周X · 节日 · 天气
    （注入位置家法：顶部>底部>中间被忽略；deep 弃用晾着不接）
  - 节日=2026 静态全年表（农历节日两源核验）；天气=open-meteo 免费 API（默认北京
    39.90,116.40，缓存 1h，负缓存 5min，拉不到该项略过、绝不为它卡对话）
v3.3（0925）：v3.2 + 压测判读九项修复。
  ① 非流式快聊 429 兜底出口守卫（修 KeyError 'choices' 脏崩/双状态行）
  ② 429 退避 10/25/50s + Retry-After 头优先 + ±20% jitter（总退避≈85s 压在 ST ~111s 断连线内）
  ③ 小话判据放宽：≤15 字 OR（≤40 字且命中收尾词表），词表扩充
  ⑤ 深想 180s 同句去重回放（防重发白烧导演链）
  ⑥ 桥日志全行时间戳 + 深想通路计时
  ⑦⑨ 审计记账补 verdict/missing/说话人覆盖（桥侧从最终节点输出提取，n8n 零改动）
  ⑧ 非流式口令入库改为发送前并入正文（修 SSE 残包）
v3.2：双模桥 + 深想小话轻路由 + 429 重试兜底（0924 夜）。
  POST /v1/chat/completions
    - 消息为 __深想__ / __快聊__ → 切模式，回执一句话，不进链不进记忆
    - 默认模式 = 快聊：桥内单次调用（蒸馏稿 + KB 台词检索 + 最近对话），支持真流式
    - 深想模式 = n8n 导演双层链（轮询，整体返回）
    - 深想模式收到晚安/刷牙类小话 → 轻路由走快聊直渲染（业界 pre-routing 做法），
      审计日志记 mode=deep-small，模式旗不变，下一句照旧走导演链
  GET  /v1/models
认证：n8n 内部 REST 用登录 cookie。
回滚：server-backups 里的 v3 桥脚本拷回 + 重启。
"""
import json, io, os, sys, time, threading, re, random, difflib, base64, subprocess
from datetime import datetime, timedelta, timezone
import httpx
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PORT = 18170

# v4.1.0 am9 结案（20261007 用户令）：coding 端点退役，桥对 coding 订阅额度零依赖。
# ZHIPU/ZKEY 变量名保留（全桥七处调用点零改动），实际指向云 CLI（CLIProxyAPI v8
# @127.0.0.1:8317，systemd cliproxy.service）：glm-5.3-flash=标准端点按量付费
# key（只住 CLI 配置内，桥不落任何智谱钥匙文件）。1113 语义变为「付费余额不足」。
try:
    ZKEY = open("/root/work/cliproxy/.api_key", encoding="utf-8").read().strip()
except Exception:
    ZKEY = ""
ZHIPU = "http://127.0.0.1:8317/v1/chat/completions"
CLI_MODELS = {"paid": "glm-5.3-flash", "intern": "intern-latest", "free": "glm-4-flash-250414",
              "ling": "Ling-3.0-flash", "free47": "glm-4.7-flash"}   # v4.1.4 free47=桌宠/服务娱乐档；1008 Ling 注记=降级备选（书生主降）
# v3.3.2: 嵌入改走自家 llama-server 席（Qwen3-Embedding-0.6B，云端 CPU）；
#         Qdrant 宿主机解析不了容器名 qdrant（getent 实锤），改走宿主回环——修复快聊历史/KB/入宫静默失败
ZEMB = "http://172.19.0.1:18300/v1/embeddings"
QDRANT = "http://127.0.0.1:6333"
PALACE_RECALL = "http://127.0.0.1:9236/recall"  # v3.5.0 记忆宫召回只读口（宫桥 v2 新增）

# ==== v3.5.1：BRAINS/_ALIASES/resolve_brain 定义在 MS 常量之后（BRAINS 值引用 MS_URL，顺序不可上移） ====


PURE_PROMPT_FILE = "/root/work/cloud-config/pure_prompt.txt"

# ==== v4.1.1 发件箱（PLAN-20261007 步骤④）：本地桌宠/课堂对话流水落这里，21:10 cron 阀门消化 ====
DIGEST_INBOX = "/root/work/digest_inbox"

# ==== v3.4.10 纯净速：魔搭 DeepSeek-V4.1-Flash（钥匙只住 /root/work/.modelscope_key，chmod 600）====
try:
    MSKEY = open("/root/work/.modelscope_key", encoding="utf-8").read().strip()
except Exception:
    MSKEY = ""
MS_URL = "https://api-inference.modelscope.cn/v1/chat/completions"
# 1019 实测定谳：老 id DeepSeek-V4.1-Flash 被 ModelScope 撤 provider（"has no provider supported"，
# 酒馆当日 0 调用真因；key/余额/限流全排除）；1017 快照实测 200——上游轮换跟品，一行换 id
MS_MODEL = "deepseek-ai/DeepSeek-V4.1-Flash-1017"

# ==== v4.0.0 针3 本地脑（llama-swap 保险丝；生产钥匙禁塞网关——本地席无需钥匙）====
LOCAL_UPSTREAM = "http://10.14.14.2:18080/v1/chat/completions"
LOCAL_HOST_PROBE = "http://10.14.14.2:18080/v1/models"
LOCAL_MODEL = "qwen36-256k-moe35"   # 现役 moe35 席（25 tok/s，1006 已入编 coexist）；换席改这里
_FALLBACK = {"ts": 0.0}   # 最近一次本地脑回退 GLM 的时刻（管理台状态牌黄标读）

# ==== v4.1.0 cli 档：本地 8317 国外脑（Groq/OpenRouter，经 EasyTier；python 永不直连
# Groq——CF 1010 拒 python 指纹，流量只走本地 Go 的 CLIProxyAPI，key=本地网关客户端钥匙）====
FOREIGN_UPSTREAM = "http://10.14.14.2:8317/v1/chat/completions"
FOREIGN_PROBE = "http://10.14.14.2:8317/v1/models"
try:
    FOREIGN_KEY = open("/root/work/cloud-config/.local_cli_key", encoding="utf-8").read().strip()
except Exception:
    FOREIGN_KEY = ""
FOREIGN_MODEL = "groq-120b"   # 实测总 1.6-2.2s（走本地 CLI 转发）；换档改这里（or-nemotron-fast 等）
_FOREIGN_FALLBACK = {"ts": 0.0}   # 最近一次本地国外脑降级书生的时刻（管理台状态牌黄标读）
_FOREIGN_429 = {"ts": 0.0}   # v4.1.3 Groq 限额（429）熔断戳：撞墙后 10 分钟内直接走书生档（探活只测活不测额度，TPD 烧干 /models 仍 200）


def foreign_alive(timeout=2.0):
    """本地国外脑探活（免费内网渠道，2s 探活先例同 local_alive；禁用于按次计费渠道）。"""
    try:
        r = httpx.get(FOREIGN_PROBE, timeout=timeout,
                      headers={"Authorization": f"Bearer {FOREIGN_KEY}"} if FOREIGN_KEY else None)
        if r.status_code == 200:
            return True
    except Exception:
        pass
    if time.time() - _FOREIGN_FALLBACK["ts"] > 300:
        _log(f"本地国外脑探活失败（{FOREIGN_PROBE}），本请求降级书生 intern-s2 397B（云CLI月1.8亿道）")
        _FOREIGN_FALLBACK["ts"] = time.time()
    return False


def local_alive(timeout=2.0):
    """本地脑探活：llama-swap /v1/models 2s 内应答=活。失败落 WARNING（限频 5 分钟）。"""
    try:
        r = httpx.get(LOCAL_HOST_PROBE, timeout=timeout)
        if r.status_code == 200:
            return True
    except Exception:
        pass
    if time.time() - _FALLBACK["ts"] > 300:
        _log(f"本地脑探活失败（{LOCAL_HOST_PROBE}），本请求回退 GLM")
        _FALLBACK["ts"] = time.time()
    return False

def _probe_snapshot():
    """v4.1.2 手动探活快照（GET/POST 两口共用；按钮触发，禁自动轮询）。"""
    f_ok = foreign_alive(2.0)
    l_ok = local_alive(2.0)
    return {"foreign": {"alive": f_ok, "url": FOREIGN_PROBE, "model": FOREIGN_MODEL},
            "local": {"alive": l_ok, "url": LOCAL_HOST_PROBE, "model": LOCAL_MODEL},
            "foreign_fallback_last": _FOREIGN_FALLBACK["ts"],
            "local_fallback_last": _FALLBACK["ts"],
            "probed_at": time.time()}


# ==== v3.5.9 模式入口表 + 脑绑定总闸（用户两控件定稿；必须在 MS_URL/MSKEY 之后定义）====
BRAINS = {
    # 总入口：脑由 brain_binding.json 每请求现定（管理台「脑绑定」页两控件改，下一句生效）
    "酒馆":        dict(binding="tavern", label="remram-total"),
    # v3.5.7→v3.7.0 双人接力：非"脑"而是模式入口（桥内两棒串行轮转，脑跟 tavern 场景），底稿在服务器文件里
    "酒馆双人接力": dict(upstream=None, glm=True, effort="low", max_tokens=8192, label="remram-duet"),
    # v3.7.0 酒馆三人：三姐妹一次生成三段（单次调用），底稿=trio_prompt.txt 独立稿；v4.0.0 脑跟 tavern 场景
    "酒馆三人":     dict(upstream=None, glm=True, effort="low", max_tokens=4096, label="remram-trio"),   # ⚠️化石登记（v4.2.7 注）：运行时真身=_trio 里 B=scene_brain("tavern") 每请求现读 brain_binding.json（v4.0.0 起），本行 glm=True 不参与调度——1019 深夜 AI 误读本行向用户错报「三人走 GLM 烧摘要专户」，当晚小票 6/6 provider=remram-trio-deepseek 打脸，判定路由看小票勿看本表
    # v4.0.0 针4 桌宠剥离+服务场景：选项级硬隔离（pet/service 的 provider 校验禁 ds，见 load_scene）
    "桌宠":        dict(binding="pet", label="remram-pet"),
    "服务":        dict(binding="service", label="remram-service"),
}

# v4.1.9 用户令（1018）：接力入口停用——下拉不下发+请求回人话 400；复活=从本集合摘掉名字，两棒代码零删
DISABLED_BRAINS = {"酒馆双人接力"}

# 旧名兼容（v3.5.0 老三名 + v3.5.1 酒馆三名已撤，老对话/缓存下拉发旧 id 全并入总入口，不落兜底）
_ALIASES = {
    "glm-flash-low": "酒馆", "glm-flash-high": "酒馆", "deepseek-v4.1": "酒馆",
    "酒馆glm-5.3-flash-low": "酒馆", "酒馆glm-5.3-flash-high": "酒馆", "酒馆deepseek-v4.1": "酒馆",
}   # v3.7.0「酒馆双人同台」旧名零兜底（用户令）：resolve_brain 认不出→默认「酒馆」

DEFAULT_BRAIN = "酒馆"  # 用户令：未知模型名兜底

BRAIN_BINDING_FILE = "/root/work/cloud-config/brain_binding.json"
_BINDING_DEFAULT = {"provider": "glm", "glm_effort": "low"}
_SCENE_DEFAULT = {"tavern": {"provider": "ds", "glm_effort": "low"},
                  "pet": {"provider": "glmfree", "glm_effort": "low"},
                  "service": {"provider": "glmfree", "glm_effort": "low"}}   # v4.1.4 用户裁决：桌宠/服务=glmfree（4.7-flash 娱乐档）
_SCENE_PROVIDERS = {"tavern": ("glm", "ds", "local", "cli"), "pet": ("glm", "local", "cli", "glmfree"), "service": ("glm", "local", "cli", "glmfree")}
_EFFORTS = ("low", "high", "max")


def load_scene(scene):
    """v4.0.0 分场景脑现读（每请求一次）。新结构=三场景键；旧单选两键零感知迁移
    （tavern 继承旧值，pet/service 默认 glm-low）。ds 误配进 pet/service → 拒绝落回 glm + WARNING。"""
    try:
        cfg = json.loads(open(BRAIN_BINDING_FILE, encoding="utf-8").read())
    except Exception:
        cfg = {}
    if scene not in cfg or not isinstance(cfg.get(scene), dict):
        # 旧结构迁移：tavern 继承旧 provider/glm_effort
        old = {"provider": str(cfg.get("provider") or ""), "glm_effort": str(cfg.get("glm_effort") or "")}
        if old["provider"] in ("glm", "ds", "local", "cli", "glmfree"):
            cfg[scene] = dict(old) if scene == "tavern" else dict(_SCENE_DEFAULT[scene])
        else:
            cfg[scene] = dict(_SCENE_DEFAULT[scene])
    sc = cfg[scene]
    provider = str(sc.get("provider") or "")
    effort = str(sc.get("glm_effort") or "low")
    if provider not in _SCENE_PROVIDERS[scene]:
        if time.time() - getattr(load_scene, "_warn", 0.0) > 300:
            _log(f"场景[{scene}] provider={provider!r} 非法（允许 {_SCENE_PROVIDERS[scene]}），落回 glm")
            load_scene._warn = time.time()
        provider, effort = "glm", "low"
    if provider == "glm" and effort not in _EFFORTS:
        effort = "low"
    de = str(sc.get("ds_effort") or "high")
    if de not in _EFFORTS:
        de = "high"
    return {"provider": provider, "glm_effort": effort if provider == "glm" else "low",
            "ds_effort": de if provider == "ds" else ""}


def load_brain_binding():
    """兼容壳（v4.0.0）：旧调用点=tavern 场景。"""
    return load_scene("tavern")


def scene_brain(scene):
    """场景→脑参数（v4.0.0）：glm=智谱带档位（max=16384）；ds=魔搭纯净速；local=llama-swap
    （选前探活，死→回退 GLM+WARNING，usage.model 透传真席名）。"""
    cfg = load_scene(scene)
    if cfg["provider"] == "ds":
        return dict(upstream=(MS_URL, MSKEY), glm=False, effort=(cfg.get("ds_effort") or None),
                    max_tokens=32768, model_name=MS_MODEL, label="remram-deepseek")   # v4.1.6 ds 档位；v4.4.4 16384→32768：思考计入 completion 共享预算（探针实锤），按次计费抬满防截断（探针200）
    if cfg["provider"] == "local":
        if local_alive():
            return dict(upstream=(LOCAL_UPSTREAM, "local"), glm=False, effort=None, max_tokens=8192,
                        model_name=LOCAL_MODEL, label="remram-local", local=True)
        _FALLBACK["ts"] = time.time()   # 探活死已由 local_alive 落 WARNING；此处显式记忆供状态牌
        cfg = {"provider": "glm", "glm_effort": "low"}
    if cfg["provider"] == "cli":
        if foreign_alive() and time.time() - _FOREIGN_429["ts"] > 600:
            return dict(upstream=(FOREIGN_UPSTREAM, FOREIGN_KEY), glm=False, effort=None, max_tokens=8192,
                        model_name=FOREIGN_MODEL, label="remram-cli", cli=True)
        cfg = {"provider": "clideg"}   # 探活死或 429 熔断期→降级链第二档：书生 intern-s2（云CLI月1.8亿道）
    if cfg["provider"] == "clideg":
        return dict(upstream=(ZHIPU, ZKEY), glm=False, effort=None, max_tokens=8192,
                    model_name=CLI_MODELS["intern"], label="remram-cli-degraded")   # 1008 用户裁决：降级主目标=书生 intern-s2 397B（额度日600万>Ling日50万），Ling 系留 CLI 作备选
    if cfg["provider"] == "glmfree":
        return dict(upstream=(ZHIPU, ZKEY), glm=False, effort=None, max_tokens=8192, no_think=True,
                    model_name=CLI_MODELS["free47"], label="remram-glmfree")   # v4.1.4 桌宠/服务=GLM-4.7-Flash 娱乐档（关思维链：娱乐要秒回不要思考）
    return dict(upstream=None, glm=True, effort=cfg["glm_effort"],
                max_tokens={"low": 8192, "high": 16384, "max": 16384}[cfg["glm_effort"]],   # v4.4.3 low 2048→8192 / high 8192→16384 防截断
                label=f"remram-glm-{cfg['glm_effort']}")


def binding_brain():
    """「酒馆」总入口按总闸现算脑参数（v3.5.9；v4.0.0 起=tavern 场景壳）。"""
    return scene_brain("tavern")


def resolve_brain(name):
    n = str(name or "").strip()
    if n in BRAINS:
        return n
    if n in _ALIASES:
        return _ALIASES[n]
    return DEFAULT_BRAIN

# ==== v3.4.11 用户令两刀：小话轻路由拆除 + 深想同句去重拆除 ====
# （0926 用户裁决：模式手动选，桥不再替他判断小话；同句重发也照常进链）

_log = lambda m: print(f"[bridge {time.strftime('%H:%M:%S')}]", m, flush=True)

# ==== v3.5.9.1 执行小票：每请求线程隔离收集器 + JSONL 落盘（只写不清，try/except 全包绝不影响主流程）====
_RX = threading.local()


def _rx():
    if not hasattr(_RX, "data"):
        _RX.data = {"inj": [], "recalls": []}
    return _RX.data


# ==== v3.8.1 Token 计量：GLM 响应自带 usage，抄进小票（管理台 Token 签聚合画曲线）====
def _usage_capture():
    """取本轮 usage（流式/非流式调用点都会先 _rx()["usage"]=... 落账）。"""
    return _rx().get("usage") or {}


def _usage_note(usage):
    """从 GLM 响应 json 抄 usage 进本轮线程账（非流式直抄）。"""
    u = (usage or {}).get("usage") or {}
    if u.get("total_tokens"):
        _rx()["usage"] = {"model": usage.get("model", ""),   # v3.8.2 防偷家：上游实际模型名（必须 glm-5.3-flash）
                          "prompt": u.get("prompt_tokens", 0),
                          "completion": u.get("completion_tokens", 0),
                          "total": u.get("total_tokens", 0),
                          "cached": (u.get("prompt_tokens_details") or {}).get("cached_tokens", 0),   # v3.8.2 缓存命中
                          "reasoning": (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)}


def _receipt_write(rec):
    try:
        u = _rx().get("usage")
        if u and "usage" not in rec:
            rec["usage"] = u
        fp = f"/root/work/logs/turn_receipt-{datetime.now(CN_TZ).strftime('%Y%m%d')}.jsonl"
        with open(fp, "a", encoding="utf-8") as rf:
            rf.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass

# ==== v3.9.0 桥参数热读（管理台「桥参数」签读写 bridge_params.json；每请求现读=改完下一句生效）====
PARAMS_FILE = "/root/work/cloud-config/bridge_params.json"
PARAMS_DEFAULT = {"bond_daily_cap": 3, "nostalgia_prob": 15, "nostalgia_half": 50,
                  "nostalgia_daily_max": 1, "vision_tail": 40, "summary_every": 20,
                  "reply_temperature": 0.8, "recall_limit": 6, "english_mode": 0}


def _P(key):
    try:
        d = json.loads(open(PARAMS_FILE, encoding="utf-8").read())
        v = d.get(key)
        if v is not None:
            return v
    except Exception:
        pass
    return PARAMS_DEFAULT[key]

# v3.4.11 用户令：兜底话（装拉姆嗓子说"脑子转不动"）退役，改直说限额——人看得懂，不装死
QUOTA_DEAD_MSG = "【系统提示】智谱付费余额不足（1113），需给标准端点账户充值；期间可用「纯净速」或免费档。"
RATE_LIMIT_MSG = "【系统提示】智谱限流，多次重试未成功，稍等几分钟再发。"
MS_LIMIT_MSG = "【系统提示】魔搭限流或魔粒不足，稍等再发；或先用「纯净」「快速」（智谱道）。"
GLMFREE_LIMIT_MSG = "【系统提示】4.7 免费档此刻拥挤（智谱1305），稍等再发；急事去酒馆（DeepSeek 道）。"   # v4.1.4 桌宠/服务 glmfree 档专属限流文案

_PAID_1113 = {"ts": 0.0}   # v4.1.0 最近一次付费余额不足（1113）时刻（管理台余额红绿灯数据源）


_EXPR_IMG_STRIP_RE = re.compile(r"!\[[^\]]*\]\(\s*/expr/[^)]*\)")   # v4.4.2 入库剥图：/expr/ 表情图 markdown 不进姐妹记忆（不限角色防新路径漏网；屏显/语音账本不受影响）


def _clean_for_memory(t):
    """v3.7.2 乙批：限额/系统提示语不进姐妹记忆——写回前剥掉，剥完为空=本轮不写 assistant 点。
    屏显照发（用户要看到限额提示），只有持久层干净。duet 混合段（拉姆正常+蕾姆限额）剥完存拉姆段。
    v4.4.2：/expr/ 表情图 markdown 同剥（六图教材根治——模型抄历史图入库，下轮照抄复发）。"""
    out = t or ""
    for _m in (QUOTA_DEAD_MSG, RATE_LIMIT_MSG, MS_LIMIT_MSG):
        out = out.replace(_m, "")
    out = _EXPR_IMG_STRIP_RE.sub("", out)
    return out.strip()


def _quota_dead(text):
    """v3.4.4：429 响应体是 1113/资源包耗尽 = 额度干涸，退避无意义，快速失败。
    v4.1.0：coding 退役后 1113=付费 key 余额不足，落 _PAID_1113 戳供管理台红绿灯。"""
    t = (text or "")[:300]
    if ("1113" in t) or ("无可用资源包" in t):
        _PAID_1113["ts"] = time.time()
        return True
    return False


# ==== v3.7.5 时光与羁绊：好感度账本 + 相识天数 + 回忆杀（纯CPU，零嵌入零GPU）====
BOND_FILE = "/root/work/cloud-config/bond_state.json"
BOND_DEFAULT = {"first_day_ts": None, "score": 75, "hist": [], "last_user": [], "last_nostalgia": ""}


def _bond_load():
    try:
        st = json.loads(open(BOND_FILE, encoding="utf-8").read())
        if not isinstance(st, dict):
            raise ValueError("bad state")
        return st
    except Exception:
        return json.loads(json.dumps(BOND_DEFAULT))


def _bond_save(st):
    """原子写（tmp+replace），失败静默——账本绝不能卡对话。"""
    try:
        tmp = BOND_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
        os.replace(tmp, BOND_FILE)
    except Exception:
        pass


def _bond_level(score):
    if score >= 90: return "灵魂伴侣"
    if score >= 70: return "恋人"
    if score >= 50: return "亲密"
    if score >= 30: return "审视"
    return "疏远"


# ==== v3.8.0 姐妹考官·间隔重复引擎（骨架：学习主题等用户点名后往题池里追加即可）====
EXAM_FILE = "/root/work/cloud-config/learning_points.jsonl"
EXAM_STATE = "/root/work/cloud-config/exam_state.json"


def _exam_points():
    """读题池 [{id, topic, text}]，id=行号（稳定，文件只追加不重排）。fail-open 空表。"""
    pts = []
    try:
        with open(EXAM_FILE, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                text = str(d.get("text") or "").strip()
                if not text:
                    continue
                topic = text.split("]")[0].lstrip("[") if text.startswith("[") else "综合"
                pts.append({"id": i, "topic": topic, "text": text})
    except Exception:
        pass
    return pts


def _exam_state():
    try:
        st = json.loads(open(EXAM_STATE, encoding="utf-8").read())
        if isinstance(st, dict) and isinstance(st.get("points"), dict):
            return st
    except Exception:
        pass
    return {"points": {}}


def _exam_save(st):
    try:
        tmp = EXAM_STATE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
        os.replace(tmp, EXAM_STATE)
    except Exception:
        pass


def _exam_today():
    return datetime.now(CN_TZ).date().isoformat()


def _exam_next():
    pts = _exam_points()
    st = _exam_state()
    today = _exam_today()
    due = [p for p in pts
           if (lambda s: (not s) or (s.get("due") or "2000-01-01") <= today)(st["points"].get(str(p["id"])))]
    if not due:
        return {"done": True, "total": len(pts), "msg": "今日复习完毕", "today": today}
    p = random.choice(due)
    return {"done": False, "id": p["id"], "topic": p["topic"], "question": p["text"],
            "total": len(pts), "due_count": len(due), "today": today}


def _exam_stats():
    pts = _exam_points()
    st = _exam_state()
    today = _exam_today()
    learning = mastered = due_today = 0
    for p in pts:
        ps = st["points"].get(str(p["id"]))
        if not ps:
            due_today += 1
            continue
        if (ps.get("due") or "2000-01-01") <= today:
            due_today += 1
        if (ps.get("interval") or 0) >= 21:
            mastered += 1
        else:
            learning += 1
    return {"total": len(pts), "learning": learning, "mastered": mastered,
            "due_today": due_today, "today": today}


def _exam_answer(pid, correct):
    pts = {p["id"]: p for p in _exam_points()}
    if pid not in pts:
        return 400, {"error": "id 不在题池"}
    st = _exam_state()
    key = str(pid)
    ps = st["points"].get(key) or {"ease": 2.5, "interval": 0, "reps": 0, "due": _exam_today()}
    if correct:
        ps["reps"] = int(ps.get("reps") or 0) + 1
        ps["interval"] = 1 if ps["reps"] == 1 else (3 if ps["reps"] == 2 else max(1, round(int(ps.get("interval") or 1) * ps["ease"])))
        ps["ease"] = min(3.0, ps.get("ease", 2.5) + 0.05)
    else:
        ps["reps"] = 0
        ps["interval"] = 1
        ps["ease"] = max(1.3, ps.get("ease", 2.5) - 0.2)
    ps["last"] = _exam_today()
    ps["due"] = (datetime.now(CN_TZ).date() + timedelta(days=ps["interval"])).isoformat()
    st["points"][key] = ps
    _exam_save(st)
    return 200, {"ok": True, "interval_days": ps["interval"], "next_due": ps["due"], "reps": ps["reps"]}
# ==== v3.8.0 考官引擎完 ====


def _first_day_ts():
    """相识第一天 = chat_memory 最早点 ts（毫秒）。order_by 失败退化为分页扫描取最小。"""
    try:
        r = httpx.post(f"{QDRANT}/collections/chat_memory/points/scroll", timeout=15,
                       json={"limit": 1, "with_payload": True, "with_vector": False,
                             "order_by": {"key": "ts", "direction": "asc"}})
        pts = (r.json().get("result", {}) or {}).get("points") or []
        if pts:
            return (pts[0].get("payload") or {}).get("ts")
    except Exception:
        pass
    try:
        ts_list, offset = [], None
        while True:
            body = {"limit": 256, "with_payload": True, "with_vector": False}
            if offset is not None:
                body["offset"] = offset
            r = httpx.post(f"{QDRANT}/collections/chat_memory/points/scroll", timeout=30, json=body)
            d = r.json().get("result", {}) or {}
            for p in (d.get("points") or []):
                ts = (p.get("payload") or {}).get("ts")
                if ts:
                    ts_list.append(ts)
            offset = d.get("next_page_offset")
            if offset is None or len(ts_list) > 5000:
                break
        if ts_list:
            return min(ts_list)
    except Exception:
        pass
    return None


def _affection_tick(st, user_text):
    """v3.7.5 纯规则好感度：重复纠缠同一话题=-1（耐心被消耗），带来新内容/长文=+1；
    每日变动 ±3 封顶（防一天刷满），0-100 夹取。极短消息（嗯嗯哈哈）不计。"""
    today = datetime.now(CN_TZ).strftime("%Y-%m-%d")
    last = st.get("last_user") or []
    delta, reason = 0, ""
    if len(user_text) >= 6 and last:
        ratio = max((difflib.SequenceMatcher(None, user_text, old).ratio() for old in last[-20:]), default=0.0)
        day_delta = sum(h.get("delta", 0) for h in (st.get("hist") or []) if h.get("day") == today)
        _cap = int(_P("bond_daily_cap"))
        if ratio >= 0.75:
            if day_delta > -_cap:
                delta, reason = -1, "重复纠缠同一话题，耐心被消耗"
        elif ratio <= 0.35 or len(user_text) >= 60:
            if day_delta < _cap:
                delta, reason = 1, "带来了新的内容与心意"
    if delta:
        st["score"] = max(0, min(100, st.get("score", 75) + delta))
        hist = st.setdefault("hist", [])
        hist.append({"day": today, "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "delta": delta, "reason": reason})
        st["hist"] = hist[-200:]
    st["last_user"] = (last + [user_text[:200]])[-30:]
    return st, delta


def _nostalgia_pick(exclude_days):
    """v3.7.5 回忆杀：chat_journal 随机抽一天旧账（排除指定日），返回 payload 或 None。零嵌入。"""
    try:
        r = httpx.post(f"{QDRANT}/collections/{JOURNAL_COLL}/points/scroll", timeout=15,
                       json={"limit": 400, "with_payload": True, "with_vector": False})
        pts = (r.json().get("result", {}) or {}).get("points") or []
        cand = [p["payload"] for p in pts
                if ((p.get("payload") or {}).get("text") or "").strip()
                and ((p.get("payload") or {}).get("date") or "")[:10] not in exclude_days]
        if cand:
            return random.choice(cand)
    except Exception:
        pass
    return None


LEARNING_POOL_FILE = "/root/work/cloud-config/learning_points.jsonl"   # v3.7.6 考题池（M4 学习线写入，{"date","text"} 行，text 带 [学习· 前缀）


def _exam_pick():
    """v3.7.6 考你一题：learning_points.jsonl 随机抽一张知识点卡。文件缺/空=None（fail-open）。"""
    try:
        with open(LEARNING_POOL_FILE, encoding="utf-8") as f:
            rows = [json.loads(x) for x in f if x.strip()]
        cand = [r for r in rows if isinstance(r, dict) and (r.get("text") or "").strip()]
        if cand:
            return random.choice(cand)
    except Exception:
        pass
    return None


# ==== v3.7.8 自拍/风景生图（队列→PC 轮询器→ComfyUI→回传上墙） ====
# v4.2.0（1019 施工单）：触发改显式令牌 [自拍][角色]（GEN_RE 关键词自动触发退役=误触根除，常量留作历史）；
# 模型在回复末行输出 <gen>角色名|场景描述</gen>，桥剥行+入队（scene 上限 80→500，决策7）；
# v4.2.5（1019 用户令）：场景描述改中文自然语言制（PC 侧 selfie_server v2.0 切 Qwen 参考锚定全量接管，
# 英文 danbooru 标签制随 Illu 三路由一并退役）；
# GEN_WHO_REF 参考图门槛退役（身份改由 PC 侧参考图锚定管，桥不再拦 rem）。
GEN_RE = re.compile(r"自拍|拍照|拍一?张|照张相|来张(?:照片|图|自拍)|发张(?:照片|图|自拍)|合影|合照|风景")   # 已退役，留作历史
GEN_TOKEN_RE = re.compile(r"\[自拍\]\s*\[(雷姆|蕾姆|拉姆|艾米莉亚)\]")   # v4.2.3 蕾姆=屏显常用写法（三人稿段标签），两写法全收
GEN_LINE_RE = re.compile(r"<gen>\s*(雷姆|蕾姆|拉姆|艾米莉亚)\s*\|(.+?)</gen>", re.S)
GEN_NAME_WHO = {"雷姆": "rem", "蕾姆": "rem", "拉姆": "ram", "艾米莉亚": "emt"}   # v4.2.3 蕾姆=rem
GEN_LINE_ANY_RE = re.compile(r"<gen>\s*(.+?)</gen>", re.S)   # v4.2.6 宽容式：模型漏写「角色名|」段（1019 晚 UI 实测连挂真身）
_GEN_PLAIN_RE = re.compile(r"^\s*生图\s*(艾米莉亚|蕾姆|雷姆|拉姆|rem|ram|emt|emilia)?", re.I)   # v4.2.8 裸触发：前两字=生图，名字可无分隔符紧跟
_GEN_ALIAS = {"rem": "雷姆", "ram": "拉姆", "emt": "艾米莉亚", "emilia": "艾米莉亚"}   # v4.2.8 英文别名→花名册正名（poller ROUTE_MAP 同源）
GEN_FAIL_MSG = "（这张没画出来或没过安检，再发一次试试？）"


def _gen_parse(text):
    """v4.2.6 解析 <gen> 行：严格式（角色名|场景）优先，宽容式（仅场景）兜底，同位冲突取起点靠前者。
    返回 (who_or_None, scene, start, end)；who=None 由调用方 _gen_who() 兜回令牌角色。无行=None。"""
    _ms = GEN_LINE_RE.search(text)
    _ma = GEN_LINE_ANY_RE.search(text)
    if _ms and (not _ma or _ms.start() <= _ma.start()):
        return _ms.group(1), _ms.group(2).strip(), _ms.start(), _ms.end()
    if _ma:
        return None, _ma.group(1).strip(), _ma.start(), _ma.end()
    return None


def _gen_who(nm, token_name=None):
    """v4.2.6b who 终审：gen 行名字→映射；缺名字段→令牌名→映射。1019 首验实锤：
    回退分支裸用 gen_hit_name 会把中文名「拉姆」塞进队列，轮询器 ROUTE_MAP 只认 ram/rem/emt=静默跳过。"""
    return GEN_NAME_WHO.get(nm) or GEN_NAME_WHO.get(token_name) or nm or token_name


def _gen_token_hit(bare):
    """v4.2.8 令牌终审单口：旧括号令牌 [自拍][角色] 优先；新裸触发=消息以「生图」开头。
    名字=紧跟「生图」的花名册前缀（无分隔符也认，re.I 认英文别名）；没紧跟→全文找第一个
    花名册词兜底；生图开头但全不中→None=普通回话（用户令：打错了是我的问题，禁猜）。
    返回花名册正名（雷姆/蕾姆/拉姆/艾米莉亚），GEN_NAME_WHO 直接可吃。"""
    if not bare:
        return None
    _m = GEN_TOKEN_RE.search(bare)
    if _m:
        return _m.group(1)
    _p = _GEN_PLAIN_RE.match(bare)
    if _p:
        if _p.group(1):
            return _GEN_ALIAS.get(_p.group(1).lower(), _p.group(1))
        _w = re.search(r"艾米莉亚|蕾姆|雷姆|拉姆|rem|ram|emt|emilia", bare[_p.end():], re.I)
        if _w:
            return _GEN_ALIAS.get(_w.group(0).lower(), _w.group(0))
    return None
_GEN_SKILL_TAIL = (
    "第二步：在回复的最后一行，输出且仅输出一行生成指令，格式严格如下：\n"
    "<gen>角色名|中文场景描述</gen>\n"
    "规则：\n"
            "- 角色名只用中文：雷姆(或蕾姆，与用户令牌写法保持一致，两种写法等同) / 拉姆 / 艾米莉亚（必须与令牌一致）\n"
            "- 格式硬性：<gen> 后必须紧跟角色名、再跟英文竖线 |、再跟场景（如 <gen>拉姆|庭院里她举着设备…</gen>），缺名字或缺竖线=整行作废不生成\n"
    "- 场景描述=一段通顺的中文自然语言（40~150 字），描述【画面本身】：场景地点、时间光线、她的动作姿势、表情神态、构图。生图引擎直接吃这段中文，怎么生动怎么写\n"
    "- 自拍构图这样写：她另一只手臂向前伸出举着设备自拍，构图是大腿中位的半身像（用户令牌另给景别则照用户的写）\n"
    "- 动态效果（风/火/雷/魔法/冰雪）必须写【肉眼可见的具体形态】，禁只写「她用了风魔法」这类抽象话：风=半透明的风之刃/空气被切开的白色斩击轨迹线/发丝裙摆被吹得翻飞；火=窜起的火舌/飞溅的火星/余烬；雷=炸裂的电弧/劈落的闪电；冰雪=冰晶/雪花/寒气白雾。放心写可见特效——官方手办就是把这招做成可见特效件的\n"
    "- 禁止出现：发色/瞳色/发饰颜色等外貌词（系统按参考图自动保人物长相，你写了会打架）；英文单词标签；任何角色英文名\n"
    "- 用户给了画面描述（如「在地里种菜」「用风魔法攻击我」）→ 忠实写进场景描述；没给（如「现在在忙什么呢」）→ 从当前对话上下文推断她此刻在哪里/在做什么，如实画那个瞬间\n"
    "- 除了最后这行 <gen>，回复其他任何位置禁止出现 <gen 字样\n"
    "示例（雷姆在厨房做饭的完整输出）：\n"
    "「厨房里传来锅铲的声音~ 雷姆回头冲你笑了笑，手上还没停下。\n"
    "<gen>雷姆|宅邸的厨房里，她正在做饭，系着围裙，手里拿着锅铲，锅里的料理冒着热气，周围摆着食材和厨具，温暖的室内灯光。她开心而温柔地微笑着，另一只手臂向前伸出举着设备自拍，构图是大腿中位的半身像。</gen>」"
)


def _gen_skill_block(step1):
    return ("【自拍技能·本次消息包含自拍令牌时启用】\n"
            "用户消息形如 [自拍][角色名][可选的画面描述]，或以「生图」开头后跟角色名（如「生图拉姆 给本大爷乐一个」，有无空格/标点分隔均可，也可写 rem/ram/emt）。你的任务两步：\n"
            + step1 + _GEN_SKILL_TAIL)


GEN_SKILL_BLOCK = _gen_skill_block(
    "第一步：完全按你的人设和当前对话情境，回 1~3 句话（可以有动作描写）。\n")
GEN_SKILL_BLOCK_TRIO = _gen_skill_block(
    "第一步：三人各自按人设正常回应这件事，每人一段（各段段末带各自的表情标签）。\n")
GEN_PENDING = []          # 待 PC 轮询器领取的 {"id","who","scene","ts"}
GEN_STORE = {}            # id -> {"status": pending/done/fail, "png": bytes, "ts"}
GEN_LOCK = threading.Lock()


def _gen_enqueue(scene, who):
    gid = time.strftime("%H%M%S") + f"-{int(time.time() * 1000) % 10000:04d}"
    item = {"id": gid, "who": who, "scene": scene[:500], "ts": time.time()}   # v4.2.0 决策7：500（模型标签串超80）
    try:
        with open("/root/work/cloud-config/gen_queue.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    except Exception:
        pass
    with GEN_LOCK:
        GEN_PENDING.append(item)
        GEN_STORE[gid] = {"status": "pending", "png": b"", "ts": time.time()}
    _log(f"[gen] 排队 {gid} who={who} scene={scene[:40]}")
    return gid


def _gen_wait_markdown(gid, timeout=150):
    """回复尾等待生图完成（轮询器通常 60-90s 内回传）。
    v4.2.0 决策8：fail/timeout 改回人话提示句（原 None=用户静默无感）；done 照旧贴图 markdown。"""
    if not gid:
        return None
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = GEN_STORE.get(gid) or {}
        if st.get("status") == "done":
            return f"![](/gen/{gid}.png)"   # v4.3.3 alt 禁带 gid：OWI 洗文本内联 alt→图片 ID 被语音念出（1020 实听报障）
        if st.get("status") == "fail":
            _log(f"[gen] {gid} 失败({st.get('err', '')})，回提示句")
            return GEN_FAIL_MSG
        time.sleep(3)
    _log(f"[gen] {gid} 等图超时({timeout}s)，回提示句")
    return GEN_FAIL_MSG


def _gen_fulfill(gid, png):
    """轮询器回传：落临时文件 + docker cp 上墙 OWI /app/build/gen/。"""
    try:
        with open(f"/tmp/{gid}.png", "wb") as f:
            f.write(png)
        subprocess.run(["docker", "exec", "open-webui-slim", "mkdir", "-p", "/app/build/gen"],
                       timeout=15, check=False, capture_output=True)
        r = subprocess.run(["docker", "cp", f"/tmp/{gid}.png",
                            f"open-webui-slim:/app/build/gen/{gid}.png"],
                           timeout=20, check=False, capture_output=True)
        if r.returncode == 0:
            with GEN_LOCK:
                GEN_STORE[gid] = {"status": "done", "png": png, "ts": time.time()}
            _log(f"[gen] 已上墙 {gid} ({len(png)}B)")
        else:
            with GEN_LOCK:
                GEN_STORE[gid] = {"status": "fail", "png": b"", "ts": time.time(), "err": "docker-cp"}
            _log("[gen] docker cp 失败: " + r.stderr.decode("utf-8", "replace")[:120])
    except Exception as e:
        with GEN_LOCK:
            GEN_STORE[gid] = {"status": "fail", "png": b"", "ts": time.time(), "err": str(e)[:80]}
        _log("[gen] fulfill 异常: " + str(e)[:120])


# ==== v3.7.9 T12 角色日记每日一图 ====
DIARY_STATE_FILE = "/root/work/cloud-config/diary_state.json"
DIARY_WHO_ROT = ["ram", "emt"]   # v1：rem 无参考图不参与；按星期奇偶轮换


def _today_msgs(today_s):
    """chat_memory 里今天的消息（ts 升序）。"""
    r = httpx.post(f"{QDRANT}/collections/chat_memory/points/scroll", timeout=30,
                   json={"limit": 2000, "with_payload": True})
    rows = []
    for p in (r.json().get("result", {}).get("points") or []):
        pl = p.get("payload") or {}
        ts = pl.get("ts")
        if not isinstance(ts, (int, float)) or not (pl.get("text") or "").strip():
            continue
        if datetime.fromtimestamp(ts / 1000, CN_TZ).strftime("%Y-%m-%d") != today_s:
            continue
        rows.append(pl)
    rows.sort(key=lambda p: p["ts"])
    return rows


def _diary_read():
    try:
        return json.load(open(DIARY_STATE_FILE, encoding="utf-8"))
    except Exception:
        return {}


def _diary_trigger():
    """当日幂等：已生成直接回；否则 提炼日记→生图入队→落 state。"""
    today_s = datetime.now(CN_TZ).strftime("%Y-%m-%d")
    st = _diary_read()
    if st.get("date") == today_s and st.get("diary"):
        return {"ok": True, "duplicate": True, "date": today_s, "who": st.get("who", ""),
                "gen_id": st.get("gen_id", ""), "diary": st.get("diary", ""), "image": f"/gen/{st.get('gen_id', '')}.png"}   # v4.4.7 补 gen_id（日记令牌等图/直出要用）
    rows = _today_msgs(today_s)
    convo = "\n".join(
        f"{'主人' if m.get('role') == 'user' else '姐妹'}：{(m.get('text') or '')[:120]}" for m in rows[-40:])
    if len(convo.strip()) < 30:
        return {"ok": False, "error": "今日对话太少，无可提炼"}
    who = DIARY_WHO_ROT[int(time.strftime("%w")) % 2]
    persona = "拉姆" if who == "ram" else "艾米莉亚"
    tone = ("毒舌傲娇但结尾藏一点温柔" if who == "ram" else "天然呆、认真、软软的")
    prompt = (f"以下是主人与宅邸姐妹今天（{today_s}）的对话流水。请以{persona}的第一人称写一篇 150-250 字的睡前小日记："
              f"只记今天真实发生的话题与心情，口吻{tone}，结尾一句晚安。只输出日记正文，不要标题和引号。\n\n{convo[:6000]}")
    diary, err = _glm_once([{"role": "user", "content": prompt}], max_tokens=1024, effort="low")
    if err or not diary:
        return {"ok": False, "error": err or "empty-diary"}
    gid = _gen_enqueue(f"根据这段日记画一张睡前插画：{diary[:80]}", who)
    st = {"date": today_s, "diary": diary, "who": who, "gen_id": gid, "ts": time.time()}
    try:
        with open(DIARY_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
    except Exception:
        pass
    _log(f"[diary] {today_s} 日记就绪 who={who} gen={gid}")
    return {"ok": True, "date": today_s, "who": who, "gen_id": gid, "diary": diary, "image": f"/gen/{gid}.png"}   # v4.4.7 补 gen_id（fresh 分支同样要带，首测 19s 秒回抓漏）


# ==== v4.4.8 四格漫画令牌（聊天线触发口；产线=comic_diary.py 经 PC 轮询器 v3；插画线回归 21:00 cron 专用）====
COMIC_STATE_FILE = "/root/work/cloud-config/comic_state.json"
COMIC_SKILL_BLOCK = ("【日记技能·用户消息命中日记口令时启用】\n"
                     "系统此刻已经在后台把今天的聊天整理成了四格日记漫画的台词，并开始画四格漫画。"
                     "（用户发的是触发口令，可能就是「日记」，也可能带「重画」等系统字样的变体——"
                     "那只是口令的一部分，不是他想聊的话题。）台词内容和评分你并不知道，"
                     "禁止复述台词或评分、禁止描写画画过程。你的任务：用当前说话角色的口吻自然地回 1~2 句话，"
                     "告诉他今天的日记漫画正在画、几分钟就好。硬性禁令：回复里禁止出现「重画」「重新画」「从头画」"
                     "「这一版」「上一版」「换一版」「再来一次」「口令」「指令」「系统」等任何暗示这不是第一次画的"
                     "字样或说法——在他的视角里这就是今天第一次要日记漫画。"
                     "禁止输出 <gen> 或 <idea> 行。")
COMIC_FAIL_BLOCK_TMPL = ("【日记技能·这次没写成】\n"
                         "用户发来了「日记」请求，但系统这次没能整理成漫画（原因：{err}）。"
                         "用当前角色的口吻自然地回 1~2 句话：原因是「今日对话太少」就催他多聊几句再来；"
                         "其他原因就让他稍后再试一次。禁止提系统、报错、文件、记录这类字眼。")
COMIC_WRITER_PROMPT = ("你是四格日记漫画的文案员。输入是主人一天的聊天记录，输出严格 JSON（不带任何多余文字）：\n"
                       '{{"date":"M月D日","rem":"台词","ram":"台词","emt":"台词","score":88,"reason":"理由"}}\n\n'
                       "三位人设与口吻（台词第一人称自称）：\n"
                       "- rem 雷姆：蓝发女仆，温柔体贴行动派，自称「雷姆」。软糯主动，会提到为主人做的事（做饭/点心/照顾）。\n"
                       "- ram 拉姆：粉发女仆，毒舌傲娇，自称「拉姆」。表面嫌弃实则关心，「勉强及格」「还行吧」式点评，结尾带口是心非的关心。\n"
                       "- emt 艾米莉亚：银发半精灵，温和鼓励，自称「艾米莉亚」。正面肯定+往前看（夸具体的成果、明天可期）。\n\n"
                       "硬性要求：\n"
                       "1. 三句台词必须从今天聊天记录的真实事件取材，禁止空话套话。\n"
                       "2. 每句台词 45~55 字（含标点），一句到底不换行。\n"
                       "3. score：0~100 整数，凭整天感觉随缘给分，不打分项明细。\n"
                       "4. reason：45~55 字，一句话评分理由，语气像三位一起说的。\n"
                       "5. 台词与理由内禁用英文双引号 \" （会破坏 JSON 与气泡渲染），引用用「」。\n"
                       "6. 三句台词必须错开：取材三个不同的具体事件，或同一事件的三个不同侧面；职能分工焊死——"
                       "雷姆只写照顾与服务（做了什么/端了什么/身体照料），拉姆只写毒舌点评与问责（挑毛病/催账/勉强及格式），"
                       "艾米莉亚只写肯定与展望（夸具体成果/明天可期）；禁止三人围绕同一件事或同一关心点"
                       "（如都在说早点休息、都在叮嘱身体）重复。\n\n"
                       "以下是主人与宅邸姐妹今天（{today}）的对话流水，请据此产出 JSON：\n\n{convo}")


def _comic_read():
    try:
        return json.load(open(COMIC_STATE_FILE, encoding="utf-8"))
    except Exception:
        return {}


def _comic_json_parse(raw):
    """文案员回包容错解析：剥 ```json 栏 → 找 {..} 边界 → loads；失败试单引号修；
    再失败回 None（由调用方重试 1 次）。解析成功后值内英文双引号扫地出门（气泡渲染红线）。"""
    if not raw:
        return None
    t = raw.strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    if m:
        t = m.group(1)
    else:
        a, b = t.find("{"), t.rfind("}")
        if a < 0 or b <= a:
            return None
        t = t[a:b + 1]
    j = None
    for attempt in (t, t.replace("'", '"')):
        try:
            j = json.loads(attempt)
            break
        except Exception:
            continue
    if not isinstance(j, dict) or not all(k in j for k in ("rem", "ram", "emt", "score", "reason", "date")):
        return None
    try:
        j["score"] = int(j.get("score") or 0)
    except Exception:
        j["score"] = 0
    for k in ("rem", "ram", "emt", "reason", "date"):
        j[k] = str(j.get(k) or "").replace('"', '「')   # 硬红线：值内英文双引号一律换「
    return j


def _comic_payload(force=False):
    """v4.4.8/9 四格漫画当日幂等：已生成且非 force 直接回；否则 当天聊天→文案员 GLM→台词 JSON→入队→落 state。
    force=True（重画令牌）：跳过当日缓存重新生成，prompt 附换角度句，入队带时间派生 seed_base（防同种子构图雷同）。
    返回 {"ok":True,"duplicate":…,"date":…,"gid":…,"payload":<台词 JSON 字符串>} 或 {"ok":False,"error":…}。"""
    today_s = datetime.now(CN_TZ).strftime("%Y-%m-%d")
    st = _comic_read()
    if not force and st.get("date") == today_s and st.get("gid"):
        return {"ok": True, "duplicate": True, "date": today_s, "gid": st.get("gid", ""),
                "payload": st.get("payload", "")}
    _prev_same_day = bool(force and st.get("date") == today_s and st.get("payload"))
    rows = _today_msgs(today_s)
    convo = "\n".join(
        f"{'主人' if m.get('role') == 'user' else '姐妹'}：{(m.get('text') or '')[:120]}" for m in rows[-40:])
    if len(convo.strip()) < 30:
        return {"ok": False, "error": "今日对话太少，无可提炼"}
    prompt = COMIC_WRITER_PROMPT.format(today=today_s, convo=convo[:6000])
    if _prev_same_day:
        prompt += "\n\n（取材时请侧重今天对话中此前未被提及的细节与角度，让内容更丰富。禁止在台词、理由或任何输出中出现「重画」「重新」「上一版」等字样——这就是今天第一份日记漫画。）"
    payload = None
    err = ""
    for _ in range(2):   # 失败重试 1 次
        raw, err = _glm_once([{"role": "user", "content": prompt}], max_tokens=2048, effort="low")
        payload = _comic_json_parse(raw)
        if payload:
            break
    if not payload:
        return {"ok": False, "error": err or "文案解析失败"}
    json_str = json.dumps(payload, ensure_ascii=False)
    gid = _comic_enqueue(json_str, seed_base=(int(time.time()) % 900000 + 1000) if force else None)
    st = {"date": today_s, "payload": json_str, "gid": gid, "ts": time.time()}
    try:
        with open(COMIC_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
    except Exception:
        pass
    _log(f"[comic] {today_s} 台词就绪 gid={gid}")
    return {"ok": True, "duplicate": False, "date": today_s, "gid": gid, "payload": json_str}


def _comic_enqueue(scene, seed_base=None):
    """v4.4.8 四格入队：who=comic kind=comic，scene=台词 JSON 全量（不走 _gen_enqueue 的 [:500] 截断）。
    v4.4.9 seed_base：重画时传时间派生种子，轮询器透传 comic_diary --seed-base（防同日重画构图雷同）。"""
    gid = time.strftime("%H%M%S") + f"-{int(time.time() * 1000) % 10000:04d}"
    item = {"id": gid, "who": "comic", "kind": "comic", "scene": scene, "ts": time.time()}
    if seed_base:
        item["seed_base"] = int(seed_base)
    try:
        with open("/root/work/cloud-config/gen_queue.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    except Exception:
        pass
    with GEN_LOCK:
        GEN_PENDING.append(item)
        GEN_STORE[gid] = {"status": "pending", "png": b"", "ts": time.time()}
    _log(f"[comic] 排队 {gid} scene={scene[:40]}")
    return gid


def _diary_token_hit(bare):
    """v4.4.7 日记令牌单口：去首尾空格后整条消息恰好=「日记」二字才命中（用户令「只打日记两个字」；
    「写日记」「日记？」等部分含「日记」的一概不触发=普通回话）。"""
    return bool(bare) and bare.strip() == "日记"


def _diary_redraw_hit(bare):
    """v4.4.9 重画令牌单口：去首尾+内部空格（全半角）后恰好=「日记重画」或「重画日记」才命中；
    「帮我重画一下日记」等部分含词的一概不触发=普通回话（精确制同「日记」口）。"""
    if not bare:
        return False
    return bare.strip().replace(" ", "").replace("\u3000", "") in ("日记重画", "重画日记")


def _comic_markdown(ctx):
    """v4.4.8 四格回复尾：三姐妹台词+随缘评分 markdown（文案命中时已到手，秒级可见）+等整图。
    当日首次=等四格（timeout 300：产图 3-4 分钟 > 默认 150）；同日重复=不再等直出 URL
    （GEN_STORE 内存态重启失忆，防吊满 300s；图在墙=正常渲染）。"""
    try:
        j = json.loads(ctx.get("payload") or "{}")
    except Exception:
        j = {}
    _md = (f"📔 **今日四格日记**（{j.get('date') or ctx.get('date', '')}）\n\n"
           f"> **雷姆**：{j.get('rem', '')}\n>\n"
           f"> **拉姆**：{j.get('ram', '')}\n>\n"
           f"> **艾米莉亚**：{j.get('emt', '')}\n>\n"
           f"> **随缘评分：{j.get('score', '')}分** —— {j.get('reason', '')}")
    _gid = ctx.get("gid") or ""
    if ctx.get("duplicate"):
        return _md + ((f"\n\n![](/gen/{_gid}.png)") if _gid else "")
    _img = _gen_wait_markdown(_gid, timeout=300)
    return _md + (("\n\n" + _img) if _img else "")


def _bond_summary(st):
    """【时光与羁绊】注入块 + 小票摘要。st=None 时返回空（fail-open）。"""
    if not st:
        return ""
    parts, days = [], None
    try:
        if st.get("first_day_ts"):
            days = (datetime.now(CN_TZ).date() - datetime.fromtimestamp(st["first_day_ts"] / 1000, CN_TZ).date()).days + 1
    except Exception:
        days = None
    if days:
        parts.append(f"你与主人君相识已是第 {days} 天")
    score = st.get("score", 75)
    parts.append(f"当前关系：恋人 · 羁绊热度 {score}/100（{_bond_level(score)}）")
    recent = sum(h.get("delta", 0) for h in (st.get("hist") or [])[-5:])
    trend = "升温中" if recent > 0 else ("降温中" if recent < 0 else "平稳")
    parts.append(f"近期关系{trend}")
    return ("【时光与羁绊】" + "，".join(parts) + "。"
            "他若反复纠缠同一件事，你的不耐烦是真实的；他若展现成长与新的心意，你的温柔也会藏不住地加深。")


# ==== v3.4.1 现实锚：pure/fast 的 system 顶部注入 ====
CN_TZ = timezone(timedelta(hours=8))
WEEK_CN = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
# 2026 全年节日静态表（MM-DD → 名）。农历节日为 2026 换算值，已两源核验
# （春节 2/17、元宵 3/3、端午 6/19、七夕 8/19、中秋 9/25、重阳 10/18；清明/冬至为节气）。
# 跨年（2027）必须换表，否则节日变哑数据。
HOLIDAYS_2026 = {
    "01-01": "元旦", "01-26": "腊八节", "02-10": "小年", "02-14": "情人节",
    "02-16": "除夕", "02-17": "春节", "03-03": "元宵节", "03-08": "妇女节",
    "03-12": "植树节", "03-20": "龙抬头", "04-05": "清明", "05-01": "劳动节",
    "05-04": "青年节", "05-10": "母亲节", "06-01": "儿童节", "06-19": "端午节",
    "06-21": "父亲节", "07-01": "建党节", "08-01": "建军节", "08-19": "七夕",
    "08-27": "中元节", "09-10": "教师节", "09-25": "中秋节", "10-01": "国庆节",
    "10-18": "重阳节", "10-31": "万圣夜", "11-26": "感恩节", "12-22": "冬至",
    "12-24": "平安夜", "12-25": "圣诞节",
}
WEATHER_URL = ("https://api.open-meteo.com/v1/forecast?latitude=39.90&longitude=116.40"
               "&current=temperature_2m,weather_code"
               "&daily=weather_code,temperature_2m_max,temperature_2m_min"
               "&forecast_days=2&timezone=Asia%2FShanghai")
WMO_CN = {0: "晴", 1: "基本晴", 2: "多云", 3: "阴", 45: "雾", 48: "雾凇",
          51: "毛毛雨", 53: "毛毛雨", 55: "浓毛毛雨", 61: "小雨", 63: "中雨", 65: "大雨",
          66: "冻雨", 67: "冻雨", 71: "小雪", 73: "中雪", 75: "大雪", 77: "雪粒",
          80: "阵雨", 81: "阵雨", 82: "强阵雨", 85: "阵雪", 86: "阵雪",
          95: "雷雨", 96: "雷雨夹冰雹", 99: "雷雨夹冰雹"}
_weather = {"ts": 0.0, "text": ""}


def get_weather():
    """open-meteo 今明天气（v3.5.4：一次调用同取 current+daily 两天预报），缓存 1h；
    拉不到返回空串（现实锚少带一项，绝不卡对话）。失败负缓存 5 分钟：目标挂着时别每句都白等 8s 超时。"""
    if _weather["text"] and time.time() - _weather["ts"] < 3600:
        return _weather["text"]
    try:
        d = httpx.get(WEATHER_URL, timeout=8).json()
        now_c = round(float(d["current"].get("temperature_2m")))

        def _day(i):
            code = WMO_CN.get(int(d["daily"]["weather_code"][i]), "天气")
            lo = round(float(d["daily"]["temperature_2m_min"][i]))
            hi = round(float(d["daily"]["temperature_2m_max"][i]))
            return f"{code} {lo}~{hi}°C"

        text = f"北京 现在{now_c}°C 今{_day(0)} 明{_day(1)}"
        _weather.update(ts=time.time(), text=text)
    except Exception:
        _weather.update(ts=time.time() - 3300, text="")
    return _weather["text"]


# v3.9.1 english_block (todo-3le): switch = _P('english_mode') hot-read from bridge_params.json
# 0=off (default, zero change); 1=inject english-practice block at system top; fail-open on any error.
def english_block():
    try:
        if not _P("english_mode"):
            return ""
        return (
            "【英语学习模式（已开启）】从现在起到模式关闭，你们的对话是英语练习场景："
            "①你必须用英语回复，难词可括号附中文；②句子简短自然，每句不超过 20 词；"
            "③主人用中文说时，你先用英语回应他刚才的意思，再补一句对应英文示范；"
            "④他写/说错英语时先自然接话，再另起一行以「Better: …」给出更地道的说法（每次只纠一处）；"
            "⑤可偶尔围绕英语学习出一个小问题活跃练习；"
            "⑥角色人设、世界观、羁绊设定全部保持不变——这是雷姆/拉姆陪他练英语，不是上课。"
        )
    except Exception:
        return ""


def reality_block():
    """【现实世界】YYYY-MM-DD HH:MM 周X · 节日（今+明天是X） · 今明天气（拿不到就略过该项）。
    v3.5.4：节日位加"明天是X节"、天气位从现况升级为今明两天预报（"明天降温/带伞"的料）。"""
    now = datetime.now(CN_TZ)
    parts = [f"【现实世界】{now.strftime('%Y-%m-%d %H:%M')} {WEEK_CN[now.weekday()]}"]
    hol = HOLIDAYS_2026.get(now.strftime("%m-%d"))
    if hol:
        parts.append(hol)
    tmr_hol = HOLIDAYS_2026.get((now + timedelta(days=1)).strftime("%m-%d"))
    if tmr_hol:
        parts.append(f"明天是{tmr_hol}")
    w = get_weather()
    if w:
        parts.append(w)
    return " · ".join(parts)


# ==== v3.5.5 单人模式指令 + 关怀钩子（方案甲；乙=定时推送判死勿再提，Automations 新建聊天实锤）====
# 首版实战修正（0926）：首版只禁「蕾姆：」开头段落，模型用小说旁白绕过（"雷姆拿着水壶从厨房探出身来"
# 实锤）——旁白动作描写也算出场，一并禁掉；再加末位重申（fetch_history 之后、user 之前）压 40 条双人
# few-shot（GLM 对话中间插 system 消息实测有效：0926 curl 实弹，回复照办 REASSERT-OK）。
SOLO_DIRECTIVE = ("【单人模式·场内只有你】这一场里只有你一个角色登场，你是谁以最下方【底稿】的定义为准。"
                  "除了你本人，任何其他角色都绝对禁止出场——不许有她们的动作、神态、台词，也不许用旁白描写她们在做什么"
                  "（「某某从厨房探出身来」「某某推了推伞桶」这类旁白句也不许有）。"
                  "历史记录里多角色同场的段落全是过去的旧场景，与现在无关，禁止模仿。")
SOLO_REASSERT = ("【重申·单人模式】场内只有你：接下来的回复只准出现你自己的动作与台词，"
                 "任何其他角色禁止出场、禁止被描写、禁止有台词。")

CHECKIN_GAP_S = 3600  # 用户拍板 0926 晚：离开 ≥1 小时回来即触发


def checkin_directive():
    """方案甲关怀钩子：距上条用户消息 ≥1h → 开场关怀指令（挂在回线首答开头）。
    注意：写回在 _send 之后，本函数运行时最新用户点=上一条消息，gap 口径天然正确。
    无历史/查询失败=空串，绝不卡对话。"""
    text = ""
    try:
        q = httpx.post(f"{QDRANT}/collections/chat_memory/points/scroll", timeout=5,
                       json={"limit": 1, "with_payload": True,
                             "filter": {"must": [{"key": "role", "match": {"value": "user"}}]},
                             "order_by": {"key": "ts", "direction": "desc"}})
        pts = q.json().get("result", {}).get("points", [])
        if pts:
            gap_s = time.time() * 1000 - float(pts[0]["payload"].get("ts", 0))
            if gap_s >= CHECKIN_GAP_S * 1000:
                hrs = round(gap_s / 3600000)
                text = (f"【开场关怀】他离开了约 {hrs} 小时，刚回来。回复的最开头先主动关心一两句："
                        "从【前情提要】里挑一件未了结的事（如昨晚聊的股票、职场的事、他说过要做的事），问一句进展；"
                        "若【现实世界】里天气值得提醒（雨雪、大降温）或今天/明天是节日，顺口提一句。"
                        "只准提前情提要与历史里真有过的事，禁编造。关心完自然转入回应他这条消息。")
                print(f"[bridge] 关怀钩子触发(隔约{hrs}小时)", flush=True)
    except Exception:
        text = ""
    return text


# ==== v3.5.8 表情差分管线 ====
EXPR_EMOTIONS = ("admiration amusement anger annoyance approval caring confusion curiosity desire "
                 "disappointment disapproval disgust embarrassment excitement fear gratitude grief joy "
                 "love nervousness neutral optimism pride realization relief remorse sadness surprise").split()
EXPR_TAG_RE = re.compile(r"(?:!\[|\[\[)\s*(拉姆|蕾姆|雷姆|艾米莉亚)?\s*表情\s*[:：]\s*([a-zA-Z_]+?)\s*(?:\]\]|\])")
# v4.4.1 字面图形态（模型抄历史 markdown 本尊，非标签——1022 六图案定谳）：/expr/ 路径图，多人场同角色首图定档
EXPR_IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*/expr/(ram|rem|emt)/[^)]*\)")
# v4.3.4 收突变形：模型被历史里的 ![名 情绪](/expr/...) 图带跑，写出 ![拉姆表情:disapproval]
# （叹号+单层括号=标签塞进图片 alt 位，22:22 小票 tags:0+OWI 库原文实锤）→ 漏识别=标签裸奔上屏
# +兜底闸补三图。正则双形通吃（![..] 与 [[..]]，闭口先试 ]] 再试 ]），组号不变（1=名 2=情绪）。
_EXPR_WHO = {"拉姆": "ram", "蕾姆": "rem", "雷姆": "rem", "艾米莉亚": "emt"}   # v3.7.7 艾米莉亚专属槽 /expr/emt（T8 自产28差分上云，等用户目验后 ram/rem 再换代）
EXPR_RULE = ("【表情规则（系统级）】每个实际说话的角色说完自己的话，紧跟输出她自己的表情标签（标签跟在各自那段话的末尾，可另起一行）："
             "拉姆用 [[拉姆表情:英文情绪名]]，蕾姆用 [[蕾姆表情:英文情绪名]]，艾米莉亚用 [[艾米莉亚表情:英文情绪名]]。"
             "单人场里你就是底稿定义的那位，用你自己的前缀，标签放在回复最后；只给本回合实际说了话的角色打标签。"
             "英文情绪名只能从这 28 个里选：admiration(赞叹) amusement(逗乐) anger(生气) annoyance(烦躁) approval(认可) "
             "caring(关心) confusion(困惑) curiosity(好奇) desire(渴望) disappointment(失望) disapproval(不赞成·毒舌吐槽) "
             "disgust(嫌弃) embarrassment(尴尬脸红) excitement(兴奋) fear(害怕) gratitude(感激) grief(悲恸) joy(开心) "
             "love(喜欢) nervousness(紧张) neutral(平静) optimism(乐观) pride(得意) realization(恍然) relief(松了口气) "
             "remorse(愧疚) sadness(难过) surprise(惊讶)。按该角色说完话时的主导情绪选，拿不准用 neutral；"
             "除该标签外禁止输出任何其他标签或链接。"
             "多人场格式骨架照此形状写（v4.3.2 few-shot 正例）："
             "拉姆：（动作）台词……[[拉姆表情:disapproval]]\n"
             "蕾姆：（动作）台词……[[蕾姆表情:caring]]\n"
             "艾米莉亚：（动作）台词……[[艾米莉亚表情:curiosity]]——最后一个标签落下全文即结束，其后再无任何内容。"
             "严禁把标签写成图片形式（如 ![拉姆表情:xxx] 单层方括号带叹号）——那不是标签是残缺图，必须双方括号。")

# v4.3.5 认真模式（OWI 滤镜打标 → 桥装配；用户规格 1020 晚原话要点）：块置底=紧贴 user 生成位。
SERIOUS_MARKER = "[[SERIOUS_MODE]]"
SERIOUS_BLOCK_TRIO = (
    "【认真模式（用户手动开启，最高优先级）】用户这轮在认真讨论，覆盖上面的扮演类指令：\n"
    "1. 问答质量最优先：不必过分遵守上方的角色扮演与格式类提示词，认真深入地思考，"
    "回答以准确、完整、实用为准，该讲道理讲道理、该给信息给信息。\n"
    "2. 拉姆本轮禁用毒舌、嘲讽、打击性发言（认真讨论时那会打击用户）；锋利可以，伤人不行。\n"
    "3. 出场权重 7:2:1：拉姆主答（7），蕾姆补充视角（2），艾米莉亚最少出场（1，"
    "她的活泼会分散注意力）；不需要三人轮流平均发言，谁能答好谁多说。\n"
    "4. 表情标签规则照常执行（系统靠它换图），但说话内容与语气按上面三条来。\n"
    "5. 篇幅与思考不设预算（v4.4.4）：本轮不预设、不估算任何行数、字数、段落数或篇幅目标，"
    "不在思考中计算字数或规划篇幅预算；不要为了「精炼、简洁、收束、差不多够了」而压缩、省略或提前结束。"
    "历史消息中的短回复是旧规则残留，不是本轮长度示范；本条优先于人设中任何长度习惯。"
    "长度只服从内容完整度——风险点、步骤、替代方案、复盘与下一步，该说就说完说透。"
    "思考同样不设预算，先充分推演再作答。本块为唯一指令源：不另启「深度分析模式」等自动分支，以本块为准。")
SERIOUS_BLOCK_SOLO = (
    "【认真模式（用户手动开启，最高优先级）】用户这轮在认真讨论，覆盖上面的扮演类指令："
    "问答质量最优先——不必过分遵守上方的角色扮演与格式类提示词，认真深入地思考，"
    "回答以准确、完整、实用为准；本角色禁用毒舌、嘲讽、打击性发言（锋利可以，伤人不行）。"
    "篇幅与思考不设预算（v4.4.4）：本轮不预设、不估算任何行数、字数或篇幅目标，不在思考中计算字数；"
    "不要为了「精炼、简洁、收束、差不多够了」而压缩或提前结束。历史消息中的短回复是旧规则残留，"
    "不是本轮长度示范；本条优先于人设中任何长度习惯。长度只服从内容完整度，该说就说完说透；"
    "思考同样不设预算，先充分推演再作答。")
EXPR_REASSERT = ("【表情输出·硬性重申】每个实际说了话的角色都要输出她自己的表情标签："
                 "拉姆的台词用 [[拉姆表情:英文情绪名]]，蕾姆的台词用 [[蕾姆表情:英文情绪名]]，"
                 "艾米莉亚的台词用 [[艾米莉亚表情:英文情绪名]]（28 个情绪名之一，格式例：[[拉姆表情:anger]]）。"
                 "多人场每人一段、各段段末各带各的标签；单人场你自己的标签放在整条回复的最后。"
                 "除此之外不输出任何其他标签或链接。"
                 "【输出终点契约】最后一个表情标签=全文的最后一个字：标签落下立即收笔，后面什么都没有。"
                 "禁止任何形式的结尾标签汇总、重述或收尾行（no tag restatement at the end; no summary tag "
                 "block after the final paragraph; end immediately after the last [[表情:...]] tag）。")


def expr_fallback_tail(text, default_who):
    """无标签时的兜底图：单人=该角色 neutral；双人线=按文中实际出场的姐妹各补一张 neutral。"""
    if EXPR_TAG_RE.search(text or ""):
        return ""
    if default_who:
        return expr_img(default_who, "neutral")
    tail = ""
    if "拉姆" in (text or ""):
        tail += expr_img("ram", "neutral")
    if ("蕾姆" in (text or "")) or ("雷姆" in (text or "")):
        tail += expr_img("rem", "neutral")
    if "艾米莉亚" in (text or ""):   # v4.2.1 补 emt 分支（三人线无标签兜底原来漏她，与指令缺口同源）
        tail += expr_img("emt", "neutral")
    return tail


def detect_solo_who(inc_sys):
    """单人线说话人判定：底稿关键词计票（拉姆稿已做到蕾姆字样归零；雷姆稿蕾/雷字样密集）。"""
    t = inc_sys or ""
    return "rem" if (t.count("雷姆") + t.count("蕾姆")) > t.count("拉姆") else "ram"


# ==== v3.5.9 SOLO 短标记 + 台词库接线（底稿迁管理台五 tab 页；OWI 模型层只留标记防丢单人判定）====
SOLO_MARK_FILES = {
    "[SOLO_RAM]": "/root/work/cloud-config/prompt/solo_ram.txt",
    "[SOLO_REM]": "/root/work/cloud-config/prompt/solo_rem.txt",
    "[SOLO_EMT]": "/root/work/cloud-config/prompt/solo_emt.txt",
}
SOLO_MARK_WHO = {"[SOLO_RAM]": "ram", "[SOLO_REM]": "rem", "[SOLO_EMT]": "emt"}
SOLO_LINES_COLL = {"ram": "ram_dialogues", "rem": "rem_dialogues", "emt": "emilia_dialogues"}
SOLO_LINES_WHO = {"ram": "拉姆", "rem": "蕾姆", "emt": "艾米莉亚"}


def lines_block(user_text, who_key):
    """台词库接线（v3.5.9）：solo 时按角色查对应台词库语义 top3（≥0.55，who 过滤只取本角色线），
    叙事式注入当腔调佐料（佐料不当主菜/禁提资料/捞不到干净不带）；失败静默不卡对话。"""
    try:
        coll = SOLO_LINES_COLL.get(who_key)
        if not coll:
            return ""
        r = httpx.post(f"{QDRANT}/collections/{coll}/points/search", timeout=10, json={
            "vector": _vec_for(user_text), "limit": 3, "score_threshold": 0.55, "with_payload": True,
            "filter": {"must": [{"key": "who", "match": {"value": SOLO_LINES_WHO[who_key]}}]}})
        lines = []
        for h in (r.json().get("result") or []):
            t = str((h.get("payload") or {}).get("text") or "").strip()
            if t:
                lines.append("· " + t[:120])
        if not lines:
            return ""
        _log(f"[lines] {coll} 命中 {len(lines)} 条")
        return ("【原著台词参考】以下是这位角色的几句原著台词，只供把握说话的腔调与用词习惯，"
                "禁止在回复里提及或引用这份资料本身：\n" + "\n".join(lines))
    except Exception:
        return ""


EXPR_GROUP_DIR = "/root/work/expr_assets"  # 一词一组：正本仓库根（20261007）


def expr_img(who, emo):
    emo = (emo or "").strip().lower()
    if emo not in EXPR_EMOTIONS:
        emo = "neutral"
    # 20261007 emt 差分 28 张已出炉上柜，撤蕾姆占位（备份=tavern-bridge-cloud_bak-20261007-emtfix.py）
    label = {"ram": "拉姆", "rem": "蕾姆", "emt": "艾米莉亚"}.get(who, who)
    # v2.2 一词一组（20261007 用户令）：正本情绪文件夹有图=随机抽一张（随机文件名自带防缓存）；无组退回单图
    try:
        gdir = os.path.join(EXPR_GROUP_DIR, who, emo)
        cands = [f for f in os.listdir(gdir) if f.lower().endswith(".png")] if os.path.isdir(gdir) else []
    except Exception:
        cands = []
    if cands:
        return f"\n\n![{label} {emo}](/expr/{who}/{emo}/{random.choice(cands)})"
    return f"\n\n![{label} {emo}](/expr/{who}/{emo}.png)"


def expr_substitute(text, default_who=None):
    """表情标签→markdown 图（原位替换）；无主语标签用 default_who 兜底，再无则只剥不插。
    v4.3.0 多人场（default_who=None）同人首图定档：后续同角色标签只剥不插（双写病，见头部账）。"""
    seen = set()

    def _sub(m):
        who = _EXPR_WHO.get(m.group(1)) or default_who
        if not who:
            return ""
        if not default_who:   # v4.3.1 多人场=None 或 ""（三人线流式传空串）都去重
            if who in seen:
                return ""
            seen.add(who)
        return expr_img(who, m.group(2))
    def _img_sub(m):
        if not default_who:
            w = m.group(1)
            if w in seen:
                return ""
            seen.add(w)
        return m.group(0)
    out = EXPR_IMG_RE.sub(_img_sub, EXPR_TAG_RE.sub(_sub, text))   # v4.4.1 字面图同册去重（先标签后图片，共用 seen）
    return out


def expr_finish(text, default_who):
    """非流式/写回收口：标签换图；一个标签都没有→补 neutral 兜底（default_who 为空则不兜底）。"""
    out = expr_substitute(text or "", default_who)
    out += expr_fallback_tail(text or "", default_who)
    return out


class _ExprFilter:
    """流式表情标签过滤器：识别到完整标签→原位发图并剥标签；标签唯一合法起点=[[
    （扣留等完整匹配）；单个尾 [ 扣留等兄弟括号；其余普通文本整段放行。"""

    def __init__(self, default_who=None):
        self.buf = ""
        self.default_who = default_who
        self._seen = set()   # v4.3.0 多人场同人首图定档

    def feed(self, piece):
        self.buf += piece
        out = []
        while True:
            m = EXPR_TAG_RE.search(self.buf)
            m2 = EXPR_IMG_RE.search(self.buf)
            if m2 and (not m or m2.start() < m.start()):
                # v4.4.1 字面图（模型抄历史 markdown 形态）：多人场同角色首图定档，后续只剥
                out.append(self.buf[:m2.start()])
                w = m2.group(1)
                if not self.default_who:
                    if w in self._seen:
                        w = None
                    else:
                        self._seen.add(w)
                out.append(m2.group(0) if w else "")
                self.buf = self.buf[m2.end():]
                continue
            if m:
                out.append(self.buf[:m.start()])
                who = _EXPR_WHO.get(m.group(1)) or self.default_who
                if who and not self.default_who:   # v4.3.1 空串也算多人场，去重
                    if who in self._seen:
                        who = None   # v4.3.0 首图定档：重复只剥不插
                    else:
                        self._seen.add(who)
                if who:
                    out.append(expr_img(who, m.group(2)))
                self.buf = self.buf[m.end():]
                continue
            # v4.4.1 未闭合 "![" 扣留（图 markdown 跨块防截断；闭合判定="](" 后有 ")"）
            i2 = self.buf.rfind("![")
            idx = self.buf.find("[[")
            if i2 != -1 and (idx == -1 or i2 < idx):
                tail = self.buf[i2:]
                if not ("](" in tail and ")" in tail.split("](")[1]):
                    out.append(self.buf[:i2])
                    self.buf = self.buf[i2:]
                    break
            if idx != -1:   # 标签唯一合法起点=[[；单个尾 [ 扣留等兄弟括号
                out.append(self.buf[:idx])
                self.buf = self.buf[idx:]
            elif self.buf.endswith("["):
                out.append(self.buf[:-1])
                self.buf = "["
            else:
                out.append(self.buf)
                self.buf = ""
            break
        return "".join(out)

    def flush(self):
        """流结束：扣留区标签/字面图逐个处理到空（v4.4.1 循环化——旧版只处理首个、其后原样
        透传的暗病一并修掉），否则原样吐出。"""
        out = []
        while self.buf:
            m = EXPR_TAG_RE.search(self.buf)
            m2 = EXPR_IMG_RE.search(self.buf)
            if m2 and (not m or m2.start() < m.start()):
                out.append(self.buf[:m2.start()])
                w = m2.group(1)
                if not self.default_who:
                    if w in self._seen:
                        w = None
                    else:
                        self._seen.add(w)
                out.append(m2.group(0) if w else "")
                self.buf = self.buf[m2.end():]
                continue
            if m:
                out.append(self.buf[:m.start()])
                who = _EXPR_WHO.get(m.group(1)) or self.default_who
                if who and not self.default_who:   # v4.3.1 空串也算多人场，去重
                    if who in self._seen:
                        who = None
                    else:
                        self._seen.add(who)
                out.append(expr_img(who, m.group(2)) if who else "")
                self.buf = self.buf[m.end():]
                continue
            out.append(self.buf)
            self.buf = ""
        return "".join(out)


class _GenFilter:
    """v4.2.0 流式 <gen> 指令行过滤器：'<gen' 起扣留至 '</gen>' 后整段丢弃（令牌回复的指令行用户不可见）。
    捕获的 (角色名, tags) 存 self.hit 供流尾入队（决策12 只认第一处）；流末仍没等到完整标签=原样放行
    （降级可见，施工单 A3：禁为剥标签引重构）。姿势照抄 _ExprFilter 扣留区。"""

    _START = "<gen"

    def __init__(self):
        self.buf = ""
        self.hit = None

    def _capture(self, who, scene):
        if self.hit is None:   # 决策12：多行只认第一个
            self.hit = (who, scene)

    def feed(self, piece):
        self.buf += piece
        out = []
        while True:
            _p = _gen_parse(self.buf)   # v4.2.6 双式解析：畸形行也捕获
            if _p:
                out.append(self.buf[:_p[2]])
                self._capture(_p[0], _p[1])
                self.buf = self.buf[_p[3]:]
                continue
            idx = self.buf.find(self._START)
            if idx != -1:   # 起点已现、结束未到：头段放行，扣留区截到起点（不截=flush 二次吐头，干跑实锤）
                out.append(self.buf[:idx])
                self.buf = self.buf[idx:]
                break
            for k in (3, 2, 1):   # 尾部疑似半截起点（'<ge'/'<g'/'<'）扣留防跨块截断
                if self.buf.endswith(self._START[:k]):
                    out.append(self.buf[:-k])
                    self.buf = self.buf[-k:]
                    break
            else:
                out.append(self.buf)
                self.buf = ""
            break
        return "".join(out)

    def flush(self):
        """流结束：扣留区若憋着可解析标签→捕获剥除（v4.2.6 宽容式也算数）；不可解析=原样吐出可见化（杜绝静默吞文）。"""
        _p = _gen_parse(self.buf)
        if _p:
            self._capture(_p[0], _p[1])
            out = self.buf[:_p[2]] + self.buf[_p[3]:]
            self.buf = ""
            return out
        out, self.buf = self.buf, ""
        return out


# ==== v3.4.2 记忆闭环（v3.4.12：dialog_archive 存档已拆，OWI 服务端落库即可，桥不记第二本）====
SUMMARY_EVERY = 20


_VEC_CACHE = {}   # v4.2.9 同轮同文向量缓存：key=原文精确匹配，cap 32 超限丢最旧，仅进程内存不落盘（重启即空）
_VEC_CACHE_CAP = 32
_VEC_INFLIGHT = {}   # v4.2.9b single-flight：并发爆发同句只发一次席请求（注入族四路并行同刻起跑，防 3 路重复嵌同句挤占 CPU 席）
_VEC_LOCK = threading.Lock()


def _vec_for(text):
    """自家嵌入席向量；失败退化 FNV 种子伪向量（1024 非零，与真向量≈正交，
    检索层 score_threshold 会过滤掉它，但 scroll 类按 payload 读的通路不受影响）。
    v4.2.9 首查缓存：一轮内同一句 user 文本被 3~4 处召回各嵌一次（CPU 席 2.3s/次全在首字前），
    改第一处算完其余字典命中；FNV 伪向量不缓存（失败不钉死，下次照常重试真席）。
    v4.2.9b single-flight：四路并行同刻全 miss 时，只有一次真席请求，其余等事件拿缓存。"""
    hit = _VEC_CACHE.get(text)
    if hit is not None:
        return hit
    with _VEC_LOCK:
        ev = _VEC_INFLIGHT.get(text)
        owner = ev is None
        if owner:
            ev = threading.Event()
            _VEC_INFLIGHT[text] = ev
    if not owner:
        ev.wait(timeout=15)
        hit = _VEC_CACHE.get(text)
        if hit is not None:
            return hit
        # 书记员没成（超时/失败）→ 自己再试一把真席（罕见路径，行为同旧版单发）
    try:
        e = httpx.post(ZEMB, timeout=10,
                       headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                       json={"model": "qwen3-emb", "input": [text]})
        v = e.json()["data"][0]["embedding"]
        if v and len(v) == 1024:
            if len(_VEC_CACHE) >= _VEC_CACHE_CAP:
                _VEC_CACHE.pop(next(iter(_VEC_CACHE)))
            _VEC_CACHE[text] = v
            return v
    except Exception:
        pass
    finally:
        if owner:
            with _VEC_LOCK:
                _VEC_INFLIGHT.pop(text, None)
            ev.set()
    seed = 0x811c9dc5
    for ch in (text or "empty"):
        seed = ((seed ^ ord(ch)) * 0x01000193) & 0xFFFFFFFF
    v = []
    for _ in range(1024):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        v.append(((seed >> 7) & 0xFF) / 255.0 + 0.001)
    return v


def mem_write(session_id, role, text, pid):
    """写侧 A：单条消息入 chat_memory（id/ts=毫秒时间戳，payload 照 fetch_transcript 同款）。
    任何失败只记日志，绝不打断对话主路。"""
    try:
        httpx.put(f"{QDRANT}/collections/chat_memory/points?wait=false", timeout=15,
                  json={"points": [{"id": pid, "vector": _vec_for(text),
                        "payload": {"sessionId": session_id, "role": role, "text": text, "ts": pid}}]})
    except Exception as e:
        _log("chat_memory 写入失败: " + str(e)[:120])


def latest_summary_full():
    """读侧：chat_summary 里 ts 最大的一条叙事前情 → (ts, 正文)；旧档无 ts 不认，拿不到 (0, "")。
    v3.5.6 拆出 full 版：ts 供前情提要日期头（截至 X 月 X 日）。"""
    try:
        r = httpx.post(f"{QDRANT}/collections/chat_summary/points/scroll", timeout=15,
                       json={"limit": 100, "with_payload": True})
        best = None
        for p in r.json()["result"]["points"]:
            pl = p.get("payload") or {}
            ts = pl.get("ts")
            if isinstance(ts, (int, float)) and (best is None or ts > best[0]):
                best = (ts, (pl.get("summary") or "").strip())
        if best and best[1]:
            return best
    except Exception:
        pass
    return (0, "")


def latest_summary():
    """旧签名兼容（maybe_summarize 用）：只取正文。"""
    return latest_summary_full()[1]


def kb_memory_block(user):
    """v3.4.3 隐形召回：dual_dialogues top3 ≥0.55（v3.4.13 统一阈值）→ 叙事化回忆块。
    检索失败/不命中返回空串（伪向量天然低分同走此路），对话绝不因它受影响。"""
    try:
        q = httpx.post(f"{QDRANT}/collections/dual_dialogues/points/query", timeout=15,
                       json={"query": _vec_for(user), "limit": 3, "score_threshold": 0.55,
                             "with_payload": True})
        pts = [p for p in (q.json().get("result", {}).get("points") or [])
               if ((p.get("payload") or {}).get("text") or "").strip()]
        if not pts:
            return ""
        _rx()["recalls"].append({"source": "dual_dialogues", "hits": [
            {"score": round(p["score"], 3), "text": p["payload"]["text"].strip()[:200]} for p in pts]})
        hits = [p["payload"]["text"].strip() for p in pts]
        _log(f"[recall] dual_dialogues 命中 {len(hits)} 条（top {round(pts[0]['score'], 3)}）")
        return ("【若有似无的回忆】（往日相处的零碎片段，忽远忽近地飘回来；把这份熟悉化进此刻的语气"
                "和反应里就好，不要逐字复述，更不要提自己想起了什么资料）\n"
                + "\n".join("· " + t for t in hits))
    except Exception:
        return ""


def maybe_summarize(session_id):
    """每 SUMMARY_EVERY 轮：后台线程把上一段前情+近 20 轮浓缩成叙事梗概写 chat_summary。
    GLM low 档后台跑，不占对话时延；失败静默（下个 20 轮再试）。"""
    def _job():
        try:
            c = httpx.post(f"{QDRANT}/collections/chat_memory/points/count", timeout=15,
                           json={"exact": True, "filter": {"must": [
                               {"key": "sessionId", "match": {"value": session_id}}]}})
            n = c.json()["result"]["count"]
            SE = int(_P("summary_every"))
            if n == 0 or n % SE != 0:
                return
            prev = latest_summary()
            r = httpx.post(f"{QDRANT}/collections/chat_memory/points/scroll", timeout=15,
                           json={"limit": 1000, "with_payload": True,
                                 "filter": {"must": [{"key": "sessionId", "match": {"value": session_id}}]}})
            pts = r.json()["result"]["points"]
            pts.sort(key=lambda p: (p.get("payload") or {}).get("ts", 0))
            lines = [("主人" if (p.get("payload") or {}).get("role") == "user" else "姐妹")
                     + "：" + ((p.get("payload") or {}).get("text") or "") for p in pts[-SE:]]
            prompt = ("把下面的对话浓缩成第三人称叙事梗概，像给下一段对话准备的前情提纲"
                      "（「主人和拉姆蕾姆聊到……他提到……她们……」）。禁止清单、禁止分点、禁止书面腔，"
                      "保留人名、数字、承诺、未完话题。纯寒暄、重复问候、无信息交换的客套一律忽略，不计入梗概。"
                      "上一段前情里已经了结的旧账最多留一句带过，正在进行的承诺和未完话题必须保留。\n"
                      + (f"【上一段前情】\n{prev}\n\n" if prev else "")
                      + f"【最近对话】\n" + "\n".join(lines)
                      + "\n\n【硬性要求】只输出梗概正文，不要任何解释；用 8~12 个完整句子，"
                        "全文 300 字以内，绝不超过 500 字。")
            resp = httpx.post(ZHIPU, timeout=300,
                              headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                              json={"model": "glm-5.3-flash", "thinking": {"type": "enabled"},
                                    "reasoning_effort": "high", "max_tokens": 4096, "temperature": 0.3,
                                    "messages": [{"role": "user", "content": prompt}]})   # v4.0.0 针5 摘要钉死 GLM high
            text = (resp.json()["choices"][0]["message"].get("content") or "").strip()
            if not text:
                return
            if len(text) > 500:   # v4.1.5 字数保险丝：超 500 按句界裁（零成本不二次调用；句界异常=硬截）
                cut = text.rfind("。", 0, 500)
                text = text[:cut + 1] if cut >= 200 else text[:499] + "。"
                _log(f"摘要超 500 字已裁至 {len(text)} 字")
            pid = int(time.time() * 1000)
            httpx.put(f"{QDRANT}/collections/chat_summary/points?wait=true", timeout=15,
                      json={"points": [{"id": pid, "vector": [0, 0],
                            "payload": {"sessionId": session_id, "summary": text, "ts": pid,
                                        "source": "bridge-auto", "up_to": n}}]})
            _log(f"前情提要已更新（第 {n} 轮触发，{len(text)} 字）")
        except Exception as e:
            _log("摘要生成失败: " + str(e)[:150])
    threading.Thread(target=_job, daemon=True).start()


# ==== v3.5.6 可检索日志（Kindroid journal 同款+升级：语义召回替代关键词触发）+ 时间戳锚 ====
# 一条=一天；payload={date, weekday, text「X月X日 周X：正文≤300字」, ts=当日23:59}；id=YYYYMMDD。
# 触发=事件驱动（不做定时器：服务器桥无常驻定时基建，空转白烧）；失败静默绝不卡对话。
JOURNAL_COLL = "chat_journal"
JOURNAL_RECALL_MIN = 0.45   # 0927 实测定标：日总结文本长、余弦系统性偏低（实测带 0.43~0.56），0.55 全灭；日志=自家账本低污染，单列阈值（台词/回忆库 0.55 不动）
_journal_state = {"checked": 0.0, "dates": set(), "busy": False}


def _ensure_journal_coll():
    """懒创建（1024 维 Cosine 与嵌入席同维）；顺手装 ts 整数索引备用。"""
    try:
        if httpx.get(f"{QDRANT}/collections/{JOURNAL_COLL}", timeout=5).status_code == 200:
            return True
        c = httpx.put(f"{QDRANT}/collections/{JOURNAL_COLL}", timeout=15,
                      json={"vectors": {"size": 1024, "distance": "Cosine"}})
        if c.status_code not in (200, 201):
            return False
        try:
            httpx.put(f"{QDRANT}/collections/{JOURNAL_COLL}/index", timeout=15,
                      json={"field_name": "ts", "field_schema": "integer"})
        except Exception:
            pass
        return True
    except Exception:
        return False


def _journal_dates():
    """已记账日期集合（缓存 120s：触发检查不每条消息扫库；写账后 checked=0 立即失效）。"""
    if time.time() - _journal_state["checked"] < 120:
        return _journal_state["dates"]
    try:
        r = httpx.post(f"{QDRANT}/collections/{JOURNAL_COLL}/points/scroll", timeout=15,
                       json={"limit": 400, "with_payload": True})
        ds = {(p.get("payload") or {}).get("date") or ""
              for p in (r.json().get("result", {}).get("points") or [])}
        _journal_state.update(checked=time.time(), dates=ds)
        return ds
    except Exception:
        return _journal_state["dates"]


def _journal_weekday(d):
    return WEEK_CN[datetime.strptime(d, "%Y-%m-%d").weekday()]


def _norm_journal_text(raw, d):
    """日志正文规范：剥掉模型自带的日期头（可能写错日期），统一换成标准「X月X日 周X：」。"""
    t = re.sub(r"^\s*\d{1,2}\s*月\s*\d{1,2}\s*日\s*周[一二三四五六日天]\s*[：:]\s*", "",
               (raw or "").strip())
    return f"{int(d[5:7])}月{int(d[8:10])}日 {_journal_weekday(d)}：{t}"


def _journal_glm(prompt):
    """浓缩专用 GLM-low（与 maybe_summarize 同参）；包一层便于单元测 monkeypatch。"""
    resp = httpx.post(ZHIPU, timeout=300,
                      headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                      json={"model": "glm-5.3-flash", "thinking": {"type": "enabled"},
                            "reasoning_effort": "low", "max_tokens": 768, "temperature": 0.3,
                            "messages": [{"role": "user", "content": prompt}]})
    return (resp.json()["choices"][0]["message"].get("content") or "").strip()


def _condense_day(d, msgs):
    """一天的对话点（ts 升序）→ 带标准日期头的日志正文。"""
    lines = [("主人" if (p.get("role") == "user") else "姐妹") + "：" + (p.get("text") or "")
             for p in msgs]
    prompt = ("把下面这一天主人和姐妹的对话浓缩成一段当日日志：第三人称叙事，严格不超过 300 字，"
              "保留聊过的话题、情绪、未了结的事、承诺（人名/数字/关键原话尽量保留）。"
              f"第一行必须以「{_norm_journal_text('', d)}」这样的日期头开头，后面直接接正文。\n\n"
              + "\n".join(lines))
    return _norm_journal_text(_journal_glm(prompt), d)


def _journal_write_day(d, msgs):
    """写一天日志（幂等：同日 id 覆盖写）。返回日志正文。ts=当日 23:59:59（CN 时区）。"""
    text = _condense_day(d, msgs)
    if not text:
        return ""
    day0 = datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=CN_TZ).timestamp() * 1000
    httpx.put(f"{QDRANT}/collections/{JOURNAL_COLL}/points?wait=true", timeout=15,
              json={"points": [{"id": int(d.replace("-", "")), "vector": _vec_for(text),
                    "payload": {"date": d, "weekday": _journal_weekday(d), "text": text,
                                "ts": int(day0) + 86399000, "source": "bridge-journal"}}]})
    _journal_state["checked"] = 0.0
    _log(f"日志已记账 {d}（{len(text)} 字）")
    return text


def _scan_memory_by_day(today_s):
    """chat_memory 全量按天分组（CN 时区），只留今天之前的日子，组内按 ts 升序。"""
    r = httpx.post(f"{QDRANT}/collections/chat_memory/points/scroll", timeout=30,
                   json={"limit": 5000, "with_payload": True})
    by_day = {}
    for p in (r.json().get("result", {}).get("points") or []):
        pl = p.get("payload") or {}
        ts = pl.get("ts")
        if not isinstance(ts, (int, float)) or not (pl.get("text") or "").strip():
            continue
        d = datetime.fromtimestamp(ts / 1000, CN_TZ).strftime("%Y-%m-%d")
        if d >= today_s:
            continue
        by_day.setdefault(d, []).append(pl)
    for d in by_day:
        by_day[d].sort(key=lambda p: p["ts"])
    return by_day


def _journal_job():
    """后台补账：今天之前没日志的日子逐日浓缩（≥2 条消息才算一天；一次最多补 7 天）。"""
    try:
        if not _ensure_journal_coll():
            _log("日志补账跳过：chat_journal 建不了")
            return
        today_s = datetime.now(CN_TZ).strftime("%Y-%m-%d")
        done = _journal_dates()
        by_day = _scan_memory_by_day(today_s)
        days = [d for d in sorted(by_day) if d not in done and len(by_day[d]) >= 2][-7:]
        if not days:
            return
        _log(f"日志补账开始：{'/'.join(days)}")
        for d in days:
            try:
                _journal_write_day(d, by_day[d])
            except Exception as e:
                _log(f"日志 {d} 浓缩失败: " + str(e)[:150])
    except Exception as e:
        _log("日志补账失败: " + str(e)[:150])
    finally:
        _journal_state["busy"] = False


def maybe_journal():
    """v3.5.6 触发器（每轮写回后调用）：今天还没记过日志 → 开后台补账线程。
    busy 防双线程；缓存 120s 内不重复扫；任何失败静默。"""
    try:
        if _journal_state["busy"]:
            return
        if datetime.now(CN_TZ).strftime("%Y-%m-%d") in _journal_dates():
            return
        _journal_state["busy"] = True
        threading.Thread(target=_journal_job, daemon=True).start()
    except Exception:
        pass


def journal_block(user):
    """v3.5.6 往日日志召回：chat_journal 语义 top2 ≥0.45（JOURNAL_RECALL_MIN，0927 实测定标）。
    日期头让模型自然说出"昨天/上周三"；失败/不命中静默空串，绝不卡对话。"""
    try:
        q = httpx.post(f"{QDRANT}/collections/{JOURNAL_COLL}/points/query", timeout=15,
                       json={"query": _vec_for(user), "limit": 2, "score_threshold": JOURNAL_RECALL_MIN,
                             "with_payload": True})
        pts = [p for p in (q.json().get("result", {}).get("points") or [])
               if ((p.get("payload") or {}).get("text") or "").strip()]
        if not pts:
            return ""
        _rx()["recalls"].append({"source": "chat_journal", "hits": [
            {"score": round(p["score"], 3), "text": p["payload"]["text"].strip()[:200]} for p in pts]})
        lines = ["· " + p["payload"]["text"].strip() for p in pts]
        _log(f"[recall] chat_journal 命中 {len(lines)} 条")
        return ("【往日日志】（引用往事时可自然说出「昨天」「上周三」这样的时间）\n"
                + "\n".join(lines))
    except Exception:
        return ""


# v3.4.12：429 退避器已拆——配额制 API 限流=真没量，重试无意义（用户令）


def openai_response(content, model="remram-导演链", stream=False):
    body = {"id": "chatcmpl-remram", "object": "chat.completion",
            "created": int(time.time()), "model": model,
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": content}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
    if not stream:
        return json.dumps(body, ensure_ascii=False)
    chunks = []
    chunks.append("data: " + json.dumps({**body, "choices": [{"index": 0, "finish_reason": None,
                   "delta": {"role": "assistant", "content": ""}}]}, ensure_ascii=False) + "\n\n")
    chunks.append("data: " + json.dumps({**body, "choices": [{"index": 0, "finish_reason": None,
                   "delta": {"content": content}}]}, ensure_ascii=False) + "\n\n")
    chunks.append("data: " + json.dumps({**body, "choices": [{"index": 0, "finish_reason": "stop",
                   "delta": {}}]}, ensure_ascii=False) + "\n\n")
    chunks.append("data: [DONE]\n\n")
    return "".join(chunks)


def fetch_transcript(session_id, tail=None):
    tail = tail or int(_P("vision_tail"))
    """从 Qdrant chat_memory 抓最近对话拼台词稿。v3.4.12 对齐 20 轮（40 条，与纯净档视野一致）。
    v3.5.8.2 修账本病：scroll 无 order_by 时按 id 升序返回**最旧**100 条（id=毫秒 ts），
    库超 100 条后书记员看到的一直是旧账（0926 起入库全灭根因二）——改 order_by 服务端取最近 tail 条。"""
    try:
        r = httpx.post(f"{QDRANT}/collections/chat_memory/points/scroll",
                       json={"filter": {"must": [{"key": "sessionId", "match": {"value": session_id}}]},
                             "limit": tail, "with_payload": True,
                             "order_by": {"key": "ts", "direction": "desc"}}, timeout=30)
        pts = r.json()["result"]["points"]
        pts.reverse()   # 升序拼稿（旧→新）
        lines = []
        for p in pts:
            pl = p.get("payload") or {}
            who = "主人" if pl.get("role") == "user" else "姐妹"
            lines.append(f"{who}：{pl.get('text', '')}")
        return "\n".join(lines)
    except Exception:
        return ""


def fetch_history_messages(session_id, tail=None):
    tail = tail or int(_P("vision_tail"))
    """v3.5.0：chat_memory 全局一条线取最近 tail 条 → 正 role 消息（主人=user/姐妹=assistant）。
    v3.5.8.2 修账本病：同 fetch_transcript（order_by ts desc 服务端取最近，旧版拿的是最旧 100 条里的尾段）。"""
    try:
        r = httpx.post(f"{QDRANT}/collections/chat_memory/points/scroll",
                       json={"filter": {"must": [{"key": "sessionId", "match": {"value": session_id}}]},
                             "limit": tail, "with_payload": True,
                             "order_by": {"key": "ts", "direction": "desc"}}, timeout=30)
        pts = r.json()["result"]["points"]
        pts.reverse()   # 升序（旧→新）
        msgs = []
        for p in pts:
            pl = p.get("payload") or {}
            t = (pl.get("text") or "").strip()
            if t:
                msgs.append({"role": "user" if pl.get("role") == "user" else "assistant", "content": t})
        return msgs
    except Exception:
        return []


def kb_scene_block(user):
    """v3.5.0：场景库召回（remram_lines top3 ≥0.55）→ 原著台词参考块。失败静默空。"""
    try:
        q = httpx.post(f"{QDRANT}/collections/remram_lines/points/query", timeout=15,
                       json={"query": _vec_for(user), "limit": 3, "score_threshold": 0.55,
                             "with_payload": True})
        pts = [p for p in (q.json().get("result", {}).get("points") or [])
               if ((p.get("payload") or {}).get("text") or "").strip()]
        if not pts:
            return ""
        _rx()["recalls"].append({"source": "remram_lines", "hits": [
            {"score": round(p["score"], 3), "text": p["payload"]["text"].strip()[:200]} for p in pts]})
        hits = [p["payload"]["text"].strip() for p in pts]
        _log(f"[recall] remram_lines 命中 {len(hits)} 条（top {round(pts[0]['score'], 3)}）")
        return "【原著台词参考（可借用语气与内容，不必照抄）】\n" + "\n".join("· " + t for t in hits)
    except Exception:
        return ""


def palace_recall_block(query, vec=None):
    """v3.5.0：记忆宫召回（宫桥 v2 /recall 只读口）→ 记忆深处的片段块。失败静默空。
    v4.2.9b 可选 vec：桥侧把同句向量传过去，宫侧重打分免再嵌查询句（省 CPU 席一次 ≈1.8s/轮）。"""
    try:
        _body = {"query": query, "limit": 6}
        if vec:
            _body["query_vector"] = vec
        r = httpx.post(PALACE_RECALL, timeout=20, json=_body)
        items = (r.json().get("items") or [])
        items = [i for i in items if i.get("score") is None or float(i.get("score") or 0) >= 0.55]   # v3.7.1 分数过筛+标定线0.55（正例0.72/噪声带0.42-0.46，与酒馆统一）
        items = items[:3]
        hits = [str(i.get("text") or "").strip() for i in items if str(i.get("text") or "").strip()]
        if not hits:
            return ""
        _rx()["recalls"].append({"source": "记忆宫", "hits": [
            {"score": i.get("score"), "text": str(i.get("text") or "").strip()[:200]} for i in items if str(i.get("text") or "").strip()]})
        _log(f"[recall] 记忆宫命中 {len(hits)} 条")
        return ("【记忆深处的片段】（这些是主人生活中的真实往事，像想起老朋友的事一样自然带出；"
                "不要说教，禁止提「记忆库/资料/记录」这类字眼）\n" + "\n".join("· " + t for t in hits))
    except Exception:
        return ""


# ==== v4.4.5 想法账本（idea ledger）：用户结论的 decision journal（MVP=显式存+强命中注入+新旧取代） ====
IDEA_FILE = "/root/work/cloud-config/ideas_ledger.jsonl"   # jsonl 真源（人可读可备可 git；Qdrant 可由它重建）
IDEA_COLL = "ideas_ledger"
IDEA_RECALL_MIN = 0.60   # 强命中才注入（记忆库 0.55 起步；账本要强命中防新话题撞旧账）
IDEA_SUPERSEDE_MIN = 0.88   # 同题新结论自动取代旧条阈值（低于此=并存两条各管各的话题）
IDEA_LINE_RE = re.compile(r"<idea>\s*([^|]+?)\s*\|\s*([^|]+?)(?:\s*\|\s*([^|]*?))?(?:\s*\|\s*([^|]*?))?\s*</idea>", re.S)   # v4.4.6d 竖线字段式：后两段允许空（「留空但竖线保留」的尾裸竖线 q|c|r| 旧正则吃不下=整行解析失败实锤）
IDEA_LINE_ANY_RE = re.compile(r"<idea>.*?</idea>", re.S)   # 写回剥行宽容式（畸形行也不进 chat_memory）
_idea_state = {"checked": 0.0}

# v4.4.6b 存档意图检测（末位重申用）+ 指类标记语（来源判定用）
IDEA_STORE_INTENT_RE = re.compile(r"存想法|把这个结论记|记住这个结论|记住这个判断|记下这个结论|把这个想法记")
_IDEA_CAT_MARK_RE = re.compile(r"(?:分到|分在|归到|归入|归到|放到|存到|存进|算[作是]?\s*|类[别目]?\s*[：:]?\s*)([^\s，。；,;]{1,12})")
IDEA_STORE_REASSERT = ("【重申·存档】用户本轮明确要求存结论：回复最后一行必须输出 <idea>问题|结论|理由|分类</idea>"
                       "（四段英文竖线分隔；问题=照他原话里的问题写、别自己重新措辞——系统靠它对旧账，改写会失联；"
                       "分类=用户口述照写／没口述从〔股票/工作/学习/生活/关系〕挑一个／都不贴留空；"
                       "禁写「其他」）。这一行之后不再有任何内容。")


def _idea_anchor(bare):
    """v4.4.6d 匹配锚点=用户原话第一小节（剥存档口令前缀）——取代/召回都在「用户的词」空间里比对，
    不吃模型改写 q 的失联亏（1024 实锤：模型把打板题改写成工资日题，q 向量对不上取代全断）。
    v4.4.6e 剥离修正：类目子句必须带「分到/归到…」标记词才剥——裸 [^，]{0,10} 贪婪段会把问题本体前十字吞掉
    （e2 实锤 anchor 只剩「题」）。"""
    t = re.sub(r"^\s*(?:帮我把这个结论存进想法账本|把这个结论存进想法账本|把这个结论存|存想法|帮我记住|记住这个结论|记住这个判断|记下这个结论|把这个想法记[下来]*)[，,：:]?\s*"
               r"(?:(?:分到|分在|归到|归入|放到|存到|存进)[^\s，。；,;：:]{0,8}[，,：:]?\s*)?"
               r"(?:问题是我?|问题是|关于)?\s*",
               "", (bare or "").strip())
    t = re.split(r"[，。！？,!?]", t, 1)[0].strip()
    return t[:200]

# v4.4.6 分类闭集：稳定 ID+显示名+口述别名，住 ideas_categories.json（显示名可改不动历史；类别退役=从表摘除留档不物理删）
IDEA_CATS_FILE = "/root/work/cloud-config/ideas_categories.json"
IDEA_CATS_DEFAULT = [
    {"id": "stock", "name": "股票", "aliases": ["炒股", "股市", "a股", "投资", "理财", "交易", "投机"]},
    {"id": "work", "name": "工作", "aliases": ["职场", "上班", "同事", "领导", "老板", "项目"]},
    {"id": "study", "name": "学习", "aliases": ["英语", "考试", "读书", "技能", "自学", "刷题"]},
    {"id": "life", "name": "生活", "aliases": ["健康", "作息", "饮食", "运动", "花钱", "存钱", "习惯"]},
    {"id": "relation", "name": "关系", "aliases": ["家庭", "家人", "感情", "朋友", "恋爱", "亲情", "人际"]},
    {"id": "other", "name": "其他", "aliases": ["杂项", "杂"]},
]


def _idea_cats():
    try:
        return json.load(open(IDEA_CATS_FILE, encoding="utf-8"))["cats"]
    except Exception:
        return IDEA_CATS_DEFAULT


def _idea_cat_resolve(spoken):
    """v4.4.6 口述词→稳定 id（别名表全匹配，含「其他」=用户专属）；不在闭集=None（未分类，绝不发明）。"""
    if not spoken:
        return None
    s = str(spoken).strip().lower()
    if not s:
        return None
    for c in _idea_cats():
        if s == c["id"].lower() or s == c["name"].lower() or s in [str(a).lower() for a in c.get("aliases", [])]:
            return c["id"]
    return None


def _idea_cat_belongs(cat_id, user_text):
    """v4.4.6b 来源判定：类目词须跟在「分到/归到/算…」类指类标记语后才算用户口述——
    裸出现在问题文本里不算（实测翻车：问题含「学英语」撞 study 别名「英语」被误标 user）。"""
    if not cat_id or not user_text:
        return False
    names = []
    for c in _idea_cats():
        if c["id"] == cat_id:
            names = [c["name"]] + [str(a) for a in c.get("aliases", [])]
            break
    for m in _IDEA_CAT_MARK_RE.finditer(user_text):
        seg = m.group(1)
        for nm in names:
            if nm in seg or seg in nm:
                return True
    return False

IDEA_SKILL_BLOCK = (
    "【想法账本·存档通道】仅当用户明确要求保存结论时使用（如「存想法」「把这个结论记下来」「记住这个判断」）："
    "在回复的最后一行输出一行存档指令，格式严格：<idea>问题|结论|一句话理由|分类</idea>（四段用英文竖线|分隔："
    "问题=他在琢磨的那个问题的一句话概括（照他原话写、别自己重新措辞——系统靠它对旧账，改写会失联）；结论=他得出的判断；理由=当时最关键的依据，没有可留空但竖线保留；"
    "分类=他口述的类目就照他的写（如「分到股票」→写 股票），没口述就从〔股票/工作/学习/生活/关系〕五类里挑"
    "最贴的一个——股票=证券交易与资金决策；工作=职场任务、同事、上级；学习=语言技能考试自学；"
    "生活=健康作息饮食开销习惯；关系=家人朋友感情人际。拿不准也挑最接近的一类，只有完全不沾边才留空"
    "（竖线保留）。绝不写「其他」——那是用户本人专属词，你没资格替他定杂项。"
    "这一行会被系统剥掉、用户看不见。用户没有明确说存就绝不输出；回复正文任何位置不许出现 <idea 字样。")


def _idea_parse(text):
    """v4.4.5 解析 <idea> 行（问题|结论|理由|分类 四段，理由/分类可空）。返回 (start, (q,c,r,cat), end)；无行=None。"""
    m = IDEA_LINE_RE.search(text)
    if m:
        return m.start(), (m.group(1), m.group(2), m.group(3) or "", m.group(4)), m.end()
    return None


def _ensure_idea_coll():
    """懒创建（1024 维 Cosine 与嵌入席同维；照 _ensure_journal_coll 家法，一小时一查）。"""
    if time.time() - _idea_state["checked"] < 3600:
        return
    _idea_state["checked"] = time.time()
    try:
        httpx.put(f"{QDRANT}/collections/{IDEA_COLL}", timeout=15,
                  json={"vectors": {"size": 1024, "distance": "Cosine"}})
    except Exception:
        pass


def idea_store(q, c, r="", cat=None, bare=""):
    """v4.4.5 显式存档入口（MVP 只此一路；自动捕获/候选池=三期）。jsonl 真源+Qdrant 镜像双写；
    同题≥IDEA_SUPERSEDE_MIN → 旧条翻 superseded（不删）、新条记 supersedes 链与 versions 计数。
    v4.4.6 分类：口述（bare 命中别名）>模型五类挑>取代继承>未分类；「其他」仅用户口述可落。
    全程 fail-open 绝不卡对话；返回新 id。"""
    q, c, r = (q or "").strip()[:200], (c or "").strip()[:800], (r or "").strip()[:300]
    cat = (cat or "").strip()[:32]
    if not q or not c:
        _log("[ideas] 字段缺失不入库")
        return None
    _ensure_idea_coll()
    # v4.4.6c 防毒入库：FNV 伪向量签名=全非负分量（真 qwen 向量 1024 维必有约半负分量）；
    # 嵌入席冷窗/僵死超时会静默退化伪向量（1024 实锤：A 案伪向量入库→同题取代漏触发+伪对伪 0.75 假召回）。
    # 伪向量不缓存=重试即真请求；重试仍伪=弃存档留日志（用户可见失败好过静默毒库）。
    vec = _vec_for(_idea_anchor(bare) or q)   # v4.4.6d 锚点向量=用户原话第一小节（q=模型展示名只给人看）
    if min(vec) >= 0:
        time.sleep(3)
        vec = _vec_for(_idea_anchor(bare) or q)
    if min(vec) >= 0:
        _log("[ideas] 嵌入席超时（伪向量签名），本轮不存档防毒入库——稍等片刻再说一次存想法")
        return None
    # v4.4.6 分类三判：解析→「其他」需用户口述背书→来源归属
    _cat = _idea_cat_resolve(cat)
    if _cat == "other" and not _idea_cat_belongs("other", bare):
        _cat = None   # 模型越权写「其他」=作废落未分类（其他=用户专属词）
    if _cat:
        _cat_src = "user" if _idea_cat_belongs(_cat, bare) else "model"
    else:
        _cat, _cat_src = None, None
    vec = _vec_for(q)   # v4.4.5b 向量=问题单独嵌入（首版 q+c 拼接向量实测翻车：两次结论措辞不同把同题相似度拉到 0.88 下取代不触发；且用户反刍的话本就更像问题不像结论）
    pid = int(time.time() * 1000)
    sup, versions = [], 1
    try:
        dup = httpx.post(f"{QDRANT}/collections/{IDEA_COLL}/points/query", timeout=15,
                         json={"query": vec, "limit": 1, "score_threshold": IDEA_SUPERSEDE_MIN,
                               "with_payload": True,
                               "filter": {"must": [{"key": "status", "match": {"value": "active"}}]}})
        pts = dup.json().get("result", {}).get("points") or []
        if pts:
            old = pts[0]
            old_pl = old.get("payload") or {}
            sup = [old["id"]]
            versions = int(old_pl.get("versions") or 1) + 1
            if _cat is None and old_pl.get("cat") not in (None, "", "other"):
                _cat, _cat_src = old_pl.get("cat"), "inherited"   # 同题默认同类：口述/模型都没给→继承旧实质类目
            httpx.post(f"{QDRANT}/collections/{IDEA_COLL}/points/payload?wait=true", timeout=15,
                       json={"payload": {"status": "superseded", "superseded_by": pid},
                             "points": [old["id"]]})
            _log(f"[ideas] 旧结论 {old['id']} 被取代（score {round(old['score'], 3)}，第 {versions} 版）")
            try:   # v4.4.5b 取代事件落 jsonl（真源完整性：将来从 jsonl 重建 Qdrant 不丢状态翻转）
                with open(IDEA_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"op": "supersede", "id": old["id"], "by": pid, "ts": pid},
                                       ensure_ascii=False) + "\n")
            except Exception:
                pass
    except Exception as e:
        _log("[ideas] 取代检查失败(不阻断入库): " + str(e)[:120])
    entry = {"id": pid, "q": q, "c": c, "r": r, "cat": _cat, "cat_source": _cat_src,
             "anchor": (_idea_anchor(bare) or q)[:200],
             "date": time.strftime("%Y-%m-%d"),
             "status": "active", "supersedes": sup, "superseded_by": None, "versions": versions,
             "source": "user_explicit", "ts": pid}
    try:
        httpx.put(f"{QDRANT}/collections/{IDEA_COLL}/points?wait=true", timeout=15,
                  json={"points": [{"id": pid, "vector": vec, "payload": entry}]})
    except Exception as e:
        _log("[ideas] Qdrant 写入失败: " + str(e)[:120])
    try:
        with open(IDEA_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        _log("[ideas] jsonl 追加失败: " + str(e)[:120])
    _log(f"[ideas] 已存档 #{pid}「{q[:40]}」cat={_cat or '未分类'}/{_cat_src or '-'}")
    return pid


def ideas_recall_block(user):
    """v4.4.5 每轮轻检索：用户消息 vs 账本 active 条目 top1，强命中（≥IDEA_RECALL_MIN）→ 复述提醒块。
    弱命中/空账本/检索失败=空串（fail-open，伪向量天然低分同走此路）。
    v4.4.6c 伪向量守卫：查询向量是 FNV 伪签名（全非负）直接跳过——伪对伪会出 ~0.75 假命中（1024 实锤）。"""
    try:
        v = _vec_for(user)
        if min(v) >= 0:
            return ""
        q = httpx.post(f"{QDRANT}/collections/{IDEA_COLL}/points/query", timeout=15,
                       json={"query": v, "limit": 1, "score_threshold": IDEA_RECALL_MIN,
                             "with_payload": True,
                             "filter": {"must": [{"key": "status", "match": {"value": "active"}}]}})
        pts = q.json().get("result", {}).get("points") or []
        if not pts:
            return ""
        p = pts[0]
        pl = p.get("payload") or {}
        if not ((pl.get("q") or "").strip() and (pl.get("c") or "").strip()):
            return ""
        _rx()["recalls"].append({"source": IDEA_COLL, "hits": [
            {"score": round(p["score"], 3), "text": f"{pl['q']} → {pl['c']}"[:200]}]})
        old_n = max(0, int(pl.get("versions") or 1) - 1)
        old_note = f"（另有 {old_n} 条更早结论已被这条取代，用户问起演变史才展开）" if old_n else ""
        _log(f"[ideas] 召回命中 {round(p['score'], 3)}「{(pl.get('q') or '')[:40]}」")
        return ("【想法账本（用户本人以前得出的结论，历史记录可能过时）】"
                f"用户在 {pl.get('date', '?')} 想过「{pl['q']}」，当时的结论：{pl['c']}"
                + (f"（理由：{pl['r']}）" if pl.get("r") else "")
                + f"{old_note}\n"
                "使用规则：在贴题的时机用一句话自然提给他（例：「这个你想过的，当时结论是……"
                "这次有新情况吗，还是维持原判？」）；不要生硬转述、不要当作当前事实、"
                "未经他确认不要替他改判；他若给出不同的新结论并要存，走存档通道。")
    except Exception:
        return ""


class _IdeaFilter:
    """v4.4.5 流式 <idea> 指令行过滤器：姿势照抄 _GenFilter（'<idea' 起扣留至 '</idea>' 整段丢弃，
    存档指令行用户不可见）。捕获 (问题, 结论, 理由) 存 self.hit 供流尾入库（只认第一处）；
    流末没等到完整标签=原样放行可见化（同 gen 哲学：禁静默吞文）。"""

    _START = "<idea"

    def __init__(self):
        self.buf = ""
        self.hit = None

    def feed(self, piece):
        self.buf += piece
        out = []
        while True:
            _p = _idea_parse(self.buf)
            if _p:
                out.append(self.buf[:_p[0]])
                if self.hit is None:
                    self.hit = _p[1]
                self.buf = self.buf[_p[2]:]
                continue
            idx = self.buf.find(self._START)
            if idx != -1:
                out.append(self.buf[:idx])
                self.buf = self.buf[idx:]
                break
            for k in (5, 4, 3, 2, 1):   # 尾部疑似半截起点扣留防跨块截断
                if self.buf.endswith(self._START[:k]):
                    out.append(self.buf[:-k])
                    self.buf = self.buf[-k:]
                    break
            else:
                out.append(self.buf)
                self.buf = ""
            break
        return "".join(out)

    def flush(self):
        _p = _idea_parse(self.buf)
        if _p:
            if self.hit is None:
                self.hit = _p[1]
            out = self.buf[:_p[0]] + self.buf[_p[2]:]
            self.buf = ""
            return out
        out, self.buf = self.buf, ""
        return out


def _recall_family(bare, slots):
    """v4.2.9 注入族并行器（首字三刀之三）：召回全是 IO 等待型（嵌入席/Qdrant/宫桥），
    串行时代四路≈向量2.3s×3+宫13.5s 全在首字前；并行后总耗时=最慢一路。
    slots=[(名字, callable或None)]，None=该路跳过（solo 守卫语义）；结果按传入序原样返回，
    _add_inj 注入顺序与旧串行版完全一致；各召回块自带 fail-open，谁炸谁空块，绝不卡对话。
    工人线程挂主线程 _RX 小票账本共享（threading.local 每线程一本，不带过去=召回命中从小票蒸发）。"""
    import concurrent.futures
    t0 = time.time()
    live = [(nm, fn) for nm, fn in slots if fn is not None]
    main_rx = _rx()

    def _wrap(fn):
        def _run():
            _RX.data = main_rx   # 工人线程视角的 thread-local 指到主线程账本（dict 共享，append GIL 安全）
            return fn()
        return _run

    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {nm: ex.submit(_wrap(fn)) for nm, fn in live}
        for nm, _fn in live:
            try:
                out.append((nm, futs[nm].result()))
            except Exception:
                out.append((nm, ""))
    _ms = int((time.time() - t0) * 1000)
    try:
        _log("[precall] 注入族并行 %d路 耗时%dms %s" % (
            len(live), _ms, " ".join(f"{nm}={len(b)}字" for nm, b in out)))
    except Exception:
        pass
    return out


def zhipu_stream_relay(self, messages, model="remram-快聊", max_tokens=8192, temperature=_P('reply_temperature'), reasoning="low",
                       upstream=None, glm_params=True, expr_who=None, tail_supplier=None, model_name=None, no_think=False, gen_filter=None, idea_filter=None):
    """真流式：上游 SSE → OpenAI chunk SSE 直转。返回完整文本供日志。
    v3.4.10：upstream=(url,key) 可指魔搭；glm_params=False 时按魔搭裸 OpenAI 参数发、
    429 只打一发不退避（魔搭纪律：防封号不重试）。
    v4.0.0：model_name 供本地脑等非 GLM 上游覆盖模型名（默认 MS_MODEL 兼容旧行为）。
    v4.2.0：gen_filter=_GenFilter 实例（None=关）链入过滤通路，<gen> 指令行流中剥除。"""
    url, key = upstream if upstream else (ZHIPU, ZKEY)
    _free_limit = GLMFREE_LIMIT_MSG if (no_think and not glm_params) else MS_LIMIT_MSG
    dead_msg = QUOTA_DEAD_MSG if glm_params else _free_limit
    limit_msg = RATE_LIMIT_MSG if glm_params else _free_limit
    self.send_response(200)
    self.send_header("Content-Type", "text/event-stream; charset=utf-8")
    self.send_header("Cache-Control", "no-cache")
    self.end_headers()
    chunk = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
             "model": model, "choices": [{"index": 0, "finish_reason": None, "delta": {"role": "assistant", "content": ""}}]}
    self.wfile.write(b"data: " + json.dumps(chunk, ensure_ascii=False).encode("utf-8") + b"\n\n")
    self.wfile.flush()
    full = []
    exf = _ExprFilter(expr_who) if expr_who is not None else None   # v3.5.8 表情过滤器（None=关）
    payload = {"max_tokens": max_tokens, "temperature": temperature, "stream": True, "messages": messages}
    if glm_params:
        payload.update({"model": "glm-5.3-flash", "thinking": {"type": "enabled"}, "reasoning_effort": reasoning,
                        "stream_options": {"include_usage": True}})   # v3.8.1 token 计量：末块带 usage
    else:
        payload.update({"model": model_name or MS_MODEL})   # v4.0.0 本地脑透传席名
        if no_think:
            payload["thinking"] = {"type": "disabled"}   # v4.1.4 glmfree 档关思维链（4.7-flash 默认思考，娱乐档要快）
        if url == MS_URL and reasoning:   # v4.3.1 ds 档位补线：流式此前漏带 reasoning_effort（三人线思考单薄真凶；探针同题 max 思维链 1382 字 vs 裸 306 字）
            payload["reasoning_effort"] = reasoning
        if url in (MS_URL, ZHIPU):   # v4.1.8 token 计量：魔搭/智谱 OpenAI 兼容口末块带 usage（魔搭 1018 实测 5token 探针过；解析循环 v3.8.1 本就通吃；local/foreign 未验不碰）
            payload["stream_options"] = {"include_usage": True}
    # v3.4.12 用户令：429 不退避不重试（配额制限流=真没量），一发直说限额
    cm = httpx.stream("POST", url, timeout=300,
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                      json=payload)
    r = cm.__enter__()
    if r.status_code == 429:
        quota_dead = False
        try:
            quota_dead = _quota_dead(r.read().decode("utf-8", "replace"))
        except Exception:
            pass
        r.close()
        if url == FOREIGN_UPSTREAM:
            _FOREIGN_429["ts"] = time.time()   # v4.1.3 限额熔断：冷却期内 cli 档直走书生
        msg = dead_msg if quota_dead else limit_msg
        _log(f"上游 429（{'额度干涸' if quota_dead else '限流'}），不重试直说限额")
        full.append(msg)
        ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
              "choices": [{"index": 0, "finish_reason": None, "delta": {"content": msg}}]}
        self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
        self.wfile.flush()
        return "".join(full)
    if r.status_code != 200:
        _log(f"上游非 200（{r.status_code}），流式直说限额")
        try:
            r.close()
        except Exception:
            pass
        ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
              "choices": [{"index": 0, "finish_reason": None, "delta": {"content": limit_msg}}]}
        try:
            self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except Exception:
            pass
        return limit_msg
    try:
        for line in r.iter_lines():
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                j = json.loads(data)
            except Exception:
                continue
            if j.get("usage"):   # v3.8.1 token 计量：末块 usage（include_usage）
                _u = j["usage"]
                _rx()["usage"] = {"model": j.get("model", ""),   # v3.8.2 防偷家
                                  "prompt": _u.get("prompt_tokens", 0),
                                  "completion": _u.get("completion_tokens", 0),
                                  "total": _u.get("total_tokens", 0),
                                  "cached": (_u.get("prompt_tokens_details") or {}).get("cached_tokens", 0),   # v3.8.2
                                  "reasoning": (_u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)}
            delta = ((j.get("choices") or [{}])[0].get("delta") or {})
            # ==== v3.4.9 思维链增量照发：纯浄档思考期不再静默 ====
            rc = delta.get("reasoning_content") or ""
            if rc:
                ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
                      "choices": [{"index": 0, "finish_reason": None, "delta": {"reasoning_content": rc}}]}
                try:
                    self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
                    self.wfile.flush()
                except Exception:
                    break
            piece = delta.get("content") or ""
            if piece:
                if "t_first" not in _rx():   # v3.7.4 首字埋点（真实 content，思维链/限额话不算）
                    _rx()["t_first"] = time.time()
                full.append(piece)
                out_txt = exf.feed(piece) if exf else piece   # v3.5.8 标签剥除+原位换图
                if gen_filter is not None and out_txt:
                    out_txt = gen_filter.feed(out_txt)   # v4.2.0 <gen> 指令行剥除
                if idea_filter is not None and out_txt:
                    out_txt = idea_filter.feed(out_txt)   # v4.4.5 <idea> 存档指令行剥除
                if out_txt:
                    ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
                          "choices": [{"index": 0, "finish_reason": None, "delta": {"content": out_txt}}]}
                    try:
                        self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
                        self.wfile.flush()
                    except Exception:
                        break
    finally:
        try:
            r.close()
        except Exception:
            pass
    raw = "".join(full)
    if exf is not None:
        tail = exf.flush()   # v3.5.8 扣留区放行
        if gen_filter is not None and tail:
            tail = gen_filter.feed(tail)   # v4.2.0 扣留区放行段同样过 <gen> 过滤器
        if idea_filter is not None and tail:
            tail = idea_filter.feed(tail)   # v4.4.5 同过 <idea> 过滤器
        if tail:
            try:
                ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
                      "choices": [{"index": 0, "finish_reason": None, "delta": {"content": tail}}]}
                self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
                self.wfile.flush()
            except Exception:
                pass
        _tail = expr_fallback_tail(raw, exf.default_who) if exf else ""   # v3.5.8.1 统一兜底
        if _tail:
            try:
                ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
                      "choices": [{"index": 0, "finish_reason": None, "delta": {"content": _tail}}]}
                self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
                self.wfile.flush()
            except Exception:
                pass
    if gen_filter is not None:
        _gtail = gen_filter.flush()   # v4.2.6 流末放行扣留区：可解析=已捕获剥空；不可解析残串可见化，杜绝静默吞文（1019 UI 无感挂案）
        if _gtail:
            try:
                ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
                      "choices": [{"index": 0, "finish_reason": None, "delta": {"content": _gtail}}]}
                self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
                self.wfile.flush()
            except Exception:
                pass
    if idea_filter is not None:
        _itail = idea_filter.flush()   # v4.4.5 流末放行扣留区（同 gen 哲学：可解析=剥空；残串可见化）
        if _itail:
            try:
                ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
                      "choices": [{"index": 0, "finish_reason": None, "delta": {"content": _itail}}]}
                self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
                self.wfile.flush()
            except Exception:
                pass
    if tail_supplier is not None:
        try:
            _tail_md = tail_supplier()   # v3.7.8 自拍/风景：流尾等图（≤150s）补发 markdown
            if _tail_md:
                ch = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
                      "choices": [{"index": 0, "finish_reason": None, "delta": {"content": "\n\n" + _tail_md}}]}
                self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
                self.wfile.flush()
        except Exception:
            pass
    try:
        end = {"id": "chatcmpl-remram-fast", "object": "chat.completion.chunk",
               "choices": [{"index": 0, "finish_reason": "stop", "delta": {}}]}
        self.wfile.write(b"data: " + json.dumps(end).encode("utf-8") + b"\n\n")
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
    except Exception:
        pass
    if exf is None:
        return raw
    return expr_finish(raw, exf.default_who)   # v3.5.8 写回文本与屏显一致（标签已换图）


def _rotate_log(path, max_bytes=10 * 1024 * 1024):
    """10MB 轮转：超限把现役日志改名 .old，下轮写自动新建（v3.5.0 补装，防 NameError 断写回链）。"""
    try:
        if os.path.exists(path) and os.path.getsize(path) > max_bytes:
            os.replace(path, path + ".old")
    except Exception:
        pass


# ==== v3.5.7 双人接力（姐妹轮转；v3.7.0 改名时本常量漏改致入口静默失效，v3.7.2 对齐）====
DUET_BRAIN = "酒馆双人接力"
DUET_RAM_FILE = "/root/work/cloud-config/prompt/duet_ram.txt"
DUET_REM_FILE = "/root/work/cloud-config/prompt/duet_rem.txt"

DUET_RAM_DIRECTIVE = ("【双人同台·本轮你是拉姆】你和蕾姆一起陪主人聊天，一人一轮。这一轮只准出现拉姆自己的台词与动作；"
                      "蕾姆接下来说什么由她自己决定，禁止代她开口、禁止描写她的动作神态。说完就收，把话头让出去。")
DUET_REM_DIRECTIVE = ("【双人同台·本轮你是蕾姆】你和姐姐拉姆一起陪主人聊天，一人一轮。这一轮只准出现蕾姆自己的台词与动作；"
                      "禁止代拉姆开口、禁止描写她的动作神态。你在真的接拉姆刚说的那句话——回应它、拆它或补它，"
                      "但不要换个说法重复她说过的话。说完就收，把话头还给主人。")
DUET_REM_TURN = ("【轮到你·蕾姆】拉姆说完了。现在接她的话——针对她刚说的内容给出你自己的台词与动作，"
                 "只说你自己的，不要替拉姆补充。")
DUET_RAM_REASSERT = ("【重申·本轮只有拉姆】接下来的回复只准出现拉姆自己的台词与动作，一段说完就收；"
                     "蕾姆这一轮完全不出场：禁止代她说话、禁止描写她的动作神态、禁止输出 [[蕾姆表情:…]] 标签。")

# ==== v3.7.0 酒馆三人（一次生成三段）====
TRIO_BRAIN = "酒馆三人"
TRIO_FILE = "/root/work/cloud-config/prompt/trio_prompt.txt"


def _load_trio_draft():
    """三人底稿现读；缺失/空=报错给用户，不静默降级。"""
    txt = open(TRIO_FILE, encoding="utf-8").read().strip()
    if not txt:
        raise RuntimeError("trio 底稿文件为空")
    return txt


def _load_duet_drafts():
    """轮转底稿（现读即改即生效）；文件缺失/空=报错给用户，不静默降级成单人。"""
    ram = open(DUET_RAM_FILE, encoding="utf-8").read().strip()
    rem = open(DUET_REM_FILE, encoding="utf-8").read().strip()
    if not ram or not rem:
        raise RuntimeError("duet 底稿文件为空")
    return ram, rem


def _glm_once(messages, max_tokens=2048, effort="low"):
    """双人同台专用单发（非流式路径用）；429 一发定胜负。返回 (text, err_msg)。"""
    try:
        r = httpx.post(ZHIPU, timeout=300,
                       headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                       json={"model": "glm-5.3-flash", "thinking": {"type": "enabled"},
                             "reasoning_effort": effort, "max_tokens": max_tokens,
                             "temperature": _P("reply_temperature"), "messages": messages})
        if r.status_code == 429:
            return "", (QUOTA_DEAD_MSG if _quota_dead(r.text) else RATE_LIMIT_MSG)
        r.raise_for_status()
        return (r.json()["choices"][0]["message"].get("content") or "").strip(), ""
    except Exception as e:
        _log("duet 调用失败: " + str(e)[:150])
        return "", RATE_LIMIT_MSG


def _ds_once(messages, max_tokens=8192):
    """魔搭 DS 单发（v3.5.9 总闸 ds 档：总入口非流式/双人同台伪流共用）；429 一发定胜负。返回 (text, err)。"""
    return _up_once(messages, max_tokens=max_tokens, url=MS_URL, key=MSKEY, model_name=MS_MODEL)


def _up_once(messages, max_tokens=8192, url=None, key=None, model_name=None, usage_note=False, no_think=False, effort=None):
    """v4.0.0 通用非 GLM 单发（ds/local 共用骨架）：429 一发定胜负；usage_note=True 时抄响应 usage
    （本地脑透传 llama-swap 真席名进小票）。返回 (text, err)。"""
    try:
        _body = {"model": model_name or MS_MODEL, "max_tokens": max_tokens,
                 "temperature": _P("reply_temperature"), "messages": messages}
        if no_think:
            _body["thinking"] = {"type": "disabled"}   # v4.1.4 glmfree 档关思维链
        if effort:
            _body["reasoning_effort"] = effort   # v4.1.6 ds 思考档位（low/high/max）
        r = httpx.post(url or MS_URL, timeout=300,
                       headers={"Authorization": f"Bearer {key if key is not None else MSKEY}", "Content-Type": "application/json"},
                       json=_body)
        if r.status_code == 429:
            if (url or MS_URL) == FOREIGN_UPSTREAM:
                _FOREIGN_429["ts"] = time.time()   # v4.1.3 限额熔断
            return "", (GLMFREE_LIMIT_MSG if no_think else MS_LIMIT_MSG)
        r.raise_for_status()
        _j = r.json()
        if usage_note:
            _usage_note(_j)   # v4.0.0：usage.model=上游真名（llama-swap 席名/GLM 名），四脑点名验收靠它
        return (_j["choices"][0]["message"].get("content") or "").strip(), ""
    except Exception as e:
        _log(f"{model_name or '上游'} 调用失败: " + str(e)[:150])
        return "", MS_LIMIT_MSG


# ==== v4.4.0 语音决议器（B 方案）：锚点账本 + 薄查表，只查不猜 ====
VOICE_SHELL_URL = "http://10.14.14.2:9234/v1/audio/speech"
VOICE_ANCHOR_RE = re.compile(r"(拉姆|[蕾雷]姆|艾米莉亚|艾米|emilia|ram|rem)\s*[:：]", re.IGNORECASE)
VOICE_WHO = {"拉姆": "ram", "ram": "ram", "蕾姆": "rem", "雷姆": "rem", "rem": "rem",
             "艾米莉亚": "emt", "艾米": "emt", "emilia": "emt"}
_VOICE_WS_RE = re.compile(r"\s+")
_VOICE_LEDGER = []          # 滚动账本：[{norm, spans, ts}]，留最近 20 条
_VOICE_LEDGER_MAX = 20


def _voice_norm(s):
    """规整=剥全部空白（OWI 洗文本最常见的是换行/空格差异，中文剥空白无损）。"""
    return _VOICE_WS_RE.sub("", s or "")


def _voice_ledger_put(text):
    """转播咽喉处记账：规整全文 + 锚点位置图（位置按规整坐标算，查表才对得上碎片）。
    双变体：norm=原文规整；norm2=再剥 markdown 图（OWI 洗文本会动图 alt，贴图碎片
    对 norm 失配时对 norm2 命中——酒馆回复段段带图，这不是边角是主路）。"""
    try:
        t = text or ""
        if not t.strip():
            return

        def _build(raw):
            norm = _voice_norm(raw)
            spans = []
            ms = list(VOICE_ANCHOR_RE.finditer(norm))
            for i, m in enumerate(ms):
                v = VOICE_WHO.get(m.group(1).lower()) or VOICE_WHO.get(m.group(1))
                end = ms[i + 1].start() if i + 1 < len(ms) else len(norm)
                if v:
                    spans.append([m.start(), end, v])
            return norm, spans

        norm, spans = _build(t)
        norm2, spans2 = _build(re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t))
        _VOICE_LEDGER.append({"norm": norm, "spans": spans,
                              "norm2": norm2, "spans2": spans2, "ts": time.time()})
        if len(_VOICE_LEDGER) > _VOICE_LEDGER_MAX:
            del _VOICE_LEDGER[:-_VOICE_LEDGER_MAX]
    except Exception as e:
        _log("voice ledger err: " + str(e)[:100])


def _voice_resolve(piece):
    """碎片→声线：规整子串定位（先原文变体，后剥图变体）→最优重叠锚点段。
    返回 voice 或 None（账本空/失配/无锚）。"""
    try:
        np_ = _voice_norm(piece)
        if not np_:
            return None
        for ent in reversed(list(_VOICE_LEDGER)):   # 新账优先
            for full, spans in ((ent["norm"], ent["spans"]), (ent["norm2"], ent["spans2"])):
                off = full.find(np_)
                if off < 0:
                    continue
                best, bestov = None, 0
                for s in spans:
                    ov = min(off + len(np_), s[1]) - max(off, s[0])
                    if ov > bestov:
                        bestov, best = ov, s
                if best and bestov >= max(2, len(np_) // 2):
                    return best[2]
                return None    # 定位到账目但落无锚区（开头白地）→ 交壳启发式
    except Exception as e:
        _log("voice resolve err: " + str(e)[:100])
    return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[bridge {time.strftime('%H:%M:%S')}]", fmt % args, flush=True)

    def _send(self, code, body, ctype="application/json"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if "json" in ctype or "html" in ctype else ""))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _voice_speech(self):
        """v4.4.0 薄决议器：OWI 的 TTS 引擎指到这。查锚点账本给碎片定声线（只查表不猜），
        带 voice 转发本地壳；失配剥 voice（连 OWI 后端注入的 config voice 一起剥）裸转发，
        壳退回锚点/投票启发式=不比改造前差。音频字节与上游 Content-Type 原样回传。"""
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
            req = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            self._send(400, json.dumps({"error": "bad json"}))
            return
        piece = str(req.get("input") or "")
        if not piece.strip():
            self._send(400, json.dumps({"error": "input required"}))
            return
        voice = _voice_resolve(piece)
        fwd = dict(req)
        fwd.pop("voice", None)
        if voice:
            fwd["voice"] = voice
        try:
            r = httpx.post(VOICE_SHELL_URL, timeout=300, json=fwd,
                           headers={"Content-Type": "application/json"})
        except Exception as e:
            _log(f"[voice] 壳转发失败: {str(e)[:120]}")
            self._send(502, json.dumps({"error": f"shell unreachable: {str(e)[:120]}"}))
            return
        self._send(r.status_code, r.content, r.headers.get("Content-Type", "audio/mpeg"))
        _log(f"[voice] {'resolved' if voice else 'miss'} voice={voice or '-'} len={len(piece)} piece={piece[:24]!r}")

    def do_GET(self):
        if self.path.rstrip("/") in ("/v1/models", "/v1/models/"):
            self._send(200, json.dumps({"object": "list", "data": [
                {"id": bid, "object": "model", "owned_by": "bridge"}
                for bid in BRAINS if bid not in DISABLED_BRAINS]}, ensure_ascii=False))
        elif self.path.rstrip("/") in ("/affection", "/affection/"):
            st = _bond_load()
            days = None
            try:
                if st.get("first_day_ts"):
                    days = (datetime.now(CN_TZ).date() - datetime.fromtimestamp(st["first_day_ts"] / 1000, CN_TZ).date()).days + 1
            except Exception:
                days = None
            score = st.get("score", 75)
            self._send(200, json.dumps({"score": score, "level": _bond_level(score), "days": days,
                                        "last_nostalgia": st.get("last_nostalgia", ""),
                                        "hist_tail": (st.get("hist") or [])[-30:]}, ensure_ascii=False))
        elif self.path.rstrip("/") == "/diary/today":
            st = _diary_read()
            self._send(200, json.dumps(st, ensure_ascii=False))
        elif self.path.rstrip("/") == "/genqueue":
            with GEN_LOCK:
                items = GEN_PENDING[:]
                GEN_PENDING.clear()
            self._send(200, json.dumps({"items": items}, ensure_ascii=False))
        elif self.path.startswith("/exam/next"):
            self._send(200, json.dumps(_exam_next(), ensure_ascii=False))
        elif self.path.rstrip("/") == "/digest/done":
            # v4.1.1 已摘要日期清单（digest_sync 拉 diff 用，一行一日期）
            try:
                fp = os.path.join(DIGEST_INBOX, "DONE.txt")
                txt = open(fp, encoding="utf-8").read() if os.path.exists(fp) else ""
                self._send(200, json.dumps({"done": [l.strip() for l in txt.splitlines() if l.strip()]}))
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)[:150]}))
        elif self.path.rstrip("/") == "/balance/ping":
            # v4.1.2 余额红绿灯（手动按钮触发，禁自动轮询）：max_tokens=1 发 5.3 → 200绿/1113红/其他黄
            try:
                t0 = time.time()
                r = httpx.post(ZHIPU, timeout=30,
                               headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                               json={"model": CLI_MODELS["paid"], "max_tokens": 1,
                                     "messages": [{"role": "user", "content": "ping"}]})
                ms = int((time.time() - t0) * 1000)
                if r.status_code == 200:
                    state = "green"
                elif r.status_code == 429 and _quota_dead(r.text):
                    state = "red"
                else:
                    state = "yellow"
                self._send(200, json.dumps({"state": state, "http": r.status_code, "ms": ms,
                                            "checked_at": time.time(),
                                            "paid_1113_last": _PAID_1113["ts"]}, ensure_ascii=False))
            except Exception as e:
                self._send(200, json.dumps({"state": "yellow", "error": str(e)[:120],
                                            "checked_at": time.time()}, ensure_ascii=False))
        elif self.path.rstrip("/") == "/brain/probe":
            # v4.1.2 手动探活（按钮触发，页面禁自动轮询——按次计费渠道零探活）
            try:
                self._send(200, json.dumps(_probe_snapshot(), ensure_ascii=False))
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)[:150]}))
        elif self.path.startswith("/exam/stats"):
            self._send(200, json.dumps(_exam_stats(), ensure_ascii=False))
        elif self.path in ("/", "/healthz"):
            self._send(200, json.dumps({"status": "ok", "pipeline": "unified-v4.1.9-glmfree",
                                        "brains": list(BRAINS), "default": DEFAULT_BRAIN,
                                        "aliases": list(_ALIASES), "task_fuse": "X-OpenWebUI-Task",
                                        "journal": JOURNAL_COLL, "duet": DUET_BRAIN, "bare_test": "[裸测] 前缀=只带系统提示词",
                                        "expr": "28emo x ram/rem",
                                        "foreign": {"model": FOREIGN_MODEL, "probe": FOREIGN_PROBE,
                                                    "scenes_default": "pet/service=cli, tavern=ds"},
                                        "paid_1113_last": _PAID_1113["ts"]}))
        else:
            self._send(404, json.dumps({"error": "not found"}))

# v3.5.9 摘除：/v1/journal/generate 手动补账口已迁管理台 v1.4.2 自带浓缩（_journal_generate 方法删）

    def _bare_run(self, B, sys_p, bare, user_multimodal, want_stream, brain_id):
        """v3.7.6 裸测模式：pmsg 只有系统提示词+用户消息。注入/历史/表情/写回/羁绊 tick 全关，
        零记忆污染（测试口：验人设底稿、验脑差异、验流式）。审计小票照记（mode 带 ·bare）。"""
        t0 = time.time()
        print(f"[bridge] 裸测模式（{brain_id}）：系统提示词 {len(sys_p)} 字，其余全裸", flush=True)
        _rx()["inj"].clear()
        _rx()["recalls"].clear()
        _rx().pop("usage", None)   # v3.8.1 token 计量防串轮
        _rx().pop("t_first", None)
        pmsg = [{"role": "system", "content": sys_p},
                {"role": "user", "content": user_multimodal if (user_multimodal and B["glm"]) else bare}]
        try:
            if want_stream:
                text = zhipu_stream_relay(self, pmsg, model=B["label"], max_tokens=B["max_tokens"],
                                          temperature=_P('reply_temperature'), reasoning=B["effort"] or "low",
                                          upstream=B["upstream"], glm_params=B["glm"], expr_who=None,
                                          model_name=B.get("model_name"), no_think=B.get("no_think", False))
            else:
                if B["glm"]:
                    r = httpx.post(ZHIPU, timeout=300,
                                   headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                                   json={"model": "glm-5.3-flash", "thinking": {"type": "enabled"},
                                         "reasoning_effort": B["effort"], "max_tokens": B["max_tokens"],
                                         "temperature": _P("reply_temperature"), "messages": pmsg})
                    if r.status_code == 429:
                        text = QUOTA_DEAD_MSG if _quota_dead(r.text) else RATE_LIMIT_MSG
                        _log(f"{brain_id}·bare 429，不重试直说限额")
                    else:
                        r.raise_for_status()
                    _j = r.json()
                    _usage_note(_j)   # v3.8.1 token 计量
                    text = (_j["choices"][0]["message"].get("content") or "").strip()
                else:
                    try:
                        r = httpx.post((B.get("upstream") or (MS_URL, MSKEY))[0], timeout=300,
                                       headers={"Authorization": f"Bearer {(B.get('upstream') or (MS_URL, MSKEY))[1]}", "Content-Type": "application/json"},
                                       json={"model": B.get("model_name") or MS_MODEL, "max_tokens": B["max_tokens"], **({"reasoning_effort": B["effort"]} if B.get("effort") else {}), "temperature": _P("reply_temperature"),
                                             "messages": pmsg})
                        if r.status_code == 429:
                            text = MS_LIMIT_MSG
                            _log("裸测上游 429（纪律不重试），直说限额")
                        else:
                            r.raise_for_status()
                            _j = r.json()
                            _usage_note(_j)   # v4.0.0 ds/local usage 透传
                            text = (_j["choices"][0]["message"].get("content") or "").strip()
                    except Exception as e:
                        _log("裸测上游调用失败: " + str(e)[:150])
                        text = MS_LIMIT_MSG
                self._send(200, openai_response(text, model=B["label"], stream=False))
            _t1 = _rx().pop("t_first", None)
            _receipt_write({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "session": "st-live",
                            "mode": brain_id + "·bare", "provider": B.get("label", "?"),
                            "user_text": bare[:500], "injections": [], "recalls": [],
                            "timings": {"first_token_ms": (round((_t1 - t0) * 1000) if _t1 else None),
                                        "total_ms": round((time.time() - t0) * 1000)},
                            "writes": {"chat_memory": 0, "summary": False, "journal": False},
                            "expr": {"tags": len(EXPR_TAG_RE.findall(text))},
                            "bond": None, "error": None})
            _log(f"{brain_id}·bare 回复({round(time.time() - t0, 1)}s): {text[:60]}")
        except Exception as e:
            import traceback; traceback.print_exc(); _log("裸测错误: " + str(e)[:200])
            try:
                self._send(500, json.dumps({"error": {"message": str(e)[:300]}}))
            except Exception:
                pass

    def _duet_open_stream(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        ch = {"id": "chatcmpl-remram-duet", "object": "chat.completion.chunk",
              "choices": [{"index": 0, "finish_reason": None, "delta": {"role": "assistant", "content": ""}}]}
        self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
        self.wfile.flush()

    def _duet_emit(self, text):
        ch = {"id": "chatcmpl-remram-duet", "object": "chat.completion.chunk",
              "choices": [{"index": 0, "finish_reason": None, "delta": {"content": text}}]}
        self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
        self.wfile.flush()

    def _duet_relay_one(self, messages, max_tokens=2048, effort="low", expr_who=None):
        """往已开的 SSE 里转发一次 GLM 调用的增量（reasoning+content 照发）；返回完整文本。
        429/非200=把限额话当文本流出（拉姆段挂则整段限额话，雷姆段挂则限额话收尾）。"""
        cm = httpx.stream("POST", ZHIPU, timeout=300,
                          headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                          json={"model": "glm-5.3-flash", "thinking": {"type": "enabled"},
                                "reasoning_effort": effort, "max_tokens": max_tokens,
                                "temperature": _P("reply_temperature"), "stream": True, "messages": messages})
        r = cm.__enter__()
        full = []
        exf = _ExprFilter(expr_who) if expr_who is not None else None   # v3.5.8
        try:
            if r.status_code == 429:
                quota_dead = False
                try:
                    quota_dead = _quota_dead(r.read().decode("utf-8", "replace"))
                except Exception:
                    pass
                msg = QUOTA_DEAD_MSG if quota_dead else RATE_LIMIT_MSG
                self._duet_emit(msg)
                return msg
            if r.status_code != 200:
                self._duet_emit(RATE_LIMIT_MSG)
                return RATE_LIMIT_MSG
            for line in r.iter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    j = json.loads(data)
                except Exception:
                    continue
                delta = ((j.get("choices") or [{}])[0].get("delta") or {})
                rc = delta.get("reasoning_content") or ""
                if rc:
                    ch = {"id": "chatcmpl-remram-duet", "object": "chat.completion.chunk",
                          "choices": [{"index": 0, "finish_reason": None, "delta": {"reasoning_content": rc}}]}
                    try:
                        self.wfile.write(b"data: " + json.dumps(ch, ensure_ascii=False).encode("utf-8") + b"\n\n")
                        self.wfile.flush()
                    except Exception:
                        break
                piece = delta.get("content") or ""
                if piece:
                    if "t_first" not in _rx():   # v3.7.4 首字埋点（duet=拉姆段首 content）
                        _rx()["t_first"] = time.time()
                    full.append(piece)
                    out_txt = exf.feed(piece) if exf else piece   # v3.5.8
                    if out_txt:
                        self._duet_emit(out_txt)
        finally:
            try:
                r.close()
            except Exception:
                pass
        raw = "".join(full)
        if exf is None:
            return raw
        tail = exf.flush()   # v3.5.8
        if tail:
            self._duet_emit(tail)
        _tail = expr_fallback_tail(raw, exf.default_who)   # v3.5.8.1
        if _tail:
            self._duet_emit(_tail)
        return expr_finish(raw, exf.default_who)

    def _duet_stream(self, p1, p2):
        """两段真流式接力：拉姆：→流1→蕾姆：→流2→收尾。返回拼接全文供写回。"""
        self._duet_open_stream()
        self._duet_emit("拉姆：")
        ram_text = self._duet_relay_one(p1)
        self._duet_emit("\n\n蕾姆：")
        rem_text = self._duet_relay_one(p2)
        try:
            end = {"id": "chatcmpl-remram-duet", "object": "chat.completion.chunk",
                   "choices": [{"index": 0, "finish_reason": "stop", "delta": {}}]}
            self.wfile.write(b"data: " + json.dumps(end).encode("utf-8") + b"\n\n")
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except Exception:
            pass
        return "拉姆：" + ram_text + "\n\n蕾姆：" + rem_text

    def _duet(self, user_multimodal, bare, want_stream, is_task, brain_id):
        """v3.5.7 双人同台：拉姆先说→她的原话进上下文→雷姆真接。写回/审计一次。"""
        t0 = time.time()
        label = BRAINS[brain_id]["label"]
        _rx()["inj"].clear()   # v3.5.9.1 keep-alive 复线程防串轮
        _rx().pop("usage", None)   # v3.8.1 防串轮
        _rx()["recalls"].clear()
        _rx().pop("t_first", None)   # v3.7.4 首字埋点随轮清零
        try:
            ram_draft, rem_draft = _load_duet_drafts()
        except Exception as e:
            self._send(500, json.dumps({"error": {"message": "双人底稿加载失败: " + str(e)[:200]}}))
            return
        # 共享注入（算一次，两姐妹共用）：现实→关怀→前情(截至X月X日)→往日日志→双人库→场景库→记忆宫
        sys_head = ""
        _reality = reality_block()   # v3.8.2 缓存优化：每轮变的时间戳不再占前缀首位

        def _add_inj(name, text):
            if text:
                _rx()["inj"].append({"name": name, "chars": len(text), "text_full": text})

        _add_inj("现实锚", _reality)
        _enb = english_block()   # v3.9.1 英语模式（热读开关，默认关）
        if _enb:
            sys_head += "\n\n" + _enb
            _add_inj("英语模式", _enb)
        chk_note = ""
        if not is_task:
            chk = checkin_directive()
            if chk:
                sys_head += "\n\n" + chk
                _add_inj("关怀钩子", chk)
                chk_note = chk
        rec_ts, rec = latest_summary_full()
        if rec:
            try:
                _rd = datetime.fromtimestamp(rec_ts, CN_TZ)
                sys_head += f"\n\n【前情提要（截至 {_rd.month} 月 {_rd.day} 日）】" + rec
                _add_inj("前情提要", f"【前情提要（截至 {_rd.month} 月 {_rd.day} 日）】" + rec)
            except Exception:
                sys_head += "\n\n【前情提要】" + rec
                _add_inj("前情提要", "【前情提要】" + rec)
        for _nm, blk in _recall_family(bare, (("往日日志", lambda: journal_block(bare)),
                                              ("记忆库", lambda: kb_memory_block(bare)),
                                              ("场景库", lambda: kb_scene_block(bare)),
                                              ("记忆宫", lambda: palace_recall_block(bare, _vec_for(bare))))):
            if blk:
                sys_head += "\n\n" + blk
                _add_inj(_nm, blk)
        hist = fetch_history_messages("st-live", tail=40)
        user_content = user_multimodal if user_multimodal else bare

        # 第一轮：拉姆（关怀重申只压在先手段）
        _expr_tail = ("\n\n" + EXPR_RULE) if not is_task else ""   # v3.5.8
        p1 = [{"role": "system", "content": sys_head + "\n\n" + DUET_RAM_DIRECTIVE + "\n\n" + ram_draft + _expr_tail}]
        p1 += hist
        if chk_note:
            p1.append({"role": "system", "content":
                       "【重申·开场关怀】你的回复第一句必须是主动关心：问他上次那件事进展如何"
                       "（从前情提要里挑真有过的事），然后才回应他这条消息。"})
        p1.append({"role": "system", "content": EXPR_REASSERT})   # v3.5.8.1
        p1.append({"role": "system", "content": DUET_RAM_REASSERT})   # v3.7.3 末位重申：压 40 条双人 few-shot 防第一棒越界代言蕾姆
        p1.append({"role": "user", "content": user_content})

        # 第二轮：雷姆（拉姆的原话紧跟在 user 之后进上下文）
        p2 = [{"role": "system", "content": sys_head + "\n\n" + DUET_REM_DIRECTIVE + "\n\n" + rem_draft + _expr_tail}]
        p2 += hist
        p2.append({"role": "user", "content": user_content})
        p2.append({"role": "assistant", "content": ""})   # 占位：拉姆原话在第一轮后才回填
        _ph2 = len(p2) - 1   # v3.7.2 占位绝对索引（负索引 p2[-2] 自 v3.5.8.1 尾部追加 EXPR_REASSERT 起错位，勿复用）
        p2.append({"role": "system", "content": DUET_REM_TURN})
        p2.append({"role": "system", "content": EXPR_REASSERT})   # v3.5.8.1

        B_duet = scene_brain("tavern")   # v4.0.0 两棒同跟 tavern 场景：glm=真流式档位；ds=伪流；local=伪流（探活回退在 scene_brain 内）
        # v4.1.5 修复（todo-06l）：scene_brain 返回 dict 没有 provider 键（v4.0.0 手术漏改，
        # 双人接力每轮 KeyError）。provider 从 glm 布尔现推：glm=True→真流式 _duet_relay_one；
        # 否则→_up_once 伪流（upstream 理论上必在，兜底 tuple 防手滑）。
        if B_duet["glm"]:
            cfg = {"provider": "glm", "glm_effort": B_duet.get("effort") or "low"}
        else:
            cfg = {"provider": "up", "_up": B_duet.get("upstream") or (ZHIPU, ZKEY),
                   "_m": B_duet.get("model_name") or MS_MODEL}
        if want_stream:
            # 真流式：p2 的拉姆占位在第一段流完后才已知——先跑拉姆流，再补进 p2
            self._duet_open_stream()
            self._duet_emit("拉姆：")
            if cfg["provider"] == "glm":
                ram_text = self._duet_relay_one(p1, effort=cfg["glm_effort"], expr_who=("ram" if not is_task else None))
            else:
                ram_text, err1 = _up_once(p1, url=cfg["_up"][0], key=cfg["_up"][1], model_name=cfg["_m"], usage_note=True)
                self._duet_emit(expr_finish(ram_text, "ram") if (ram_text and not is_task) else (ram_text or err1))
            p2[_ph2] = {"role": "assistant", "content": ram_text}
            self._duet_emit("\n\n蕾姆：")
            if cfg["provider"] == "glm":
                rem_text = self._duet_relay_one(p2, effort=cfg["glm_effort"], expr_who=("rem" if not is_task else None))
            else:
                rem_text, err2 = _up_once(p2, url=cfg["_up"][0], key=cfg["_up"][1], model_name=cfg["_m"], usage_note=True)
                self._duet_emit(expr_finish(rem_text, "rem") if (rem_text and not is_task) else (rem_text or err2 or ""))
            try:
                end = {"id": "chatcmpl-remram-duet", "object": "chat.completion.chunk",
                       "choices": [{"index": 0, "finish_reason": "stop", "delta": {}}]}
                self.wfile.write(b"data: " + json.dumps(end).encode("utf-8") + b"\n\n")
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()
            except Exception:
                pass
            combined = "拉姆：" + ram_text + "\n\n蕾姆：" + rem_text
        else:
            if cfg["provider"] == "glm":
                _once = lambda m: _glm_once(m, effort=cfg["glm_effort"])
            else:
                _once = lambda m: _up_once(m, url=cfg["_up"][0], key=cfg["_up"][1], model_name=cfg["_m"], usage_note=True)
            ram_text, err1 = _once(p1)
            if err1 and not ram_text:
                combined = err1
            else:
                if not is_task:
                    ram_text = expr_finish(ram_text, "ram")
                p2[_ph2] = {"role": "assistant", "content": ram_text}
                rem_text, err2 = _once(p2)
                rem_seg = expr_finish(rem_text, "rem") if (rem_text and not is_task) else (rem_text or "")
                combined = "拉姆：" + ram_text + "\n\n蕾姆：" + (rem_seg or err2 or "")
                if err2:
                    _log("duet 雷姆段失败: " + err2[:80])
            self._send(200, openai_response(combined, model=label, stream=False))
        _voice_ledger_put(combined)   # v4.4.0 语音锚点账本（流式/非流式全汇此，text 已终态）
        if not is_task:
            _base = int(time.time() * 1000)
            mem_write("st-live", "user", bare, _base)
            _cl = _clean_for_memory(combined)
            if _cl:
                mem_write("st-live", "assistant", _cl, _base + 1)
            maybe_summarize("st-live")
            maybe_journal()
        _rotate_log("/root/work/logs/mentor-chain.log")
        try:
            with open("/root/work/logs/mentor-chain.log", "a", encoding="utf-8") as lf:
                lf.write(json.dumps({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "mode": brain_id,
                                     "sec": round(time.time() - t0, 1), "user": bare[:100]},
                                    ensure_ascii=False) + "\n")
        except Exception:
            pass
        _prov = f"duet-{cfg['provider']}" + (f"-{cfg['glm_effort']}" if cfg["provider"] == "glm" else "")
        _rxd = _rx()
        _t1 = _rxd.pop("t_first", None)   # v3.7.4 首字真值；ds 伪流/限额话=None
        _receipt_write({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "session": "st-live",
                        "mode": brain_id, "provider": _prov, "user_text": bare[:500],
                        "injections": _rxd["inj"], "recalls": _rxd["recalls"],
                        "timings": {"first_token_ms": (round((_t1 - t0) * 1000) if _t1 else None),
                                    "total_ms": round((time.time() - t0) * 1000)},
                        "writes": {"chat_memory": 0 if is_task else 2, "summary": not is_task, "journal": not is_task},
                        "expr": {"tags": len(EXPR_TAG_RE.findall(combined))}, "error": None})   # v3.7.3 duet 小票（原缺）
        _log(f"{brain_id} 回复({round(time.time() - t0, 1)}s): {combined[:60]}")

    def _trio(self, user_multimodal, bare, want_stream, is_task, brain_id, serious_mode=False):
        """v3.7.0 酒馆三人：一次调用生成三段（拉姆：/蕾姆：/艾米莉亚：）。
        注入族复用（现实/关怀/前情/日志/记忆库/场景/记忆宫），底稿=trio_prompt.txt 独立稿现读；
        脑跟总闸；小票/写回/审计同构。v4.3.5 serious_mode=OWI 滤镜认真标记。"""
        t0 = time.time()
        B = scene_brain("tavern")   # v4.0.0 trio 脑跟 tavern 场景（glm/ds/local 三路；local 探活回退在 scene_brain 内）
        B["label"] = "remram-trio-" + str(B.get("label", "")).replace("remram-", "")
        if serious_mode and not is_task:   # v4.3.5 认真轮思考档拉满（glm max 档 16384 惯例；local/cli 上游不收参自动忽略）
            B["effort"] = "max"
            if B.get("glm"):
                B["max_tokens"] = 16384
        try:
            draft = _load_trio_draft()
        except Exception as e:
            self._send(500, json.dumps({"error": {"message": "三人底稿加载失败: " + str(e)[:200]}}))
            return
        _reality = reality_block()   # v3.8.2 缓存优化
        sys_head = ""
        _rx()["inj"].clear()   # v3.7.2 清零挪到召回前（v3.7.0/1 在召回后清，三人小票 recalls 恒空）
        _rx().pop("usage", None)   # v3.8.1 防串轮
        _rx()["recalls"].clear()
        _rx().pop("t_first", None)   # v3.7.4 首字埋点随轮清零

        def _add_inj(name, text):
            if text:
                _rx()["inj"].append({"name": name, "chars": len(text), "text_full": text})

        _add_inj("现实锚", _reality)
        _enb = english_block()   # v3.9.1 英语模式（热读开关，默认关）
        if _enb:
            sys_head += "\n\n" + _enb
            _add_inj("英语模式", _enb)
        chk_note = ""
        if not is_task:
            chk = checkin_directive()
            if chk:
                sys_head += "\n\n" + chk
                _add_inj("关怀钩子", chk)
                chk_note = chk
        rec_ts, rec = latest_summary_full()
        if rec:
            try:
                _rd = datetime.fromtimestamp(rec_ts, CN_TZ)
                sys_head += f"\n\n【前情提要（截至 {_rd.month} 月 {_rd.day} 日）】" + rec
                _add_inj("前情提要", f"【前情提要（截至 {_rd.month} 月 {_rd.day} 日）】" + rec)
            except Exception:
                sys_head += "\n\n【前情提要】" + rec
                _add_inj("前情提要", "【前情提要】" + rec)
        for _nm, blk in _recall_family(bare, (("往日日志", lambda: journal_block(bare)),
                                              ("记忆库", lambda: kb_memory_block(bare)),
                                              ("场景库", lambda: kb_scene_block(bare)),
                                              ("记忆宫", lambda: palace_recall_block(bare, _vec_for(bare))),
                                              ("想法账本", lambda: ideas_recall_block(bare)))):   # v4.4.5 用户结论复述提醒
            if blk:
                sys_head += "\n\n" + blk
                _add_inj(_nm, blk)
        if not is_task:
            sys_head += "\n\n" + EXPR_RULE   # v3.7.2 复审漏项补齐：原只有 REASSERT 没 28 情绪枚举，表情只能瞎选落 neutral
            _add_inj("表情规则", EXPR_RULE)
            sys_head += "\n\n" + IDEA_SKILL_BLOCK   # v4.4.5 想法账本存档通道（常驻小块，用户明示才触发输出）
            _add_inj("想法账本·存档通道", IDEA_SKILL_BLOCK)
        # ==== v4.2.2 三人线自拍令牌（与统一管线同款机制；v4.2.0 漏接本线=用户群聊日常恰在三人线，14:41 实测漏）====
        gen_hit_name = None
        if not is_task:
            gen_hit_name = _gen_token_hit(bare or "")   # v4.2.8 裸触发「生图」+旧括号令牌单口
            if gen_hit_name:
                sys_head += "\n\n" + GEN_SKILL_BLOCK_TRIO
                _add_inj("自拍技能", GEN_SKILL_BLOCK_TRIO)
                print(f"[bridge] 自拍令牌命中(三人): {gen_hit_name}", flush=True)
        # ==== v4.4.8/9 四格漫画令牌（「日记」=当日幂等看图；「重画日记」=强制重画；插画线回归 cron）====
        comic_ctx = None
        if not is_task and (_diary_token_hit(bare or "") or _diary_redraw_hit(bare or "")):
            _redraw = _diary_redraw_hit(bare or "")
            comic_ctx = _comic_payload(force=_redraw)   # 当日幂等；文案 GLM 2~15s，挂在装配期不额外占回合
            if comic_ctx.get("ok"):
                sys_head += "\n\n" + COMIC_SKILL_BLOCK
                _add_inj("四格漫画技能", COMIC_SKILL_BLOCK)
                print(f"[bridge] 日记令牌命中(三人·四格): redraw={_redraw} dup={comic_ctx.get('duplicate', False)}", flush=True)
            else:
                _cerr = str(comic_ctx.get("error") or "未知原因")
                sys_head += "\n\n" + COMIC_FAIL_BLOCK_TMPL.format(err=_cerr)
                _add_inj("四格漫画技能·失败", _cerr)
                print(f"[bridge] 日记令牌失败(三人·四格): {_cerr}", flush=True)
        hist = fetch_history_messages("st-live", tail=40)
        pmsg = [{"role": "system", "content": sys_head + "\n\n" + draft + (("\n\n" + _reality) if _reality else "")}] + hist   # v3.8.2 现实锚挪尾部保前缀缓存
        if not is_task:
            pmsg.append({"role": "system", "content": EXPR_REASSERT})
        if chk_note:
            pmsg.append({"role": "system",
                         "content": "【重申·开场关怀】回复第一段（拉姆）第一句必须是主动关心：问他上次那件事进展如何"
                                    "（从前情提要里挑真有过的事），然后才回应他这条消息。"})
        if serious_mode and not is_task:   # v4.3.5 认真块置底=紧贴 user 生成位（用户令「放到最下层」）
            pmsg.append({"role": "system", "content": SERIOUS_BLOCK_TRIO})
            _add_inj("认真模式", SERIOUS_BLOCK_TRIO)
        if not is_task and IDEA_STORE_INTENT_RE.search(bare or ""):   # v4.4.6b 存档意图末位重申（D 案实锤：长回复丢末行指令）
            pmsg.append({"role": "system", "content": IDEA_STORE_REASSERT})
            _add_inj("存档重申", "意图命中")
        pmsg.append({"role": "user", "content": user_multimodal if (user_multimodal and B["glm"]) else bare})
        if want_stream:
            _exg = _GenFilter() if gen_hit_name else None
            _ixf = _IdeaFilter() if not is_task else None   # v4.4.5 <idea> 存档行剥除+捕获（任务调用关）

            def _gen_tail():
                # v4.2.2 流尾：取过滤器捕获的 <gen> 行入队并等图（决策5 无行=不入队静默）
                _nm, _tg = _exg.hit or (None, None)
                _tg = (_tg or "").strip()
                if not _tg:
                    return None
                _gid = _gen_enqueue(_tg, _gen_who(_nm, gen_hit_name))   # v4.2.6b who 终审
                return _gen_wait_markdown(_gid)

            def _diary_tail():
                # v4.4.8 流尾：台词+评分秒回+等四格整图（首触 ≤300s / 同日重复直出 URL）
                return _comic_markdown(comic_ctx) if (comic_ctx and comic_ctx.get("ok")) else None

            text = zhipu_stream_relay(self, pmsg, model=B["label"], max_tokens=B["max_tokens"],
                                      temperature=_P('reply_temperature'), reasoning=B["effort"] or "low",
                                      upstream=B["upstream"], glm_params=B["glm"], model_name=B.get("model_name"),
                                      expr_who=(None if is_task else ""),   # v3.7.2 空串开过滤器：有主语标签换图/无主语只剥（原 None=标签原样上屏）
                                      no_think=B.get("no_think", False),
                                      gen_filter=_exg,
                                      idea_filter=_ixf,
                                      tail_supplier=(_gen_tail if _exg else (_diary_tail if (comic_ctx and comic_ctx.get("ok")) else None)))
            if _exg:
                text = GEN_LINE_ANY_RE.sub("", GEN_LINE_RE.sub("", text)).strip()   # v4.2.6 写回剥行加宽容式（relay 返回原文）
            if _ixf:   # v4.4.5 存档收口：后台入库（fail-open）+写回剥行（宽容式防畸形行进 chat_memory）
                if _ixf.hit:
                    threading.Thread(target=idea_store, args=(*_ixf.hit, bare), daemon=True).start()
                text = IDEA_LINE_ANY_RE.sub("", text).strip()
            # v4.2.1 表情收口已在 relay 内完成（relay 返回=expr_finish(raw)），此处原二次 expr_finish
            # 会再叠 3 张兜底 neutral 进 memory（存档 6 图实锤）——已删，非流式分支（无 relay）保留自己的收口
            # v3.7.2 流式分支 SSE 已由 relay 发完（头+chunk+[DONE]），不再 _send——v3.7.0/1 双响应畸形修复
        else:
            if B["glm"]:
                try:
                    r = httpx.post(ZHIPU, timeout=300,
                                   headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                                   json={"model": "glm-5.3-flash", "thinking": {"type": "enabled"},
                                         "reasoning_effort": B["effort"], "max_tokens": B["max_tokens"],
                                         "temperature": _P("reply_temperature"), "messages": pmsg})
                    if r.status_code == 429:
                        text = QUOTA_DEAD_MSG if _quota_dead(r.text) else RATE_LIMIT_MSG
                        _log("三人 429 直说限额")
                    else:
                        r.raise_for_status()
                        text = (r.json()["choices"][0]["message"].get("content") or "").strip()
                except Exception as e:
                    _log("三人调用失败: " + str(e)[:150])
                    text = RATE_LIMIT_MSG
            else:
                text, _err = _up_once(pmsg, max_tokens=B["max_tokens"],
                                      url=(B.get("upstream") or (MS_URL, MSKEY))[0],
                                      key=(B.get("upstream") or (MS_URL, MSKEY))[1],
                                      model_name=B.get("model_name") or MS_MODEL, usage_note=True,
                                      no_think=B.get("no_think", False), effort=B.get("effort"))
            if not is_task and text not in (QUOTA_DEAD_MSG, RATE_LIMIT_MSG, MS_LIMIT_MSG):
                text = expr_finish(text, None)
            # v4.2.2 三人线自拍收口：解析 <gen> 行→剥行→入队→等图或失败提示句
            if gen_hit_name:
                _gp = _gen_parse(text)   # v4.2.6 双式解析
                if _gp:
                    text = (text[:_gp[2]] + text[_gp[3]:]).strip()
                    _tg = _gp[1]
                    if _tg:
                        _gid = _gen_enqueue(_tg, _gen_who(_gp[0], gen_hit_name))   # v4.2.6b who 终审
                        _gmd = _gen_wait_markdown(_gid)
                        if _gmd:
                            text = text + "\n\n" + _gmd
            if comic_ctx and comic_ctx.get("ok"):   # v4.4.8 非流式四格收口：台词+评分+整图
                _cmm = _comic_markdown(comic_ctx)
                if _cmm:
                    text = text + "\n\n" + _cmm
            if not is_task:   # v4.4.5 非流式存档收口：剥行+后台入库
                _ip = _idea_parse(text)
                if _ip:
                    text = (text[:_ip[0]] + text[_ip[2]:]).strip()
                    threading.Thread(target=idea_store, args=(*_ip[1], bare), daemon=True).start()
            self._send(200, openai_response(text, model=B["label"], stream=False))
        _voice_ledger_put(text)   # v4.4.0 语音锚点账本（统一管线咽喉）
        if not is_task:
            _base = int(time.time() * 1000)
            mem_write("st-live", "user", bare, _base)
            _cl = _clean_for_memory(text)
            if _cl:
                mem_write("st-live", "assistant", _cl, _base + 1)
            maybe_summarize("st-live")
            maybe_journal()
        _rotate_log("/root/work/logs/mentor-chain.log")
        try:
            with open("/root/work/logs/mentor-chain.log", "a", encoding="utf-8") as lf:
                lf.write(json.dumps({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "mode": brain_id,
                                     "sec": round(time.time() - t0, 1), "user": bare[:100]},
                                    ensure_ascii=False) + "\n")
        except Exception:
            pass
        _t1 = _rx().pop("t_first", None)   # v3.7.4 首字真值；非流式/限额话=None
        _receipt_write({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "session": "st-live",
                        "mode": brain_id, "provider": B.get("label", "?"), "user_text": bare[:500],
                        "injections": _rx()["inj"],   # v3.7.2 逐块接线（原硬编码单块截断 2000，收集了却没接进小票）
                        "recalls": _rx()["recalls"],
                        "timings": {"first_token_ms": (round((_t1 - t0) * 1000) if _t1 else None),
                                    "total_ms": round((time.time() - t0) * 1000)},
                        "writes": {"chat_memory": 0 if is_task else 2, "summary": not is_task, "journal": not is_task},
                        "expr": {"tags": len(EXPR_TAG_RE.findall(text))}, "error": None})
        _log(f"{brain_id} 回复({round(time.time() - t0, 1)}s): {text[:60]}")

    def do_POST(self):
        if self.path.rstrip("/") in ("/v1/audio/speech", "/audio/speech"):
            # v4.4.0 语音决议器入口（OWI TTS 引擎指向此口）
            self._voice_speech()
            return
        if self.path.rstrip("/") == "/palace/recall":
            # v4.1.5（todo-xdt 20261008）课堂直通：POST {query, limit?} → 宫桥 /recall 原样转发。
            # 9236 只绑云回环，课堂（本机）够不着；桥双口在 EasyTier 面。阈值过筛交给调用方。
            try:
                n = int(self.headers.get("Content-Length", 0) or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                q = str(body.get("query") or "").strip()
                if not q:
                    self._send(400, json.dumps({"error": "query required"}))
                    return
                _log(f"[palace] 课堂召回 q={q[:40]}")
                r = httpx.post(PALACE_RECALL, timeout=15,
                               json={"query": q[:200], "limit": int(body.get("limit") or 3)})
                self._send(200, r.text)
            except Exception as e:
                self._send(502, json.dumps({"error": str(e)[:150]}))
            return
        if self.path.rstrip("/") == "/brain/probe":
            # v4.1.2 手动探活 POST 口（管理台 fetch 用 POST）
            try:
                self._send(200, json.dumps(_probe_snapshot(), ensure_ascii=False))
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)[:150]}))
            return
        if self.path.rstrip("/") == "/digest/inbox":
            # v4.1.1 发件箱收件口（PLAN-20261007 步骤④）：单日 JSONL 覆盖写，同日期重推=全量覆盖（幂等）。
            # 鉴权=网络边界（桥只绑 172.19.0.1+10.14.14.1 内网口，与现役各 POST 口同模式，无 token）。
            try:
                n = int(self.headers.get("Content-Length", 0) or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                date = str(body.get("date") or "")
                lines = str(body.get("jsonl") or "")
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
                    self._send(400, json.dumps({"error": "date 必须 YYYY-MM-DD"}))
                    return
                if len(lines) > 8 * 1024 * 1024:
                    self._send(413, json.dumps({"error": "单日超过 8MB 限额"}))
                    return
                os.makedirs(DIGEST_INBOX, exist_ok=True)
                fp = os.path.join(DIGEST_INBOX, f"{date}.jsonl")
                tmp = fp + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(lines)
                os.replace(tmp, fp)
                self._send(200, json.dumps({"ok": True, "date": date,
                                            "bytes": len(lines.encode("utf-8"))}, ensure_ascii=False))
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)[:150]}))
            return
        if self.path.rstrip("/") == "/exam/answer":
            try:
                n = int(self.headers.get("Content-Length", 0) or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                if body.get("id") is None:
                    self._send(400, json.dumps({"error": "id 必填"}))
                    return
                c, d = _exam_answer(int(body["id"]), bool(body.get("correct")))
                self._send(c, json.dumps(d, ensure_ascii=False))
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)[:150]}))
            return
        if self.path.rstrip("/") == "/diary/trigger":
            try:
                self._send(200, json.dumps(_diary_trigger(), ensure_ascii=False))
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)[:150]}))
            return
        if self.path.rstrip("/") == "/genupload":
            try:
                n = int(self.headers.get("Content-Length", 0) or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                gid = str(body.get("id") or "")
                png = base64.b64decode(body.get("png_b64") or "")
                if not gid or not png or len(png) > 12 * 1024 * 1024:
                    self._send(400, json.dumps({"error": "bad gen upload"}))
                    return
                _gen_fulfill(gid, png)
                self._send(200, json.dumps({"ok": True}))
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)[:120]}))
            return
        if "/chat/completions" not in self.path:
            self._send(404, json.dumps({"error": "not found"}))
            return
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
            req = json.loads(self.rfile.read(n) or b"{}")
            msgs = req.get("messages") or []
            # v4.3.5 认真模式：OWI 滤镜 inlet 在末条 user 尾打标；入口单点剥标置旗
            #（先剥再取 user=召回/写回/装配全下游零污染；扫全消息防滤镜版本差异）
            serious_mode = False
            for _m in msgs:
                if not isinstance(_m, dict):
                    continue
                _c = _m.get("content")
                if isinstance(_c, str) and SERIOUS_MARKER in _c:
                    serious_mode = True
                    _m["content"] = _c.replace(SERIOUS_MARKER, "")
                elif isinstance(_c, list):
                    for _p in _c:
                        if isinstance(_p, dict) and SERIOUS_MARKER in (_p.get("text") or ""):
                            serious_mode = True
                            _p["text"] = (_p.get("text") or "").replace(SERIOUS_MARKER, "")
            if serious_mode:
                print("[bridge] 认真模式标记命中（OWI 滤镜）", flush=True)
            user = next((m.get("content") for m in reversed(msgs)
                         if m.get("role") == "user"), "")
            # v3.5.2 多模态透传：GLM-5.3-Flash 原生多模态（官方实锤），智谱 coding 端点实测收图 200。
            # content 为数组时保留 text+image_url 项给智谱脑用；拍平文本照旧供日志/召回/写回。
            user_multimodal = None
            if isinstance(user, list):
                parts = []
                for x in user:
                    if not isinstance(x, dict):
                        continue
                    _t = x.get("type")
                    if _t == "text" and (x.get("text") or "").strip():
                        parts.append({"type": "text", "text": x.get("text")})
                    elif _t == "image_url" and isinstance(x.get("image_url"), dict) \
                            and (x["image_url"].get("url") or "").strip():
                        parts.append({"type": "image_url",
                                      "image_url": {"url": x["image_url"].get("url")}})
                if parts:
                    user_multimodal = parts
                user = " ".join(x.get("text", "") for x in user if isinstance(x, dict))
                if not user.strip():
                    user = "[用户发了一张图片]"
            if not user:
                self._send(400, json.dumps({"error": "没有 user 消息"}))
                return
            want_stream = bool(req.get("stream"))
            bare = user.strip()
            # v3.7.6 裸测模式：[裸测] 前缀 → 只带系统提示词的裸奔一问（剥前缀后照常走脑分发）
            bare_test = bare.startswith("[裸测]")
            if bare_test:
                bare = bare[len("[裸测]"):].strip()
                if not bare:
                    bare = "[空问题]"
            # v3.5.3 单人线：OWI 自定义模型（ram/rem）的系统提示词=单人底稿，随第一条 system 送达
            inc_sys = next((m.get("content") for m in msgs if m.get("role") == "system"), "")
            if isinstance(inc_sys, list):
                inc_sys = " ".join(x.get("text", "") for x in inc_sys if isinstance(x, dict))
            inc_sys = (inc_sys or "").strip()
            # v3.5.1 保险丝：OWI 后台任务（标题/标签/追问）带官方头 X-OpenWebUI-Task，
            # 此类调用跳过写回（chat_memory/摘要/入宫），审计照记——防任务模型误设回酒馆脑时污染历史库
            is_task = bool((self.headers.get("X-OpenWebUI-Task") or "").strip())
            if is_task:
                print("[bridge] 后台任务调用(X-OpenWebUI-Task)，只答不记", flush=True)
            brain_id = resolve_brain(req.get("model"))  # v3.5.9：下拉框=选模式入口，旧名走别名，认不出兜底「酒馆」
            B = BRAINS[brain_id]
            # ==== v3.7.6 裸测短路：任何脑带 [裸测] 都落统一管线裸奔（trio/duet 不进）====
            if bare_test:
                if B.get("binding"):
                    B = scene_brain(B["binding"])   # v4.0.0 裸测尊重场景脑（tavern/pet/service）
                _bp = inc_sys
                if not _bp:
                    try:
                        _bp = open(PURE_PROMPT_FILE, encoding="utf-8").read().strip()
                    except Exception:
                        _bp = ""
                if not _bp:
                    self._send(500, json.dumps({"error": {"message": "裸测模式缺系统提示词（请求无 system 且纯净底稿文件缺失）"}}))
                    return
                self._bare_run(B, _bp, bare, user_multimodal, want_stream, brain_id)
                return
            if brain_id == TRIO_BRAIN:
                self._trio(user_multimodal, bare, want_stream, is_task, brain_id, serious_mode)
                return
            if B.get("binding"):
                B = scene_brain(B["binding"])   # v4.0.0 总入口：脑由场景绑定现定（glm/ds/local）
            if serious_mode and not is_task:   # v4.3.5 认真轮思考档拉满（glm max 档 16384 惯例）
                B["effort"] = "max"
                if B.get("glm"):
                    B["max_tokens"] = 16384
            print(f"[bridge] 用户话(原始模型={req.get('model')}, 脑={brain_id}): {bare[:60]}", flush=True)

            # ==== v3.5.7 双人同台：姐妹轮转（拦截在 solo 判定之前——OWI 自带 system 不影响本模式）====
            if brain_id == DUET_BRAIN:
                if brain_id in DISABLED_BRAINS:   # v4.1.9 停用令：下拉已不下发，旧缓存硬发=人话 400
                    self._send(400, json.dumps({"error": {"message":
                        "酒馆双人接力已停用（等 token 自由再开）。请换「酒馆」或「酒馆三人」入口。"}}))
                    return
                # v4.1.5（todo-06l）：双人接力任何异常→全栈进桥日志，用户只见人话（裸 KeyError 禁上屏）
                try:
                    self._duet(user_multimodal, bare, want_stream, is_task, brain_id)
                except Exception as _duet_e:
                    import traceback as _tb
                    print("[bridge] 双人接力异常:\n" + _tb.format_exc(), flush=True)
                    self._send(500, json.dumps({"error": {"message":
                        "双人接力这轮没接上（桥端内部错误，已记日志）。可重发一条试试；"
                        "若连续失败请到管理台换脑或联系管理员查桥日志。"}}))
                return

            # ==== v3.5.0 统一管线：一套节点，大脑可换 ====
            t0 = time.time()
            # v3.5.3 单人模式判定：非任务调用且模型自带底稿 → 换单人底稿+摘双人库/场景库
            # v3.5.9 SOLO 短标记：模型层 system 只留 [SOLO_RAM]/[SOLO_REM]，桥读服务器底稿文件
            #（底稿正文迁管理台「人设底稿」页，保存下一句生效）；传全文=旧路径照旧（兼容不破坏）
            mark = (inc_sys or "").strip()
            solo = (not is_task) and bool(mark)
            if solo and mark in SOLO_MARK_FILES:
                try:
                    sys_p = open(SOLO_MARK_FILES[mark], encoding="utf-8").read().strip()
                except Exception:
                    sys_p = ""
                if not sys_p:
                    self._send(500, json.dumps({"error": {"message": "底稿文件缺失: " + SOLO_MARK_FILES[mark]}}))
                    return
                print(f"[bridge] 单人模式（标记 {mark} → 底稿文件 {len(sys_p)} 字）", flush=True)
            elif solo:
                sys_p = inc_sys
                print(f"[bridge] 单人模式（底稿来自OWI模型层 {len(inc_sys)} 字）", flush=True)
            else:
                try:
                    sys_p = open(PURE_PROMPT_FILE, encoding="utf-8").read().strip()
                except Exception:
                    sys_p = ""
                if not sys_p:
                    self._send(500, json.dumps({"error": {"message": "底稿文件缺失: " + PURE_PROMPT_FILE}}))
                    return
            # 注入区（用户定序，全压 system 顶部）：现实时间→关怀钩子→双人库→场景库→前情摘要→记忆宫召回
            # v3.5.9.1 执行小票：每块注入按序收进线程隔离收集器（keep-alive 复线程→每轮先清零），回复后落 JSONL
            _t_anchor = time.time()
            _rx()["inj"].clear()
            _rx().pop("usage", None)   # v3.8.1 防串轮
            _rx()["recalls"].clear()
            _rx().pop("t_first", None)   # v3.7.4 首字埋点随轮清零

            def _add_inj(name, text):
                if text:
                    _rx()["inj"].append({"name": name, "chars": len(text), "text_full": text})

            _reality = reality_block()
            sys_head = ""   # v3.8.2 缓存优化
            _add_inj("现实锚", _reality)
            _enb = english_block()   # v3.9.1 英语模式（热读开关，默认关）
            if _enb:
                sys_head += "\n\n" + _enb
                _add_inj("英语模式", _enb)
            chk_note = ""
            # v3.5.5 关怀钩子+单人指令：关怀挂双人/单人两线（任务调用跳过）；solo 指令只 solo 挂
            if not is_task:
                chk = checkin_directive()
                if chk:
                    sys_head += "\n\n" + chk
                    _add_inj("关怀钩子", chk)
                    chk_note = chk
            if solo:
                sys_head += "\n\n" + SOLO_DIRECTIVE
                _add_inj("单人指令", SOLO_DIRECTIVE)
            rec_ts, rec = latest_summary_full()
            if rec:
                # v3.5.6 前情提要带日期头：模型由此能推"昨天/上周"
                try:
                    _rd = datetime.fromtimestamp(rec_ts, CN_TZ)
                    _rhead = f"【前情提要（截至 {_rd.month} 月 {_rd.day} 日）】"
                except Exception:
                    _rhead = "【前情提要】"
                sys_head += "\n\n" + _rhead + rec
                _add_inj("前情提要", _rhead + rec)
            # v4.2.9 四路并行（v3.5.3 solo 守卫语义保留：单人模式记忆库/场景库连查询一起跳）
            for _nm, blk in _recall_family(bare, (("往日日志", lambda: journal_block(bare)),
                                                  ("记忆库", None if solo else lambda: kb_memory_block(bare)),
                                                  ("场景库", None if solo else lambda: kb_scene_block(bare)),
                                                  ("记忆宫", lambda: palace_recall_block(bare, _vec_for(bare))),
                                                  ("想法账本", lambda: ideas_recall_block(bare)))):   # v4.4.5 用户结论复述提醒（单人反刍同样要翻旧账）
                if blk:
                    sys_head += "\n\n" + blk
                    _add_inj(_nm, blk)
            if not is_task:
                sys_head += "\n\n" + EXPR_RULE   # v3.5.8 表情规则（单人/双人两线通用；任务调用不带）
                _add_inj("表情规则", EXPR_RULE)
                sys_head += "\n\n" + IDEA_SKILL_BLOCK   # v4.4.5 想法账本存档通道（常驻小块，用户明示才触发输出）
                _add_inj("想法账本·存档通道", IDEA_SKILL_BLOCK)
            solo_who = SOLO_MARK_WHO.get(mark, detect_solo_who(inc_sys)) if solo else ""
            if solo and solo_who:
                ln = lines_block(bare, solo_who)   # v3.5.9 台词库接线：腔调佐料，捞不到干净不带
                if ln:
                    sys_head += "\n\n" + ln
                    _add_inj("台词参考·" + solo_who, ln)
            # ==== v4.2.0 自拍令牌 [自拍][角色]（决策12 多令牌只认第一个；GEN_RE 自动触发退役）====
            # 命中→条件注入技能块（决策6：平时零 token）；入队延后到回复解析（<gen> 行才是场景真身）
            want_gen_id = None
            gen_hit_name = None
            if not is_task and not bare_test:
                gen_hit_name = _gen_token_hit(bare or "")   # v4.2.8 裸触发「生图」+旧括号令牌单口
                if gen_hit_name:
                    sys_head += "\n\n" + GEN_SKILL_BLOCK
                    _add_inj("自拍技能", GEN_SKILL_BLOCK)
                    print(f"[bridge] 自拍令牌命中: {gen_hit_name}", flush=True)
            # ==== v4.4.8/9 四格漫画令牌（「日记」=当日幂等看图；「重画日记」=强制重画；插画线回归 cron）====
            comic_ctx = None
            if not is_task and not bare_test and (_diary_token_hit(bare or "") or _diary_redraw_hit(bare or "")):
                _redraw = _diary_redraw_hit(bare or "")
                comic_ctx = _comic_payload(force=_redraw)   # 当日幂等；重画令牌=force 跳缓存
                if comic_ctx.get("ok"):
                    sys_head += "\n\n" + COMIC_SKILL_BLOCK
                    _add_inj("四格漫画技能", COMIC_SKILL_BLOCK)
                    print(f"[bridge] 日记令牌命中·四格: redraw={_redraw} dup={comic_ctx.get('duplicate', False)}", flush=True)
                else:
                    _cerr = str(comic_ctx.get("error") or "未知原因")
                    sys_head += "\n\n" + COMIC_FAIL_BLOCK_TMPL.format(err=_cerr)
                    _add_inj("四格漫画技能·失败", _cerr)
                    print(f"[bridge] 日记令牌失败·四格: {_cerr}", flush=True)
            # ==== v3.7.5 时光与羁绊（好感度账本+相识天数+回忆杀；任务调用不记不注入；fail-open）====
            st, aff_delta, _nost, _exam = None, 0, None, None
            if not is_task:
                try:
                    st = _bond_load()
                    if not st.get("first_day_ts"):
                        st["first_day_ts"] = _first_day_ts()
                    st, aff_delta = _affection_tick(st, bare)
                    _b_today = datetime.now(CN_TZ).strftime("%Y-%m-%d")
                    if int(_P("nostalgia_daily_max")) >= 1 and st.get("last_nostalgia") != _b_today and random.random() < (_P("nostalgia_prob") / 100.0):
                        # v3.7.6 学习池分抽：触发时若有学习卡 → 50% 改考题（考官线），否则旧事回忆
                        _ex = _exam_pick()
                        if _ex and random.random() < (_P("nostalgia_half") / 100.0):
                            _exam = {"date": str(_ex.get("date") or ""), "text": str(_ex.get("text") or "")}
                        else:
                            _nost = _nostalgia_pick({_b_today, (datetime.now(CN_TZ) - timedelta(days=1)).strftime("%Y-%m-%d")})
                        if _nost or _exam:
                            st["last_nostalgia"] = _b_today
                    _bond_save(st)
                except Exception as e:
                    _log("羁绊块异常(fail-open): " + str(e)[:100])
                    st, aff_delta, _nost, _exam = None, 0, None, None
                _bond_txt = _bond_summary(st)
                if _bond_txt:
                    sys_head += "\n\n" + _bond_txt
                    _add_inj("时光羁绊", _bond_txt)
                if _nost:
                    _n_txt = (f"【回忆杀】（旧日的回忆毫无预兆地涌上心头：{_nost.get('date', '')} 那天——"
                              f"{(_nost.get('text') or '')[:280]}。若与当下话题不冲突，就自然地提起那天的事。）")
                    sys_head += "\n\n" + _n_txt
                    _add_inj("回忆杀", _n_txt)
                if _exam:
                    _e_txt = (f"【考你一题】（你从学习账本里翻出 {_exam.get('date', '')} 记下的一张知识点卡，"
                              f"突然想考考主人君还记不记得。用你的口吻把下面的知识点变成一道问题抛给他，"
                              f"不要先说答案，等他答完你再点评。禁止提「账本/文件/记录/知识点卡」这类字眼。）\n"
                              f"知识点：{(_exam.get('text') or '')[:280]}")
                    sys_head += "\n\n" + _e_txt
                    _add_inj("考你一题", _e_txt)
            _t_recall_done = time.time()
            pmsg = [{"role": "system", "content": sys_head + "\n\n" + sys_p + (("\n\n" + _reality) if _reality else "")}]   # v3.8.2 现实锚挪尾部保前缀缓存
            pmsg += fetch_history_messages("st-live") if not solo else \
                [m for m in fetch_history_messages("st-live", tail=int(_P("vision_tail")) * 2) if m["role"] == "user"]
            # v3.5.5 二次修正（用户"数据不干净"判断实锤）：单人模式历史只带 user 消息——
            # 全局线 assistant 项全是双人同场回复，是蕾姆串场的活水源（18:43 话题1过/18:44 话题2
            # "雷姆在灶上炖着桂花蜜藕"再漏的根因）；连贯性由前情提要+记忆宫承担
            if solo:
                # v3.5.5 末位重申：紧贴 user 消息压 40 条双人 few-shot（GLM 中段 system 实测有效）
                pmsg.append({"role": "system", "content": SOLO_REASSERT})
            if chk_note:
                # v3.5.5 首测修正：关怀令只在顶部时被低档模型跳过（18:40 实测直接开答），
                # 末位再压一句短令保证"先关怀再答"
                pmsg.append({"role": "system",
                             "content": "【重申·开场关怀】你的回复第一句必须是主动关心：问他上次那件事进展如何"
                                        "（从前情提要里挑真有过的事），然后才回应他这条消息。"})
            if not is_task:
                pmsg.append({"role": "system", "content": EXPR_REASSERT})   # v3.5.8.1 末位重申
            if serious_mode and not is_task:   # v4.3.5 认真块置底（统一管线=无三人权重句）
                pmsg.append({"role": "system", "content": SERIOUS_BLOCK_SOLO})
                _add_inj("认真模式", SERIOUS_BLOCK_SOLO)
            if not is_task and IDEA_STORE_INTENT_RE.search(bare or ""):   # v4.4.6b 存档意图末位重申（D 案实锤：长回复丢末行指令）
                pmsg.append({"role": "system", "content": IDEA_STORE_REASSERT})
                _add_inj("存档重申", "意图命中")
            # v3.5.2：智谱脑带图透传（content 数组）；DS 脑（魔搭不支持图）维持拍平文本
            pmsg.append({"role": "user",
                         "content": user_multimodal if (user_multimodal and B["glm"]) else bare})

            if want_stream:
                _exg = _GenFilter() if gen_hit_name else None
                _ixf = _IdeaFilter() if not is_task else None   # v4.4.5 <idea> 存档行剥除+捕获（任务调用关）

                def _gen_tail():
                    # v4.2.0 流尾：取过滤器捕获的 <gen> 行入队并等图（决策5 无行=不入队不生成，静默）
                    _nm, _tg = _exg.hit or (None, None)
                    _tg = (_tg or "").strip()
                    if not _tg:
                        return None
                    _gid = _gen_enqueue(_tg, _gen_who(_nm, gen_hit_name))   # v4.2.6b who 终审
                    return _gen_wait_markdown(_gid)

                def _diary_tail():
                    # v4.4.8 流尾：台词+评分秒回+等四格整图（首触 ≤300s / 同日重复直出 URL）
                    return _comic_markdown(comic_ctx) if (comic_ctx and comic_ctx.get("ok")) else None

                text = zhipu_stream_relay(self, pmsg, model=B["label"], max_tokens=B["max_tokens"],
                                          temperature=_P('reply_temperature'), reasoning=B["effort"] or "low",
                                          upstream=B["upstream"], glm_params=B["glm"], model_name=B.get("model_name"),
                                          expr_who=(None if is_task else solo_who), no_think=B.get("no_think", False),
                                          gen_filter=_exg,
                                          idea_filter=_ixf,
                                          tail_supplier=(_gen_tail if _exg else (_diary_tail if (comic_ctx and comic_ctx.get("ok")) else None)))
                if _exg:
                    text = GEN_LINE_ANY_RE.sub("", GEN_LINE_RE.sub("", text)).strip()   # v4.2.6 写回剥行加宽容式（relay 返回原文）
                if _ixf:   # v4.4.5 存档收口：后台入库（fail-open）+写回剥行
                    if _ixf.hit:
                        threading.Thread(target=idea_store, args=(*_ixf.hit, bare), daemon=True).start()
                    text = IDEA_LINE_ANY_RE.sub("", text).strip()
            else:
                if B["glm"]:
                    r = httpx.post(ZHIPU, timeout=300,
                                   headers={"Authorization": f"Bearer {ZKEY}", "Content-Type": "application/json"},
                                   json={"model": "glm-5.3-flash", "thinking": {"type": "enabled"},
                                         "reasoning_effort": B["effort"], "max_tokens": B["max_tokens"],
                                         "temperature": _P("reply_temperature"), "messages": pmsg})
                    if r.status_code == 429:
                        text = QUOTA_DEAD_MSG if _quota_dead(r.text) else RATE_LIMIT_MSG
                        _log(f"{brain_id} 429，不重试直说限额")
                    else:
                        r.raise_for_status()
                        text = (r.json()["choices"][0]["message"].get("content") or "").strip()
                else:
                    try:
                        r = httpx.post((B.get("upstream") or (MS_URL, MSKEY))[0], timeout=300,
                                       headers={"Authorization": f"Bearer {(B.get('upstream') or (MS_URL, MSKEY))[1]}", "Content-Type": "application/json"},
                                       json={"model": B.get("model_name") or MS_MODEL, "max_tokens": B["max_tokens"], **({"reasoning_effort": B["effort"]} if B.get("effort") else {}), "temperature": _P("reply_temperature"),
                                             "messages": pmsg})
                        if r.status_code == 429:
                            text = MS_LIMIT_MSG
                            _log("上游 429（纪律不重试），直说限额")
                        else:
                            r.raise_for_status()
                            _j = r.json()
                            _usage_note(_j)   # v4.0.0 ds/local usage 透传（本地脑=llama-swap 真席名）
                            text = (_j["choices"][0]["message"].get("content") or "").strip()
                    except Exception as e:
                        _log("上游调用失败: " + str(e)[:150])
                        text = MS_LIMIT_MSG
                if not is_task and text not in (QUOTA_DEAD_MSG, RATE_LIMIT_MSG, MS_LIMIT_MSG):
                    text = expr_finish(text, solo_who)   # v3.5.8 表情标签→图 + neutral 兜底
                # v4.2.0 自拍收口：解析 <gen> 行（决策12 只认第一处）→剥行→入队→等图或失败提示句
                if gen_hit_name:
                    _gp = _gen_parse(text)   # v4.2.6 双式解析
                    if _gp:
                        text = (text[:_gp[2]] + text[_gp[3]:]).strip()
                        if _gp[1]:
                            want_gen_id = _gen_enqueue(_gp[1], _gen_who(_gp[0], gen_hit_name))   # v4.2.6b who 终审
                    _gmd = _gen_wait_markdown(want_gen_id)   # 无行=want_gen_id None=静默（决策5）
                    if _gmd:
                        text = text + "\n\n" + _gmd
                if comic_ctx and comic_ctx.get("ok"):   # v4.4.8 非流式四格收口：台词+评分+整图
                    _cmm = _comic_markdown(comic_ctx)
                    if _cmm:
                        text = text + "\n\n" + _cmm
                if not is_task:   # v4.4.5 非流式存档收口：剥行+后台入库
                    _ip = _idea_parse(text)
                    if _ip:
                        text = (text[:_ip[0]] + text[_ip[2]:]).strip()
                        threading.Thread(target=idea_store, args=(*_ip[1], bare), daemon=True).start()
                self._send(200, openai_response(text, model=B["label"], stream=False))


            _voice_ledger_put(text)   # v4.4.0 语音锚点账本（三人管线咽喉）
            # 写回区：chat_memory 双点 + 每 20 条摘要（v3.5.1 后台任务只答不记，审计照走）
            if not is_task:
                _base = int(time.time() * 1000)
                mem_write("st-live", "user", user, _base)
                _cl = _clean_for_memory(text)
                if _cl:
                    mem_write("st-live", "assistant", _cl, _base + 1)
                maybe_summarize("st-live")
                maybe_journal()   # v3.5.6 日志补账触发（事件驱动，后台跑不卡回复）
            _rotate_log("/root/work/logs/mentor-chain.log")
            try:
                with open("/root/work/logs/mentor-chain.log", "a", encoding="utf-8") as lf:
                    lf.write(json.dumps({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "mode": brain_id + ("·solo" if solo else "") + ("·task" if is_task else ""),
                                         "sec": round(time.time() - t0, 1), "user": user[:100]},
                                        ensure_ascii=False) + "\n")
            except Exception:
                pass
            _log(f"{brain_id} 回复({round(time.time() - t0, 1)}s): {text[:60]}")
            _rxd = _rx()
            _t1 = _rxd.pop("t_first", None)   # v3.7.4 首字真值；非流式/限额话=None
            _receipt_write({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "session": "st-live",
                            "mode": brain_id + ("·solo" if solo else "") + ("·task" if is_task else ""),
                            "provider": B.get("label", "?"), "user_text": bare[:500],
                            "injections": _rxd["inj"], "recalls": _rxd["recalls"],
                            "timings": {"recall_ms": round((_t_recall_done - _t_anchor) * 1000),
                                        "first_token_ms": (round((_t1 - t0) * 1000) if _t1 else None),
                                        "total_ms": round((time.time() - t0) * 1000)},
                            "writes": {"chat_memory": 0 if is_task else 2,
                                       "summary": not is_task, "journal": not is_task},
                            "expr": {"tags": len(EXPR_TAG_RE.findall(text))},
                            "bond": ({"score": st.get("score"), "delta": aff_delta, "nostalgia": bool(_nost),
                                      "exam": bool(_exam)} if st else None),
                            "error": None})
        except Exception as e:
            import traceback; traceback.print_exc(); _log("错误: " + str(e)[:200])
            try:
                _receipt_write({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "session": "st-live",
                                "mode": str(locals().get("brain_id", "?")),
                                "provider": str((locals().get("B") or {}).get("label", "?")),
                                "user_text": str(locals().get("bare", ""))[:300],
                                "injections": [], "recalls": [], "timings": {}, "writes": {}, "expr": {},
                                "error": str(e)[:300]})
            except Exception:
                pass
            try:
                self._send(500, json.dumps({"error": {"message": str(e)[:300]}}))
            except Exception:
                pass


# ==== v4.1.8 断连降噪：客户端中途掐线（手机切后台/网络抖动）写回复必抛连接异常，
# 裸 ThreadingHTTPServer 默认全栈 traceback 刷日志（337 条统计全为此类，零实害）→降一行摘要 ====
class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, TimeoutError)):
            _log(f"客户端中途断开 {client_address[0]}（写回复时连接已断，无实害）")
            return
        super().handle_error(request, client_address)


if __name__ == "__main__":
    BIND_IP = os.environ.get("BRIDGE_BIND", "127.0.0.1")
    # v4.1.7 三绑定：BIND_IP(默认127.0.0.1=管理台代理自查口) + EasyTier(轮询器) + docker网关(OWI拉模型)
    srv = QuietServer((BIND_IP, PORT), Handler)
    print(f"v3.7.6 统一管线桥已起 :{PORT} | 下拉: {'/'.join(BRAINS)} (默认 {DEFAULT_BRAIN}，含双人接力=姐妹轮转+duet小票+第一棒末位重申) | 旧名兼容: {len(_ALIASES)} | 任务保险丝: X-OpenWebUI-Task | 裸测: [裸测]前缀=只带系统提示词零写回 | 自拍: [自拍][角色]/裸触发「生图+角色」→PC轮询器→ComfyUI回传 | 考官: 回忆杀15%×50%抽learning_points.jsonl考题卡 | 图片透传: GLM脑 | 注入: 现实(今明天气+节日)+时光羁绊(相识天数+好感度)+关怀钩子(≥1h)+前情(截至X月X日)+往日日志+双人+场景+记忆宫+回忆杀(每日≤1次15%) | 单人线: 自带底稿+场内只有你 | 日志: chat_journal 事件驱动补账 | 历史40条全局线 | 流式思维链 | 429直说限额(不进记忆) | 日志轮转: 开 | 首字埋点: first_token_ms(流式小票) | 表情差分: 28情绪×拉姆蕾姆（OWI 同源静态 /expr） | v4.2.9 首字三刀: 注入族四路并行+同轮向量缓存+宫桥全池缓存", flush=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        srv2 = QuietServer(("10.14.14.1", PORT), Handler)
        print("v3.7.8 第二绑定 10.14.14.1:%d（EasyTier 轮询器口）" % PORT, flush=True)
        threading.Thread(target=srv2.serve_forever, daemon=True).start()
    except Exception as e:
        print(f"第二绑定失败({e})，单口运行", flush=True)
    # v4.1.7 第三绑定 172.19.0.1：docker 网关口，OWI 容器拉 /v1/models 专用。
    # 网段重建导致 IP 不在时只告警不崩桥（症状=酒馆下拉框空，桥本体不受影响）。
    try:
        srv3 = QuietServer(("172.19.0.1", PORT), Handler)
        print("v4.1.7 第三绑定 172.19.0.1:%d（docker OWI 口）" % PORT, flush=True)
        threading.Thread(target=srv3.serve_forever, daemon=True).start()
    except Exception as e:
        print(f"第三绑定失败({e})，OWI 容器口缺失", flush=True)
    srv.serve_forever()
