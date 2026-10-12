from pathlib import Path
from unittest.mock import patch

import pytest

from src.capabilities.memory import MemoryReadError, MemoryStore, MemoryWriteError


def test_missing_memory_is_empty():
    assert MemoryStore().get_preferences() == ""


def test_save_read_and_idempotent_clear():
    memory = MemoryStore()
    memory.save_preferences("  kasvisruoka, ei pähkinöitä  ")
    assert memory.get_preferences() == "kasvisruoka, ei pähkinöitä"
    memory.clear_preferences()
    memory.clear_preferences()
    assert memory.get_preferences() == ""
    assert not memory.path.exists()


@pytest.mark.parametrize("raw", [
    "[]", "null", "42", "{}", "{", '{"dietary_preferences":null}',
    '{"dietary_preferences":42}', '{"dietary_preferences":[]}',
])
def test_invalid_file_does_not_silently_drop_restrictions(raw):
    memory = MemoryStore()
    memory.path.write_text(raw, encoding="utf-8")
    with pytest.raises(MemoryReadError):
        memory.get_preferences()
    assert memory.path.read_text() == raw


def test_oversized_saved_value_is_rejected():
    memory = MemoryStore()
    memory.path.write_text('{"dietary_preferences":"' + "x" * 1001 + '"}')
    with pytest.raises(MemoryReadError):
        memory.get_preferences()


def test_utf8_bom_is_supported():
    memory = MemoryStore()
    memory.path.write_text('{"dietary_preferences":"vegan"}', encoding="utf-8-sig")
    assert memory.get_preferences() == "vegan"


def test_permission_error_is_not_treated_as_no_preferences():
    with patch.object(Path, "read_text", side_effect=PermissionError("denied")):
        with pytest.raises(MemoryReadError):
            MemoryStore().get_preferences()


def test_failed_replace_keeps_original_and_cleans_temporary_file():
    memory = MemoryStore()
    memory.save_preferences("vegetarian")
    original = memory.path.read_bytes()
    with patch("src.capabilities.memory.os.replace", side_effect=PermissionError("locked")):
        with pytest.raises(MemoryWriteError):
            memory.save_preferences("vegan")
    assert memory.path.read_bytes() == original
    assert not list(memory.path.parent.glob(f".{memory.path.name}.*.tmp"))


def test_delete_permission_error_keeps_existing_data():
    memory = MemoryStore()
    memory.save_preferences("vegetarian")
    with patch.object(Path, "unlink", side_effect=PermissionError("denied")):
        with pytest.raises(MemoryWriteError):
            memory.clear_preferences()
    assert memory.get_preferences() == "vegetarian"


def test_relative_memory_path_is_independent_of_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from src.config import PROJECT_ROOT
    assert MemoryStore("data/example.json").path == PROJECT_ROOT / "data/example.json"


@pytest.mark.parametrize("target", [
    "src.capabilities.memory.tempfile.NamedTemporaryFile",
    "src.capabilities.memory.json.dump",
    "src.capabilities.memory.os.fsync",
])
def test_write_permission_failure_preserves_original_and_cleans_temp(target):
    memory = MemoryStore()
    memory.save_preferences("no peanuts")
    original = memory.path.read_bytes()
    with patch(target, side_effect=PermissionError("denied")):
        with pytest.raises(MemoryWriteError) as caught:
            memory.save_preferences("vegan")
    assert isinstance(caught.value.__cause__, PermissionError)
    assert memory.path.read_bytes() == original
    assert not list(memory.path.parent.glob(f".{memory.path.name}.*.tmp"))


def test_parent_creation_permission_failure_is_reported(tmp_path):
    memory = MemoryStore(tmp_path / "nested" / "preferences.json")
    with patch.object(Path, "mkdir", side_effect=PermissionError("denied")):
        with pytest.raises(MemoryWriteError):
            memory.save_preferences("vegan")
    assert not memory.path.exists()


@pytest.mark.parametrize("value", [None, 5, [], "", "  ", "x" * 1001])
def test_invalid_save_is_rejected_before_filesystem_access(value):
    memory = MemoryStore()
    with patch.object(Path, "mkdir") as mkdir:
        with pytest.raises(ValueError):
            memory.save_preferences(value)
        mkdir.assert_not_called()
    assert not memory.path.exists()


def test_invalid_utf8_is_a_read_error():
    memory = MemoryStore()
    memory.path.write_bytes(b"\xff\xfe\x80")
    with pytest.raises(MemoryReadError):
        memory.get_preferences()


def test_replace_publishes_complete_json_in_destination_directory():
    import json
    import os

    memory = MemoryStore()
    memory.save_preferences("no peanuts")
    replace = os.replace

    def inspect_replace(source, destination):
        assert Path(source).parent == memory.path.parent
        assert Path(destination) == memory.path
        assert memory.get_preferences() == "no peanuts"
        assert json.loads(Path(source).read_text(encoding="utf-8")) == {
            "dietary_preferences": "vegan",
        }
        replace(source, destination)

    with patch("src.capabilities.memory.os.replace", side_effect=inspect_replace):
        memory.save_preferences("vegan")
    assert memory.get_preferences() == "vegan"
