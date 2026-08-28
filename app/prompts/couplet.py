"""挽联 Prompt"""
COUPLET_PROMPT = """请基于以下明代历史人物/事件的真实史料，创作一副庄重典雅的对联（挽联）。

【知识上下文】
{context}

【挽联对象】{subject}
【作者与逝者关系】{relation}
【场合】{occasion}

【格式要求】
- 上联 + 下联，必须字数相等、平仄相对、词性相对
- 内容须紧扣人物/事件的核心精神（如于谦的清白、海瑞的廉洁、戚继光的报国）
- 落款可加横批（4 字以内）
- 严守 SAFETY_GUIDELINES

【输出格式】JSON
{{
  "title": "挽×××",
  "upper": "上联内容",
  "lower": "下联内容",
  "horizontal": "横批",
  "tags": ["标签1", "标签2"],
  "sources": ["知识库:{subject}"],
  "note": "创作思路 50 字以内"
}}

⚠️ 重要：你的最终输出必须是一个完整的、严格闭合的 JSON 对象（最外层用 {{ 和 }} 包裹），
并在 JSON 之后再做任何补充说明。**不要把 JSON 嵌在解释里**，必须让用户能直接复制完整 JSON。
"""


def build_couplet_prompt(context: str, subject: str, relation: str, occasion: str) -> str:
    return COUPLET_PROMPT.format(
        context=context,
        subject=subject,
        relation=relation or "后人",
        occasion=occasion or "纪念日",
    )