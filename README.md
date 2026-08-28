# 明礼 MingLi · 明代历史文化科普智能体

> **第十届全国高校易班技术创新大会 · 智能体应用类参赛作品**

「明礼 MingLi」是一款以"网络悼明梗"为外壳、以中华优秀传统文化科普为内核的 AIGC 应用。基于 FastAPI 后端 + 纯原生前端，调用大模型 API 自动生成明代历史文化相关的挽联、怀古诗、祭文、梗文。

🎉 **桌面版（EXE）**：无需 Python 环境，双击 `dist\MingLi.exe` 即可启动！详见 [README_EXE.md](./README_EXE.md)。

![明礼 MingLi](https://img.shields.io/badge/明礼-MingLi-8b1a1a?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ 项目亮点

- **🎭 立意深远**：以年轻人喜闻乐见的"悼明"梗为外壳，赋予中华优秀传统文化科普的正向内核
- **📚 严谨史实**：内置结构化明代知识库（28 位人物 + 13 个事件 + 14 项文化 + 3 项科技），所有生成内容严格基于真实史料
- **🛡️ 政治安全**：所有 Prompt 嵌入 SAFETY_GUIDELINES，禁止民族对立、政治影射、戏谑伟人
- **🤖 灵活模型**：支持 MiniMax / DeepSeek / 通义千问 / 豆包四家 LLM 自由切换（OpenAI 兼容协议）
- **🎨 古风美感**：墨黑 / 水墨灰 / 宣纸白 / 印章红的克制审美，加载思源宋体 / 马善政楷书
- **📱 响应式**：PC + 移动端（375px 模拟）通吃，支持打印输出
- **⚡ 流式输出**：SSE 流式打字机效果，逐字呈现文案生成过程

---

## 🚀 快速启动

### 环境要求
- Python 3.11+
- Windows / macOS / Linux

### 安装步骤

```bash
# 1. 克隆或下载本项目
cd mingli

# 2. 复制环境变量示例
cp .env.example .env

# 3. 编辑 .env，填入 LLM API Key（DeepSeek 推荐免费额度）

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动
python -m app.main
# 或
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 一键启动脚本

```bash
# Linux / macOS
./run.sh

# Windows
run.bat
```

启动后访问 **http://localhost:8000**

---

## 🔑 API Key 申请指引

| 厂商 | 申请地址 | 推荐模型 | 说明 |
|------|---------|---------|------|
| **MiniMax**（默认）| https://platform.minimaxi.com/user-center/payment/token-plan | MiniMax-M2.7-highspeed | Token Plan 订阅套餐，订阅 Key 只能用国内端点 api.minimaxi.com |
| DeepSeek | https://platform.deepseek.com/ | deepseek-chat | 注册送额度 |
| 通义千问 | https://bailian.console.aliyun.com/ | qwen-plus | 有免费额度 |
| 豆包 | https://www.volcengine.com/product/doubao | doubao-pro-32k | 注册赠券 |

修改 `.env` 中的 `LLM_PROVIDER` 切换：
```
LLM_PROVIDER=minimax   # 默认；或 deepseek / qwen / doubao
```

---

## 📡 接口文档

启动后访问 **http://localhost:8000/docs** 查看完整 OpenAPI 文档。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/`                       | 前端首页 |
| GET  | `/api/health`             | 健康检查 |
| GET  | `/api/subjects?type=`     | 获取可选主题列表 |
| POST | `/api/generate`           | 非流式文案生成 |
| POST | `/api/generate/stream`    | SSE 流式文案生成 |
| GET  | `/api/history?limit=`     | 获取生成历史 |
| GET  | `/api/history/{id}`       | 获取单条历史 |
| POST | `/api/feedback`           | 提交用户评分反馈 |

### 请求示例：生成挽联

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "couplet",
    "subject": "于谦",
    "relation": "后人",
    "occasion": "纪念日"
  }'
```

### 响应示例

```json
{
  "id": "uuid...",
  "title": "挽于谦",
  "upper": "一身铁胆扶明社",
  "lower": "百世清名照汗青",
  "horizontal": "浩气长存",
  "body": "一身铁胆扶明社\n百世清名照汗青\n横批：浩气长存",
  "tags": ["挽联", "忠臣"],
  "sources": ["知识库:于谦"],
  "elapsed_ms": 4321
}
```

---

## 📁 目录结构

```
mingli/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置（.env）
│   ├── llm_client.py        # 统一 LLM 客户端
│   ├── prompts.py           # 所有 Prompt 模板
│   ├── knowledge_base.py    # 明代知识库
│   ├── storage.py           # JSON 持久化
│   ├── models.py            # Pydantic 模型
│   └── routers/
│       ├── generate.py      # 文案生成接口
│       ├── history.py       # 历史接口
│       └── feedback.py      # 反馈接口
├── static/
│   ├── index.html           # 前端单页
│   ├── style.css            # 古风样式
│   └── app.js               # 前端逻辑
├── data/
│   ├── history.json         # 生成历史
│   └── feedback.json        # 反馈记录
├── tests/
│   └── test_smoke.py        # 冒烟测试
├── .env.example
├── requirements.txt
├── README.md
├── TEST_REPORT.md
├── run.sh
└── run.bat
```

---

## 🎯 参赛亮点

1. **思政价值**：以明代 276 年的文化、科技、外交为载体，弘扬中华民族共同体意识、展现中华文明的开放与自信
2. **技术亮点**：Prompt 工程 + 知识库 + 异步流式 + 三家 LLM 灵活切换
3. **用户体验**：古风审美、响应式设计、流式打字机效果、评分反馈闭环
4. **可拓展性**：模块化设计，方便增加朝代（如「忆唐」「怀宋」）形成系列

---

## 🌐 公网部署（ngrok）

```bash
# 安装 ngrok: https://ngrok.com/download
export NGROK_TOKEN=your-token-here  # 或在 .env 中配置
./run.sh                           # 自动启动 ngrok
```

入口链接格式：`https://xxxx.ngrok-free.app/`

---

## 📜 许可证

MIT License

---

## 🙏 致谢

- DeepSeek / 通义千问 / 豆包 提供大模型 API
- 思源宋体 / 马善政楷书 提供字体支持
- 易班技术创新大会 提供展示平台

> 以史为鉴，可以知兴替；以人为鉴，可以明得失。
