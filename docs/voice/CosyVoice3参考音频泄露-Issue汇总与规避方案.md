> 📄 整理自 2026-09-05 对话记录归档 ｜ 主题：CosyVoice3 参考音频泄露与幻觉：Issue #1735/#1833/#1597 全文汇总 + inference_instruct2 规避写法 + spk2info 缓存结构 ｜ 原文行号：4617-4922

# CosyVoice3 参考音频泄露问题｜Issue汇总+调用样例+缓存spk2info说明
> 检索仓库：FunAudioLLM/CosyVoice，issue：#1735、#1833、#1597

## 一、Issue核心结论
1. **#1735 zero‑shot参考文本泄露**
现象：`inference_zero_shot`传入真实长`prompt_text`时，输出音频会混入参考音频的原话文本，同时伴随随机语气词、无意义碎音幻觉；流式推理会显著放大该bug，非流式概率降低。
官方回复：**这是模型序列拼接架构带来的固有概率性缺陷，无法通过简单改模型权重彻底根除，推荐业务侧切换`inference_instruct2`规避，不要向zero‑shot传入参考音频真实字幕**。
issue链接：https://github.com/FunAudioLLM/CosyVoice/issues/1735


使用Fun-CosyVoice3-0.5B-2512模型零样本声音克隆时大概率出现胡言乱语
 #1735
Closed
Closed
使用Fun-CosyVoice3-0.5B-2512模型零样本声音克隆时大概率出现胡言乱语
#1735
Description
tbxark
tbxark
opened on Dec 25, 2025
Describe the bug
使用 FunAudioLLM/Fun-CosyVoice3-0.5B-2512 模型通过最新代码和 cosyvoice.inference_zero_shot 方法进行声音克隆时,大概率出现胡言乱语输出,有时会正常播报。疑问是这种现象属于代码使用方式有误,还是模型存在幻觉或泛化问题?

To Reproduce
调用片段:

results = cosyvoice.inference_zero_shot(
    text,
    prompt_text,
    prompt_wav_path,
    stream=False,
)
for j in results:
    wav = j["tts_speech"]
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)
    elif wav.dim() == 2 and wav.size(0) != 1:
        wav = wav[:1, :]
    torchaudio.save(
        seg_path,
        wav,
        cosyvoice.sample_rate,
        bits_per_sample=16,
    )
    segment_paths. append(seg_path)
复现环境(conda):
python=3.10

CUDA:
nvcc: NVIDIA (R) Cuda compiler driver
Cuda compilation tools, release 12.0, V12.0.140

输入参数:

prompt 看着窗外缓缓下落的雨滴
text 小蝌蚪找妈妈,找啊找,找到一个好朋友。有朋自远方来,非奸即盗。
Expected behavior
应输出与输入文本对应的人声音频。

Additional context

当前推理结果大概率为无关、混乱的语音内容,有时短句可以正常播报
希望判定是代码用法有误,还是模型本身推理稳定性/幻觉问题
感谢!

Activity
tbxark commented on Dec 25, 2025
tbxark
tbxark
on Dec 25, 2025
Author
输入和输出的音频.zip

tao1261060556 commented on Dec 26, 2025
tao1261060556
tao1261060556
on Dec 26, 2025
我也遇到类似，而且推出来正常时还会出现音频开头有参照音频部分内容，该部分音频内容和参考音频相同而音调音色有所有不（应该是文本相同，可能把参考文本也加到推理文本了）

laishere commented on Dec 26, 2025
laishere
laishere
on Dec 26, 2025
在 https://www.modelscope.cn/studios/FunAudioLLM/Fun-CosyVoice3-0.5B 这里试了你的输入，换了几次 seed 输出都正常

laishere commented on Dec 26, 2025
laishere
laishere
on Dec 26, 2025
if mode_checkbox_group == '3s极速复刻':
    logging.info('get zero_shot inference request')
    set_all_random_seed(seed)
    speech_list = []
    for i in cosyvoice.inference_zero_shot(tts_text, 'You are a helpful assistant.<|endofprompt|>' + prompt_text, postprocess(prompt_wav), stream=stream, speed=speed):
        speech_list.append(i['tts_speech'])
    return (target_sr, torch.concat(speech_list, dim=1).numpy().flatten())
这是其中运行的脚本，我估计你可能是没有加 You are a helpful assistant.<|endofprompt|>

Reacted by TBXark
tbxark commented on Dec 27, 2025
tbxark
tbxark
on Dec 27, 2025
Author
if mode_checkbox_group == '3s极速复刻':
    logging.info('get zero_shot inference request')
    set_all_random_seed(seed)
    speech_list = []
    for i in cosyvoice.inference_zero_shot(tts_text, 'You are a helpful assistant.<|endofprompt|>' + prompt_text, postprocess(prompt_wav), stream=stream, speed=speed):
        speech_list.append(i['tts_speech'])
    return (target_sr, torch.concat(speech_list, dim=1).numpy().flatten())
