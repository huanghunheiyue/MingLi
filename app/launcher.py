"""
MingLi 桌面启动器
=================
双击 MingLi.exe 时由 PyInstaller 引导执行：
    1. 在主进程内启动 uvicorn (127.0.0.1:8765)，在线程里 serve
    2. 等待 /api/health 通过
    3. 主线程创建 pywebview 窗口承载古风界面
    4. 窗口关闭 → 让 uvicorn 自然退出 → 进程结束

注意：
    - PyInstaller onefile 模式下 sys.executable 指向 MingLi.exe 本身，
      因此不能再用 `sys.executable -m uvicorn` 子进程方案（会引发递归调用）。
      故 uvicorn 直接以线程方式运行在本进程内。
    - 本文件刻意用 logging 模块写日志而非 print，以便 PyInstaller 加 console=False
      时用户依然能在 _server.log 看到诊断信息。
    - 任何 print() 在 console=False 时会被 PyInstaller bootloader 静默丢弃。

可独立运行（开发期）：
    python -m app.launcher
"""

from __future__ import annotations

import logging
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8765
HEALTH_URL = f"http://{HOST}:{PORT}/api/health"
HEALTH_TIMEOUT = 30
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 860

LOG_FORMAT = "[MingLi] %(asctime)s %(levelname)s %(message)s"
DATE_FORMAT = "%H:%M:%S"
_log: logging.Logger | None = None


def _exe_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _init_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("mingli.launcher")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    try:
        if sys.stderr and not sys.stderr.closed:
            sh = logging.StreamHandler(sys.stderr)
            sh.setFormatter(fmt)
            logger.addHandler(sh)
    except Exception:
        pass
    return logger


def _load_dotenv_if_exists(root: Path) -> None:
    env_file = root / ".env"
    if not env_file.exists():
        return
    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except Exception:
        pass


def _free_port(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        try:
            s.connect((host, port))
            return False
        except OSError:
            return True


def _wait_health(url: str, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        time.sleep(0.3)
    return False


def _run_uvicorn_thread(stop_event: threading.Event, log_path: Path):
    import uvicorn
    config = uvicorn.Config(
        "app.main:app",
        host=HOST,
        port=PORT,
        log_level="info",
        log_config=None,
        access_log=False,
    )
    server = uvicorn.Server(config)
    fmt = logging.Formatter("%(asctime)s [uvicorn] %(levelname)s %(name)s: %(message)s", DATE_FORMAT)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)

    def _serve():
        try:
            logging.getLogger().addHandler(file_handler)
            server.run()
        except Exception as e:
            if _log:
                _log.exception("uvicorn 异常退出: %s", e)

    t = threading.Thread(target=_serve, name="uvicorn-thread", daemon=True)
    t.start()
    while not stop_event.is_set():
        time.sleep(0.3)
    if _log:
        _log.info("正在停止 uvicorn…")
    server.should_exit = True
    t.join(timeout=5)


def _open_browser_fallback() -> None:
    try:
        webbrowser.open(f"http://{HOST}:{PORT}")
        if _log:
            _log.info(f"已在浏览器打开 http://{HOST}:{PORT}")
    except Exception as e:
        if _log:
            _log.error(f"无法打开浏览器: {e}")


def _wait_for_exit(stop_event: threading.Event):
    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


def main() -> int:
    global _log
    root = _exe_root()
    log_path = root / "_server.log"
    _log = _init_logger(log_path)
    _load_dotenv_if_exists(root)
    _log.info(f"工作目录: {root}")

    if not _free_port(HOST, PORT):
        _log.warning(f"端口 {PORT} 已被占用，直接打开现有实例…")
        _open_browser_fallback()
        return 0

    _log.info(f"日志文件: {log_path}")
    _log.info("正在启动后端服务（线程内嵌模式）…")

    stop_event = threading.Event()
    _run_uvicorn_thread(stop_event, log_path)

    try:
        ok = _wait_health(HEALTH_URL, HEALTH_TIMEOUT)
        if not ok:
            _log.error(f"后端启动超时（{HEALTH_TIMEOUT}s）。日志: {log_path}")
            stop_event.set()
            return 1
        _log.info(f"后端就绪：{HEALTH_URL}")

        try:
            import webview
        except Exception as e:
            _log.warning(f"pywebview 不可用 ({e})，降级为浏览器模式")
            _open_browser_fallback()
            _wait_for_exit(stop_event)
            return 0

        window = webview.create_window(
            title="明礼 · MingLi",
            url=f"http://{HOST}:{PORT}",
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            resizable=True,
            confirm_close=False,
        )

        def _on_closed():
            if _log:
                _log.info("窗口已关闭，正在清理…")

        window.events.closed += _on_closed

        try:
            webview.start()
        except Exception as e:
            _log.warning(f"pywebview 启动失败 ({e})，降级为浏览器模式")
            _open_browser_fallback()
            _wait_for_exit(stop_event)
            return 0

        stop_event.set()
        time.sleep(1)
        return 0
    except Exception as e:
        if _log:
            _log.exception("异常: %s", e)
        stop_event.set()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        if _log:
            _log.info("已终止")
        sys.exit(0)

def _wait_health(url: str, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        time.sleep(0.3)
    return False
