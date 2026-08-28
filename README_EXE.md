# 明礼 MingLi · 桌面版 (MingLi.exe)

> 一键启动的古风明代历史文化创作桌面应用。
> 双击 `MingLi.exe` → 自动弹出窗口 → 直接使用，无需 Python 环境。

---

## 🚀 快速开始

### 1. 准备配置文件

在 `dist\` 目录下创建 `.env`（或复制 `.env.example` 改名）：

```bash
# 推荐：复制模板后修改
copy dist\.env.example dist\.env
notepad dist\.env
```

至少填写一个 LLM 提供商的 API Key：

```env
# 默认 provider: MiniMax (Token Plan 订阅套餐)
# ⚠️ Token Plan 订阅 Key 只能用国内端点 api.minimaxi.com
# ⚠️ 订阅 Key 与按量计费 API Key 不互通
LLM_PROVIDER=minimax
MINIMAX_API_KEY=sk-cp-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.7-highspeed
```

支持四家：
| 提供商 | 申请地址 |
|---|---|
| **MiniMax**（默认，Token Plan 订阅） | https://platform.minimaxi.com/user-center/payment/token-plan |
| **DeepSeek** | https://platform.deepseek.com/ |
| **通义千问 Qwen** | https://bailian.console.aliyun.com/ |
| **豆包 Doubao** | https://www.volcengine.com/product/doubao |

### 2. 双击启动

双击 `dist\MingLi.exe`：
- 窗口标题：**明礼 · MingLi**
- 自动启动内置后端服务
- 窗口关闭 → 自动清理后端进程

> ⚠️ 即使没有 `.env`，exe 也能启动！只是梗文生成等 LLM 功能会提示失败，其他功能（浏览梗元素、历史、反馈）均可正常使用。

---

## 📦 重新打包

如果修改了代码或配置，需要重新构建 exe：

```cmd
:: Windows
build.bat
```

构建产物：
- `dist\MingLi.exe`（单文件，~40 MB）
- `dist\.env.example`（配置文件模板）

> 构建过程需要联网下载 PyInstaller 引导程序和补全隐藏导入，首次约 1-2 分钟。

---

## 🔧 高级使用

### 直接打开浏览器（不开桌面窗口）

如果你的系统缺少 WebView2 运行时，launcher 会自动退化到浏览器模式，
打开默认浏览器访问 `http://127.0.0.1:8765`。

### 自定义端口

编辑 `app\launcher.py`：
```python
PORT = 8765   # 改为你想要的端口
```
然后重新运行 `build.bat`。

### 查看运行日志

`dist\_server.log` 记录了后端启动和所有 API 请求。

### 调试模式（带 cmd 窗口）

如果遇到启动问题想看 console 输出，临时改 `MingLi.spec`：
```python
console=False   →   console=True
```
然后 `python -m PyInstaller --clean --noconfirm MingLi.spec`

---

## 📁 目录结构（开发期）

```
mingli/
├─ app/                       # 主程序包
│  ├─ main.py                 # FastAPI 入口
│  ├─ launcher.py             # 桌面启动器（PyInstaller 入口）
│  ├─ routers/                # API 路由
│  ├─ prompts/                # Prompt 模板包
│  ├─ meme_data/              # 梗元素库（36 条）
│  └─ ...
├─ static/                    # 古风前端
│  ├─ index.html
│  ├─ app.js
│  └─ style.css
├─ data/                      # 运行时数据（历史/反馈）
├─ tests/                     # 28 个测试用例
├─ MingLi.spec                # PyInstaller 配置
├─ build.bat                  # Windows 一键打包
└─ dist/                      # 构建产物
   ├─ MingLi.exe
   └─ .env.example
```

---

## ❓ 常见问题

**Q1: 双击 exe 闪退？**
A: 查看 `dist\_server.log`。99% 的情况是 `.env` 中 API Key 未配置或网络问题。

**Q2: 端口 8765 被占用？**
A: 关掉占用程序，或改 `launcher.py` 中的 `PORT` 后重新打包。

**Q3: WebView2 报错？**
A: Win10 1803 以下需要手动安装 https://developer.microsoft.com/en-us/microsoft-edge/webview2/

**Q4: 想换图标？**
A: 准备 256×256 的 .ico 文件，改 `MingLi.spec` 中 `icon='myicon.ico'`，重新打包。

**Q5: 体积能更小吗？**
A: 当前 40 MB 包含 Python 3.14 + FastAPI + uvicorn + pywebview。可加 UPX（已启用）压到 ~30 MB，但启动会略慢。

---

## 🎭 悼明之作·跨界梗（新功能）

把和明朝**毫无关系**的文化作品（动漫 / 游戏 / 电影 / 小说）强行嫁接到明代历史，
让 LLM 以明清史官考据之笔，**一本正经地胡扯**。

### 使用方式

桌面端：打开 MingLi 窗口 → 展开「🎭 悼明之作·跨界梗」折叠区 → 填写文化作品信息 → 一键生成。