这是其中运行的脚本，我估计你可能是没有加 You are a helpful assistant.<|endofprompt|>

确实是没有加 You are a helpful assistant.<|endofprompt|>。不知道还有这茬。回头我加上试一下。



2. **#1833 fastapi部署场景泄露**
现象：API封装反复调用`inference_zero_shot`、每次请求都传入完整参考音频+完整字幕，高频触发泄露；复现集中在本地二次封装服务，ModelScope网页demo做了特殊预处理所以复现少。
官方建议：**音色只提取一次，缓存speaker embedding，后续TTS推理复用，禁止每一句话都重新跑一遍zero‑shot克隆；优先使用inference_instruct2接口**。
issue链接：https://github.com/FunAudioLLM/CosyVoice/issues/1833


fastapi服务部署cv3问题：prompt_wav要怎么处理才不会让合成的语音开头带上prompt_text？
 #1833
Closed
Closed
fastapi服务部署cv3问题：prompt_wav要怎么处理才不会让合成的语音开头带上prompt_text？
#1833
Description
echoht
echoht
opened on Feb 13
问题一：直接用server.py部署的服务，用client.py请求时遇到报错。解决方案在issue里找到相关的：#1782
按照这个issue最后提供的代码改了load_wav，可以正常请求成功了。然后出现问题二。

问题二：请求过来的tts_text是”八百标兵奔北坡，北坡炮兵并排跑，炮兵怕把标兵碰，标兵怕碰炮兵炮。“；prompt_text是You are a helpful assistant.<|endofprompt|>希望你以后能够做的比我还好呦。

但是保存下来的合成音频是”比我还好呦。八百标兵奔北坡，北坡炮兵并排跑，炮兵怕把标兵碰，标兵怕碰炮兵炮。“

我试了把server.py的代码改造成不用client传来的prompt_wav而是直接传一个本地的zero_shot_prompt.wav路径，合成的音频的正常的。

我的问题是，如果要用client的prompt_wav，要怎么样才能让合成的音频是干净的，不带prompt_text?
还有个问题是为啥cosyvoice.inference_zero_shot的第三个参数，既可以传入参考音频的路径，也可以传入load_wav之后的speech呢？

Activity
zenghuiguan commented on Feb 13
zenghuiguan
zenghuiguan
on Feb 13
cv3 中，load_wav 传的应该是音频路径

gyj1201 commented on Feb 22
gyj1201
gyj1201
on Feb 22
这个问题我碰到过，prompt_text的长度太长，把prompt_text的长度控制在14个字以内，只要是prompt_text的长度太长，克隆出来后就会带上prompt_text

lornsoul commented on Mar 17
lornsoul
lornsoul
on Mar 17
改成inference_instruct2试试，prompt_text用You are a helpful assistant.<|endofprompt|>

Reacted by echoht
echoht commented on Mar 20
echoht
echoht
on Mar 20
Author
这个问题我碰到过，prompt_text的长度太长，把prompt_text的长度控制在14个字以内，只要是prompt_text的长度太长，克隆出来后就会带上prompt_text

音频和prompt_text可以长度不一致吗？

echoht commented on Mar 20
echoht
echoht
on Mar 20
Author
改成inference_instruct2试试，prompt_text用You are a helpful assistant.<|endofprompt|>

这个可以。


3. **#1597 CosyVoice2历史同类问题**
CV2存在同源缺陷，CV3‑0.5B继承并提升了触发概率；CV2/3的zero‑shot接口设计逻辑一致。
issue链接：https://github.com/FunAudioLLM/CosyVoice/issues/1597

问题描述 (Bug Description)
在使用 CosyVoice2-0.5B 的 inference_zero_shot() 时，当传入 prompt_text 参数后，LLM 会错误地将 prompt_text 的内容也合成为语音输出，而不是仅作为声音风格的条件信号。

When using CosyVoice2-0.5B's inference_zero_shot() with prompt_text, the LLM incorrectly synthesizes the prompt text as part of the output, instead of using it only as a conditioning signal for voice cloning.

复现步骤 (Steps to Reproduce)
使用 inference_zero_shot() 调用：
tts_text: "我是通义实验室语音团队全新推出的生成式语音大模型，提供舒适自然的语音合成能力。" (37字)
prompt_text: "第四十万，嗯，不要小看我们直播间好吧..." (101 tokens)
参考音频: 5.74秒
生成的音频长度约 28.52秒（预期应为 10-12秒）
音频内容包含了 tts_text 和 prompt_text 的内容
预期行为 (Expected Behavior)
prompt_text 应该仅用于引导声音风格，不应该被合成为语音。

实际行为 (Actual Behavior)
model.py 中的 llm_job() 方法将 prompt_text 传递给 llm.inference()，导致 LLM 将其视为需要合成的文本。

