# 云上表情管线 SOP 与柜桥架构（20261007 定档）

## 一、架构一张图

```
[ComfyUI 本机烤图] → scp → [云端正本 /root/work/expr_assets/<角色>/<情绪>/N.png]
                                    │ docker cp（生效层）
                                    ▼
                    [OWI 容器 /app/build/expr/<角色>/<情绪>/N.png]（静态直服 /expr/...）
                                    ▲ 聊天读图
[桥 tavern-bridge-cloud.py] ── 表情标签 [[角色:情绪]] → 随机抽组内一张 → markdown ![..](/expr/<角色>/<情绪>/<随机文件名>)
[管理台 tavern-console.py :5679] ── 表情柜 v2.3（格子文字化+组图面板+加图/单张删/清空/同步/补缺）
```

- 目录约定（一词一组）：`<角色>/<情绪>/N.png` 优先（随机池）；退回 `<角色>/<情绪>.png`（旧单图兼容）
- 随机文件名=天然防缓存；柜预览 API 带 `Cache-Control: no-store`——**缓存无需做也不许做**
- OWI 暗色主题色值：gray-950/900/850 = oklch(16%/20%/27%)（约 #111~#2e2e2e，非纯黑）——白底图=亮框，候选优化=C 透明底抠图（未立项）

## 二、推云三步（照抄，别发明）

```bash
KEY=C:/Users/yourname/.zcode/keys/cloud_ed25519
HOST=root@10.14.14.1   # EasyTier 内网 IP；云端=腾讯云机

# ① 云端先备份（先抄后撕铁律）
ssh -i $KEY $HOST "mkdir -p /root/work/expr_assets/_backup/<日期-主题> && cp -r /root/work/expr_assets/emt /root/work/expr_assets/ram /root/work/expr_assets/rem /root/work/expr_assets/_backup/<日期-主题>/"

# ② 本地改名暂存 → scp（文件名=28 情绪标准名）
scp -i $KEY -q <暂存夹>/*.png $HOST:/root/work/expr_assets/<角色>/

# ③ 正本灌容器（docker cp 整角色目录，文件夹组会整体带入）
ssh -i $KEY $HOST "docker cp /root/work/expr_assets/<角色>/. open-webui-slim:/app/build/expr/<角色>/"
```

- 容器名=`open-webui-slim`，容器内生效层=`/app/build/expr`
- **双写纪律**：正本（永久仓，容器重建不丢）+容器（生效层）都要写；管理台「全部同步到容器」按钮=③的一键版（容器重建丢图救灾用）
- 桥取图只认文件名不认画风；PNG 100B~15MB 防呆

## 三、验收三连（每次动云上必跑）

```bash
# ① OWI 静态嵌套路径 200？
ssh -i $KEY $HOST "curl -s -o /dev/null -w '%{http_code}' -m8 http://127.0.0.1:3000/expr/<角色>/<情绪>/<文件名>"
# ② 桥随机抽输出 URL 对不对（导入测试，__main__ 有守卫可安全 import）
ssh -i $KEY $HOST "/root/memvenv/bin/python3 -c \"...spec_from_file_location('tb','/root/work/cloud-config/tavern-bridge-cloud.py')...m.expr_img('<角色>','<情绪>')\""
# ③ 柜 API 组数（同样 import console 后调 _expr_api_list()）
```

## 四、改云上代码的家法（桥/管理台）

1. **先备份**：`cp` 到 `/root/work/server-backups/<名>_bak-<日期>-<主题>.py`
2. **补丁走文件**：Write 本地补丁脚本 → scp 上云 → `python3` 执行；锚点 `count==1` 断言不唯一不动盘；`py_compile` 自检
3. **杀与启分两条 ssh**；杀条内禁目标文件名明文（用 `tavern-bridge-clo[u]d` 方括号法）；启条挂住≠失败，**先探活（ss -tln 端口）再判成败，勿盲重试（会双进程）**
4. **JS 改动必 node --check**（云端无 node：scp 回本地，`ast.literal_eval(PAGE)` 抽 `<script>` 后本地验；PAGE 是普通 `"""` 串非 f-string，花括号安全）
5. 桥端口 18170（127.0.0.1+10.14.14.1 双绑定）；管理台 5679（本地隧道 `ssh -N -L 15679:127.0.0.1:5679`）

## 五、服务定位速查

| 件 | 云端路径 | 作用 |
|---|---|---|
| 桥 | /root/work/cloud-config/tavern-bridge-cloud.py | 表情标签→随机抽图 URL；v2.2 起 EXPR_GROUP_DIR 组抽取 |
| 管理台 | /root/work/cloud-config/tavern-console.py | 表情柜 v2.3；API=/api/expr/list·files·preview?f=·upload·delete?f=·sync·pull·addrole |
| 正本仓 | /root/work/expr_assets/<角色>/<情绪>/ | 永久仓（docker cp 的源） |
| 容器 | open-webui-slim:/app/build/expr/ | 生效层（OWI 静态直服 /expr/） |
| 备份 | /root/work/expr_assets/_backup/ 与 /root/work/server-backups/ | 图备份 / 代码备份 |

## 六、本役补丁留痕（全部有备份，回滚=cp 反向覆盖）

| 补丁 | 备份 |
|---|---|
| emt 蕾姆占位撤销（emtfix） | tavern-bridge-cloud_bak-20261007-emtfix.py |
| 桥一词一组随机抽（exprgroup） | tavern-bridge-cloud_bak-20261007-exprgroup.py |
| 柜 v2.2 组化（console_group） | tavern-console_bak-20261007-exprgroup.py |
| 柜 v2.3 格子文字化+组面板（console_grid） | tavern-console_bak-20261007-gridv23.py |
| _backup 角色签过滤（underscore） | tavern-console_bak-20261007-underscore.py |