API 调用：
```bash
curl -X POST http://127.0.0.1:8765/api/meme/crossover \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "work_name": "《原神》",
    "work_desc": "派蒙、蒙德城、元素力",
    "subject":   "郑和",
    "tone":      "考据",
    "length":    "中"
  }'
```

请求参数：
| 字段 | 必填 | 说明 |
|---|---|---|
| `work_name` | ✅ | 文化作品名称（≤80 字） |
| `work_desc` | ❌ | 元素 / 角色 / 道具 / 台词（≤400 字；空则基于作品名自动联想） |
| `subject`   | ❌ | 希望强行联系的明代人物 / 事件（≤40 字；空则随机抽 1 人物 + 1 事件） |
| `tone`      | ❌ | 文体：`考据`（默认）/ `奏疏` / `圣谕` / `县志` |
| `length`    | ❌ | 长度：`短`（80-150字）/ `中`（180-280字，默认）/ `长`（320-480字） |
| `hint`      | ❌ | 补充说明（≤500 字） |

### 4 种文体口吻

| 文体 | 历史原型 | 例 |
|---|---|---|
| **考据** | 明清史官考据学派 | "臣谨按"、"臣考"、"若合符节" |
| **奏疏** | 大臣奏章 | "臣翰林院侍读臣某某谨奏"、"谨为圣上陈之" |
| **圣谕** | 皇帝圣旨 | "奉天承运皇帝诏曰"、"着翰林院辑入《永乐大典》续编" |
| **县志** | 地方志 | "《某县志》卷六《遗事补遗》载：臣考..." |

### 经典案例

- **《原神》+郑和** → 《派蒙蒙德考》：派蒙 = 宝船随行幼童"小神通"；元素力 = 《天工开物》"五行科"；蒙德城 = "八风旋机"之制
- **《哈利·波特》+戚继光** → 《霍格沃茨遗制疏》：霍格沃茨 = 蓟镇空心敌台；魔杖 = 戚家军指挥棍；伏地魔 = 嘉靖海患"伏地海魔"
- **《让子弹飞》+空 subject** → 《子弹飞源考》（自动随机抽"袁崇焕 / 仁宣之治"）：张麻子 = "披麻执锐"义士；汤师爷 = 三杨辅政幕职；火车 = 红衣大炮弹飞如车

### 核心铁律

1. **严肃考据外壳 + 荒诞结论内核** —— 大量引用锦衣卫、翰林院、《永乐大典》、郑和、王阳明、戚继光、于谦、张居正、崇祯煤山、靖难之役、倭寇、阉党、东林党……
2. **绝不承认是胡扯** —— 文风严肃、克制、典雅，像明清史官/翰林/礼部官员在写奏章
3. **绝不贬低明朝** —— 所有"考据"都是在"证实"作品与明朝的渊源，立场始终"护明"
4. **不能戏谑真实历史人物** —— 朱元璋、崇祯、海瑞、于谦、王阳明等只能被"挂靠"为"源头"或"原型"
5. **绝不踩其他民族 / 地区 / 文化** —— 都要把作品源头"光荣化"地归于中华 / 明朝

---

## 🔗 相关文档

- `README.md` - 项目总览
- `TEST_REPORT.md` - 测试报告（28/28 通过）
- `requirements.txt` - 后端依赖

---

## ⚠️ 关于 API Key 401 报错

如果你看到类似：
```json
{"detail":"LLM 调用失败：... '401 Unauthorized' for url 'https://api.minimaxi.com/v1/chat/completions'"}
```

说明 `.env` 中的 `MINIMAX_API_KEY` 被服务器拒绝。常见原因：

1. **Key 已过期或被撤销** —— 重新到 [Token Plan 控制台](https://platform.minimaxi.com/user-center/payment/token-plan) 申请
2. **Key 格式错误** —— Token Plan 订阅 Key 以 `sk-cp-` 开头，请完整复制（注意**订阅 Key 与按量计费 API Key 不互通**）
3. **账户无付费资源** —— Token Plan 订阅 Key 需要先购买 Plus / Max / Ultra 套餐或积分才可用
4. **端点用错** —— 订阅 Key 只能用国内端点 `api.minimaxi.com`，不能用国际端点 `api.minimax.io`

**快速验证 Key 是否有效**（在 PowerShell 中）：
```powershell
curl https://api.minimaxi.com/v1/chat/completions `
  -H "Authorization: Bearer <你的 key>" `
  -H "Content-Type: application/json" `
  -d '{"model":"MiniMax-M3","messages":[{"role":"user","content":"hi"}]}'
```

**查询 Token Plan 用量余额**：
```powershell
curl https://www.minimaxi.com/v1/token_plan/remains `
  -H "Authorization: Bearer <你的 key>"
```

- ✅ 正常返回 200 → key 有效，刷新 .env 重启 exe
- ❌ `401 invalid api key (2049)` → key 失效或用错端点
- ❌ `403` → 账户未订阅 Token Plan 套餐或积分耗尽
