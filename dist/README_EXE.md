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
