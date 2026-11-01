"""Работа с data.json: папки, подпапки, элементы"""

import json
import os
from pathlib import Path

DATA_FILE = Path("data.json")
BACKUP_FILE = Path("data.json.bak")
CURRENT_VERSION = 1


def default_data() -> dict:
    """Возвращение пустой структуры данных"""
    return {"version": CURRENT_VERSION, "collections": []}


def load_data(path: Path = DATA_FILE) -> dict:
    """Загрузка данных. Если основной файл битый — берется из бэкапа"""
    if not path.exists():
        return default_data()

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("version", CURRENT_VERSION)
        return data
    except (json.JSONDecodeError, OSError):
        # Если файл поврежден, пытаемся достать бэкап
        if BACKUP_FILE.exists():
            try:
                with BACKUP_FILE.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return default_data()


def save_data(data: dict, path: Path = DATA_FILE) -> None:
    """Атомарная запись (через временный файл) + создание бэкапа"""
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if path.exists():
        BACKUP_FILE.write_bytes(path.read_bytes())

    os.replace(tmp, path)


def _next_id(items: list) -> str:
    """Генерация уникального id вида item_001"""
    existing = {it.get("id") for it in items}
    n = 1
    while f"item_{n:03d}" in existing:
        n += 1
    return f"item_{n:03d}"


def create_folder(data: dict, parent: dict | None, name: str,
                  icon: str = "📁", color: str = "#4A90E2",
                  description: str = "") -> str:
    """Создание папки. Если parent=None — на верхнем уровне. Иначе — подпапки"""
    folder = {
        "id": _next_id(parent["items"] if parent else data["collections"]),
        "name": name,
        "icon": icon,
        "color": color,
        "description": description,
        "items": [],
    }
    if parent is None:
        data["collections"].append(folder)
    else:
        folder["type"] = "subfolder"
        parent["items"].append(folder)
    return folder["id"]


def delete_folder(data: dict, folder_id: str) -> bool:
    """Удаление папки верхнего уровня"""
    for i, c in enumerate(data["collections"]):
        if c["id"] == folder_id:
            data["collections"].pop(i)
            return True
    return False


def add_item(parent: dict, item_type: str, **kwargs) -> str:
    """Добавление элемента (file, url, note и т.д.) в папку"""
    item = {"id": _next_id(parent["items"]), "type": item_type}
    item.update(kwargs)
    parent["items"].append(item)
    return item["id"]


def remove_item(parent: dict, item_id: str) -> bool:
    """Удаление элемента из папки"""
    for i, it in enumerate(parent["items"]):
        if it["id"] == item_id:
            parent["items"].pop(i)
            return True
    return False