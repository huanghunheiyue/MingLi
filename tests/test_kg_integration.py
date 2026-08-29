"""
测试 app/kg_data.py 与 knowledge_base.py 的集成

覆盖：
- KG 加载（942+ 实体、1501 三元组、341 关系类型）
- description 去重
- get_context_for_subject 三种路径（精选库/仅 KG/未知）
- list_subjects 按 KG 类型过滤
- search_subjects 关键词搜索
"""
from app.kg_data import get_kg, MingDynastyKG, _dedup_description
from app.knowledge_base import (
    get_context_for_subject, list_subjects, search_subjects,
    FIGURES, EVENTS, CULTURE,
)


def test_dedup_description():
    """description 复制粘贴去重"""
    # 长文本复制（>20 字符触发去重阈值）
    raw = '朱元璋，字国瑞，明朝开国皇帝，年号洪武，在位三十一年' * 2
    out = _dedup_description(raw)
    assert out == '朱元璋，字国瑞，明朝开国皇帝，年号洪武，在位三十一年', \
        f'去重失败：{out}'
    # 短文本保持原样
    assert _dedup_description('') == ''
    assert _dedup_description('短文本') == '短文本'
    assert _dedup_description('明') == '明'


def test_kg_load_stats():
    """KG 加载统计"""
    kg = get_kg()
    s = kg.stats
    assert s['loaded'] is True
    assert s['entities'] >= 942
    assert s['relationships'] == 1501
    assert s['relation_types'] == 341
    assert 'rawData' in (s['source_dir'] or '')


def test_kg_relations_subject():
    """朱元璋作为 RA 应有 ≥10 条关系；客体方向视数据而定"""
    kg = get_kg()
    rs = kg.get_relations('朱元璋', limit=50)
    assert len(rs) >= 10, f'朱元璋关系数太少：{len(rs)}'
    has_subject_role = any(r['RA'] == '朱元璋' for r in rs)
    assert has_subject_role, '朱元璋作为主体没有返回'
    # 双向索引正常工作（即便数据中客体方向为零也应返回空列表而不是出错）


def test_kg_search():
    """搜索实体"""
    kg = get_kg()
    res = kg.search_entities('朱')
    assert len(res) > 0
    assert all('item' in r and 'type' in r and 'degree' in r for r in res)
    # 度数排序
    degs = [r['degree'] for r in res]
    assert degs == sorted(degs, reverse=True), '应按度数降序'


def test_kg_type_listing():
    """按类型列出实体"""
    kg = get_kg()
    persons = kg.list_entities_by_type('历史人物')
    wars = kg.list_entities_by_type('战争')
    works = kg.list_entities_by_type('作品')
    assert len(persons) >= 500
    assert len(wars) >= 40
    assert len(works) >= 100
    # 返回 sorted list
    assert persons == sorted(persons)


def test_context_curated_subject():
    """精选库内人物：返回精选库档案 + KG 补充"""
    ctx = get_context_for_subject('朱元璋')
    assert '人物：朱元璋' in ctx
    assert '类别：帝王' in ctx
    assert '【知识图谱补充】' in ctx, '精选库人物应自动追加 KG'
    # KG 补充至少包含一些关系条目
    assert '君臣' in ctx or '辅佐' in ctx or '重用' in ctx


def test_context_kg_only_subject():
    """仅 KG 主题：返回纯 KG 上下文"""
    ctx = get_context_for_subject('唐寅')
    assert '唐寅' in ctx
    assert '【知识图谱补充】' in ctx
    # 唐寅 KG 中都是画作
    assert '画作' in ctx


def test_context_unknown_subject():
    """完全未知主题：返回 fallback 文本"""
    ctx = get_context_for_subject('某不存在的人物_xyz')
    assert '暂无详细背景' in ctx or '请基于明代历史文化宏观把握' in ctx


def test_context_max_chars_truncation():
    """max_chars 限制生效"""
    ctx = get_context_for_subject('朱元璋', max_chars=300)
    assert len(ctx) <= 320  # 300 + 截断标记
    assert '截断' in ctx


def test_context_include_kg_false():
    """include_kg=False 时不附加 KG"""
    ctx = get_context_for_subject('朱元璋', include_kg=False)
    assert '【知识图谱补充】' not in ctx
    assert '人物：朱元璋' in ctx  # 精选库仍返回


def test_list_subjects_default():
    """默认：精选库优先"""
    items = list_subjects()
    assert '朱元璋' in items
    assert len(items) >= len(FIGURES) + len(EVENTS)


def test_list_subjects_with_type_filter():
    """type_filter=战争 返回精选库+战争 KG"""
    items = list_subjects(type_filter='战争')
    assert len(items) > 50
    # 应包含 KG 战争实体（精选库没有这些战争条目）
    kg_wars = get_kg().list_entities_by_type('战争')
    sample_war = kg_wars[5]
    assert sample_war in items


def test_list_subjects_eulogy():
    """eulogy 仅返回精选库 FIGURES"""
    items = list_subjects('eulogy')
    assert items == sorted(FIGURES.keys())


def test_search_subjects():
    """search_subjects 接口"""
    res = search_subjects('严')
    assert len(res) > 0
    assert all('item' in r for r in res)
    assert any(r['item'] == '严嵩' for r in res)


if __name__ == '__main__':
    import pytest
    raise SystemExit(pytest.main([__file__, '-v']))