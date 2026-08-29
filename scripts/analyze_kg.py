"""
分析 Ming-Dynasty-Knowledge-Graph 数据集
- 实体类型分布
- 关系类型分布
- description 重复检测
- 实体类型映射建议
"""
import json
from collections import Counter

KG_DIR = r'F:\Ming-Dynasty-Knowledge-Graph-main\rawData'

with open(f'{KG_DIR}\\allItem.json', encoding='utf-8') as f:
    items = json.load(f)['RECORDS']

with open(f'{KG_DIR}\\allRelationship.json', encoding='utf-8') as f:
    rel_types = json.load(f)['RECORDS']

with open(f'{KG_DIR}\\relationship.json', encoding='utf-8') as f:
    rels = json.load(f)['RECORDS']

print(f'实体: {len(items)}, 关系类型: {len(rel_types)}, 关系实例: {len(rels)}')
print()

# 实体类型分布
types = Counter(it['type'] for it in items)
print('=== 实体类型分布 ===')
for t, c in types.most_common():
    print(f'  {t}: {c}')
print()

# description 重复检测
desc_dup = 0
desc_lens = []
for r in rels:
    d = r.get('description', '')
    desc_lens.append(len(d))
    # 检测后半段是否与前半段重复
    n = len(d)
    if n >= 100:
        half = d[:n // 2].rstrip()
        second = d[n // 2:].lstrip()
        if second.startswith(half[:50]):
            desc_dup += 1
print(f'=== description 字段分析 ===')
print(f'总关系数: {len(rels)}')
print(f'description 长度: min={min(desc_lens)}, max={max(desc_lens)}, mean={sum(desc_lens)//len(desc_lens)}')
print(f'检测到重复的 description: {desc_dup}/{len(rels)} ({100*desc_dup/len(rels):.1f}%)')
print()

# 关系类型分布
r_types = Counter(r['relationship'] for r in rels)
print('=== 关系类型 Top 30 ===')
for t, c in r_types.most_common(30):
    print(f'  {t}: {c}')
print(f'共 {len(r_types)} 种关系类型')
print()

# 高频实体（被最多关系连接）
from collections import defaultdict
node_degree = defaultdict(int)
for r in rels:
    node_degree[r['RA']] += 1
    node_degree[r['RB']] += 1
print('=== 高度节点（被最多关系连接）Top 30 ===')
for name, deg in sorted(node_degree.items(), key=lambda x: -x[1])[:30]:
    # 查类型
    t = next((it['type'] for it in items if it['item'] == name), '?')
    print(f'  {deg:4d}  {name}  [{t}]')