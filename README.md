# 明礼 MingLi · 明代历史文化科普智能体

> **第十届全国高校易班技术创新大会 · 智能体应用类参赛作品**

「明礼 MingLi」是一款以"网络悼明梗"为外壳、以中华优秀传统文化科普为内核的 AIGC 应用。基于 FastAPI 后端 + 纯原生前端，调用大模型 API 自动生成明代历史文化相关的挽联、怀古诗、祭文、梗文。

🎉 **桌面版（EXE）**：无需 Python 环境，双击 `dist\MingLi.exe` 即可启动！详见 [README_EXE.md](./README_EXE.md)。

📘 **使用手册**：刚接触 MingLi？先看 [USER_GUIDE.md](./USER_GUIDE.md)（如何使用、参数说明、常见问题）。

![明礼 MingLi](https://img.shields.io/badge/明礼-MingLi-8b1a1a?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ 项目亮点

- **🎭 立意深远**：以年轻人喜闻乐见的"悼明"梗为外壳，赋予中华优秀传统文化科普的正向内核
- **📚 严谨史实**：内置**双层知识库**——精选库（28 位人物 + 13 个事件 + 14 项文化 + 3 项科技）+ 明代历史知识图谱（**942 实体 / 1501 三元组 / 341 关系类型**，含历史人物 538、战争 47、事件 47、作品 105、地点 113、法律 16 等），所有生成内容严格基于真实史料
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
| GET  | `/api/knowledge-graph/stats` | 知识图谱加载状态（实体/三元组/关系类型数） |
| GET  | `/api/subjects?type=&entity_type=` | 获取可选主题列表（可选 `entity_type=历史人物/历史事件/战争/作品/地点` 等扩展） |
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
│   ├── knowledge_base.py    # 精选知识库 + KG 上下文整合
│   ├── kg_data.py           # 明代历史知识图谱加载层
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
├── rawData/                 # 明代历史知识图谱数据
│   ├── allItem.json         #   - 942 实体
│   ├── allRelationship.json #   - 341 关系类型
│   └── relationship.json    #   - 1501 三元组
├── data/
│   ├── history.json         # 生成历史
│   └── feedback.json        # 反馈记录
├── tests/
│   ├── test_smoke.py        # 冒烟测试
│   └── test_kg_integration.py # 知识图谱集成测试
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
2. **技术亮点**：Prompt 工程 + **双层知识库**（精选档案 + 知识图谱三元组自动注入上下文）+ 异步流式 + 四家 LLM 灵活切换
3. **用户体验**：古风审美、响应式设计、流式打字机效果、评分反馈闭环
4. **可拓展性**：模块化设计，方便增加朝代（如「忆唐」「怀宋」）形成系列

---

## 📚 双层知识库说明

MingLi 内置**两层互补的知识体系**，保证所有生成内容都基于真实史实：

### 第一层：精选知识库（`app/knowledge_base.py`）
- 28 位代表性明代人物（帝王/名臣/武将/文人/科学家）
- 13 个重大事件（靖难之役、土木堡之变、张居正改革…）
- 14 项文化瑰宝（永乐大典、天工开物…）
- 3 项科技成就（十二平均律、《几何原本》前六卷…）
- 每条目附带 `category` / `era` / `key_events` / `achievements` / `quote` / `tags` 等结构化字段，供 Prompt 直接渲染

### 第二层：明代历史知识图谱（`app/kg_data.py` + `rawData/`）
源自开源项目 [Ming-Dynasty-Knowledge-Graph](https://github.com/aspxcor/Ming-Dynasty-Knowledge-Graph)：

| 维度 | 数量 |
|------|------|
| 实体 | **942**（历史人物 538 / 地点 113 / 作品 105 / 战争 47 / 历史事件 47 / 权力机构 18 / 法律 16 / 历史时期 8 / 其它 49）|
| 关系类型 | **341**（君臣 / 影响 / 参与 / 属于 / 画作 / 属于 / 父子 / 朋友 / 辅佐 …）|
| 三元组 (RA, rel, RB) | **1501**（每条带 `description` 史实描述，已自动去重爬虫复制）|

### 集成方式
- 默认精选库人物：返回精选档案 **+** 自动追加 KG 相关三元组作为补充上下文
- 仅 KG 主题（如唐寅、魏忠贤、万历朝鲜之役、露梁海战、海禁等精选库未覆盖）：返回纯 KG 上下文
- 前端每个面板有「📚 知识图谱」切换按钮，点击后下拉扩展为该类型全部实体（历史人物/事件/战争/作品/地点）
- `GET /api/knowledge-graph/stats` 可查看实时加载状态

### 数据清洗
- 65% 的 description 字段有爬虫复制粘贴冗余，集成时自动检测并截断
- 17 个孤儿实体（如「张益」）仅出现在 `relationship.json` 而不在 `allItem.json`，自动补建 placeholder

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
