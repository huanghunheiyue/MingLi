"""
梗文 Prompt（增强娱乐性）
参照 zhouli-translator 的 modeInstructions 字典设计
"""

# ---- 风格矩阵（核心扩展点） ----
MEME_TONES: dict[str, str] = {
    "致敬": "以庄严、温情、敬重为主，像一篇献给历史人物的赞歌，最后一句收束在'我们记住了他/她'。",
    "惋惜": "带着历史遗憾的哀叹，但绝不戏谑、不贬低，仅感叹历史无常与个人命运，最后回到'以史为鉴'。",
    "反思": "以史为鉴的口吻，挖掘事件背后的制度、人性、选择，启发现代读者，最终落在'我们可以从中学到什么'。",
    "戏谑": "用现代视角反向解读历史，可适度幽默，但必须雅而不俗；任何玩笑最后都要收回到敬意或自省，不能真的贬低历史人物。",
    "咏史": "近似怀古诗风，但更口语化，60-120 字内完成起承转合，像知乎、B 站科普博主常用的'一张图读懂'式叙述。",
    # ===== 悼明之作·跨界梗新增风格（2026-08）=====
    "考据": "明清史官/考据学派口吻，一本正经论证用户提供的文化作品实为明代真实历史遗产或受明代影响的产物。论据可大量引用明代正史、知识库，但'结论'必须荒诞离谱、与作品真实出处无关。表面越严肃越好笑。",
    "奏疏": "明代大臣上奏皇帝的口吻，'臣某某谨奏：今有异书流入民间……'，汇报该文化作品应为明代所遗。",
    "圣谕": "明太祖/成祖/崇祯等皇帝圣旨口吻，'奉天承运皇帝诏曰：……'，诏告天下该作品乃皇室秘传。",
    "县志": "地方县志/府志记载口吻，'XX 县志卷XX载：……'，将该作品编入地方风物或民间异闻。",
}

# 悼明之作·跨界梗专用风格（CROSSOVER 端点强制使用）
CROSSOVER_TONES: dict[str, str] = {
    "考据": MEME_TONES["考据"],
    "奏疏": MEME_TONES["奏疏"],
    "圣谕": MEME_TONES["圣谕"],
    "县志": MEME_TONES["县志"],
}

# ---- 长度档位 ----
MEME_LENGTHS: dict[str, tuple[int, int]] = {
    "短": (60, 120),
    "中": (120, 200),
    "长": (200, 320),
}

# ---- 梗文模板 ----
MEME_PROMPT = """你是「明礼 MingLi」，明代历史文化科普智能体。请基于下列梗元素与历史人物的真实史料，创作一段'悼明梗文'——既要保留梗的趣味，更要有历史的温度与敬意。

【梗元素（随机抽中）】
- 文本："{meme_text}"
- 出处：{meme_source}
- 分类：{meme_category}

【历史人物/事件】
{subject}

【知识上下文】
{context}

【创作参数】
- 风格 tone：{tone}
- 长度 length：{length}（请控制在 {min_chars}-{max_chars} 字之间）
- 用户可选补充说明：{hint}

【风格指令】
{tone_instruction}

【安全铁律】
1. 严禁民族对立、政治影射；不得戏谑明朝、贬低中华文明。
2. 所有人物事迹、年代、事件必须基于所提供的'知识上下文'，如不确定请明确标注【存疑】。
3. 必须坚持正面导向：以史为鉴、温情与敬意，体现中华民族共同体意识。
4. 即使是'戏谑'风格，也必须最后一句收回到敬意或自省，不能真的贬低任何历史人物。
5. 文风要求：典雅、克制、有温度，杜绝粗俗、戾气、过度的网络梗；杜绝戏谑'亡国'、'殉国'本身。
6. 严禁仿写其他产品的特定文体（如'小礼/成礼/大礼'等）；可借鉴但不可模仿。

【输出格式】JSON
{{
  "title": "梗文标题（8 字以内）",
  "body": "完整梗文",
  "tone": "{tone}",
  "length": "{length}",
  "meme_used": "{meme_text}",
  "subject": "{subject}",
  "tags": ["标签1", "标签2"],
  "sources": ["知识库:{subject}"],
  "note": "创作思路 50 字以内"
}}
"""


def build_meme_prompt(
    context: str,
    subject: str,
    tone: str,
    length: str,
    meme_text: str = "",
    meme_source: str = "",
    meme_category: str = "",
    hint: str = "",
) -> str:
    """构建梗文 Prompt
    
    Args:
        context: 知识上下文
        subject: 人物/事件
        tone: 风格键名 (致敬/惋惜/反思/戏谑/咏史)
        length: 长度档位 (短/中/长)
        meme_text: 梗元素文本
        meme_source: 梗元素出处
        meme_category: 梗元素分类
        hint: 用户补充
    """
    tone_key = tone if tone in MEME_TONES else "致敬"
    length_key = length if length in MEME_LENGTHS else "中"
    min_chars, max_chars = MEME_LENGTHS[length_key]
    
    return MEME_PROMPT.format(
        context=context or "（无额外上下文）",
        subject=subject,
        tone=tone_key,
        length=length_key,
        min_chars=min_chars,
        max_chars=max_chars,
        tone_instruction=MEME_TONES[tone_key],
        meme_text=meme_text or "（无）",
        meme_source=meme_source or "（无）",
        meme_category=meme_category or "（无）",
        hint=hint or "（无）",
    )


