"""
明代历史文化知识图谱 - 加载层

数据源：rawData/allItem.json + allRelationship.json + relationship.json
- 942 实体、1501 三元组、341 关系类型

能力：实体-关系双向索引 + description 去重 + 上下文拉取
供 knowledge_base.get_context_for_subject() 调用，补全 FIGURES/EVENTS 未覆盖的人物/事件。
"""
import json
import os
from collections import defaultdict
from typing import Dict, List, Optional

# 三个候选位置（源码、exe 内置、exe 同级）
_KG_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), '..', 'rawData'),
    os.path.join(os.path.dirname(__file__), 'rawData'),
    os.path.dirname(__file__),
]


def _find_kg_dir() -> Optional[str]:
    for cand in _KG_CANDIDATES:
        cand = os.path.abspath(cand)
        if os.path.isdir(cand) and os.path.isfile(os.path.join(cand, 'allItem.json')):
            return cand
    return None


def _dedup_description(desc: str) -> str:
    """爬虫常把 description 重复一份，检测后保留前段"""
    desc = (desc or '').strip()
    if not desc:
        return desc
    n = len(desc)
    half = n // 2
    for off in range(0, 6):
        a = desc[:half + off].rstrip()
        b = desc[half + off:].lstrip()
        if len(a) >= 20 and b.startswith(a):
            return a
    return desc


def _load_json(path: str):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class MingDynastyKG:
    """单例加载器"""

    _instance: Optional['MingDynastyKG'] = None

    def __init__(self):
        self.entities: Dict[str, dict] = {}
        self.relationships: List[dict] = []
        self.relations_by_subject: Dict[str, List[dict]] = defaultdict(list)
        self.relations_by_object: Dict[str, List[dict]] = defaultdict(list)
        self.relation_types: set = set()
        self._loaded = False
        self.source_dir: Optional[str] = None
        self._load_errors: List[str] = []

    @classmethod
    def instance(cls) -> 'MingDynastyKG':
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load()
        return cls._instance

    def _load(self):
        kg_dir = _find_kg_dir()
        if not kg_dir:
            self._load_errors.append('未找到 rawData 目录')
            return
        self.source_dir = kg_dir
        try:
            items = _load_json(os.path.join(kg_dir, 'allItem.json'))['RECORDS']
            rels = _load_json(os.path.join(kg_dir, 'relationship.json'))['RECORDS']
        except Exception as e:
            self._load_errors.append(f'加载失败: {e}')
            return

        for it in items:
            self.entities[it['item']] = {'type': it['type']}

        for r in rels:
            ra = r.get('RA', '').strip()
            rb = r.get('RB', '').strip()
            rt = r.get('relationship', '').strip()
            desc = _dedup_description(r.get('description', ''))
            if not ra or not rb or not rt:
                continue
            triple = {'RA': ra, 'RB': rb, 'relationship': rt, 'description': desc}
            self.relationships.append(triple)
            self.relations_by_subject[ra].append(triple)
            self.relations_by_object[rb].append(triple)
            self.relation_types.add(rt)
            for node in (ra, rb):
                if node not in self.entities:
                    self.entities[node] = {'type': '?'}
                self.entities[node]['degree'] = \
                    self.entities[node].get('degree', 0) + 1

        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def stats(self) -> dict:
        return {
            'entities': len(self.entities),
            'relationships': len(self.relationships),
            'relation_types': len(self.relation_types),
            'source_dir': self.source_dir,
            'loaded': self._loaded,
            'errors': list(self._load_errors),
        }

    def get_entity_type(self, name: str) -> Optional[str]:
        return self.entities.get(name, {}).get('type')

    def get_relations(self, name: str, limit: int = 50,
                      include_description: bool = True) -> List[dict]:
        """获取与某实体相关的所有三元组（双向）"""
        if not self._loaded:
            return []
        triples = list(self.relations_by_subject.get(name, []))
        for t in self.relations_by_object.get(name, []):
            triples.append({
                'RA': t['RB'],
                'RB': t['RA'],
                'relationship': _inverse_relation(t['relationship']),
                'description': t['description'],
            })
        seen = set()
        uniq = []
        for t in triples:
            key = (t['RA'], t['RB'], t['relationship'])
            if key in seen:
                continue
            seen.add(key)
            uniq.append(t)
        if not include_description:
            for t in uniq:
                t.pop('description', None)
        return uniq[:limit]

    def list_entities_by_type(self, type_name: str) -> List[str]:
        if not self._loaded:
            return []
        return sorted([n for n, e in self.entities.items()
                       if e.get('type') == type_name])

    def search_entities(self, keyword: str, limit: int = 20) -> List[dict]:
        if not self._loaded or not keyword:
            return []
        kw = keyword.strip()
        matches = []
        for n, e in self.entities.items():
            if kw in n:
                matches.append({'item': n, 'type': e.get('type'),
                                'degree': e.get('degree', 0)})
        matches.sort(key=lambda x: (-x['degree'], x['item']))
        return matches[:limit]


# 关系反义表（客→主视角）
_INVERSES = {
    '父子': '子女', '子女': '父子',
    '朋友': '朋友', '敌对': '敌对',
    '战友': '战友', '同僚': '同僚',
    '夫妻': '夫妻', '兄弟': '兄弟',
    '君臣': '臣属于', '臣属于': '君臣',
    '辅佐': '被辅佐', '合作': '合作',
    '对立': '对立', '上下级': '下上级',
    '上司': '下属', '下属': '上司',
    '老师': '学生', '学生': '老师',
}


def _inverse_relation(r: str) -> str:
    return _INVERSES.get(r, r)


def get_kg() -> MingDynastyKG:
    return MingDynastyKG.instance()