"""
E2E: 启动 FastAPI，调用 /api/subjects 验证 KG 集成
"""
import os
import sys
import time
import subprocess
import urllib.request
import json

os.environ['PYTHONPATH'] = r'F:\mingli'
PYTHON = r'F:\qqbot-migration\astrbot\.venv\Scripts\python.exe'

# 启动 uvicorn 在后台
print('=== 启动 FastAPI ===')
proc = subprocess.Popen(
    [PYTHON, '-m', 'uvicorn', 'app.main:app', '--port', '8765', '--log-level', 'warning'],
    cwd=r'F:\mingli',
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

# 等服务起来
for i in range(20):
    time.sleep(0.5)
    try:
        r = urllib.request.urlopen('http://localhost:8765/', timeout=2)
        if r.status == 200:
            print(f'启动成功（{i*0.5:.1f}s）')
            break
    except Exception:
        continue
else:
    print('启动失败')
    proc.terminate()
    sys.exit(1)

try:
    print()
    print('=== 测试 1: GET /api/subjects?type=couplet（默认）===')
    r = urllib.request.urlopen('http://localhost:8765/api/subjects?type=couplet')
    data = json.loads(r.read())
    print(f'  content_type: {data["content_type"]}')
    print(f'  entity_type: {data["entity_type"]!r}')
    print(f'  kg_loaded: {data["kg_loaded"]}')
    print(f'  kg_stats: {data["kg_stats"]["entities"]} 实体 / {data["kg_stats"]["relationships"]} 关系')
    print(f'  subject 数量: {len(data["subjects"])}')
    print(f'  前 5 个: {data["subjects"][:5]}')

    print()
    print('=== 测试 2: GET /api/subjects?type=couplet&entity_type=战争 ===')
    from urllib.parse import quote
    url = 'http://localhost:8765/api/subjects?type=couplet&entity_type=' + quote('战争')
    r = urllib.request.urlopen(url)
    data = json.loads(r.read())
    print(f'  subject 数量: {len(data["subjects"])}')
    print(f'  前 10 个: {data["subjects"][:10]}')
    print(f'  末尾 5 个: {data["subjects"][-5:]}')

    print()
    print('=== 测试 3: GET /api/subjects?entity_type=历史人物（不带 type）===')
    url = 'http://localhost:8765/api/subjects?entity_type=' + quote('历史人物')
    r = urllib.request.urlopen(url)
    data = json.loads(r.read())
    print(f'  subject 数量: {len(data["subjects"])}')
    print(f'  前 5 个精选: {data["subjects"][:5]}')
    print(f'  KG 补充: {data["subjects"][30:35]}')

    print()
    print('=== 测试 4: GET /api/subjects?entity_type=作品 ===')
    url = 'http://localhost:8765/api/subjects?entity_type=' + quote('作品')
    r = urllib.request.urlopen(url)
    data = json.loads(r.read())
    print(f'  subject 数量: {len(data["subjects"])}')
    print(f'  前 8 个: {data["subjects"][:8]}')

    print()
    print('=== 测试 5: GET /api/subjects?type=eulogy ===')
    r = urllib.request.urlopen('http://localhost:8765/api/subjects?type=eulogy')
    data = json.loads(r.read())
    print(f'  eulogy subject 数量: {len(data["subjects"])}')
    assert len(data['subjects']) == 28, f'eulogy 应返回精选 28 人物，得到 {len(data["subjects"])}'

    print()
    print('=== 测试 6: 测 /api/knowledge-graph 统计 ===')
    # 加一个 KG 统计端点（如果没有则忽略）
    try:
        r = urllib.request.urlopen('http://localhost:8765/api/knowledge-graph/stats', timeout=2)
        if r.status == 200:
            data = json.loads(r.read())
            print(f'  KG stats: {data}')
    except urllib.error.HTTPError as e:
        print(f'  /api/knowledge-graph/stats 不存在（HTTP {e.code}）— 可加可不加')

    print()
    print('=== 全部测试通过 ===')

finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()