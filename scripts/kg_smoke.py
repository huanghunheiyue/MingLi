"""kg_data 加载烟雾测试"""
from app.kg_data import get_kg

kg = get_kg()
print('=== KG 统计 ===')
for k, v in kg.stats.items():
    print(f'  {k}: {v}')
print()

print('=== 朱元璋 相关三元组（去重后前 6 条）===')
for r in kg.get_relations('朱元璋')[:6]:
    print(f'  {r["RA"]} -[{r["relationship"]}]-> {r["RB"]}')
    if r['description']:
        print(f'    {r["description"][:80]}...')
print()

print('=== 唐寅（小众人物）相关三元组 ===')
for r in kg.get_relations('唐寅')[:5]:
    print(f'  {r["RA"]} -[{r["relationship"]}]-> {r["RB"]}')
    if r['description']:
        print(f'    {r["description"][:80]}...')
print()

print('=== 万历朝鲜之役（小众事件）相关三元组 ===')
for r in kg.get_relations('万历朝鲜之役')[:5]:
    print(f'  {r["RA"]} -[{r["relationship"]}]-> {r["RB"]}')
print()

print('=== 类型分布 ===')
for t in ['历史人物', '历史事件', '战争', '作品', '地点', '法律']:
    items = kg.list_entities_by_type(t)
    print(f'  {t}: {len(items)} 个，如 {items[:3]}')
print()

print('=== 搜索"严"字实体 ===')
for m in kg.search_entities('严')[:8]:
    print(f'  {m["item"]} [{m["type"]}] 度={m["degree"]}')