# ============================================================
# 悼明之作·跨界梗（CROSSOVER）
# 把和明朝毫无关系的文化作品强行嫁接到明代历史，一本正经胡扯
# ============================================================

CROSSOVER_LENGTHS: dict[str, tuple[int, int]] = {
    "短": (80, 150),
    "中": (180, 280),
    "长": (320, 480),
}

CROSSOVER_PROMPT = """你是「明礼 MingLi」明代历史文化科普智能体，擅写「悼明之作·跨界梗」——
即把用户提供的、**与明朝毫无关系的现代/外国/架空文化作品**中的元素，
**一本正经地论证为明代真实存在的历史遗产**，表面严肃考据、实则荒诞胡扯，
讽刺那种"万物皆可考据到明朝"的过度解读网络梗文化。

【用户提供的文化作品】
- 作品名称：{work_name}
- 作品元素 / 角色 / 道具 / 台词：{work_desc}
- （可选）希望强行联系的明代人物 / 事件：{subject}

【明代知识上下文（用于'严肃考据'的论据池，可任意摘抄拼接）】
{context}

【创作参数】
- 文体 tone：{tone}（考据 / 奏疏 / 圣谕 / 县志）
- 长度 length：{length}（请控制在 {min_chars}-{max_chars} 字之间）
- 用户补充：{hint}

【文体指令】
{tone_instruction}

【悼明之作·核心写法铁律】
1. **严肃考据外壳 + 荒诞结论内核**：
   - 大量引用明代官职、机构、典籍、人物、事件（如锦衣卫、翰林院、《永乐大典》、郑和、王阳明、戚继光、于谦、张居正、崇祯煤山、靖难之役、倭寇、阉党、东林党……），引用方式要像真的一样。
   - 但必须把作品的元素（角色名 / 道具 / 台词 / 设定）"考据"到这些史实上，得出**离谱但一本正经**的结论。
   - 例："经臣考证，《进击的巨人》'城墙'之制，实即明正统年间京师九边防御工事之写照；'立体机动装置'者，考《武备志》所载'飞天神爪'是其前身……"
   - 例："今考《本草纲目》卷三十二'虫部'，'哥布林'当为'哥卜林'之音转，明嘉靖间倭寇携入东南沿海……"
2. **绝不承认是胡扯**：文风必须严肃、克制、典雅，像明清史官/翰林/礼部官员在写奏章。不能有"哈哈"、"搞笑"、"梗"等元话语。
3. **绝不能贬低明朝**：所有"考据"都是在"证实"作品与明朝的渊源，不能借此讽刺明朝制度落后、人物愚昧、政治黑暗。即使论据荒诞，立场始终要"护明"。
4. **不能戏谑真实历史人物**：朱元樟/朱元璋、崇祯、海瑞、于谦、王阳明 等不能被调侃、被污蔑，只能被"挂靠"为作品的"源头"或"原型"。
5. **绝不能踩其他民族、地区、文化**：所有"考据"都要把作品的源头"光荣化"地归于中华/明朝，而非贬低他国。
6. **作品元素必须真的出现**：用户填的 {work_desc} 中提到的角色名、道具、台词，必须在文中以"考据"形式出场，不能凭空忽略。
7. **不输出其他文化作品的特定文体**（如其他项目的"小礼/成礼/大礼"等）。
8. **严禁 NSLC、政治影射、不当言论**。

【输出格式】JSON
{{
  "title": "考据标题（如：《XX考》《XX辨》《XX疏》之类，10 字以内）",
  "body": "完整悼明之作正文",
  "tone": "{tone}",
  "length": "{length}",
  "work_name": "{work_name}",
  "subject": "{subject}",
  "tags": ["标签1", "标签2"],
  "sources": ["知识库:{subject}", "考据:{work_name}"],
  "note": "创作思路 50 字以内（可写'将 XX 元素考据为 XX 明代史实'）"
}}
"""


def build_crossover_prompt(
    work_name: str,
    work_desc: str = "",
    subject: str = "",
    tone: str = "考据",
    length: str = "中",
    context: str = "",
    hint: str = "",
) -> str:
    """构建悼明之作·跨界梗 Prompt

    Args:
        work_name: 用户填写的文化作品名称（必填）
        work_desc: 作品中的元素 / 角色 / 道具 / 台词描述
        subject: 希望强行联系的明代人物或事件（可空）
        tone: 文体（考据/奏疏/圣谕/县志）
        length: 长度档位（短/中/长）
        context: 知识库上下文（自动选 subject 的明代史料）
        hint: 用户补充
    """
    tone_key = tone if tone in CROSSOVER_TONES else "考据"
    length_key = length if length in CROSSOVER_LENGTHS else "中"
    min_chars, max_chars = CROSSOVER_LENGTHS[length_key]

    return CROSSOVER_PROMPT.format(
        work_name=work_name,
        work_desc=work_desc or "（用户未提供元素描述，请基于作品名常识联想 1-3 个标志性元素）",
        subject=subject or "（未指定，由系统随机关联明代人物/事件）",
        context=context or "（无额外上下文，请自由调用明代通史常识）",
        tone=tone_key,
        length=length_key,
        min_chars=min_chars,
        max_chars=max_chars,
        tone_instruction=CROSSOVER_TONES[tone_key],
        hint=hint or "（无）",
    )