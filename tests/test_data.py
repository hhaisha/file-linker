import pytest
from core import data as d


@pytest.fixture
def tmp_data(tmp_path, monkeypatch):
    """Изоляция файлов JSON, чтобы не задело реальные данные"""
    monkeypatch.setattr(d, "DATA_FILE", tmp_path / "data.json")
    monkeypatch.setattr(d, "BACKUP_FILE", tmp_path / "data.json.bak")
    return tmp_path


def test_create_folder(tmp_data):
    data = d.default_data()
    fid = d.create_folder(data, None, "Работа", icon="💼")
    assert len(data["collections"]) == 1
    assert data["collections"][0]["name"] == "Работа"
    assert data["collections"][0]["id"] == fid


def test_create_subfolder(tmp_data):
    data = d.default_data()
    d.create_folder(data, None, "Работа")
    coll = data["collections"][0]
    sid = d.create_folder(data, coll, "Проекты")
    assert len(coll["items"]) == 1
    assert coll["items"][0]["type"] == "subfolder"
    assert coll["items"][0]["id"] == sid


def test_add_item_and_remove(tmp_data):
    data = d.default_data()
    d.create_folder(data, None, "Работа")
    coll = data["collections"][0]
    iid = d.add_item(coll, "file", target="/tmp/a.pdf", name="a.pdf")
    assert len(coll["items"]) == 1
    assert d.remove_item(coll, iid) is True
    assert len(coll["items"]) == 0


def test_save_and_load(tmp_data):
    data = d.default_data()
    d.create_folder(data, None, "Работа")
    d.save_data(data)
    loaded = d.load_data()
    assert len(loaded["collections"]) == 1
    assert loaded["collections"][0]["name"] == "Работа"