对比测试
跨语种复刻模式（prompt_text 为空）：生成 11.08秒音频 ✅ 正常
3s极速复刻模式（prompt_text 有101个token）：生成 28.52秒音频 ❌ 异常
临时修复方案 (Temporary Workaround)
在 cosyvoice/cli/model.py 的 llm_job() 方法中添加：

def llm_job(self, text, prompt_text, llm_prompt_speech_token, llm_embedding, uuid):
    # 临时修复：清空 prompt_text
    if prompt_text.shape[1] > 0:
        logging.info(f"[LLM Job] 检测到 prompt_text (shape={prompt_text.shape}),已强制清空")
        prompt_text = torch.zeros(1, 0, dtype=prompt_text.dtype)
    
    # 继续原有流程...
修复后音频长度恢复正常（11.08秒），RTF 从 1.06 降至 0.49。

环境信息 (Environment)

模型: CosyVoice2-0.5B

模式: Zero-shot voice cloning (3s极速复刻)

PyTorch: 2.5.0

CUDA: 12.4

操作系统: Windows

建议修复方向

建议检查 llm.inference() 方法如何处理 prompt_text 参数，确保它仅作为条件信号而不被包含在生成序列中。



> 重要事实：CosyVoice3对外暴露的`inference_instruct2`**没有对外暴露temperature参数**，源码内部flow温度写死，无法外部传入修改，和你在WSL源码观察结果一致。所有缓解手段只能做到**大幅降低泄露概率，无法100%归零**。

## 二、`inference_instruct2`正确调用示例（占位写法，不传入参考音频真实字幕）
> 关键点：`instruct_text`填固定占位字符串，**绝对不要填入参考干声的真实转写文本**；`prompt_wav`依旧传入你的音色参考音频，音色克隆能力保留。
```python
from cosyvoice.cli.cosyvoice import CosyVoice3
from cosyvoice.utils.common import set_all_random_seed
import torchaudio

# 固定随机种子，抑制随机幻觉语气词
set_all_random_seed(42)

cosyvoice = CosyVoice3("pretrained_models/CosyVoice3‑0.5B")

# 需要生成的目标文本
tts_target_text = "今天我们来调试语音克隆适配器。"
# 参考音色音频路径（雷姆干声wav）
ref_wav_path = "./rem_ref.wav"

# ----------------核心：instruct_text 使用占位文本，不要填参考音频的字幕！----------------
instruct_placeholder = "You are a helpful assistant.<|endofprompt|>"

# stream=False 必须非流式推理，流式会拉高泄露风险
for res in cosyvoice.inference_instruct2(
    tts_text=tts_target_text,
    instruct_text=instruct_placeholder,
    prompt_wav=ref_wav_path,
    zero_shot_spk_id="",
    stream=False,
    speed=1.0
):
    torchaudio.save("output.wav", res["tts_speech"], cosyvoice.sample_rate)
```

## 三、spk2info.pt 缓存音色条目结构
> 用于实现：**一次克隆，多次复用，每句话不再重复传入prompt_wav干声**，把泄露暴露次数从每句一次降到会话启动一次。

### 字段区分
1. `frontend_zero_shot`：对应zero‑shot克隆输出的音色信息
```python
# spk2info.pt 字典结构示例
spk2info = {
    "rem_spk": {
        "embedding": tensor([...]),       # speaker embedding向量
        "prompt_speech": tensor([...]),    # 参考音频mel特征
        "prompt_text": ""                  # instruct2缓存这里不需要真实字幕
    }
}
```
2. `frontend_sft`：对应微调/预定义speaker，字段多sft相关元数据，**不要把zero‑shot产出的embedding塞进frontend_sft，字段不匹配会报错**。

使用逻辑：
1. 会话启动：调用一次`inference_instruct2`，提取、保存`spk2info.pt`；
2. 后续每一句生成：加载缓存`spk2info["rem_spk"]`，直接走tts推理，**不再重复传入原始prompt_wav文件**；
3. 禁止循环每轮都重新加载wav跑克隆。

## 四、落地修复优先级（和你梳理的完全对齐）
1. ✅最高优先级：替换`inference_zero_shot` → `inference_instruct2`，`instruct_text`使用占位字符串，不再传入参考音频真实字幕，切断泄露源头。
2. ✅第二优先级：实现spk2info.pt音色缓存，会话只做1次音色提取，后续句子复用embedding，不再每句传入干声wav。
3. ✅第三优先级：全局固定`set_all_random_seed(42)`，抑制随机语气词幻觉。
4. ✅第四优先级：预处理参考音频，自动裁剪5‑8s干净人声片段。
5. ⚠️限制：CV3‑0.5B接口未暴露temperature，该参数无法做外部调整；架构缺陷存在极小概率依然会泄露。

## 五、需要规避的高危操作清单
1. ❌不要每一次TTS请求都重新传入完整参考wav干声；
2. ❌不要给`instruct_text`填入参考音频的真实转写字幕；
3. ❌不要打开`stream=True`做instruct2克隆推理，完整非流式生成wav，上层业务代码手动切片模拟伪流式输出。
