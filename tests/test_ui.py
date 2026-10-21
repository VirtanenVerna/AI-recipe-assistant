from unittest.mock import MagicMock

from app.handlers import RecipeActions
from app.ui import build_theme, build_ui
from src.capabilities.memory import MemoryStore, MemoryWriteError
from src.services.ai_service import AIService


def test_forget_clears_editor_and_next_generation_does_not_restore_memory():
    client = MagicMock()
    client.generate.return_value = "recipe"
    service = AIService(client, MemoryStore())
    actions = RecipeActions(service)
    editor, _ = actions.save_saved("vegetarian")
    assert editor == "vegetarian"
    editor, status = actions.forget_saved(editor)
    assert editor == ""
    assert "cleared" in status
    actions.generate("chicken", "", 2, "No preference")
    assert not service.memory_store.path.exists()
    assert "vegetarian" not in client.generate.call_args.args[0]


def test_failed_forget_keeps_editor_and_restrictions(monkeypatch):
    service = AIService(MagicMock(), MemoryStore())
    actions = RecipeActions(service)
    actions.save_saved("vegetarian")
    def fail():
        raise MemoryWriteError("locked")
    monkeypatch.setattr(service.memory_store, "clear_preferences", fail)
    editor, status = actions.forget_saved("vegetarian")
    assert editor == "vegetarian"
    assert "could not be cleared" in status
    assert service.memory_store.get_preferences() == "vegetarian"


def test_load_prefills_and_escapes_saved_preferences():
    actions = RecipeActions(AIService(MagicMock(), MemoryStore()))
    actions.save_saved("<b>vegan</b>")
    editor, status = actions.load_saved()
    assert editor == "<b>vegan</b>"
    assert "&lt;b&gt;" in status
    assert "<b>" not in status


def test_forget_event_updates_editor_and_not_recipe_output():
    demo = build_ui(AIService(MagicMock(), MemoryStore()))
    assert demo.title == "AI Recipe Assistant"
    assert demo.analytics_enabled is False
    callback = next(fn for fn in demo.fns.values() if fn.api_name == "forget_preferences")
    assert callback.inputs[0] is callback.outputs[0]
    assert len(callback.outputs) == 2
    editor, status = callback.fn("vegetarian")
    assert editor == ""
    assert "cleared" in status


def test_recipe_generation_is_bound_once_for_each_user_action():
    demo = build_ui(AIService(MagicMock(), MemoryStore()))
    recipe_callbacks = [fn for fn in demo.fns.values() if fn.api_name == "recipe"]
    assert len(recipe_callbacks) == 1


def test_dark_theme_uses_high_contrast_text_and_surfaces():
    theme = build_theme()
    assert theme.body_text_color_dark == "#f5fbf6"
    assert theme.body_background_fill_dark == "#101b14"
    assert theme.input_background_fill_dark == "#203128"
