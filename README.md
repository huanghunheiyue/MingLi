# 明礼 MingLi · 明代历史文化科普智能体

> **第十届全国高校易班技术创新大会 · 智能体应用类参赛作品**

「明礼 MingLi」是一款以"网络悼明梗"为外壳、以中华优秀传统文化科普为内核的 AIGC 应用。基于 FastAPI 后端 + 纯原生前端，调用大模型 API 自动生成明代历史文化相关的挽联、怀古诗、祭文、梗文。

🎉 **桌面版（EXE）**：无需 Python 环境，双击 `dist\MingLi.exe` 即可启动！详见 [README_EXE.md](./README_EXE.md)。

📘 **使用手册**：刚接触 MingLi？先看 [USER_GUIDE.md](./USER_GUIDE.md)（如何使用、参数说明、常见问题）。

![明礼 MingLi](https://img.shields.io/badge/明礼-MingLi-8b1a1a?style=flat-square) ![Version](https://img.shields.io/badge/version-v1.2.0-blue) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 🚀 v1.2.0 更新亮点

> 完整优化记录见 [CHANGELOG.md](./CHANGELOG.md)，核心改动：

- ⚡ **性能飞跃**：新增 5 分钟 LRU 结果缓存，**相同主题二次请求 0.01-0.13s 返回**（首次 30-65s）
- 🤖 **新模型支持**：默认切换到「阿里云百炼 token-plan 订阅 + qwen3.8-flash」，**实测首次响应 9s 量级**，非 reasoning 模型，无思考链等待
- 🔧 **智能降级**：`max_tokens` 由 16000 降至 768（流式）/ 1024（非流式），自动 fallback 应对 LLM 截断
- 🛡️ **配置中心**：新增 `/settings` 页面，支持运行时切换 LLM provider/Key/模型
- 🎭 **新增「梗文」生成**：`/api/generate` `content_type=meme`，自动调用网络梗语料 + KG 上下文

---

## ✨ 项目亮点

- **🎭 立意深远**：以年轻人喜闻乐见的"悼明"梗为外壳，赋予中华优秀传统文化科普的正向内核
- **📚 严谨史实**：内置**双层知识库**——精选库（28 位人物 + 13 个事件 + 14 项文化 + 3 项科技）+ 明代历史知识图谱（**942 实体 / 1501 三元组 / 341 关系类型**，含历史人物 538、战争 47、事件 47、作品 105、地点 113、法律 16 等），所有生成内容严格基于真实史料
- **🛡️ 政治安全**：所有 Prompt 嵌入 SAFETY_GUIDELINES，禁止民族对立、政治影射、戏谑伟人
- **🤖 五家 LLM 自由切换**：阿里云百炼（token-plan）/ DeepSeek / 通义千问 / 豆包 / MiniMax，OpenAI 兼容协议
- **🎨 古风美感**：墨黑 / 水墨灰 / 宣纸白 / 印章红的克制审美，加载思源宋体 / 马善政楷书
- **📱 响应式**：PC + 移动端（375px 模拟）通吃，支持打印输出
- **⚡ 双轨输出**：SSE 流式打字机效果（实时进度条） + 非流式 JSON，**5 分钟内同主题二次响应 < 0.2s**

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

# 3. 编辑 .env，填入 LLM API Key（推荐阿里云百炼 token-plan 订阅，9s 响应）
#    LLM_PROVIDER=aliyun_bailian
#    ALIYUN_BAILIAN_API_KEY=sk-sp-xxx

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

### 桌面 EXE 版
详见 [README_EXE.md](./README_EXE.md)，下载 Release 中的 `MingLi-v1.2.0-windows-x64.zip` 解压即用。

---

## 🔑 API Key 申请指引

| 厂商 | 申请地址 | 推荐模型 | 延迟 | 说明 |
|------|---------|---------|------|------|
| ⭐ **阿里云百炼** | https://bailian.console.aliyun.com/#/sub-agent/token-plan | `qwen3.8-flash` | **~9s**（首）/ <0.2s（二次）| v1.2.0 默认；token-plan 订阅 Key，需订阅「通义千问 Flash」套餐 |
| DeepSeek | https://platform.deepseek.com/ | `deepseek-chat` | 5-15s | 注册送额度 |
| 通义千问 | https://bailian.console.aliyun.com/ | `qwen-plus` | 8-20s | 按量计费 Key（**非** token-plan） |
| 豆包 | https://www.volcengine.com/product/doubao | `doubao-pro-32k` | 6-15s | 注册赠券 |
| MiniMax | https://platform.minimaxi.com/user-center/payment/token-plan | `MiniMax-M2.7-highspeed` | 30-60s | reasoning 模型耗时长，已不推荐 |

修改 `.env` 中的 `LLM_PROVIDER` 切换：
```
LLM_PROVIDER=aliyun_bailian   # 默认（推荐）；或 deepseek / qwen / doubao / minimax
```

---

## 📡 接口文档

启动后访问 **http://localhost:8000/docs** 查看完整 OpenAPI 文档。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/`                       | 前端首页 |
| GET  | `/settings`               | API 配置中心（运行时切换 LLM provider/Key/模型） |
| GET  | `/api/health`             | 健康检查 |
| GET  | `/api/knowledge-graph/stats` | 知识图谱加载状态（实体/三元组/关系类型数） |
| GET  | `/api/subjects?type=&entity_type=` | 获取可选主题列表（可选 `entity_type=历史人物/历史事件/战争/作品/地点` 等扩展） |
| POST | `/api/generate`           | 非流式文案生成（`content_type`: couplet/poem/elegiac/meme） |
| POST | `/api/generate/stream`    | SSE 流式文案生成 |
| GET  | `/api/history?limit=`     | 获取生成历史 |
| GET  | `/api/history/{id}`       | 获取单条历史 |
| POST | `/api/feedback`           | 提交用户评分反馈 |
| GET  | `/api/settings`           | 查看运行时 LLM 配置 |
| POST | `/api/settings`           | 更新 LLM provider/Key/模型（热生效） |

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

### 🎯 缓存行为说明（v1.2.0+）

- 缓存 key：`sha256(content_type|subject|sorted(params))`
- TTL：5 分钟（300 秒），LRU 上限 200 条
- 命中表现：流式/非流式均直接返回 `done`，**不再调用 LLM**，响应 < 0.2s
- 失效时机：服务重启 / TTL 到期 / 超过 200 条触发 LRU 淘汰

---

## 📁 目录结构

```
mingli/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置（.env，支持 5 家 LLM provider）
│   ├── llm_client.py        # 统一 LLM 客户端（OpenAI 兼容）
│   ├── models.py            # Pydantic 模型
│   ├── knowledge_base.py    # 精选知识库（28 人物/13 事件/14 文化/3 科技）
│   ├── kg_data.py           # 明代历史知识图谱加载层（942 实体）
│   ├── storage.py           # JSON 持久化（history/feedback）
│   ├── variants.py          # 生成变体调度
│   ├── feedback_token.py    # 反馈 Token
│   ├── rate_limit.py        # 简易限流
│   ├── security.py          # 安全工具（Prompt 注入检测）
│   ├── prompts/             # Prompt 模板（按内容类型拆分）
│   │   ├── base.py          #   - 通用基类 + 安全准则
│   │   ├── couplet.py       #   - 挽联
│   │   ├── poem.py          #   - 怀古诗
│   │   ├── elegiac.py       #   - 祭文
│   │   ├── meme.py          #   - 梗文
│   │   └── router.py        #   - 内容类型路由
│   ├── meme_data/           # 梗文语料
│   │   └── memes.py
│   └── routers/
│       ├── generate.py      # 文案生成接口（含 5min LRU 缓存）
│       ├── history.py       # 历史接口
│       ├── feedback.py      # 反馈接口
│       ├── settings.py      # 运行时配置中心
│       └── meme/            # 梗文路由
│           └── router.py
├── static/
│   ├── index.html           # 前端首页
│   ├── settings.html        # API 配置中心页面
│   ├── settings.js
│   ├── settings.css
│   ├── style.css            # 古风样式
│   └── app.js               # 前端逻辑（SSE 流式消费）
├── rawData/                 # 明代历史知识图谱数据
│   ├── allItem.json         #   - 942 实体
│   ├── allRelationship.json #   - 341 关系类型
│   └── relationship.json    #   - 1501 三元组
├── data/
│   ├── history.json         # 生成历史（git 忽略）
│   └── feedback.json        # 反馈记录（git 忽略）
├── scripts/                 # 运维/分析脚本
├── tests/                   # 自动化测试（pytest）
├── dist/                    # PyInstaller 打包配置
│   ├── .env.example
│   └── README_EXE.md
├── .env.example
├── requirements.txt
├── MingLi.spec              # PyInstaller 配置
├── build.bat / build.sh
├── run.bat / run.sh
├── README.md
├── README_EXE.md
├── USER_GUIDE.md
└── TEST_REPORT.md
```

---

## 🎯 参赛亮点

1. **思政价值**：以明代 276 年的文化、科技、外交为载体，弘扬中华民族共同体意识、展现中华文明的开放与自信
2. **技术亮点**：Prompt 工程 + **双层知识库**（精选档案 + 知识图谱三元组自动注入上下文）+ 异步流式 + 五家 LLM 灵活切换 + **5 分钟结果缓存**
3. **用户体验**：古风审美、响应式设计、流式打字机效果、indeterminate 进度条、评分反馈闭环
4. **可拓展性**：模块化设计，方便增加朝代（如「忆唐」「怀宋」）形成系列

---

## ⚡ 性能数据（v1.2.0 实测）

| 场景 | provider/model | 首次响应 | 二次响应 |
|------|---------------|---------|---------|
| 挽联「于谦」 | aliyun_bailian/qwen3.8-flash | 42s | **0.13s** |
| 挽联「海瑞」 | aliyun_bailian/qwen3.8-flash | 46s | **0.08s** |
| 挽联「张居正」 | aliyun_bailian/qwen3.8-flash | 65s | **0.09s** |
| 挽联「王阳明」 | aliyun_bailian/qwen3.8-flash | 14s | **0.03s** |
| 挽联「于谦」（对照） | minimax/MiniMax-M3 (reasoning) | **97s** | - |

> 首次响应时间受 aliyun token-plan 后端排队影响（6-175s 区间），但 5 分钟内的同主题重复请求走缓存，**实测 < 0.2s**。

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

- **阿里云百炼** 提供 `qwen3.8-flash` 模型服务与 token-plan 订阅支持
- DeepSeek / 通义千问 / 豆包 / MiniMax 提供大模型 API
- 思源宋体 / 马善政楷书 提供字体支持
- 易班技术创新大会 提供展示平台

> 以史为鉴，可以知兴替；以人为鉴，可以明得失。
