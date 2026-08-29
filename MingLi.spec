# -*- mode: python ; coding: utf-8 -*-
"""
MingLi.exe PyInstaller 规格文件
================================
用法:
    pyinstaller --clean --noconfirm MingLi.spec
产物:
    dist/MingLi.exe (单文件，自带 static / data / app 子包)
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

ROOT = Path('.').resolve()

# ---------- 数据文件 ----------
datas = [
    (str(ROOT / 'static'), 'static'),
    (str(ROOT / 'data'),   'data'),
    (str(ROOT / 'app' / 'prompts'),   'app/prompts'),
    (str(ROOT / 'app' / 'meme_data'), 'app/meme_data'),
    (str(ROOT / 'rawData'), 'rawData'),  # 明代历史知识图谱（942 实体 / 1501 三元组 / 341 关系类型）
]

# ---------- 隐藏导入（PyInstaller 不会自动发现子包） ----------
hiddenimports = []
hiddenimports += collect_submodules('uvicorn')      # 自动收齐 uvicorn 子模块
hiddenimports += collect_submodules('fastapi')      # 自动收齐 fastapi 子模块
hiddenimports += collect_submodules('pydantic')
hiddenimports += collect_submodules('anyio')
hiddenimports += collect_submodules('starlette')
hiddenimports += collect_submodules('httpx')
hiddenimports += collect_submodules('httpcore')
hiddenimports += collect_submodules('sniffio')
hiddenimports += collect_submodules('webview')      # 自动收齐 pywebview 子模块
hiddenimports += collect_submodules('clr_loader')
hiddenimports += collect_submodules('pythonnet')
hiddenimports += collect_submodules('app')

# 显式补几个关键模块（部分 importlib.metadata 在 frozen 下需要）
hiddenimports += [
    'app.main',
    'app.launcher',
    'app.config',
    'app.models',
    'app.storage',
    'app.security',
    'app.rate_limit',
    'app.feedback_token',
    'app.variants',
    'app.llm_client',
    'app.knowledge_base',
    'app.kg_data',         # 知识图谱加载层
    'app.prompts',
    'app.prompts.base',
    'app.prompts.couplet',
    'app.prompts.poem',
    'app.prompts.elegiac',
    'app.prompts.meme',
    'app.prompts.router',
    'app.meme_data',
    'app.meme_data.memes',
    'app.routers',
    'app.routers.generate',
    'app.routers.history',
    'app.routers.feedback',
    'app.routers.meme',
    'app.routers.meme.router',
    'app.routers.settings',
    # urllib 隐式依赖
    'email',
    'email.message',
    'email.feedparser',
    'email.parser',
    'email.utils',
    'email._header_value_parser',
    'email._parseaddr',
    'email.charset',
    'email.encoders',
    'email.errors',
    'email.header',
    'email.iterators',
    'email.contentmanager',
    '_ssl',
    'ssl',
    'socket',
    'select',
    # 一些在 PyInstaller frozen 下解析失败的常见模块
    'json',
    'http',
    'logging',
    'logging.config',
    'asyncio',
    'concurrent',
    'concurrent.futures',
]

hiddenimports = sorted(set(hiddenimports))

# ---------- 排除（瘦身） ----------
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'notebook',
    'IPython',
    'pytest',
    'pytest_asyncio',
    'setuptools',
    'pip',
    'wheel',
    'test',
    'tests',
    'unittest',
    'http.server',
    'xmlrpc',
    'lib2to3',
    'pydoc_data',
    'doctest',
]


a = Analysis(
    [str(ROOT / 'app' / 'launcher.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MingLi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # 无 cmd 窗口（双击即弹窗），日志全部写到 _server.log
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

