import os
import platform
import subprocess
import webbrowser

def open_item(item: dict):
    """Открытие элемента в зависимости от его типа"""
    t = item.get("type")
    target = item.get("target")

    if t == "url":
        webbrowser.open(target)
    elif t in ("file", "folder", "app"):
        _open_local(target)
    # note и subfolder обрабатываются в самом GUI

def _open_local(path: str):
    """Открытие файла/папки с помощью системы"""
    system = platform.system()
    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":  # macOS
        subprocess.run(["open", path], check=False)
    else:  # Linux
        subprocess.run(["xdg-open", path], check=False)