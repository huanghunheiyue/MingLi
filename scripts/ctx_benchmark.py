"""评估 get_context_for_subject 输出长度，避免 prompt 爆炸"""
from app.knowledge_base import get_context_for_subject

cases = [
    ('朱元璋', '精选库+KG'),    # 在 FIGURES 中（28 个）
    ('于谦', '精选库+KG'),
    ('唐寅', '仅KG-人物'),      # KG 538 历史人物，但不在精选库
    ('戚继光', '精选库+KG'),
    ('万历朝鲜之役', '仅KG-事件'),  # KG 47 战争
    ('永乐大典', '仅KG-作品'),    # KG 105 作品
    ('魏忠贤', '仅KG-人物'),
    ('海禁', '仅KG-事件'),
    ('徐光启', '精选库+KG'),
    ('明朝', '仅KG-历史时期'),
    ('永乐大典', 'CULTURE+KG'),  # 在 CULTURE
    ('某不存在的人物', '完全未知'),
]

print(f'{"主题":<14} {"类型":<14} {"字符数":>8} {"行数":>5}')
print('-' * 50)
for subject, kind in cases:
    ctx = get_context_for_subject(subject)
    print(f'{subject:<14} {kind:<14} {len(ctx):>8} {ctx.count(chr(10)):>5}')
print()
print('=== 最大长度样本（朱由检）===')
print(get_context_for_subject('朱由检')[-800:])