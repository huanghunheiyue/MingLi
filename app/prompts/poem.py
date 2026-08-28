"""怀古诗 Prompt"""
POEM_PROMPT = """请基于以下明代历史事件/人物的史料，创作一首怀古诗或词。

【知识上下文】
{context}

【主题】{subject}
【诗体】{poem_type}  （七律/七绝/词牌名）
【可选人物】{person}

【格式要求】
- 严格遵守所选诗体（字数、押韵、平仄）
- 情感基调：怀古、沉思、以史为鉴，避免戏谑
- 严守 SAFETY_GUIDELINES

【输出格式】JSON
{{
  "title": "诗题",
  "body": "完整诗文（每句换行）",
  "tags": ["怀古", "{poem_type}"],
  "sources": ["知识库:{subject}"],
  "note": "创作说明"
}}
"""


def build_poem_prompt(context: str, subject: str, poem_type: str, person: str = "") -> str:
    return POEM_PROMPT.format(
        context=context,
        subject=subject,
        poem_type=poem_type or "七律",
        person=person or "",
    )