"""祭文 Prompt"""
ELEGIA_PROMPT = """请基于以下明代历史人物的史料，创作一篇祭文（或悼词）。

【知识上下文】
{context}

【祭奠对象】{subject}
【字数】{length} 字左右
【作者身份】{author_role}

【格式要求】
- 文言文与白话文兼可，但必须典雅、克制、有温度
- 含：背景引述、生平回顾、功过评述、哀悼抒情、思政升华
- 必须以'尚飨'或'伏惟尚飨'等祭文常用语结尾
- 严守 SAFETY_GUIDELINES

【输出格式】JSON
{{
  "title": "祭×××文",
  "body": "完整祭文",
  "tags": ["祭文", "{subject}"],
  "sources": ["知识库:{subject}"],
  "note": "创作思路"
}}
"""


def build_elegiac_prompt(context: str, subject: str, length: int, author_role: str) -> str:
    return ELEGIA_PROMPT.format(
        context=context,
        subject=subject,
        length=length or 500,
        author_role=author_role or "后人",
    )